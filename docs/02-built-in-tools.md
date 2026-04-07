# Claude Code Built-in Tools

Analysis of all built-in tools from the Claude Code source.

## Overview

Claude Code provides ~30+ built-in tools that the LLM can call during the agent loop.
Tools are defined as schemas (name, description, input parameters) and passed to the
API. The LLM decides which tools to call based on the user's request.

Each tool has two parts:
1. **Schema** — what the LLM sees (name, description, parameters)
2. **Handler** — what actually executes when the tool is called

## Tool Categories

### Core File Tools

| Tool | Description |
|------|-------------|
| **Read** | Read files from the filesystem. Supports text, images, PDFs, and Jupyter notebooks. Accepts path, offset, and limit parameters. |
| **Edit** | Exact string replacement in files. Takes `old_string` and `new_string` — fails if `old_string` isn't unique. Has `replace_all` flag for bulk renames. |
| **Write** | Create or overwrite files. Used for new files; Edit is preferred for modifications. |
| **NotebookEdit** | Replace contents of a specific cell in a Jupyter notebook. |

### Search Tools

| Tool | Description |
|------|-------------|
| **Bash** | Execute shell commands. Has timeout support, captures stdout/stderr. The most versatile tool. |
| **Glob** | Find files by glob pattern (e.g., `**/*.py`, `src/**/*.ts`). Returns paths sorted by modification time. |
| **Grep** | Search file contents using ripgrep. Supports regex, glob filters, file type filters, context lines, and multiple output modes (`content`, `files_with_matches`, `count`). |

### Web Tools

| Tool | Description |
|------|-------------|
| **WebFetch** | Fetch a URL, convert HTML to markdown, and process with a fast model. Read-only, 15-minute cache. |
| **WebSearch** | Search the web for up-to-date information. Returns processed results. |

### Agent & Task Tools

| Tool | Description |
|------|-------------|
| **Agent** | Spawn a sub-agent to handle work in parallel. Each agent gets its own context and tools. Supports background execution and git worktree isolation. |
| **SendMessage** | Send a message to a running agent or cross-session peer. Resumes the agent with full context preserved. |
| **TaskCreate** | Create a task to track progress on complex work. |
| **TaskGet** | Retrieve a task by ID with full details. |
| **TaskUpdate** | Update task status (`in_progress`, `completed`), subject, or dependencies. |
| **TaskList** | List all tasks with status and completion info. |
| **TaskStop** | Stop a running background task. |
| **TaskOutput** | Output and track task progress (internal). |

### Planning Tools

| Tool | Description |
|------|-------------|
| **EnterPlanMode** | Enter plan mode to explore the codebase and design an implementation approach before writing code. |
| **ExitPlanMode** | Exit plan mode when the plan is ready for user approval. |

### Git Worktree Tools

| Tool | Description |
|------|-------------|
| **EnterWorktree** | Create an isolated git worktree and switch into it. Allows parallel work without affecting the main working tree. |
| **ExitWorktree** | Exit the worktree and return to the original directory. |

### Scheduling Tools

| Tool | Description |
|------|-------------|
| **CronCreate** | Schedule a prompt to run on a cron schedule or at a future time. |
| **CronDelete** | Cancel a scheduled cron job by ID. |
| **CronList** | List all scheduled cron jobs. |
| **RemoteTrigger** | Manage scheduled remote Claude Code agents via the claude.ai API. |

### User Interaction Tools

| Tool | Description |
|------|-------------|
| **AskUserQuestion** | Ask the user multiple choice questions to gather info or clarify ambiguity. |
| **Skill** | Invoke slash commands (pre-built helpers like `/commit`, `/review-pr`). |

### Infrastructure Tools

| Tool | Description |
|------|-------------|
| **ToolSearch** | Lazy-load deferred tool schemas. Tools can be registered but not fully loaded until needed, reducing prompt size. |
| **LSP** | Interact with Language Server Protocol servers for code intelligence (go-to-definition, references, etc.). |
| **ListMcpResourcesTool** | List available resources from configured MCP servers. |
| **ReadMcpResourceTool** | Read a specific resource from an MCP server. |
| **Config** | Get or set Claude Code configuration settings. |

### Team/Swarm Tools

| Tool | Description |
|------|-------------|
| **TeamCreate** | Create a new team to coordinate multiple agents working together. |
| **TeamDelete** | Remove team and task directories when swarm work is complete. |

### Platform-Specific Tools

| Tool | Description |
|------|-------------|
| **PowerShell** | Execute PowerShell commands (Windows only). |

## Tool Execution Flow

```
LLM response includes tool_use block
    │
    ├── Permission check (allowed? denied? needs user approval?)
    │
    ├── Execute tool handler
    │   ├── Read-only tools can run in parallel (Glob, Grep, Read)
    │   └── Write tools run serially (Bash, Edit, Write)
    │
    ├── Format result as tool_result
    │
    └── Append to messages, loop back to LLM
```

Key implementation details:
- **Parallel execution**: Read-only tools are batched and run concurrently.
  Write tools are serialized to avoid conflicts.
- **Streaming execution**: Tools can start executing before the full LLM
  response is received (when the tool_use block is complete).
- **Permission system**: Each tool call is checked against allow/deny rules
  before execution. Users can pre-approve patterns (e.g., `Bash(git add:*)`).
- **Deferred loading**: Tools can be registered with just a name and loaded
  on-demand via `ToolSearch` to keep the system prompt small.

## What We Implement in vibe-flow

Current (`src/agent.py`):
- [x] bash
- [x] read_file
- [x] write_file

Next candidates:
- [ ] edit (string replacement — more precise than full file rewrite)
- [ ] grep (search file contents)
- [ ] glob (find files by pattern)
- [ ] agent (sub-agent spawning)
