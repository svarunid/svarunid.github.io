# AGENTS.md
This file contains guidelines for AI coding agents to follow when working on this project (Zhura).

## Project
Zhura is an AI agent that's embedded into my personal and professional portfolio. It's primary purpose is to act as a conversational bot and help visitors know more about me. It also has capabilities to identify the intent of the visitor and notify me via email or schedule a meet with me. The project also contains the portfolio that has information about everything related to me.

The project uses a monorepo structure wherein the code for different parts (frontend, backend, etc.) exists inside the same repository. Use appropriate package managers & configurations for each part of the project.

All information needed to compose the portfolio is stored in the files inside `data/` folder. Use it to populate content for different sections of the portfolio.

## Version Control
The project will use Git for version control. The default branch name will be `main`. The project will use GitHub for hosting the repository. The repository will be private.

Use the standard commit message conventions as per the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) configuration.

Not much pre-commit hooks are required for the project.
