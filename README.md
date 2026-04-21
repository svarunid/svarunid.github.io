# Personal Website

This repository contains my personal website.

## Repository Layout

- **`client/`** - The frontend application
  - `src/` - Source files for the static site, including Liquid templates, TypeScript, and styles.
  - `eleventy.config.js` - Configuration for the Eleventy static site generator.
  - `package.json` - Frontend dependencies and build scripts.

## Architecture

The frontend is built on a hybrid architecture combining static site generation and modern client-side tooling:
- **Eleventy (11ty)**: Handles the core content generation and templating (Liquid). It provides a fast, SEO-friendly foundation.
- **Vite**: Acts as the build tool and development server. It processes TypeScript and CSS, offering instant HMR (Hot Module Replacement) and optimized production builds.
- **TailwindCSS**: Used for utility-first styling, ensuring a consistent and responsive design system.

## Project Setup

### Prerequisites

- **Node.js 20+** & **pnpm**

### Getting Started

Install frontend dependencies and start the development server.

```bash
cd client
# Install dependencies
pnpm install

# Start the development server (runs Eleventy + Vite + Tailwind)
pnpm dev
```
The website will be available at `http://localhost:8080`.
