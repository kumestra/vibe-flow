# Project Guidelines

## Git
- Working directory is already the repo root — use `git` directly, no `-C` flag needed.
- Always push to remote immediately after creating a commit.
- When running `git commit`, run it as a standalone command only — never chain it with other commands using `&&`, `;`, `|`, or any other operator.
- Never stage binary files (images, PDFs, compiled binaries, etc.).
- Before writing a commit message, run `git diff --cached` to review all staged changes.
