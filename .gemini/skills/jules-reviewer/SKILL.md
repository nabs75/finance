---
name: jules-reviewer
description: Autonomously review and control code using Jules (https://jules.google). Use this skill to submit code for deep analysis, security audits, or compliance checks against Google-style standards before final validation.
---

# Jules Reviewer Skill

This skill allows you to leverage **Jules**, Google's autonomous coding agent, to review and control your code. Jules runs in a secure, isolated environment, clones your repository, and can perform complex reviews, bug fixes, and feature additions.

## Workflow

### 1. Setup (One-time)
If Jules is not installed, install it:
`npm install -g @google/jules`
Then log in:
`jules login`

### 2. Configure Context (Recommended)
Jules is most effective when it has an `AGENTS.md` file in the repository root. This file tells Jules about your project, coding standards, and build/test tools.
- Copy the template from `assets/AGENTS.md` to your repo root.
- Customize it for your project.

### 3. Submit a Review
To start a review session, use the following pattern:
`jules remote new --repo <repo_name> --session "<review_prompt>"`

**Example Prompts:**
- "Review the security of my authentication logic in src/auth.ts."
- "Analyze this PR for potential memory leaks and performance bottlenecks."
- "Ensure all changes in the last 5 commits follow our internal coding standards defined in AGENTS.md."

### 4. Monitor & Pull Results
- **List active sessions**: `jules remote list --session`
- **Check status**: `jules remote list --session <session_id>`
- **Retrieve results**: When finished, Jules typically creates a Pull Request. You can also pull the modified code using `jules remote pull --session <session_id>`.

## Key Resources
- **CLI Reference**: See [jules_cli_guide.md](references/jules_cli_guide.md) for a full list of commands.
- **Templates**: Use `assets/AGENTS.md` to define project-specific rules for Jules.

## When to use this Skill
- Before merging a critical Pull Request.
- When you need a "second pair of eyes" that is highly specialized in Google-style engineering.
- To automate repetitive review tasks (e.g., checking for consistent error handling).
- When a task requires running the full test suite in an isolated environment.
