# Design Doc: Codebase Q&A Agent

A learning project that covers every core AI agent concept by building a practical tool — an agent that answers questions about a code repository.

---

## Purpose

Build a minimal AI agent from scratch (no frameworks) that:
- Takes a code repository path as input
- Answers natural language questions about the code
- Finds bugs, explains architecture, generates documentation
- Demonstrates: agent loop, tools, MCP, skills, sub-agents, hooks, context management

---

## Tech Stack

- **Language:** Python
- **LLM:** Claude (via Anthropic SDK)
- **MCP:** `mcp` Python library (for building MCP server)
- **Package manager:** uv
- **No frameworks** (no LangChain, no CrewAI) — the point is to learn by building each concept

---

## Architecture Overview

```
User
  │
  ▼
┌─────────────────────────────────┐
│  Main Agent (agent loop)         │
│  - Receives user question        │
│  - Thinks about what to do       │
│  - Calls tools                   │
│  - Observes results              │
│  - Repeats until answer is ready │
├─────────────────────────────────┤
│  Tools (built-in)                │    MCP Servers (external)
│  - read_file                     │    - SQLite (Q&A history)
│  - search_code                   │    - Fetch (live docs)
│  - list_files                    │
│  - run_command                   │
├─────────────────────────────────┤
│  Skills (loaded conditionally)   │
│  - architecture-analysis         │
│  - bug-finding                   │
│  - code-explanation              │
├─────────────────────────────────┤
│  Hooks (always execute)          │
│  - log every tool call           │
│  - block reading .env files      │
│  - validate file exists before read │
├─────────────────────────────────┤
│  Sub-agents (parallel workers)   │
│  - per-file analysis             │
│  - parallel search               │
└─────────────────────────────────┘
```

---

## Build Steps

Each step introduces one concept. Build and test each step before moving to the next.

### Step 1: Agent Loop + Tools

**Goal:** Build the core loop and hardcoded tools.

**What to build:**

```python
# agent.py — the core agent loop

import anthropic

client = anthropic.Anthropic()

# Define tools
tools = [
    {
        "name": "read_file",
        "description": "Read the contents of a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to repo root"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "search_code",
        "description": "Search for a pattern in the codebase using grep",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string"},
                "file_type": {"type": "string", "description": "e.g. py, js, ts"}
            },
            "required": ["pattern"]
        }
    },
    {
        "name": "list_files",
        "description": "List files in a directory",
        "input_schema": {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Directory path relative to repo root"}
            },
            "required": ["directory"]
        }
    },
    {
        "name": "run_tests",
        "description": "Run the test suite or a specific test file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Optional: specific test file"}
            }
        }
    }
]

# Tool execution — actually perform the action
def execute_tool(name, input):
    if name == "read_file":
        # Read and return file contents
        ...
    elif name == "search_code":
        # Run grep/ripgrep and return results
        ...
    elif name == "list_files":
        # List directory contents
        ...
    elif name == "run_tests":
        # Run pytest and return output
        ...

# The agent loop
def agent_loop(user_question, repo_path):
    messages = [{"role": "user", "content": user_question}]
    system = f"You are a code assistant for the repository at {repo_path}."

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=system,
            tools=tools,
            messages=messages
        )

        # Check if model wants to use a tool
        if response.stop_reason == "tool_use":
            # Extract tool calls from response
            tool_calls = [b for b in response.content if b.type == "tool_use"]

            # Add assistant's response to history
            messages.append({"role": "assistant", "content": response.content})

            # Execute each tool and collect results
            tool_results = []
            for tc in tool_calls:
                result = execute_tool(tc.name, tc.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tc.id,
                    "content": result
                })

            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            # Model is done — extract and return text
            text = "".join(b.text for b in response.content if hasattr(b, "text"))
            return text
```

**What you learn:** How tool definitions work, the tool_use/tool_result flow, the think-act-observe loop.

**Test:** Ask "What does this project do?" and "What files are in the src directory?" — the agent should use tools and answer.

---

### Step 2: MCP

**Goal:** Move tools into an MCP server. The agent discovers tools at runtime instead of hardcoding them.

**What to build:**

