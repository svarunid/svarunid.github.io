from contextlib import AsyncExitStack
from typing import Any, Optional

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.types import CallToolResult, Tool

from ..config import settings


class MCPClient:
  def __init__(self):
    self.session: Optional[ClientSession] = None
    self.exit_stack = AsyncExitStack()

  async def connect(self):
    """Connect to the MCP server via Streamable HTTP."""
    try:
      read_stream, write_stream = await self.exit_stack.enter_async_context(
        streamable_http_client(settings.composio_mcp_url)
      )

      self.session = await self.exit_stack.enter_async_context(
        ClientSession(read_stream, write_stream)
      )
      await self.session.initialize()
      return self
    except Exception as e:
      print(f"Failed to connect to MCP server: {e}")
      raise e

  async def get_tools(self) -> list[Tool]:
    """List available tools from the MCP server."""
    if not self.session: raise RuntimeError("MCP Client not connected")
    return await self.session.list_tools().tools

  async def call_tool(self, name: str, arguments: dict[str, Any]) -> CallToolResult:
    """Call a tool on the MCP server."""
    if not self.session: raise RuntimeError("MCP Client not connected")
    return await self.session.call_tool(name, arguments)

  async def close(self):
    """Close the connection."""
    await self.exit_stack.aclose()
