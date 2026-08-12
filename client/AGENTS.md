# AGENTS.md (Client)

Instructions for coding agents working on the portfolio frontend.

## Design direction

Use dense information architecture with a minimal visual language:

- Prefer semantic HTML, high information density, and restrained decoration.
- Use monospace typography where it supports scanning and alignment.
- Follow an 8px spacing rhythm and use subtle one-pixel boundaries.
- Maintain WCAG AA contrast and visible keyboard focus states.
- Keep layouts fluid and content-first across mobile and desktop sizes.
- Avoid unnecessary motion and respect `prefers-reduced-motion`.

## Architecture

- Eleventy renders HTML from Liquid templates and JSON data.
- Vite processes browser assets and integrates Tailwind CSS v4.
- TypeScript is available for interactive browser components, including a future agent UI.
- The frontend must remain deployable as a static GitHub Pages artifact.
- Agent credentials and model calls must never be placed in client code. A future agent should call a separately deployed API.

Do not add React, TanStack, or another application framework for an isolated interactive component. Reconsider that choice only if the portfolio becomes a predominantly dynamic application.

## Development

- Use the Node.js and pnpm versions pinned in the repository's `mise.toml`.
- Use `pnpm`; do not use npm or Yarn.
- Use the scripts declared in `package.json` rather than introducing parallel commands.
- Do not start the development server or run a build unless the user explicitly requests it.
- Run `pnpm typecheck` when TypeScript is changed and the user has authorized validation.
- Tailwind v4 configuration belongs in `src/styles/site.css`; do not add a JavaScript Tailwind configuration without a concrete need.
- Prefer static Liquid rendering for portfolio content and TypeScript only for genuine client interaction.
