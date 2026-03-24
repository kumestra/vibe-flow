# Project Guidelines

## Git
- Working directory is already the repo root — use `git` directly, no `-C` flag needed.
- Always push to remote immediately after creating a commit.
- When running `git commit`, run it as a standalone command only — never chain it with other commands using `&&`, `;`, `|`, or any other operator.
- Never stage binary files (images, PDFs, compiled binaries, etc.).
- Before writing a commit message, run `git diff --cached` to review all staged changes.

## Web Search
- Use web search when you:
  1. Do not know something and local sources (codebase, docs, git history) don't have the answer.
  2. Are not confident in your answer — verify rather than guess.
  3. Suspect your knowledge may be outdated (e.g., library APIs, CLI flags, best practices, version-specific behavior).
