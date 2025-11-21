from fastapi import Depends, Header, Request
from typing import Annotated

from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse

from ..core.agent import Agent, agent


router = APIRouter()

@router.post("/chat")
async def chat(
  request: Request, agent: Annotated[Agent, Depends(lambda: agent)],
  x_chat_uid: str | None = Header(None, alias="X-Chat-UID"),
  x_chat_sid: str | None = Header(None, alias="X-Chat-SID")
) -> StreamingResponse:
  ...
