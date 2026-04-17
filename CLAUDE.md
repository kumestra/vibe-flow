# Claude Code Source Analysis

## Project Goal

Analyze the Claude Code source code (`~/git-repos/claude-code-source`) and rewrite the core agent logic in Python. This is a learning project for understanding how AI agents work by reading real production code.

## Approach

Iterative cycle:
1. **Analyze** — read source code in `~/git-repos/claude-code-source` (read-only, never modify)
2. **Document** — write analysis docs in `docs/`
3. **Implement** — rewrite the analyzed part in Python in `src/`
4. Repeat for each layer/feature

## Source Reference

- Source location: `~/git-repos/claude-code-source`
- Language: TypeScript (1,902 files, ~512K lines)
- Key entry points traced so far:
  - `src/entrypoints/cli.tsx` — CLI dispatcher (302 lines)
  - `src/main.tsx` — full CLI setup, Commander.js options, launches REPL (4,683 lines)
  - `src/replLauncher.tsx` — thin launcher, renders `<App><REPL /></App>` (22 lines)
  - `src/components/App.tsx` — React context providers wrapper (55 lines)
  - `src/screens/REPL.tsx` — interactive conversation UI, handles user input (5,005 lines)
  - `src/query.ts` — core agent loop: call LLM → execute tools → loop (1,729 lines)

## Core Agent Loop (Simplified)

```
while true:
    response = call_llm(messages, system_prompt, tools)
    
    if response has no tool calls:
        return response  # done
    
    tool_results = execute_tools(response.tool_calls)
    messages = messages + response + tool_results
    # loop back
```

## Writing Style

When writing markdown files, use GitHub-Flavored Markdown (GFM). All GFM features are available — use whichever ones make the document better:

- Emoji if it improves readability or tone
- Mermaid diagrams if they clarify architecture or flow
- Tables, task lists, alerts, footnotes, math, etc.

The goal is clear, effective documentation. If a GFM feature helps, use it.

## Progress So Far

### What's been analyzed and documented:

1. **Core agent loop** (`docs/01-entry-point-and-core-loop.md`) — how query.ts works
2. **Built-in tools** (`docs/02-built-in-tools.md`) — all 30+ tools, categories, execution flow
3. **Navigating the source** (`docs/03-navigating-the-source.md`) — strategy for exploring 512K lines
4. **System prompt overview** (`docs/04-system-prompt.md`) — how the prompt is assembled
5. **Prompt caching** (`docs/05-prompt-caching.md`) — prefix caching, cost model, design rules
6. **Why Claude Code works** (`docs/06-why-claude-code-works.md`) — same API, better engineering
7. **LLM API comparison** (`docs/07-llm-api-comparison.md`) — OpenAI vs Anthropic in detail
8. **Static system prompt analysis** (`docs/08-system-prompt-static-analysis.md`) — deep dive into all 7 static sections with actual prompt text
9. **Dynamic system prompt analysis** (`docs/09-system-prompt-dynamic-analysis.md`) — all 11 dynamic sections, caching mechanism
10. **System prompt summary** (`docs/10-system-prompt-summary.md`) — caching lifecycle, MCP best practices
11. **Anthropic API pricing** (`docs/11-anthropic-api-pricing.md`) — cost model
12. **OpenAI API data structures** (`docs/12-openai-api-data-structures.md`) — end-to-end tool calling example
13. **Anthropic API data structures** (`docs/13-anthropic-api-data-structures.md`) — end-to-end tool use example
14. **Key API difference** (`docs/14-key-api-difference-text-plus-tool.md`) — Claude returns text + tool call together
15. **Transformer architecture** (`docs/15-transformer-architecture.md`) — pipeline from API input to token output
16. **Tool execution deep dive** (`docs/16-tool-execution-deep-dive.md`) — the complete 12-step pipeline from tool_use to tool_result, with source file references for every layer
17. **Sub-agent design** (`docs/17-sub-agent-design.md`) — general concept: recursive agent loop, isolation, parallelism
18. **Sub-agent source analysis** (`docs/18-sub-agent-source-analysis.md`) — complete source-level deep dive: AgentTool, runAgent, built-in agents, tool filtering, fork path, worktree isolation, sync/async execution, cleanup
19. **Skills design** (`docs/19-skills-design.md`) — general concept of the skills system
20. **Tool execution Python rewrite plan** (`docs/20-tool-execution-python-rewrite-plan.md`) — 6-phase incremental roadmap for porting Claude Code's 12-step tool pipeline to Python

