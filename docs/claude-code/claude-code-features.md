# Claude Code Features Overview

A complete bird's-eye view of all Claude Code capabilities.

## Slash Commands (~70+)

### Session & Navigation

| Command | Aliases | Description |
|---|---|---|
| `/clear` | `/reset`, `/new` | Clear conversation history |
| `/resume` | `/continue` | Resume past session by ID or name |
| `/branch` | `/fork` | Branch current conversation |
| `/rewind` | `/checkpoint` | Rewind conversation/code to earlier state |
| `/export` | | Export conversation as plain text |
| `/rename` | | Name the current session |
| `/compact` | | Compress context (optional focus instructions) |
| `/help` | | Show help and available commands |

### Configuration & Settings

| Command | Aliases | Description |
|---|---|---|
| `/config` | `/settings` | Open settings UI |
| `/model` | | Change AI model |
| `/effort` | | Set effort level: low, medium, high, max, auto |
| `/permission` | `/allowed-tools` | View/update tool permissions |
| `/theme` | | Change color theme |
| `/keybindings` | | Edit keyboard shortcuts config |
| `/terminal-setup` | | Configure terminal keybindings |
| `/fast` | | Toggle fast mode on/off |
| `/vim` | | Toggle vim editing mode |
| `/color` | | Set prompt bar color |

### Memory & Context

| Command | Description |
|---|---|
| `/memory` | Edit CLAUDE.md files, enable/disable auto-memory |
| `/context` | Visualize context usage as colored grid |
| `/init` | Initialize project with CLAUDE.md |

### Development & Tools

| Command | Description |
|---|---|
| `/diff` | View uncommitted changes per-turn |
| `/add-dir` | Add working directory to session |
| `/hooks` | View hook configurations |
| `/mcp` | Manage MCP server connections |
| `/chrome` | Configure Chrome browser automation |
| `/ide` | Manage IDE integrations |
| `/agents` | Manage agent configurations |
| `/plugin` | Manage plugins |
| `/reload-plugins` | Reload all active plugins |
| `/skills` | List available skills |

### Git & GitHub

| Command | Description |
|---|---|
| `/pr-comments` | Fetch comments from a GitHub PR |
| `/security-review` | Analyze pending changes for vulnerabilities |
| `/install-github-app` | Set up GitHub Actions app for repo |

### Info & Utilities

