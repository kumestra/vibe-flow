# Navigating the Claude Code Source

The Claude Code source is ~1,600 TypeScript files and ~512K lines. You don't read
all of it. You find the structure, then zoom in.

## Strategy: Structure → Pattern → Zoom

### Step 1: Find the structure

Start with the top-level directories:

```bash
ls ~/git-repos/claude-code-source/src/
```

Key directories:
- `src/entrypoints/` — where execution starts (CLI, web, etc.)
- `src/tools/` — all built-in tools
- `src/services/` — core services (API calls, tool orchestration, etc.)
- `src/components/` — React UI components
- `src/screens/` — top-level screens (REPL, etc.)

### Step 2: Find the pattern

Each tool lives in its own directory under `src/tools/`:

```
src/tools/
├── AgentTool/
├── AskUserQuestionTool/
├── BashTool/
├── BriefTool/
├── ConfigTool/
├── EnterPlanModeTool/
├── EnterWorktreeTool/
├── ExitPlanModeTool/
├── ExitWorktreeTool/
├── FileEditTool/
├── FileReadTool/
├── FileWriteTool/
├── GlobTool/
├── GrepTool/
├── LSPTool/
├── ListMcpResourcesTool/
├── MCPTool/
├── NotebookEditTool/
├── ReadMcpResourceTool/
├── RemoteTriggerTool/
├── ScheduleCronTool/
├── SendMessageTool/
├── SkillTool/
├── SleepTool/
├── TaskCreateTool/
├── TaskGetTool/
├── TaskListTool/
├── TaskOutputTool/
├── TaskStopTool/
├── TaskUpdateTool/
├── TeamCreateTool/
├── TeamDeleteTool/
├── TodoWriteTool/
├── ToolSearchTool/
├── WebFetchTool/
├── WebSearchTool/
├── shared/          ← shared utilities
└── utils.ts
```

Each tool directory follows the same pattern:

```
GlobTool/
├── GlobTool.ts    ← schema definition + call() handler
├── UI.tsx         ← React component for rendering output
└── prompt.ts      ← system prompt instructions for this tool
```

Once you see this pattern, you know exactly where to look for any tool.

### Step 3: Zoom in with search

Don't read files top to bottom. Use targeted searches:

```bash
# Find all tool names
grep -r '"name"' src/tools/*/  --include="*.ts" | grep -v test

# Find where a specific function is defined
grep -rn "function runTools" src/

# Find how tools are registered
grep -rn "toolDefinitions\|allTools\|registerTool" src/ --include="*.ts"

# Find the execution entry point for a tool
grep -n "async.*call(" src/tools/GlobTool/GlobTool.ts

# Find how a tool's result flows back
grep -rn "tool_result\|toolResult" src/ --include="*.ts"
```

## Common Patterns in the Source

### Tool definition pattern

Every tool has:
1. **Schema** — `name`, `description`, `input_schema` (what the LLM sees)
2. **call()** — the handler that runs when the tool is invoked
3. **UI component** — React component to render the tool's output
4. **Prompt** — instructions added to the system prompt about when/how to use the tool

### Finding how things connect

When you find a function and want to know what calls it:

```bash
# Who calls runTools?
grep -rn "runTools" src/ --include="*.ts"

# Who imports from query.ts?
grep -rn "from.*query" src/ --include="*.ts"
```

When you find a type and want to understand it:

```bash
# Find the type definition
grep -rn "interface ToolUseBlock\|type ToolUseBlock" src/ --include="*.ts"
```

## Key Insight

You navigate a large codebase the same way Claude Code's own tools work:

| Task | Tool | Manual equivalent |
|------|------|-------------------|
| Find files by name | Glob | `find . -name "*.ts"` |
| Search file contents | Grep | `grep -rn "pattern" src/` |
| Read specific file | Read | `cat src/tools/GlobTool/GlobTool.ts` |

The tools exist because this is how you explore any large codebase — you
don't read everything, you search for what you need.

## Suggested Exploration Order

If you want to understand Claude Code's internals:

1. `src/tools/GlobTool/GlobTool.ts` — simplest tool, learn the pattern
2. `src/tools/FileReadTool/FileReadTool.ts` — core tool, more complex
3. `src/tools/BashTool/BashTool.ts` — most complex, sandboxing + permissions
4. `src/query.ts` — the agent loop that ties it all together
5. `src/services/tools/toolOrchestration.ts` — how tools are batched and executed
