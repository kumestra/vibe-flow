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

### What's been implemented:

- `src/agent.py` — minimal agent loop using OpenAI API (gpt-4o)
- `src/tools/` — tool directory structure mirroring Claude Code:
  - `src/tools/bash/` — execute shell commands
  - `src/tools/read_file/` — read files
  - `src/tools/write_file/` — write files
- `pyproject.toml` — uv Python project with `vibe-flow` entry point
- `.env` — OpenAI API key (gitignored)

### What to do next:

- Add more tools: `edit` (string replacement), `grep` (search contents), `glob` (find files)
- Improve system prompt: split into sections mirroring Claude Code's static/dynamic pattern
- Add environment info to dynamic prompt (CWD, OS, date)
- Add per-tool prompts (usage guidelines in tool descriptions)
- Add permission system (auto-allow read tools, ask for write tools)
- Add context management (compaction when approaching limits)
- Add streaming responses
- Add parallel tool execution

## Directory Structure

```
docs/           — analysis documents (01-10 so far)
src/
├── __init__.py
├── agent.py    — core agent loop
└── tools/
    ├── __init__.py       — tool registry
    ├── bash/             — shell command execution
    ├── read_file/        — file reading
    └── write_file/       — file writing
.env            — API key (gitignored)
pyproject.toml  — uv project config
CLAUDE.md       — this file
```

## Preferences

- **OpenAI only** — user only has an OpenAI API key. Always use `from openai import OpenAI` and `gpt-4o`. Never use Anthropic SDK.
- **Commit workflow** — when asked to "commit and push", run commands separately: `git add` first, then `git commit` alone (never chain commit with other commands), then `git push`. This prevents unintended commits if something fails.
- **Doc analysis style** — for large analysis tasks, work section-by-section: read source → write analysis with actual source text + design patterns + lessons → append to doc → confirm before moving on. This builds deep understanding.
- **Auto memory disabled** — all persistent context lives in this CLAUDE.md, not in `~/.claude` auto memory. This project moves across dev environments.

## Technical Notes

- Project uses `uv` for Python package management
- User only has OpenAI API key — use OpenAI SDK, not Anthropic
- Entry point: `uv run vibe-flow` or `uv run python src/agent.py`
- Git branch: `tmp-claude-code-analysis`
- All docs follow GFM with emoji, mermaid, tables where helpful
