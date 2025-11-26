import hashlib
import json
import re
import struct
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, TextIO

from sqlalchemy import JSON, Column, DateTime, LargeBinary, Text, text
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel, select

from ..core import Database, OpenRouterClient


class Content(SQLModel, table=True):
  id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
  meta: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
  content: str = Field(sa_column=Column(Text))
  chash: str = Field(sa_column=Column(Text))
  fhash: str = Field(sa_column=Column(Text))
  created_at: datetime = Field(sa_column=Column(DateTime, server_default=func.now()))
  updated_at: datetime = Field(sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now()))

  def __str__(self):
    return f"Content(id={self.id}, content={self.content})"

  def __repr__(self):
    return f"Content(id={self.id}, content={self.content})"

class Question(SQLModel, table=True):
  id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
  cid: str = Field(foreign_key="content.id")
  meta: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
  question: str = Field(sa_column=Column(Text))
  embedding: bytes = Field(sa_column=Column(LargeBinary))
  created_at: datetime = Field(sa_column=Column(DateTime, server_default=func.now()))

class MarkdownChunker:
  SECTION = re.compile(r'^(#{1,6})\s+(.*)')
  LINK = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
  IMG = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')

  def __call__(self, file: TextIO):
    def ri(m):
      alt, url = m.group(1), m.group(2)
      ref_num = len(cur["refs"]) + 1
      cur["refs"].append(f"[{ref_num}]: {url}")
      return f"![{alt}][{ref_num}]"

    def rl(m):
      alt, url = m.group(1), m.group(2)
      ref_num = len(cur["refs"]) + 1
      cur["refs"].append(f"[{ref_num}]: {url}")
      return f"[{alt}][{ref_num}]"

    chunks, cur = [], None
    for line in file:
      if not (line := line.strip()): continue
      m = self.SECTION.match(line)
      if m:
        if cur:
          chunks.append(f"{'\n'.join(cur['content'])}{('\n\n' + '\n'.join(cur['refs'])) if cur['refs'] else ''}")
        cur = {"content": [], "refs": []}
        continue
      line = self.LINK.sub(rl, line)
      line = self.IMG.sub(ri, line)
      cur["content"].append(line)

    if cur:
      chunks.append(f"{'\n'.join(cur['content'])}{('\n\n' + '\n'.join(cur['refs'])) if cur['refs'] else ''}")
    return chunks

class Embedder:
  def __init__(self, model: str, client: OpenRouterClient):
    self.model = model
    self.client = client

  async def get_dimension(self):
    emb = await self.client.embed(self.model, "abc")
    return len(emb)

  async def embed(self, text: str):
    return await self.client.embed(self.model, text)

class Knowledge:
  def __init__(
    self, db: Database, description: str, embedder: Embedder, model: str, client: OpenRouterClient,
    filters: Optional[Dict[str, Any]] = None
  ):
    self.db = db
    self.description = description
    self.embedder = embedder
    self.filters = filters

    self.model = model
    self.client = client

    self._initialized = False

  async def initialize(self):
    """Initialize vector extension for the Question table."""
    if self._initialized: return

    async with self.db.session() as dbs:
      dimension = await self.embedder.get_dimension()
      await dbs.exec(text(
        f"SELECT vector_init('question', 'embedding', 'dimension={dimension},type=FLOAT32,distance=cosine');"
      ))
      await dbs.commit()

    self._initialized = True

  async def search(self, query: str, k: int = 5, filter: Dict[str, Any] = None) -> List[Content]:
    """Search for relevant content using vector similarity."""
    await self.initialize()

    embedding = await self.embedder.embed(query)
    async with self.db.session() as dbs:
      if filter:
        conditions = " AND ".join([
          f"json_extract(q.meta, '$.{key}') = {f"'{value}'" if isinstance(value, str) else value}"
          for key, value in filter.items()
        ])

        query = f"""
          SELECT q.cid
          FROM vector_full_scan_stream('question', 'embedding', vector_as_f32(:query)) AS v
          JOIN question AS q ON q.rowid = v.rowid
          WHERE {conditions}
          ORDER BY v.distance ASC
          LIMIT :limit
        """
      else:
        query = """
          SELECT q.cid
          FROM vector_full_scan_stream('question', 'embedding', vector_as_f32(:query)) AS v
          JOIN question AS q ON q.rowid = v.rowid
          ORDER BY v.distance ASC
          LIMIT :limit
        """

      result = await dbs.exec(text(query), {"query": struct.pack(f"{len(embedding)}f", *embedding), "limit": k})
      questions = result.fetchall()

      if not questions: return []

      result = await dbs.exec(select(Content).where(Content.id.in_([q.cid for q in questions])))
      contents = result.all()

      return contents

  async def index(self, file: str, chunker: Callable):
    """Index a document by chunking, generating questions, and storing embeddings."""
    await self.initialize()
    with open(file, 'r', encoding='utf-8') as f:
      chunks = chunker(f)

    fhash = hashlib.sha256(file.encode()).hexdigest()
    async with self.db.session() as dbs:
      for chunk in chunks:
        chash = hashlib.sha256(chunk.encode()).hexdigest()

        result = await dbs.exec(select(Content).where(Content.chash == chash))
        if result.one_or_none(): continue

        content = Content(content=chunk, chash=chash, fhash=fhash, meta={"file": file})
        dbs.add(content)
        await dbs.flush()

        for question in await self._generate_questions(chunk):
          embedding = await self.embedder.embed(question["question"])
          dbs.add(Question(
            cid=content.id, question=question["question"], meta=question["metadata"],
            embedding=struct.pack(f"{len(embedding)}f", *embedding)
          ))
      await dbs.commit()

  async def _generate_questions(self, chunk: str) -> List[str]:
    prompt = """
    Given the text provided, generate a comprehensive array of questions that the text would answer.
    Return the response strictly as a valid JSON array objects with a `question` key containing the question.
    """

    format = {
      "type": "json_schema", "strict": "true", "name": "questions",
      "description": "A list of questions that the text would answer.",
      "schema": {
        "type": "array",
        "items": {
          "type": "object",
          "description": "A question that the text would answer.",
          "properties": {
            "question": {
              "type": "string",
              "description": "The question that the text would answer."
            }
          }
        }
      }
    }

    if self.filters:
      prompt += "\nTry to extract the metadata associated with the text given to you and include them in the `metadata` key of the JSON object."

      format["schema"]["items"]["properties"]["metadata"] = self.filters

    async for chunk in self.client.generate(
      self.model, [{"type": "message", "role": "user", "content": [{"type": "input_text", "text": chunk}]}],
      prompt=prompt, format=format
    ):
      match chunk.get("type"):
        case "message":
          try:
            return json.loads(chunk.get("message").get("content")[0].get("text"))
          except json.JSONDecodeError:
            raise ValueError("Failed to generate questions")
