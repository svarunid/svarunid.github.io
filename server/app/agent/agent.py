import json
from typing import Any, Dict, List, Optional, Union

from ..core import OpenRouterClient
from .knowledge import Knowledge
from .sessions import Sessions
from .tools import FunctionTool, MCPTool


class Agent:
  """AI agent for managing conversational interactions.

  Orchestrates conversations using language models with support for:
  - Function/tool calling via MCP and custom functions
  - Knowledge base semantic search
  - Session persistence and management
  - Streaming response generation

  Attributes:
    model: Name of the language model to use.
    client: OpenRouter API client for model interactions.
    sessions: Session manager for conversation persistence.
    instructions: System instructions/prompt for the agent.
    tools: Optional list of tools (FunctionTool or MCPTool) available to the agent.
    knowledge: Optional knowledge base for semantic search.
    is_initialized: Flag indicating if the agent has been initialized.
  """
  def __init__(
    self, model: str, client: OpenRouterClient, instructions: str, sessions: Sessions,
    knowledge: Optional[Knowledge] = None, tools: Optional[List[Union[FunctionTool, MCPTool]]] = None
  ):
    self.model = model
    self.client = client
    self.sessions = sessions
    self.instructions = instructions

    self.tools = tools
    self.knowledge = knowledge
    if tools:
      self._tools = {}

    self.is_initialized = False

  async def initialize(self):
    """Initialize the agent by setting up tools and knowledge base.

    Connects to MCP tools, registers function tools, and initializes the knowledge
    base. Updates system instructions with available tools and knowledge base info.
    Should be called once before using the agent.
    """
    if self.is_initialized: return

    if self.knowledge:
      await self.knowledge.initialize()
      self.instructions += "\n\n" + f"""
      # KNOWLEDGE BASE
      The knowledge base is an information pool available to for you to perform semantic search and retrieve
      relevant information to answer the user's query.

      A list of available knowledge bases:
      - {self.knowledge.description}
      """
      search_knowledge_tool = FunctionTool(
        name="search_knowledge",
        description="Performs semantic search to find information that best answers the given query.",
        parameters={
          "type": "object",
          "properties": {
            "query": {
              "type": "string",
              "description": "The natural-language question used to retrieve semantically relevant information."
            },
            "k": {
              "type": "integer",
              "description": "Number of top results to return (default: 5)."
            },
          },
          "required": ["query"]
        },
        function=self.knowledge.search,
      )

      if self.knowledge and self.knowledge.filters:
        search_knowledge_tool.parameters["properties"]["filter"] = {
          "type": "object",
          "description": "Additional field-level constraints that restrict which knowledge entries can be returned.",
          "properties": self.knowledge.filters,
        }
        search_knowledge_tool.parameters["required"].append("filter")

      if self.tools: self.tools.append(search_knowledge_tool)
      else: self.tools = [search_knowledge_tool]


    if self.tools:
      tool_instructions = "\n\n" + """
      # TOOLS
      Tools allow you to perform actions via function calls. Call appropriate tools based on the instructions and the user's query.

      ## TOOL INSTRUCTIONS
      """
      tool_has_instructions = False
      for t in self.tools:
        if isinstance(t, FunctionTool):
          self._tools[t.name] = t
        elif isinstance(t, MCPTool):
          await t.connect()
          if t.instructions:
            tool_has_instructions = True
            tool_instructions += "\n- " + t.instructions
          for m in await t.get_tools():
            self._tools[m.name] = m

      if tool_has_instructions:
        self.instructions += tool_instructions

    self.is_initialized = True

  async def close(self):
    """Clean up agent resources.

    Closes connections to MCP tools and performs cleanup.
    Should be called during application shutdown.
    """
    if not self.is_initialized: return

    if self.tools:
      for t in self.tools:
        if isinstance(t, MCPTool):
          await t.close()

    self.is_initialized = False

  async def _generate_with_functions(self, messages: List[Dict[str, Any]]):
    """Generate responses with function calling support.

    Internal method that handles streaming generation with automatic function
    execution. When functions are called, executes them and recursively continues
    generation with the results.

    Args:
      session: Session object containing conversation messages.

    Yields:
      str: Text deltas from the streaming response.
    """
    async for chunk in self.client.generate(
      self.model, [{k: v for k, v in m.items() if k != "context"} for m in messages],
      prompt=self.instructions, tools={k: v.to_dict() for k, v in self._tools.items()}
    ):
      match chunk.get("type"):
        case "delta":
          yield chunk.get("delta")
        case "message":
          messages.append(chunk.get("message"))
        case "functions":
          functions = chunk.get("functions")
          messages.extend(functions)
          for f in functions:
            messages.append({
              "id": f["id"], "type": "function_call_output", "call_id": f["call_id"],
              "output": await self._tools[f["name"]](**json.loads(f["arguments"]))
            })

          async for nested_chunk in self._generate_with_functions(messages):
            yield nested_chunk

  async def __call__(self, uid: str, sid: str, message: str):
    """Process a user message and generate a streaming response.

    Main entry point for agent interactions. Retrieves or creates a session,
    adds the user message, and generates a streaming response.

    Args:
      uid: User identifier.
      sid: Session identifier.
      message: User's message text.

    Yields:
      str: Text deltas from the streaming response.
    """
    session = await self.sessions.get_session(sid=sid)
    if not session: session = await self.sessions.create_session(uid, sid)
    print(f"Session: ", session)

    messages = session.messages + [{ # type: ignore
      "type": "message", "role": "user", "content": [{"type": "input_text", "text": message}]
    }]

    async for chunk in self._generate_with_functions(messages):
      yield chunk
    await self.sessions.update_session(sid, messages) # type: ignore