### What's been implemented:

- `src/vibe_flow/agent.py` — agent loop using LiteLLM: streams tokens, runs tool calls serially, fires `on_token` / `on_tool_call` / `on_tool_result` callbacks
- `src/vibe_flow/tool_base.py` — `Tool` ABC, `ToolUseContext`, `ToolResult`
- `src/vibe_flow/tool_runner.py` — `run_tool_use`: lookup → parse → call
- `src/vibe_flow/tools/` — one tool: `get_current_time` (`read_file` and `write_file` removed)
- `src/vibe_flow/system_prompt.py` — builds system prompt string
- `src/vibe_flow/logger.py` — SQLite session logger; three tables: `session`, `event`, `tool`
- `src/vibe_flow/main.py` — Textual TUI: streaming `Static` widget, `RichLog` history with markdown rendering and tool call display
- `pyproject.toml` — uv project; depends on `litellm`, `textual`, `python-dotenv`
- `logs/vibe_flow.db` — SQLite log file (gitignored); MCP SQLite server points here
- `.env` — API key (gitignored)

### What to do next:

Recommended order:

1. **Permissions** — gate tool execution behind a y/n prompt in the TUI before adding dangerous tools
2. **bash + write_file tools** — makes the agent actually useful; requires permissions first
3. **MCP client** — let vibe-flow consume MCP servers (JSON-RPC over stdio/SSE), exposing remote tools to the agent loop dynamically
4. **Sub-agents** — spawn a second `query()` call with a restricted tool set; return its result as a tool result to the parent

## Directory Structure

```
docs/              — analysis documents
logs/
└── vibe_flow.db   — SQLite session log (gitignored)
src/
└── vibe_flow/
    ├── agent.py         — agent loop: LLM → tools → loop, with callbacks
    ├── logger.py        — SQLite session logger
    ├── main.py          — Textual TUI entry point
    ├── system_prompt.py — system prompt builder
    ├── tool_base.py     — Tool ABC, ToolUseContext, ToolResult
    ├── tool_runner.py   — run_tool_use: lookup → parse → call
    └── tools/
        ├── __init__.py        — tool registry
        └── get_current_time/
.env               — API key (gitignored)
pyproject.toml     — uv project config
CLAUDE.md          — this file
```

## Preferences

- **LiteLLM + gpt-4o** — use `litellm.acompletion` with `model="gpt-4o"`. Never use the Anthropic SDK directly.
- **Commit workflow** — when asked to "commit and push", run commands separately: `git add` first, then `git commit` alone (never chain commit with other commands), then `git push`. This prevents unintended commits if something fails.
- **Doc analysis style** — for large analysis tasks, work section-by-section: read source → write analysis with actual source text + design patterns + lessons → append to doc → confirm before moving on. This builds deep understanding.
- **Auto memory disabled** — all persistent context lives in this CLAUDE.md, not in `~/.claude` auto memory. This project moves across dev environments.
- **Code line length** — when writing or editing Python code, keep every line to a maximum of 80 characters. Wrap long expressions, hoist long literals into locals, and break long function signatures across multiple lines rather than letting a line exceed 80. This applies to code only, not to docs or commit messages.

## Technical Notes

- Project uses `uv` for Python package management
- Entry point: `uv run vibe-flow`
- MCP SQLite server configured locally; points at `logs/vibe_flow.db`
- Git branch: `tmp-claude-code-analysis`
- All docs follow GFM with emoji, mermaid, tables where helpful
