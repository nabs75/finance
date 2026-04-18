# AGENTS.md (Root)

## Project Context
This is a monorepo containing multiple independent projects and specialized AI agent skills.
- **auto-alert-monitor**: Car scraping and alerting system.
- **global-news-front**: Next.js news frontend.
- **news-auto-feeder**: Automated news rewriting and publishing pipeline.
- **test-interface**: UI/UX playground.
- **Skills**: A collection of `.skill` files and their development directories for Gemini CLI.

## Monorepo Structure
Each project is located in its own directory and has its own `AGENTS.md` for specific instructions.

## Jules Instructions
1.  **Architecture**: Review how the different projects could share logic or components.
2.  **Security**: Check for leaked secrets or insecure patterns across the entire codebase.
3.  **Skills Validation**: Review the logic and instructions in the `.skill` and `SKILL.md` files to ensure they are efficient and safe.
4.  **Consistency**: Ensure consistent naming and coding standards across the different projects.
