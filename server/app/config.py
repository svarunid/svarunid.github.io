from pydantic_settings import BaseSettings


class Settings(BaseSettings):
  """Application configuration settings loaded from environment variables.
  
  Attributes:
    db: Database connection string or path.
    model: Name of the AI model to use for generation.
    embedding_model: Name of the model to use for embeddings.
    composio_mcp_url: URL for the Composio MCP server.
    openrouter_api_key: API key for OpenRouter service.
    frontend_url: URL of the frontend application for CORS.
  """
  db: str
  model: str
  embedding_model: str
  composio_mcp_url: str
  openrouter_api_key: str
  frontend_url: str

settings = Settings() # type: ignore
