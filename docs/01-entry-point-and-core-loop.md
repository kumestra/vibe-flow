# Claude Code: Entry Point and Core Agent Loop

## Overview

This document traces the execution path from when a user runs `claude` to the core agent loop that powers the conversation.

## Call Chain

```
claude (command)
  → cli.js (bundled entry point, defined in package.json "bin")
    → src/entrypoints/cli.tsx → main()
      → Checks special flags (--version, --daemon, ssh, etc.)
      → Falls through to: import('../main.js').main()
        → src/main.tsx → main()
          → Commander.js parses CLI args
          → .action() handler: init config, auth, analytics, tools, MCP
          → launchRepl()
            → src/replLauncher.tsx
              → Renders <App><REPL /></App> via Ink (React for terminal)
                → src/screens/REPL.tsx
                  → User types input → onQuery()
                    → src/query.ts → query() → queryLoop()
                      → THE CORE AGENT LOOP
```

## 1. Entry Point: `cli.tsx` (302 lines)

File: `src/entrypoints/cli.tsx`

A routing dispatcher. Checks argv for special modes and routes to fast paths:

| Argument | Handler | Purpose |
|----------|---------|---------|
| `--version` | Print and exit | Zero imports needed |
| `--daemon-worker` | `runDaemonWorker()` | Background worker process |
| `remote-control` | `bridgeMain()` | Remote control mode |
| `daemon` | `daemonMain()` | Long-running supervisor |
| `ps/logs/attach/kill` | `bg.*Handler()` | Background session management |
| _(none)_ | `import('../main.js')` | **Normal interactive mode** |

Key design: all imports are **dynamic** (`await import(...)`) to minimize startup time for fast paths.

## 2. Main Setup: `main.tsx` (4,683 lines)

File: `src/main.tsx`

The bulk of this file is the Commander.js `.action()` handler (~2,750 lines). It:

1. Initializes configs, auth, analytics, GrowthBook (feature flags)
2. Loads MCP servers, tools, commands, plugins, skills
3. Shows setup screens (trust dialog, login) if needed
4. Handles special modes (--print, --continue, --resume, SSH, teleport)
5. For normal interactive mode: calls `launchRepl()`

## 3. REPL Launcher: `replLauncher.tsx` (22 lines)

File: `src/replLauncher.tsx`

Thin wrapper that renders the Ink (React for terminal) component tree:

```tsx
await renderAndRun(root, <App {...appProps}>
    <REPL {...replProps} />
</App>);
```

## 4. App Wrapper: `App.tsx` (55 lines)

File: `src/components/App.tsx`

Three nested React context providers:

```
FpsMetricsProvider → StatsProvider → AppStateProvider → children
```

Provides global state to the entire component tree.

## 5. REPL Screen: `REPL.tsx` (5,005 lines)

File: `src/screens/REPL.tsx`

The interactive conversation UI. The key function is `onQueryImpl()` (line 2661):

1. Prepare IDE integration
2. Generate session title from first user message
3. Build tool use context (available tools, MCP clients)
4. Build system prompt + user context + system context
5. Call `query()` — the async generator that streams responses
6. Process each streamed event via `onQueryEvent()`

The critical call:

```typescript
for await (const event of query({
  messages, systemPrompt, userContext, systemContext,
  canUseTool, toolUseContext, querySource
})) {
  onQueryEvent(event);
}
```

## 6. Core Agent Loop: `query.ts` (1,729 lines)

File: `src/query.ts`

The `queryLoop()` function is an async generator with a `while(true)` loop. Simplified:

```
queryLoop():
  while true:
    // 1. PREPARE
    - Apply context compaction if conversation is too long
    - Build full system prompt with system context
    
    // 2. CALL LLM
    for message in deps.callModel(messages, systemPrompt, tools):
      yield message  // stream to UI
      if message contains tool_use blocks:
        needsFollowUp = true
    
    // 3. CHECK — done if no tool calls
    if not needsFollowUp:
      return { reason: 'completed' }
    
    // 4. EXECUTE TOOLS
    for update in runTools(toolUseBlocks, ...):
      yield update.message  // stream results to UI
      toolResults.append(update.message)
    
    // 5. LOOP BACK
    messages = [...messages, ...assistantMessages, ...toolResults]
    turnCount += 1
    // → back to top of while(true)
```

### What the complexity handles

The other ~1,600 lines handle:
- **Context compaction** — when conversation gets too long, summarize older messages
- **Auto-compact** — proactive compaction before hitting token limits
- **Microcompact** — fine-grained compaction of tool results
- **Error recovery** — prompt-too-long, max-output-tokens, media size errors
- **Streaming tool execution** — start executing tools while LLM is still streaming
- **Abort handling** — user interrupts (Ctrl+C)
- **Memory prefetch** — load relevant memories in parallel
- **Skill discovery** — find relevant skills during the turn
- **Analytics/telemetry** — track performance and usage
- **Feature flags** — conditional behavior via GrowthBook gates
- **Max turns** — safety limit on loop iterations
- **Queued commands** — process slash commands and notifications mid-turn

## Example: User Says "Fix the bug in auth.ts"

```
Turn 1: Send to Claude API
  ← Claude: "I need to read auth.ts" → tool_use: Read(auth.ts)
  → Execute Read tool → returns file contents
  → Append [assistant message + tool result] to messages

Turn 2: Send to Claude API (with file contents in context)
  ← Claude: "Found the bug, fixing..." → tool_use: Edit(auth.ts, ...)
  → Execute Edit tool → modifies file
  → Append [assistant message + tool result] to messages

Turn 3: Send to Claude API (with edit confirmation)
  ← Claude: "Fixed! The issue was a missing null check..."
  → No tool_use → needsFollowUp = false → return
```

## Next Steps

- Trace `deps.callModel()` — the actual Anthropic API call
- Trace `runTools()` — how tools are executed
- Trace tool definitions — how Read, Edit, Bash, etc. are defined