| Command | Aliases | Description |
|---|---|---|
| `/cost` | | Token usage statistics |
| `/usage` | | Plan limits and rate limit status |
| `/stats` | | Daily usage, streaks, model preferences |
| `/doctor` | | Diagnose installation issues |
| `/version` | | Version number |
| `/feedback` | `/bug` | Submit feedback |
| `/release-notes` | | View changelog |
| `/copy` | | Copy last response to clipboard |
| `/btw` | | Side question (doesn't add to history) |
| `/tasks` | | List/manage background tasks |
| `/plan` | | Enter plan mode |
| `/voice` | | Toggle push-to-talk dictation |

### Remote & Account

| Command | Aliases | Description |
|---|---|---|
| `/remote-control` | `/rc` | Make session available from claude.ai |
| `/desktop` | `/app` | Continue in desktop app |
| `/install-slack-app` | | Install Claude Slack app |
| `/login` | | Sign in |
| `/logout` | | Sign out |
| `/exit` | `/quit` | Exit CLI |

---

## Keyboard Shortcuts (~40+)

### General Controls

| Shortcut | Action |
|---|---|
| `Ctrl+C` | Cancel current input or generation |
| `Ctrl+D` | Exit Claude Code |
| `Ctrl+L` | Clear terminal screen (keeps history) |
| `Ctrl+G` | Open prompt in external text editor |
| `Ctrl+O` | Toggle verbose output |
| `Ctrl+R` | Reverse search command history |
| `Ctrl+V` / `Cmd+V` / `Alt+V` | Paste image from clipboard |

### Text Editing

| Shortcut | Action |
|---|---|
| `Ctrl+K` | Delete to end of line |
| `Ctrl+U` | Delete entire line |
| `Ctrl+Y` | Paste deleted text |
| `Alt+B` | Move cursor back one word |
| `Alt+F` | Move cursor forward one word |

### Background & Task Management

| Shortcut | Action |
|---|---|
| `Ctrl+B` | Background running tasks |
| `Ctrl+F` | Kill all background agents (press twice) |
| `Ctrl+T` | Toggle task list visibility |

### Navigation & Mode Switching

| Shortcut | Action |
|---|---|
| `Up/Down` | Navigate command history |
| `Shift+Tab` / `Alt+M` | Cycle permission modes |
| `Alt+P` | Switch model |
| `Alt+T` | Toggle extended thinking |
| `Esc Esc` | Rewind/summarize conversation |

### Multiline Input

| Shortcut | Action |
|---|---|
| `\ + Enter` | Quick escape (all terminals) |
| `Option+Enter` | macOS default |
| `Shift+Enter` | iTerm2, WezTerm, Ghostty, Kitty |
| `Ctrl+J` | Line feed |

### Voice

| Shortcut | Action |
|---|---|
| `Hold Space` | Push-to-talk dictation (when enabled) |

---

## CLI Flags (~35+)

### Session Management

```
claude                       # Start interactive session
claude "query"               # Start with initial prompt
claude -p "query"            # Print mode (non-interactive)
cat file | claude -p "query" # Process piped content
claude -c                    # Continue most recent conversation
claude -r "<session>"        # Resume session by ID or name
--session-id "UUID"          # Use specific session ID
--name, -n                   # Set display name
--fork-session               # Create new session ID when resuming
```

### Model & Effort

```
--model          # Set AI model (claude-sonnet-4-6, claude-opus-4-6, etc.)
--effort         # Set effort level: low, medium, high, max
```

### Input / Output

```
--print, -p                # Non-interactive print mode
--output-format            # text, json, stream-json
--input-format             # text, stream-json
--json-schema              # Get validated JSON matching a schema
--include-partial-messages # Include partial streaming events
```

### Tool & Permission Control

```
--tools              # Restrict tools or "default" for all
--allowedTools       # Tools that execute without prompting
--disallowedTools    # Tools removed from context
--permission-mode    # plan, auto-accept, normal
--dangerously-skip-permissions  # Skip all permission prompts
```

### Context & Performance

```
--add-dir          # Add additional working directories
--max-turns        # Limit number of agentic turns
--max-budget-usd   # Maximum dollar amount before stopping
--fallback-model   # Fallback when default is overloaded
```

### System Prompt

```
--system-prompt              # Replace entire default prompt
--system-prompt-file         # Load system prompt from file
--append-system-prompt       # Append to default prompt
--append-system-prompt-file  # Append file contents to prompt
```

### Advanced

```
--worktree, -w     # Isolated git worktree session
--chrome           # Enable browser automation
--remote           # Create web session on claude.ai
--from-pr          # Resume from GitHub PR
--debug            # Enable debug mode
--verbose          # Verbose logging
--mcp-config       # Load MCP servers from JSON
--ide              # Auto-connect to IDE
--agent            # Specify agent for session
--plugin-dir       # Load plugins from directory
```

---

## Core Systems

### MCP (Model Context Protocol)

Connect external tools and data sources to Claude Code.

- **Server types**: Remote HTTP, SSE (streaming), local stdio
- **Auth**: OAuth with fixed callback ports or pre-configured credentials
- **Scopes**: Local, Project, User (with precedence hierarchy)
- **Config**: `.mcp.json` with environment variable expansion
- **Capabilities**: Tool search, prompts as slash commands, resources
- **Popular servers**: Sentry, GitHub, PostgreSQL, Google Calendar, Gmail

### Hooks System (25+ Events)

Run custom logic in response to Claude Code events.

**Events:**
- `SessionStart` / `SessionEnd` - Session lifecycle
- `UserPromptSubmit` - Intercept user input
- `PreToolUse` / `PostToolUse` / `PostToolUseFailure` - Tool lifecycle
- `PermissionRequest` - Handle permission dialogs
- `SubagentStart` / `SubagentStop` - Agent lifecycle
- `PreCompact` / `PostCompact` - Context compaction
- `Notification`, `Stop`, `ConfigChange` - System events
- `WorktreeCreate` / `WorktreeRemove` - Worktree events

**Hook types:**
- Bash commands
- HTTP webhooks
- Prompt-based (Claude answers questions)
- Agent-based (subagents handle logic)

**Features:** Pattern matching, exit code control, JSON output, async background hooks

### Memory System

**CLAUDE.md files** (auto-loaded at session start):
- Project: `.claude/CLAUDE.md`
- User: `~/.claude/CLAUDE.md`
- Path-specific rules with matchers
- Team-sharable via `.claude/rules/`

**Auto-memory:**
- Persists decisions/context across sessions
- Storage: `~/.claude/memory/`
- Manage with `/memory` command

### Permission Modes

| Mode | Behavior |
|---|---|
| **Normal** | Prompt for each tool use |
| **Plan** | Approve plan once, execute all steps |
| **Auto-Accept** | No prompts, auto-approve everything |

- Toggle with `Shift+Tab`
- Granular per-tool rules with wildcards
- Bash command patterns, file path patterns
- MCP tool restrictions

### Agent Teams & Subagents

- Spawn specialized subagents for parallel work
- Built-in types: research, debugger, data scientist, validator
- Run in foreground or background
- Isolated worktrees per agent
- Custom subagents via `--agents` JSON

### Skills & Plugins

**Built-in skills:** `/simplify`, `/loop`, `/claude-api`

**Custom skills:** Create in `.claude/skills/` with frontmatter config

**Plugins:**
- Official Anthropic marketplace
- Install/manage with `/plugin`
- Code intelligence, integrations, output styles
- Auto-updates

---

## Integrations

### VS Code

- Extension in marketplace
- Inline prompt box with file/folder references
- Resume remote sessions from claude.ai
- Parallel conversations
- Switch to terminal mode

### JetBrains

- IntelliJ IDEA, PyCharm, WebStorm, RubyMine, CLion, GoLand, etc.
- Install via marketplace
- Remote Development and WSL support

### Git

- Create commits and PRs directly
- Branch detection and management
- Git worktrees for parallel sessions
- Turn-by-turn diffs with `/diff`
- Security review of pending changes

### GitHub

- GitHub Actions integration
- PR comments fetching
- Code review automation
- PR attribution and status display
- Slack integration

### Chrome

- Browser automation and testing
- Test local web apps
- Debug with console logs
- Form filling automation
- Data extraction from web pages

### Remote & Web

- Remote Control sessions from claude.ai
- Teleport between web and terminal
- Cloud environments
- Session sharing across devices

### Desktop App (macOS & Windows)

- Native application
- Local and remote sessions
- SSH sessions
- Enterprise configuration

### Voice

- Push-to-talk dictation
- Configurable language and keybinding
- Toggle with `/voice`

---

## Settings & Configuration

### Configuration Scopes (highest to lowest precedence)

1. **Local**: `.claude/local.json` - machine-specific
2. **Project**: `.claude/settings.json` - repo-wide
3. **User**: `~/.claude/settings.json` - all projects

### Key Settings

| Setting | Description |
|---|---|
| `model` | AI model (with aliases: `sonnet`, `opus`) |
| `effortLevel` | low, medium, high, max |
| `temperature` | Creativity/randomness (0-2) |
| `theme` | Color theme |
| `outputStyle` | Response format |
| `tools` | Restrict available tools |
| `permissions` | Per-tool permission rules |
| `sandboxEnabled` | Filesystem/network isolation |
| `sandboxPaths` | Paths accessible in sandbox |
| `hooks` | Hook configurations |
| `plugins` | Enabled plugins |

---

## Security & Compliance

- **Sandbox mode** - Filesystem and network isolation
- **Permission-based architecture** - Granular tool control
- **Zero Data Retention (ZDR)** - Optional
- **Sensitive file exclusion** - Prevent accidental exposure
- **Healthcare compliance (BAA)** - Available
- **Enterprise device management** - Policy support
- **Audit** - Configuration change tracking
