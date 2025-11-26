import inspect
from contextlib import AsyncExitStack
from functools import partial
from typing import Any, Callable, Dict, List, Optional

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import CallToolResult


class FunctionTool:
  def __init__(self, name: str, description: str, parameters: Dict[str, Any], function: Callable):
    if not callable(function): raise ValueError(f"Tool {name} is not callable")

    self.name = name
    self.description = description
    self.parameters = parameters
    self.function = function

  def to_dict(self) -> Dict[str, Any]:
    return {"type": "function", "name": self.name, "description": self.description, "parameters": self.parameters}

  async def __call__(self, **kwargs: Any) -> Any:
    if inspect.iscoroutinefunction(self.function): return await self.function(**kwargs)
    return self.function(**kwargs)


class MCPTool:
  def __init__(self, url: str, instructions: Optional[str]):
    self.url = url
    self.instructions = instructions
    self.session: Optional[ClientSession] = None
    self.exit_stack = AsyncExitStack()

  async def connect(self):
    try:
      read_stream, write_stream, _ = await self.exit_stack.enter_async_context(
        streamablehttp_client(self.url)
      )

      self.session = await self.exit_stack.enter_async_context(
        ClientSession(read_stream, write_stream)
      )
      await self.session.initialize()
    except Exception as e:
      print(f"Failed to connect to MCP server: {e}")
      raise e

  async def close(self):
    await self.exit_stack.aclose()

  async def get_tools(self) -> List[FunctionTool]:
    if not self.session: raise RuntimeError("MCP Tool not connected")
    result = await self.session.list_tools()
    return [
      FunctionTool(t.name, t.description, t.inputSchema, partial(self.call_tool, t.name))
      for t in result.tools
    ]

  async def call_tool(self, name: str, **arguments: Any) -> CallToolResult:
    if not self.session: raise RuntimeError("MCP Tool not connected")
    return await self.session.call_tool(name, arguments)
