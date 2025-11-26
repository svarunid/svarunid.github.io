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
  """Database model for storing document content chunks.
  
  Attributes:
    id: Unique identifier for the content.
    meta: Metadata dictionary for additional information.
    content: The actual text content.
    chash: SHA-256 hash of the content for deduplication.
    fhash: SHA-256 hash of the source file.
    created_at: Timestamp when the content was created.
    updated_at: Timestamp when the content was last updated.
  """
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
  """Database model for storing generated questions with embeddings.
  
  Each question is associated with a content chunk and includes a vector
  embedding for semantic search.
  
  Attributes:
    id: Unique identifier for the question.
    cid: Foreign key reference to the associated Content.
    meta: Metadata dictionary for filtering and categorization.
    question: The question text.
    embedding: Binary-encoded vector embedding of the question.
    created_at: Timestamp when the question was created.
  """
  id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
  cid: str = Field(foreign_key="content.id")
  meta: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
  question: str = Field(sa_column=Column(Text))
  embedding: bytes = Field(sa_column=Column(LargeBinary))
  created_at: datetime = Field(sa_column=Column(DateTime, server_default=func.now()))

class MarkdownChunker:
  """Chunk markdown documents by sections with reference link normalization.
  
  Splits markdown content by headers and converts inline links and images
  to reference-style links for cleaner chunking.
  """
  SECTION = re.compile(r'^(#{1,6})\s+(.*)')
  LINK = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
  IMG = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')

  def __call__(self, file: TextIO):
    """Chunk a markdown file into sections.
    
    Args:
      file: Text file object containing markdown content.
      
    Returns:
      List[str]: List of markdown content chunks, one per section.
    """
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
  """Generate vector embeddings using OpenRouter API.
  
  Attributes:
    model: Name of the embedding model to use.
    client: OpenRouter client for API interactions.
  """
  def __init__(self, model: str, client: OpenRouterClient):
    self.model = model
    self.client = client

  async def get_dimension(self):
    """Get the dimensionality of the embedding model.
    
    Returns:
      int: Number of dimensions in the embedding vector.
    """
    emb = await self.client.embed(self.model, "abc")
    return len(emb)

  async def embed(self, text: str):
    """Generate an embedding vector for the given text.
    
    Args:
      text: Text content to embed.
      
    Returns:
      List[float]: Vector embedding of the text.
    """
    return await self.client.embed(self.model, text)

class Knowledge:
  """Knowledge base with vector search and automatic question generation.
  
  Manages a knowledge base by indexing documents, generating questions,
  and providing semantic search capabilities using vector embeddings.
  
  Attributes:
    db: Database instance for storage.
    description: Human-readable description of the knowledge base.
    embedder: Embedder instance for generating vectors.
    filters: Optional schema for metadata filtering.
    model: Name of the language model for question generation.
    client: OpenRouter client for API interactions.
  """
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
    """Initialize the vector search extension for the Question table.
    
    Sets up the sqlite-vector extension with the appropriate dimension
    for the embedding model. Should be called once before using the knowledge base.
    """
    if self._initialized: return

    async with self.db.session() as dbs:
      dimension = await self.embedder.get_dimension()
      await dbs.exec(text(
        f"SELECT vector_init('question', 'embedding', 'dimension={dimension},type=FLOAT32,distance=cosine');"
      ))
      await dbs.commit()

    self._initialized = True

  async def search(self, query: str, k: int = 5, filter: Dict[str, Any] = None) -> List[Content]:
    """Search for relevant content using vector similarity.
    
    Performs semantic search by embedding the query and finding the most similar
    questions in the database, then returning their associated content.
    
    Args:
      query: Natural language search query.
      k: Number of top results to return (default: 5).
      filter: Optional metadata filters to constrain results.
      
    Returns:
      List[Content]: List of matching content chunks ordered by relevance.
    """
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
    """Index a document by chunking, generating questions, and storing embeddings.
    
    Processes a document by:
    1. Chunking the content using the provided chunker
    2. Generating questions that each chunk would answer
    3. Creating vector embeddings for each question
    4. Storing everything in the database
    
    Args:
      file: Path to the document file to index.
      chunker: Callable that takes a file object and returns content chunks.
    """
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
    """Generate questions that a content chunk would answer.
    
    Uses the language model to generate comprehensive questions with optional
    metadata extraction based on the configured filters.
    
    Args:
      chunk: Text content to generate questions for.
      
    Returns:
      List[str]: List of generated questions with metadata.
      
    Raises:
      ValueError: If the model fails to generate valid JSON output.
    """
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
