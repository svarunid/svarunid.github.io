from typing import List, Optional, Union

from ..core import OpenRouterClient
from .knowledge import Knowledge
from .sessions import Sessions
from .tools import FunctionTool, MCPTool


class Agent:
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
    if self.is_initialized: return

    if self.tools:
      self.instructions += "\n\n" + """
      # TOOLS
      Tools allow you to perform actions via function calls. Call appropriate tools based on the instructions and the user's query.

      A list of available tools:
      """
      for t in self.tools:
        if isinstance(t, FunctionTool):
          self._tools[t.name] = t
        elif isinstance(t, MCPTool):
          await t.connect()
          self.instructions += "\n- " + t.instructions
          for m in await t.get_tools():
            self._tools[m.name] = m

    if self.knowledge:
      await self.knowledge.initialize()
      self.instructions += "\n\n" + f"""
      # KNOWLEDGE BASE
      The knowledge base is an information pool available to for you to perform semantic search and retrieve
      relevant information to answer the user's query.

      A list of available knowledge bases:
      - {self.knowledge.description}
      """
      self._tools["search_knowledge"] = FunctionTool(
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

      if self.knowledge.filters:
        self._tools["search_knowledge"].parameters["properties"]["filter"] = {
          "type": "object",
          "description": "Additional field-level constraints that restrict which knowledge entries can be returned.",
          "properties": self.knowledge.filters,
        }
        self._tools["search_knowledge"].parameters["required"].append("filter")

    self.is_initialized = True

  async def close(self):
    if not self.is_initialized: return

    for t in self.tools:
      if isinstance(t, MCPTool):
        await t.close()

    self.is_initialized = False

  async def _generate_with_functions(self, session):
    async for chunk in self.client.generate(
      self.model, [{k: v for k, v in m.items() if k != "context"} for m in session.messages],
      prompt=self.instructions, tools=self._tools
    ):
      match chunk.get("type"):
        case "delta":
          yield chunk.get("delta")
        case "message":
          session.messages.append(chunk.get("message"))
        case "functions":
          functions = chunk.get("functions")
          session.messages.extend(functions)
          for f in functions:
            session.messages.append({
              "id": f["id"], "type": "function_call_output", "call_id": f["call_id"],
              "output": await self._tools[f["name"]](**f["arguments"])
            })

          async for nested_chunk in self._generate_with_functions(session):
            yield nested_chunk

  async def __call__(self, uid: str, sid: str, message: str):
    message = {"type": "message", "role": "user", "content": [{"type": "input_text", "text": message}]}

    session = await self.sessions.get_session(sid=sid)
    if not session: session = await self.sessions.create_session(uid, sid)

    session.messages.append(message)
    try:
      async for chunk in self._generate_with_functions(session):
        yield chunk

    except Exception as e:
      print(e)