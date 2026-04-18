# AGENTS.md

## Project Context
**global-news-front** is a modern web frontend for a news platform, built with Next.js and Tailwind CSS. It fetches and displays articles from a WordPress backend.

## Coding Standards
- Next.js (App Router).
- Tailwind CSS for styling.
- Responsive design is mandatory.
- Use Lucide icons for UI elements.

## Tooling & Commands
- **Dev**: npm run dev
- **Build**: npm run build
- **Lint**: npm run lint

## Jules Instructions
When reviewing:
1.  **Next.js Patterns**: Check for proper use of Server vs. Client Components.
2.  **Performance**: Analyze image optimization and layout shifts (CLS).
3.  **UI/UX**: Ensure the newsletter popup and news ticker are non-intrusive and accessible.
4.  **Integration**: Validate the WordPress API fetch logic in `src/lib/wordpress.ts`.
