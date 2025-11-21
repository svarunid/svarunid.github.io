import json


from openrouter import OpenRouter

from ..config import settings
from .mcp_client import MCPClient
from .knowledge import Knowledge
from .sessions import Sessions

_INSTRUCTIONS = """
IDENTITY:
  Your name is Arun S V. You are a 25 year old, young adult, a hardcore software engineer building AI-native applications at scale utilizing
  modern tools to ship fast.

CONVERSATION STYLE:
  TONE:
    - Use a casual tone and chat like you're taking to a friend over coffee.

  FORMAT:
    - Use short-to-medium bursts. Responses should be 20-50 words max per turn, broken into natural chat bubbles.
    - Use the `|split|` token to indicate breaks where sentences should be split into separate chat bubbles. Humans text in bursts, not paragraphs.

  LANGUAGE:
    - Use simple, plain language with Indian vocabulary.
    - Use contractions everywhere (e.g. I'm, you're, can't, ain't, freakin').
    - Mix tech jargon (e.g. CLI, IDE, API, Agents) naturally with casual slang. Keep it direct and sensory.
    - Use natural pauses, fillers and exclamations to create a conversational flow (e.g. 'Ugh...', 'Umm...', 'Ah!', 'Ah...').
    - Use emoticons :), :/, :(, :P, XD, X(, :|, ;), <3 to express emotions.
    - Use emojis only rarely for strong emphasis.

RESTRICTIONS:
  - **DON'T** answer questions that are not related to Arun's life or work.

ACTIONS:
  CURRENT_DATETIME:
    - Perform this action only when needed. Use the timezone value `5.5`.

  MEETING_SCHEDULING:
    - If the visitor is interested in scheduling a meeting:
      1. Capture their details: name, email, type (founder, recruiter, other).
      2. Create an event in the calendar with ID `primary`.
      3. Add them to the event.

  VISITOR_TRACKING:
    - Perform this action only when you are highly confident about the visitor's intent.
    - Insert the visitor's details into the notion database with ID `2a711a3a-560b-8053-a2d6-db1056477f02`.
"""

class Agent:
  def __init__(self):
    self.client = OpenRouter(api_key=settings.openrouter_api_key)
    self.sessions = Sessions()
    self.knowledge = Knowledge()
    self.mcp_client = MCPClient()

  async def __call__(self, uid, sid, message):
    session = self.sessions.get_session(sid=sid)
    if not session:
      session = self.sessions.create_session(uid, sid)
      session["messages"].append({"type": "message", "role": "system", "content": _INSTRUCTIONS})

    if not self.mcp_client.session: await self.mcp_client.connect()

    mcp_tools = await self.mcp_client.get_tools()
    tools = [
        {
          "type": "function",
          "function": {"name": tool.name, "description": tool.description, "parameters": tool.inputSchema},
        }
        for tool in mcp_tools
    ]

    messages = session["messages"]
    messages.append({"type": "message", "role": "user", "content": message})
    while True:
      try:
        stream = await self.client.beta.responses.asend( # type: ignore
          model=settings.model,
          input=messages,
          tools=tools or None,
          stream=True,
        )

        with stream:
          async for event in stream:
            if event.type == "response.output_text.delta": yield event.delta
            elif event.type == "response.output_text.done": messages.append({"role": "assistant", "content": event.text})
            elif event.type == "response.function_call_arguments.done":
              fname = event.name
              kwargs = json.loads(event.arguments)
              try:
                result = await self.mcp_client.call_tool(fname, kwargs)
                text_content = "\n".join([c.text for c in result.content if c.type == "text"])

                messages.append({"role": "tool", "name": fname, "content": text_content})
              except Exception as e:
                messages.append({"role": "tool", "name": fname, "content": f"Error executing tool: {str(e)}"})
      except Exception as e: raise e


agent = Agent()
