import inspect
import json
from contextlib import AsyncExitStack
from functools import partial
from typing import Any, Callable, Dict, List, Optional

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import CallToolResult


class FunctionTool:
  """Wrapper for custom Python functions as agent tools.

  Encapsulates a Python function with metadata for use as an agent tool,
  supporting both synchronous and asynchronous functions.

  Attributes:
    name: Unique identifier for the tool.
    description: Human-readable description of what the tool does.
    parameters: JSON schema describing the function parameters.
    function: The callable function to execute.
  """
  def __init__(self, name: str, description: str, parameters: Dict[str, Any], function: Callable):
    if not callable(function): raise ValueError(f"Tool {name} is not callable")

    self.name = name
    self.description = description
    self.parameters = parameters
    self.function = function

  def to_dict(self) -> Dict[str, Any]:
    """Convert the tool to a dictionary representation.

    Returns:
      Dict[str, Any]: Dictionary with tool metadata in OpenRouter format.
    """
    return {"type": "function", "name": self.name, "description": self.description, "parameters": self.parameters}

  async def __call__(self, **kwargs: Any) -> Any:
    """Execute the tool function with the provided arguments.

    Automatically handles both sync and async functions.

    Args:
      **kwargs: Keyword arguments to pass to the function.

    Returns:
      Any: The return value of the function.
    """
    if inspect.iscoroutinefunction(self.function): return await self.function(**kwargs)
    return self.function(**kwargs)


class MCPTool:
  """Client for Model Context Protocol (MCP) server integration.

  Connects to an MCP server and exposes its tools to the agent.
  Manages the connection lifecycle and tool invocation.

  Attributes:
    url: URL of the MCP server.
    instructions: Instructions for using the MCP tools.
    session: Active MCP client session (None until connected).
    exit_stack: Async context manager stack for resource cleanup.
  """
  def __init__(self, url: str, instructions: Optional[str]):
    self.url = url
    self.instructions = instructions
    self.session: Optional[ClientSession] = None
    self.exit_stack = AsyncExitStack()

  async def connect(self):
    """Establish connection to the MCP server.

    Initializes the MCP client session and prepares for tool invocation.
    Should be called before using get_tools() or call_tool().

    Raises:
      Exception: If connection to the MCP server fails.
    """
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
    """Close the MCP server connection and clean up resources.

    Should be called during agent shutdown to properly release resources.
    """
    await self.exit_stack.aclose()

  async def get_tools(self) -> List[FunctionTool]:
    """Retrieve available tools from the MCP server.

    Returns:
      List[FunctionTool]: List of function tools available from the MCP server.

    Raises:
      RuntimeError: If called before connect() or if not connected.
    """
    if not self.session: raise RuntimeError("MCP Tool not connected")
    result = await self.session.list_tools()
    return [
      FunctionTool(t.name, t.description if t.description else "", t.inputSchema, partial(self.call_tool, t.name))
      for t in result.tools
    ]

  async def call_tool(self, name: str, **arguments: Any) -> str:
    """Invoke a tool on the MCP server.

    Args:
      name: Name of the tool to invoke.
      **arguments: Keyword arguments to pass to the tool.

    Returns:
      CallToolResult: Result from the MCP tool execution.

    Raises:
      RuntimeError: If called before connect() or if not connected.
    """
    if not self.session: raise RuntimeError("MCP Tool not connected")
    result = await self.session.call_tool(name, arguments)
    return json.dumps([c.model_dump() for c in result.content])
