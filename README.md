# Personal Website

Static portfolio for Arun S V, generated with Eleventy and deployed to GitHub Pages.

## Architecture

- **Eleventy + Liquid** render the portfolio from templates and JSON data.
- **Vite** handles the development server and browser assets.
- **Tailwind CSS** provides styling through its Vite plugin.
- **TypeScript** is retained for future interactive features such as an agent chat component.

The portfolio remains a static frontend. If the agent returns, its model calls, secrets, rate limiting, and optional conversation storage should live in a separately deployed API service.

## Repository layout

```text
client/
  src/
    _data/       Portfolio content
    _includes/   Liquid components
    styles/      Tailwind entry stylesheet
  eleventy.config.js
  package.json
.github/workflows/
```

Keeping the frontend under `client/` leaves room for a future `server/` without turning the repository into a workspace prematurely.

## Development

Requirements:

- [Volta](https://volta.sh/) with experimental pnpm support enabled by setting
  `VOLTA_FEATURE_PNPM=1`.

The project pins Node.js 24.18.0 and pnpm 10.20.0 in `client/package.json`. Volta selects both automatically while working inside `client/`; CI uses the same pins.

```bash
cd client
pnpm install
pnpm dev
```

The development site is available at `http://localhost:8080`.

## Commands

- `pnpm dev` — run Eleventy with the Vite-powered development server.
- `pnpm build` — generate the production site in `client/dist`.
- `pnpm typecheck` — check browser TypeScript without emitting files.
- `pnpm format` — format source and configuration files.
- `pnpm format:check` — verify formatting without changing files.

GitHub Actions validates pushes and pull requests. Deployment remains explicit and occurs for tags matching `pages-v*`.
