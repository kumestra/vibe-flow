# Claude Code Memory & Persistence

How Claude Code remembers things across and within conversations.

## Four Layers of Context

| Layer | Scope | Persistence | How to manage |
|---|---|---|---|
| **Project CLAUDE.md** | Per-repo (shared with team) | Permanent (checked into git) | Edit `.claude/CLAUDE.md` or files in `.claude/rules/` |
| **User CLAUDE.md** | All projects (personal) | Permanent (local file) | Edit `~/.claude/CLAUDE.md` |
| **Auto memory** | Per-project (personal) | Across conversations | `/memory` command or edit files in `~/.claude/projects/<project>/memory/` |
| **Conversation context** | Current session only | Until session ends or `/clear` | Automatic; `/clear` to reset |

## CLAUDE.md Files

Instruction files loaded automatically at session start. They tell Claude *how* to behave in your project.

- **Project level**: `.claude/CLAUDE.md` — repo conventions, build commands, coding style. Checked into git so the whole team shares it.
- **User level**: `~/.claude/CLAUDE.md` — personal preferences that apply across all projects.
- **Rules directory**: `.claude/rules/` — additional rule files, can have path-based matchers.

### Precedence (highest to lowest)

1. Local (`.claude/local.json`)
2. Project (`.claude/settings.json`)
3. User (`~/.claude/settings.json`)

## Auto Memory

Claude automatically builds up notes about you, the project, and your feedback over time. These persist across conversations.

### Memory types

| Type | Purpose | Example |
|---|---|---|
| **user** | Your role, preferences, expertise | "Senior backend dev, new to React" |
| **feedback** | Corrections to Claude's behavior | "Don't mock the database in tests" |
| **project** | Ongoing work context, decisions | "Auth rewrite driven by compliance" |
| **reference** | Pointers to external resources | "Bugs tracked in Linear project INGEST" |

### Storage

- Index file: `~/.claude/projects/<project>/memory/MEMORY.md`
- Individual memory files: `~/.claude/projects/<project>/memory/<topic>.md`
- Each file has YAML frontmatter with `name`, `description`, `type`

### Managing auto memory

- `/memory` command — toggle on/off, browse/edit memory files
- Disable via settings: `"autoMemoryEnabled": false` in `.claude/settings.json`
- Disable via env: `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`
- Ask Claude to "remember X" or "forget X" in conversation

## Conversation Context

The live chat history in the current session.

- `/clear` resets it (does **not** touch CLAUDE.md or auto memory)
- `/compact` compresses it to save token space (can provide focus instructions)
- Automatically compressed as context window fills up
- `/context` shows a visual grid of current usage

## What NOT to save in auto memory

Auto memory is for things that can't be derived from code or git:

- Code patterns / architecture → read the code
- Git history / who changed what → `git log` / `git blame`
- Debugging solutions → the fix is in the commit
- Anything already in CLAUDE.md
- Temporary in-progress task details
