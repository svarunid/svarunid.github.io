import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .agent import Agent, MCPTool, Sessions
from .agent.knowledge import Embedder, Knowledge, MarkdownChunker
from .config import settings
from .core import Database, OpenRouterClient
from .routes import admin
from .utils import generate_device_uid


@asynccontextmanager
async def lifespan(app: FastAPI):
  app.state.db = Database(settings.db)
  await app.state.db.initialize()

  client = OpenRouterClient(settings.openrouter_api_key)
  knowledge = Knowledge(
    db=app.state.db, model=settings.model, client=client,
    embedder=Embedder(settings.embedding_model, client),
    description="A pool of Arun's personal & professional information",
    filters={
      "section": {
        "type": "string",
        "description": "Indicates the category to which the information belongs.",
        "enum": ["personal", "education", "work", "productivity", "tools", "goals", "philosophy", "work-style"]
      }
    }
  )
  await knowledge.index("data/journey.md", MarkdownChunker())

  with open("actions.txt", "r") as f:
    actions = f.read()

  tools = [
    MCPTool(
      url=settings.composio_mcp_url,
      instructions=actions,
    )
  ]

  with open("prompt.txt", "r") as f:
    instructions = f.read()

  app.state.agent = Agent(
    model=settings.model, client=client, instructions=instructions,
    sessions=Sessions(app.state.db), knowledge=knowledge, tools=tools,
  )
  await app.state.agent.initialize()
  yield
  await app.state.agent.close()
  await app.state.db.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
  CORSMiddleware,  # type: ignore
  allow_origins=["http://127.0.0.1:8080", "http://localhost:8080", settings.frontend_url],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
  expose_headers=["X-Chat-UID", "X-Chat-SID"],
)

app.include_router(admin.router)

@app.post("/chat")
async def chat(
  request: Request,
  x_chat_uid: str | None = Header(None, alias="X-Chat-UID"),
  x_chat_sid: str | None = Header(None, alias="X-Chat-SID")
) -> StreamingResponse:
  if not x_chat_uid: x_chat_uid = generate_device_uid(request)
  if not x_chat_sid: x_chat_sid = str(uuid.uuid4())

  body = await request.json()
  return StreamingResponse(
    app.state.agent(x_chat_uid, x_chat_sid, body["message"]),
    headers={"X-Chat-UID": x_chat_uid, "X-Chat-SID": x_chat_sid}
  )

@app.post("/voice")
async def voice(
  request: Request,
  x_chat_uid: str | None = Header(None, alias="X-Chat-UID"),
  x_chat_sid: str | None = Header(None, alias="X-Chat-SID")
) -> StreamingResponse:
  pass
