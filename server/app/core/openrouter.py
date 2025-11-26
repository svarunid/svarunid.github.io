import json
from typing import Any, Dict, List, Optional

from openrouter import OpenRouter

from ..config import settings


class OpenRouterClient:
  def __init__(self, api_key: Optional[str] = None):
    self._client = OpenRouter(api_key=api_key or settings.openrouter_api_key)

  async def embed(self, model: str, content: str) -> List[float]:
    """Generate embeddings for text content using OpenRouter API."""
    response = await self._client.embeddings.generate_async(
      model=model,
      input=content
    )
    return response.data[0].embedding

  async def generate(
    self, model: str, messages: List[Dict[str, Any]], prompt: Optional[str] = None,
    format: Optional[Dict[str, Any]] = None, tools: Optional[Dict[str, Any]] = None
  ):
    if prompt: messages = [{"type": "message", "role": "system", "content": [{"type": "input_text", "text": prompt}]}] + messages

    stream = await self._client.beta.responses.send_async(
      model=model, stream=True, input=messages,
      tools=list(tools.values()) if tools else [],
      text={"format": format} if format else None
    )

    functions = {}
    async with stream:
      async for event in stream:
        match event.type:
          case "response.created": pass
          case "response.in_progress": pass
          case "response.output_item.added":
            item = event.item
            if item.type == "function_call":
              functions[item.id] = {"id": item.id, "type": item.type, "name": item.name, "call_id": item.call_id}
          case "response.function_call_arguments.done":
            functions[event.item.id]["arguments"] = json.loads(event.item.arguments)
          case "response.output_text.delta":
            yield {"type": "delta", "delta": event.delta}
          case "response.output_text.done": pass
          case "response.output_item.done":
            item = event.item
            if item.type == "message":
              yield {"type": "message", "message": item.model_dump()}
          case "response.completed":
            yield {"type": "functions", "functions": functions}
