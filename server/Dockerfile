FROM python:3.14-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY . .

RUN

EXPOSE 8000

CMD uv run python scripts/index_knowledge.py data/* && uv run fastapi run src/main.py
