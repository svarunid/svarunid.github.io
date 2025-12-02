FROM python:3.14-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY app ./app
COPY data ./data
COPY prompt.txt actions.txt zhura.db ./

EXPOSE 8000

CMD ["uv", "run", "fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
