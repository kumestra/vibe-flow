# AI Agent Concepts — Learning Notes

Everything below was learned through interactive Q&A inside Claude Code, organized by topic.

---

## 1. What Makes Something an "AI Agent"

An AI agent is an LLM-powered application that can **take actions**, not just generate text. The two concepts that are universal to **every** AI agent — regardless of model, programming language, or purpose — are:

- **Agent Loop** (Think → Act → Observe → Repeat)
- **Tool Use** (LLM outputs a structured call → system executes → result returns to LLM)

If it has these two things, it's an agent. Everything else (MCP, skills, hooks, sub-agents, plugins) is optional and added when the problem demands it.

---

## 2. Tools / Function Calling

### What It Is

The mechanism that lets an LLM do more than generate text. Instead of outputting a plain answer, the LLM outputs a structured request (function name + arguments), an external system executes it, and the result is fed back to the LLM.

### History

- **Pre-2023:** LLMs were text-only. People used hacky workarounds like asking the model to output JSON and parsing it manually.
- **June 2023:** OpenAI introduced "function calling" in GPT-3.5/GPT-4 — the watershed moment.
- **Late 2023–2024:** Anthropic, Google, and others added their own implementations. It became an industry standard.

### "Function Calling" vs "Tool Use"

Same mechanism, different names:

- **Function calling** — OpenAI's original term (June 2023). Their API used a `functions` parameter.
- **Tool use** — Anthropic's preferred term. Broader framing — a "tool" isn't limited to a code function. In November 2023, even OpenAI renamed their API parameter from `functions` to `tools`.

"Tool use" won and became the standard term.

### How It Works at the API Level

Tools are defined as a **separate top-level `tools` parameter** in the API request — not embedded in the system prompt. The API is stateless, so the full `tools` array is sent with **every** request.

```json
{
  "model": "claude-opus-4-6",
  "system": "You are a helpful assistant.",
  "tools": [
    {
      "name": "get_weather",
      "description": "Get weather for a city",
      "input_schema": {
        "type": "object",
        "properties": { "city": { "type": "string" } },
        "required": ["city"]
      }
    }
  ],
  "messages": [
    { "role": "user", "content": "What's the weather in Tokyo?" }
  ]
}
```

When the model wants to use a tool, it responds with a `tool_use` block (in an `assistant` message). The result goes back as a `tool_result` wrapped in a `user` message. The `tool_use_id` links results to requests — important when multiple tools are called in parallel.

### Full API Request with Chat History

```json
{
  "model": "claude-opus-4-6",
  "max_tokens": 1024,
  "system": "You are a helpful travel assistant.",
  "tools": [ { "name": "get_weather", ... } ],
  "messages": [
    { "role": "user", "content": "Hi, I'm planning a trip to Tokyo" },
    { "role": "assistant", "content": "Nice! Want me to check the weather?" },
    { "role": "user", "content": "Yes please" },
    { "role": "assistant", "content": [
        { "type": "tool_use", "id": "tool_abc123", "name": "get_weather",
          "input": { "city": "Tokyo" } }
    ]},
    { "role": "user", "content": [
        { "type": "tool_result", "tool_use_id": "tool_abc123",
          "content": "Tokyo: 22°C, partly cloudy" }
    ]},
    { "role": "assistant", "content": "It's currently 22°C and partly cloudy in Tokyo." },
    { "role": "user", "content": "What about Osaka?" }
  ]
}
```

---

## 3. MCP (Model Context Protocol)

### Why MCP Exists

Tool use works, but has a scaling problem: every AI app must implement its own integration code for every service. If App A and App B both want GitHub access, they both write custom code. MCP solves this with a standard protocol — like USB for AI tools.

```
Without MCP:
  App A ──custom code──> GitHub
  App B ──custom code──> GitHub  (duplicated effort)

With MCP:
  App A ─┐                ┌── GitHub MCP Server (built once)
         ├── MCP protocol ├── Slack MCP Server  (built once)
  App B ─┘                └── Database MCP Server (built once)
```

### How It Works

1. App (MCP client) connects to MCP server and asks: "What tools do you have?"
2. MCP server responds with tool definitions (same format as raw tool use)
3. App puts those discovered tools into the LLM API `tools` parameter
4. When LLM responds with a `tool_use`, the app routes the call to the correct MCP server
5. MCP server executes the action against the real service and returns the result
6. App sends the result back to the LLM

