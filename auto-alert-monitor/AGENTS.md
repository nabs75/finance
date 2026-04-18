# AGENTS.md

## Project Context
**auto-alert-monitor** is a car scraping and monitoring tool. It scrapes sites like Leboncoin, Autoscout24, and LaCentrale to find vehicles matching specific filters and sends alerts.

## Coding Standards
- TypeScript for backend logic.
- Modular scrapers located in `src/scrapers/`.
- Configuration managed via JSON files in `config/`.

## Tooling & Commands
- **Lint**: npm run lint (if configured)
- **Build**: tsc

## Jules Instructions
When reviewing:
1.  **Scraper Robustness**: Check if selectors are fragile and suggest more resilient approaches.
2.  **Error Handling**: Ensure that scraping failures are logged and don't crash the service.
3.  **Proxy & Rate Limiting**: Check how `proxy-manager.ts` handles rotations and avoids bans.
4.  **Database**: Validate data integrity when saving to `db.ts`.
