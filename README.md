# Personal Website & Agent

This project is a monorepo containing my personal website and a sophisticated AI agent companion. The system is designed to be a living digital representation of myself, capable of interacting with visitors through a chat interface powered by a custom knowledge base.

## Repository Layout

The project is organized into two primary directories, separating the frontend presentation layer from the backend intelligence:

- **`client/`** - The frontend application
  - `src/` - Source files for the static site, including Liquid templates, TypeScript, and styles.
  - `eleventy.config.js` - Configuration for the Eleventy static site generator.
  - `vite.config.ts` - Configuration for Vite, handling asset bundling and HMR.
  - `package.json` - Frontend dependencies and build scripts.

- **`server/`** - The backend API and AI agent
  - `app/` - Core application logic.
    - `agent/` - The brain of the system, containing the Agent implementation, Knowledge Base management, and Tool definitions.
    - `core/` - Core infrastructure including Database connections and OpenRouter client.
    - `routes/` - FastAPI route definitions.
  - `data/` - Raw knowledge base files (Markdown) used to seed the agent's memory.
  - `zhura.db` - SQLite database storing embeddings and relational data.

## Architecture

### Client
The frontend is built on a hybrid architecture combining the best of static site generation and modern client-side tooling:
- **Eleventy (11ty)**: Handles the core content generation and templating (Liquid). It provides a fast, SEO-friendly foundation.
- **Vite**: Acts as the build tool and development server. It processes TypeScript and CSS, offering instant HMR (Hot Module Replacement) and optimized production builds.
- **TailwindCSS**: Used for utility-first styling, ensuring a consistent and responsive design system.

### Server
The backend is a **FastAPI** application designed to serve as the cognitive engine:
- **Agent Protocol**: Implements the **Model Context Protocol (MCP)** to standardize how the agent interacts with tools and resources.
- **Knowledge Base**: Uses **SQLite** with `sqliteai-vector` for efficient vector storage and retrieval. This allows the agent to perform semantic searches over my personal data (stored as Markdown).
- **LLM Integration**: Connects to **OpenRouter** to access various Large Language Models, allowing flexibility in choosing the best model for the task.
- **Dependency Management**: Uses **uv**, a fast Python package installer and resolver.

## Project Setup

### Prerequisites

Ensure you have the following installed:

- **Node.js 20+** & **pnpm**: For the frontend.
- **Python 3.13+**: For the backend.
- **uv**: For Python dependency management.
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### Configuration

1. **Server Environment**:
   Create a `.env` file in the `server/` directory. You can copy `.env.example` as a template.
   ```bash
   cp server/.env.example server/.env
   ```
   Required variables include `OPENROUTER_API_KEY` and database configurations.

## Getting Started

### 1. Server Setup

Initialize the backend environment and start the API server.

```bash
cd server
# Sync dependencies
uv sync

# Start the FastAPI development server
fastapi dev app/main.py
```
The server will be available at `http://127.0.0.1:8000`.

### 2. Client Setup

Install frontend dependencies and start the development server.

```bash
cd client
# Install dependencies
pnpm install

# Start the development server (runs Eleventy + Vite + Tailwind)
pnpm dev
```
The website will be available at `http://localhost:8080`.