```python
# mcp_server.py — a standalone MCP server

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Codebase Tools")

@mcp.tool()
def read_file(path: str) -> str:
    """Read the contents of a file"""
    with open(path) as f:
        return f.read()

@mcp.tool()
def search_code(pattern: str, file_type: str = "") -> str:
    """Search for a pattern in the codebase"""
    import subprocess
    cmd = ["grep", "-r", pattern, "."]
    if file_type:
        cmd.extend(["--include", f"*.{file_type}"])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

@mcp.tool()
def list_files(directory: str = ".") -> str:
    """List files in a directory"""
    import os
    return "\n".join(os.listdir(directory))

mcp.run()
```

```python
# agent.py — modified to discover tools from MCP

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def get_tools_from_mcp():
    server = StdioServerParameters(command="python", args=["mcp_server.py"])
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            return tools  # These go into the API's tools parameter

async def call_mcp_tool(name, arguments):
    # Route tool call to MCP server
    ...
```

**What you learn:** Tool discovery, why MCP exists (decouple tool definition from agent code), the client-server pattern.

**Test:** Same questions as Step 1, but now tools come from the MCP server. Add a second MCP server (e.g., `@modelcontextprotocol/server-fetch`) and see tools from both servers merged.

---

### Step 3: Context Management

**Goal:** Handle the finite context window when working with large codebases.

**What to build:**

- **Truncation:** If a file is too large, read only first N lines + relevant sections
- **Summarization:** When conversation history grows long, summarize older messages
- **Selective loading:** Don't read entire files — search first, then read specific sections

```python
def execute_read_file(path):
    content = read_file(path)
    if len(content) > 5000:  # Too big for context
        return f"[File truncated — {len(content)} chars total]\n" + content[:5000]
    return content

def compact_messages(messages):
    """When messages exceed threshold, summarize older ones"""
    if count_tokens(messages) > 50000:
        old = messages[:len(messages)//2]
        summary = client.messages.create(
            model="claude-haiku-4-5",  # Cheap model for summarization
            messages=[{"role": "user", "content": f"Summarize this conversation:\n{old}"}]
        )
        return [{"role": "user", "content": f"[Previous context summary]: {summary}"}] + messages[len(messages)//2:]
    return messages
```

**What you learn:** Why context management matters, token budgeting, compaction strategies.

**Test:** Point at a large repo. Ask a question that requires reading many files. Without management, it breaks. With management, it works.

---

### Step 4: Sub-agents

**Goal:** Parallelize work by spawning child agent conversations.

**What to build:**

```python
import asyncio

async def analyze_module(question, repo_path):
    """Spawn sub-agents to analyze multiple files in parallel"""
    files = list_python_files(repo_path)

    async def analyze_one_file(file_path):
        """Each sub-agent gets its own conversation"""
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=f"Analyze this file and answer: {question}",
            tools=tools,
            messages=[{"role": "user", "content": read_file(file_path)}]
        )
        return {"file": file_path, "analysis": response.content}

    # Run all sub-agents in parallel
    results = await asyncio.gather(*[analyze_one_file(f) for f in files])

    # Main agent combines results
    combined = "\n".join(f"## {r['file']}\n{r['analysis']}" for r in results)
    final = client.messages.create(
        model="claude-sonnet-4-6",
        messages=[{"role": "user", "content": f"Combine these analyses:\n{combined}"}]
    )
    return final
```

**What you learn:** Context isolation, parallel execution, result aggregation.

**Test:** Ask "Find potential bugs in this module" — watch sub-agents analyze files in parallel and the main agent combine findings.

---

### Step 5: Skills

**Goal:** Add conditionally-loaded instruction sets for different types of questions.

**What to build:**

```
skills/
├── architecture/
│   └── SKILL.md      # "When analyzing architecture: find entry points,
│                      #  trace imports, identify patterns..."
├── bug-finding/
│   └── SKILL.md      # "When finding bugs: check error handling,
│                      #  look for off-by-one errors, verify null checks..."
└── explain-code/
    └── SKILL.md      # "When explaining code: start with the high-level
                       #  purpose, then walk through the implementation..."
```

