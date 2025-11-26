from pydantic_settings import BaseSettings


class Settings(BaseSettings):
  db: str
  model: str
  embedding_model: str
  composio_mcp_url: str
  openrouter_api_key: str
  frontend_url: str

settings = Settings() # type: ignore
