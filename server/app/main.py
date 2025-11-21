from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings

app = FastAPI()

app.add_middleware(
  CORSMiddleware,  # type: ignore
  allow_origins=["localhost:8080", settings.frontend_url],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)