```python
def load_relevant_skills(user_question):
    """Load skills based on question type"""
    skills_dir = "skills/"
    loaded = []
    for skill_folder in os.listdir(skills_dir):
        # Read just the frontmatter (name + description)
        frontmatter = read_frontmatter(f"{skills_dir}/{skill_folder}/SKILL.md")
        # Simple relevance check (could be more sophisticated)
        if is_relevant(frontmatter["description"], user_question):
            full_content = read_file(f"{skills_dir}/{skill_folder}/SKILL.md")
            loaded.append(full_content)
    return "\n".join(loaded)

def agent_loop(user_question, repo_path):
    skill_text = load_relevant_skills(user_question)
    system = f"""You are a code assistant for {repo_path}.

{skill_text}"""
    # ... rest of agent loop
```

**What you learn:** Conditional loading, context efficiency, instructions vs capabilities.

**Test:** Ask "explain the main function" vs "find bugs in auth.py" — different skills load for each.

---

### Step 6: Hooks

**Goal:** Add guaranteed lifecycle checks that always execute.

**What to build:**

```python
# hooks.py

def pre_tool_use(tool_name, tool_input):
    """Runs BEFORE every tool call — guaranteed, not LLM-dependent"""

    # Security: block reading sensitive files
    if tool_name == "read_file":
        blocked = [".env", "credentials", "secret", ".pem"]
        if any(b in tool_input.get("path", "") for b in blocked):
            return {"blocked": True, "reason": "Sensitive file access blocked"}

    # Validation: check file exists before reading
    if tool_name == "read_file":
        if not os.path.exists(tool_input["path"]):
            return {"blocked": True, "reason": f"File not found: {tool_input['path']}"}

    return {"blocked": False}

def post_tool_use(tool_name, tool_input, tool_result):
    """Runs AFTER every tool call"""

    # Logging: record every tool call for debugging
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "tool": tool_name,
        "input": tool_input,
        "result_length": len(str(tool_result))
    }
    with open("agent_log.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

# Integrate into agent loop
def execute_tool(name, input):
    # Pre-hook
    check = pre_tool_use(name, input)
    if check["blocked"]:
        return f"BLOCKED: {check['reason']}"

    # Execute
    result = _execute_tool_impl(name, input)

    # Post-hook
    post_tool_use(name, input, result)

    return result
```

**What you learn:** Guaranteed execution vs LLM judgment, lifecycle events, security guardrails.

**Test:** Try asking the agent to read `.env` — hook blocks it. Check `agent_log.jsonl` — every tool call is logged regardless of what the LLM does.

---

## Project Structure

```
codebase-qa-agent/
├── pyproject.toml
├── src/
│   ├── agent.py              # Core agent loop (Step 1)
│   ├── tools.py              # Tool definitions + execution (Step 1)
│   ├── mcp_server.py         # MCP server wrapping tools (Step 2)
│   ├── mcp_client.py         # MCP client for tool discovery (Step 2)
│   ├── context.py            # Context window management (Step 3)
│   ├── subagents.py          # Sub-agent spawning + aggregation (Step 4)
│   ├── skills.py             # Skill loading logic (Step 5)
│   └── hooks.py              # Pre/post hook system (Step 6)
├── skills/
│   ├── architecture/SKILL.md
│   ├── bug-finding/SKILL.md
│   └── explain-code/SKILL.md
├── tests/
│   ├── test_agent_loop.py
│   ├── test_tools.py
│   ├── test_mcp.py
│   └── test_hooks.py
└── README.md
```

---

## Dependencies

```toml
[project]
dependencies = [
    "anthropic",       # Claude API client
    "mcp",             # MCP server + client library
]

[dependency-groups]
dev = [
    "pytest",
    "pytest-asyncio",  # For async sub-agent tests
]
```

---

## Notes for Implementation

- Build each step incrementally — get Step 1 working before touching Step 2
- Use `claude-haiku-4-5` for cheap operations (summarization, sub-agents) and `claude-sonnet-4-6` for the main agent
- Keep the MCP server as a separate process — this is how real MCP works
- Test with a small, familiar repo first (this project itself works well)
- Each step should have its own tests proving the concept works
