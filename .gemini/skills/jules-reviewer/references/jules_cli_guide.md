# Jules CLI Guide

Jules is an autonomous coding agent from Google. This guide covers the basic CLI commands for interacting with it.

## Installation & Setup

1.  **Install**: `npm install -g @google/jules`
2.  **Login**: `jules login`
3.  **Check Version**: `jules --version`

## Working with Remote Sessions

A **Session** is a unit of work. Jules clones your repo, performs the task, and can create a PR.

-   **Start Review Session**: 
    `jules remote new --repo <repo_name> --session "Review this code for [security/style/logic] errors. Check against [file_path]."`
-   **List Sessions**: `jules remote list --session`
-   **Get Session Status/Log**: `jules remote list --session <session_id>`
-   **Pull Results**: `jules remote pull --session <session_id>`

## Key Integration: AGENTS.md

Jules looks for `AGENTS.md` in the repository root to understand:
-   **Context**: What the project is about.
-   **Rules**: Coding standards, prohibited patterns.
-   **Tools**: Specific commands Jules should use (e.g., `npm run lint`).

Example structure:
```markdown
# AGENTS.md

## Project Context
[Description]

## Instructions
[Rules for Jules]

## Tooling
[Build/Test/Lint commands]
```

## Tips for Review
When asking Jules to "Review", be specific:
- "Review the security of my authentication logic in src/auth.ts."
- "Compare my implementation in src/utils.ts with the legacy one in old_utils.ts."
- "Check if my changes in src/api.ts break any existing endpoints."
