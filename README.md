# vibe-flow

`vibe-flow` is a small Python rewrite of Claude Code's core agent loop.
The project is meant for learning: read production agent code, document
what it does, then rebuild the essential pieces in Python.

Right now the runnable app is intentionally minimal:

- OpenAI-powered chat loop
- One built-in tool: `get_current_time`
- A small system prompt builder
- A basic tool execution pipeline

## Prerequisites

- Python 3.12+
- `uv`
- An OpenAI API key

## Setup

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_api_key_here
```

Install dependencies:

```bash
uv sync
```

## Run

Start the agent with:

```bash
uv run vibe-flow
```

You can also run the entrypoint directly:

```bash
uv run python src/agent.py
```

Once it starts, type your prompt at `>`.
Use `quit` or `exit` to leave the REPL.

## Example

```text
$ uv run vibe-flow
Minimal Agent (type 'quit' to exit)
---------------------------------------------

> what time is it in UTC?
  [tool] get_current_time({"timezone":"UTC"})

2026-04-13T01:23:45.000000+00:00
```

## Project Layout

```text
docs/        analysis notes and design writeups
src/         Python implementation
.codex/      project-level Codex config
CLAUDE.md    working notes and project context
```

## Notes

- The current agent code uses the OpenAI Python SDK.
- The runnable agent in [`src/agent.py`](/home/t/git-repos/vibe-flow/src/agent.py:1)
  currently hardcodes `gpt-4o`.
- The repo-level Codex config in
  [`.codex/config.toml`](/home/t/git-repos/vibe-flow/.codex/config.toml:1)
  sets Codex's project model to `gpt-5.4`, which is separate from the
  Python app's own model constant.