**The LLM never talks to the MCP server directly.** It just sees tools in the standard format. It doesn't know MCP exists.

### Key Difference from Raw Tool Use

| | Raw tool use | With MCP |
|---|---|---|
| Who defines tools? | Developer, hardcoded | MCP server, discovered at runtime |
| Reusable across apps? | No | Yes, plug and play |
| Adding a new service | Write code in your app | Connect to an existing MCP server |

### MCP as Open Standard

MCP was created by Anthropic but released as an open standard. Adopted by Cursor, VS Code Copilot, Windsurf, Gemini CLI, and many others.

### When to Use MCP with Claude Code

Claude Code already has strong built-in tools (Read, Write, Edit, Bash, Grep, Glob, WebSearch). Only add MCP when you need to:

1. **Connect to an external service** (GitHub API, database, Slack, Figma) — Claude Code can't reach these natively
2. **Gain a capability it doesn't have** (browser automation, image generation) — genuinely missing ability

MCP servers for filesystem, git, or web fetching are mostly redundant with Claude Code's built-in tools.

### Example: PostgreSQL MCP

PostgreSQL itself doesn't launch an MCP server. A separate program (the MCP server) acts as a bridge:

```
Claude Code ←→ PostgreSQL MCP Server ←→ PostgreSQL Database
                (a Node.js/Python app)    (the actual DB engine)
```

The MCP server receives SQL from Claude Code, sends it to PostgreSQL, and returns results. PostgreSQL has no idea MCP exists.

---

## 4. Skills

### What It Is

A folder containing instructions (and optionally scripts/resources) that teaches an AI agent **how to approach a specific type of task**. The simplest form is just a `SKILL.md` file with plain English instructions.

### How Skills Differ from Tools and MCP

```
Tools  → let the agent DO things (read files, run commands)
MCP    → let the agent ACCESS things (databases, APIs, services)
Skills → teach the agent HOW to do things (workflows, best practices)
```

### How Skills Reach the LLM

Skills are **NOT an LLM API concept**. There's no `skills` parameter. They're purely a client-side pattern — the agent reads the markdown files and injects them as text into the system prompt/context.

| Concept | API mechanism |
|---|---|
| Tools | Dedicated `tools` parameter |
| MCP | Tools discovered from servers, put into `tools` parameter |
| Skills | Plain text injected into system prompt or context |

### Progressive Loading (Context Efficiency)

Skills use a two-step loading process:

1. **Always loaded:** YAML frontmatter only (name + description, ~100 tokens per skill). Claude Code uses this to decide relevance.
2. **Loaded on demand:** Full `SKILL.md` content, only when the current task matches. Referenced files are loaded when `SKILL.md` mentions them. Scripts are executed and only their output enters context.

### Skills vs CLAUDE.md

- **CLAUDE.md** — always in context, every conversation. For project-wide rules.
- **Skills** — loaded conditionally. For specific task workflows. Saves context window space.

### When Skills Are Valuable

- Enforcing multi-step workflows (TDD, deployment checklists)
- Project-specific conventions too detailed for CLAUDE.md
- Slash commands for repetitive tasks
- Team sharing — everyone gets the same instructions

For solo developers with simple workflows, CLAUDE.md + just talking to Claude Code covers most cases.

---

## 5. Sub-agents

### What It Is

The main Claude Code instance spawning another instance of itself to handle a subtask. Each sub-agent gets its own fresh context window.

### Why Sub-agents Exist

1. **Parallelism** — multiple subtasks run simultaneously instead of sequentially
2. **Context window protection** — research/exploration happens in a separate context, only a summary returns to the main conversation

### At the API Level

Nothing special — a sub-agent is just another separate LLM API conversation. Same model, same tools, different context.

---

## 6. Hooks

### What It Is

User-defined commands that execute automatically at specific points in Claude Code's lifecycle. For example: before a Bash command runs, after a file is edited, before a commit.

### Key Difference from Skills

| | Skill | Hook |
|---|---|---|
| Who decides to use it? | LLM ("this looks relevant") | System (pattern matched, always fires) |
| Can it be skipped? | Yes, LLM might not load it | No, guaranteed execution |
| Runs where? | Inside context window (as text) | Outside context window (as code) |
| Reliability | Best effort | 100% |

