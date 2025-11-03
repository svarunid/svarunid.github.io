# AGENTS.md (Server)
This file contains server-specific guidelines for AI coding agents working on the backend of Zhura.

## Technical Guidelines

### Python Environment & Tooling
[uv](https://docs.astral.sh/uv/) is the default python project manager.

- Use the `uv init <options> <path>` command to create a new project. This will create a project structure and follow `pyproject.toml` specification. Also initializes git repository.
  - Add the `--app` (default behavior) flag to create a project for an application (intended for web servers and command-line tools & scripts).
  - Add the `--bare` flag to only create a pyproject.toml. Disables creating extra files like `README.md`, the `src/` tree, `.python-version` files, etc.
  - Use `--name` to specify the name of the project.
- Use `uv add <options> <packages>` to install project dependencies. Alternatively, use `uv remove <packages>` to uninstall them.
  - Add `--dev` to install packages as development dependencies.
  - Use `--group` to specify a group name for the package. This is useful for organizing dependencies into logical groups, such as "dev", "test", "prod", etc.
- Using `uv sync <options>` ensures that all project dependencies are installed and up-to-date with the lockfile.
  - Add `--upgrade` to allow package upgrades, ignoring pinned versions in any existing output file.
- Use `uv run <filename>.py` or `uv run <command>` to run the script or python or package commands in the project environment.
- Use `uvx ruff check` to invoke the ruff linter to check issues in the project.
  - Add `--fix` flag to fix any fixable errors.
  - Add `--watch` flag to re-lint on file changes.
  - Use `--select` to select rule sets.
- Use `uvx ruff format` to automatically format the codebase according to the Ruff style guide.

### Backend
The project's backend hosts all the functionalities related to database access, agent interface, calling third-party services, and more. It is built on Python with FastAPI & Agno (for agents).

#### FastAPI
- Use type hints for all function parameters and return values
- Use Pydantic models for request and response validation
- Use appropriate HTTP methods with path operation decorators (@app.get, @app.post, etc.)
- Use dependency injection for shared logic like database connections and authentication
- Use background tasks for non-blocking operations
- Use proper status codes for responses (201 for creation, 404 for not found, etc.)
- Use APIRouter for organizing routes by feature or resource
- Use path parameters, query parameters, and request bodies appropriately
- Use environment variables for sensitive information like API keys and database credentials

Use the context7 MCP server with library ID `websites/fastapi_tiangolo` to refer to the FastAPI library.

#### Agno
Agno is a Python framework for building multi-agent systems with memory & tools.

Use the contex7 MCP server with library ID `websites/agno` to refer to the Agno library.
