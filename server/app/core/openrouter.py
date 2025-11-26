import json
from typing import Any, Dict, List, Optional

from openrouter import OpenRouter

from ..config import settings


class OpenRouterClient:
  """Client for interacting with the OpenRouter API.
  
  Provides methods for generating embeddings and streaming text generation
  with support for function calling and structured output formats.
  """
  def __init__(self, api_key: Optional[str] = None):
    """Initialize the OpenRouter client.
    
    Args:
      api_key: Optional API key for OpenRouter. If not provided, uses the
      key from application settings.
    """
    self._client = OpenRouter(api_key=api_key or settings.openrouter_api_key)

  async def embed(self, model: str, content: str) -> List[float]:
    """Generate embeddings for text content using OpenRouter API.
    
    Args:
      model: Name of the embedding model to use.
      content: Text content to generate embeddings for.
      
    Returns:
      List[float]: Vector embedding representation of the input text.
    """
    response = await self._client.embeddings.generate_async(
      model=model,
      input=content
    )
    return response.data[0].embedding

  async def generate(
    self, model: str, messages: List[Dict[str, Any]], prompt: Optional[str] = None,
    format: Optional[Dict[str, Any]] = None, tools: Optional[Dict[str, Any]] = None
  ):
    """Generate streaming text responses with optional function calling.
    
    Streams responses from the OpenRouter API, handling text deltas, function calls,
    and structured message outputs.
    
    Args:
      model: Name of the language model to use.
      messages: List of conversation messages in OpenRouter format.
      prompt: Optional system prompt to prepend to messages.
      format: Optional structured output format specification.
      tools: Optional dictionary of available tools for function calling.
      
    Yields:
      Dict[str, Any]: Stream events containing deltas, messages, or function calls.
        Event types include:
        - {"type": "delta", "delta": str}: Text generation delta.
        - {"type": "message", "message": dict}: Complete message object.
        - {"type": "functions", "functions": dict}: Function call results.
    """
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