**Skills = guidelines** (LLM should follow, but might not). **Hooks = guardrails** (system enforces, always fires).

For anything that **must** happen — security checks, formatting, validation — use hooks.

---

## 7. Plugins

### What It Is

A packaging/distribution format that bundles skills, hooks, MCP servers, and sub-agents into a single installable unit.

```
my-plugin/
├── skills/        ← skills
├── agents/        ← sub-agents
├── hooks/         ← hooks
├── mcp-servers/   ← MCP servers
└── plugin.json    ← metadata
```

### Current Adoption

Plugins are the **newest and least adopted** concept. Most people today still configure MCP, skills, and hooks directly. Plugins become valuable when sharing complete workflows across teams or publicly. The ecosystem is similar to npm — most people use individual packages, not mega-frameworks.

---

## 8. The Agent Loop

The fundamental cycle every AI agent repeats:

```
Think → Act (use a tool) → Observe (read the result) → Repeat
```

This continues until the task is done. Every interaction follows this loop. It's universal across all agent frameworks and implementations.

---

## 9. Context Window

The finite "working memory" of the LLM — all text it can reference when generating a response (system prompt, tool definitions, conversation history, skill content, etc.). Key management strategies:

- **Auto-compaction** — summarizing old messages as conversation grows
- **Selective loading** — skills loaded only when relevant
- **Sub-agents** — heavy research happens in isolated contexts
- **Script execution** — only output enters context, not source code

---

## 10. Concept Hierarchy and Universality

### Universal (every AI agent has these):

```
Agent Loop + Tool Use
```

True regardless of model, language, or purpose.

### Optional (added when needed):

| Concept | When to add |
|---|---|
| MCP | Need external service connections |
| Skills | Need loadable instruction sets |
| Sub-agents | Complex/parallel tasks |
| Hooks | Guaranteed lifecycle checks |
| Plugins | Distribution/sharing |
| Context management | Long conversations or large data |

### Cross-platform equivalents:

| Concept | Claude Code | Cursor | GitHub Copilot | Codex CLI |
|---|---|---|---|---|
| Project instructions | CLAUDE.md | .cursorrules | .github/copilot-instructions.md | AGENTS.md |
| Tools | Built-in | Built-in | Built-in | Built-in |
| MCP | Supported | Supported | Supported | Supported |
| Skills | Supported | Supported | — | Supported |

---

## 11. Practical Notes

### Claude Code Debugging

Claude Code debugs by **reading and reasoning**, not by using a traditional debugger. It can't set breakpoints or step through code line by line. Its approach is essentially print debugging: add print statements → run → read output → reason → fix → verify.

Debugger MCP servers exist (Microsoft DebugMCP, mcp-debugger, node-debugger-mcp) but aren't mainstream yet due to context window cost and decision-making overhead per step.

### Claude Code for SRE

Claude Code can help with SRE tasks reactively (debug pods, analyze logs, write Terraform), but it can't monitor continuously or auto-respond to alerts — you must start it manually. Dedicated SRE agents (Datadog Bits AI, AWS multi-agent SRE) run 24/7 and react to alerts automatically. Both use the same underlying concepts.

### Programming Languages

Python dominates AI agents (~80%), TypeScript is growing fast. Claude Code itself is built in TypeScript. For learning/building agents, Python has the most examples and tutorials; TypeScript is closer to how production dev tools are built.

### Open Source

Claude Code's source is on GitHub (78K+ stars) but development is primarily by Anthropic employees. Community contributes via building skills, hooks, MCP servers, and plugins — not by modifying Claude Code itself.

### Frameworks vs From Scratch

Top production agents (Claude Code, Cursor, Copilot, Devin) are built from scratch for full control. Frameworks (LangChain, CrewAI) are popular for internal tools and prototypes. For learning, building from scratch is recommended — frameworks hide the concepts you're trying to understand.

---

## 12. Timeline

| When | What happened |
|---|---|
| June 2023 | OpenAI introduces function calling (GPT-3.5/GPT-4) |
| Nov 2023 | OpenAI renames `functions` → `tools` parameter |
| 2024 | Tool use becomes industry standard across all providers |
| 2024–2025 | Anthropic introduces MCP as open standard |
| Oct 2025 | Anthropic introduces Skills |
| Early 2026 | Hooks system released for Claude Code |
| 2026 | Plugins emerge as packaging/distribution format |
