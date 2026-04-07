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

## Directory Structure

```
docs/           — analysis documents
src/            — Python rewrite
CLAUDE.md       — this file
```
