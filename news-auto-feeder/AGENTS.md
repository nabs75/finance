# AGENTS.md

## Project Context
**news-auto-feeder** is an automated content pipeline. It watches trends, uses AI to rewrite news articles, and publishes them automatically to WordPress and social media.

## Coding Standards
- TypeScript based.
- AI logic centralized in `src/ai-rewriter.ts`.
- Publisher logic in `src/wp-publisher.ts`.

## Tooling & Commands
- **Build**: tsc
- **Test**: npm test

## Jules Instructions
When reviewing:
1.  **AI Prompts**: Review the rewrite prompts in `ai-rewriter.ts` for quality and anti-hallucination.
2.  **Security**: Ensure API keys (WP, Social, AI) are handled via environment variables only.
3.  **Reliability**: Check the trend-watching logic for accuracy and frequency.
4.  **Concurrency**: Ensure multiple feeds don't overlap or cause race conditions.
