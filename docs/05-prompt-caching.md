# Prompt Caching

How LLM APIs cache tokens to reduce cost and latency, and how this
shapes AI agent design.

## The Problem

Every API call sends the full conversation:

```
[system prompt] + [chat history] + [new message]
```

Without caching, a 100-turn conversation reprocesses the entire history
from scratch on every turn. Costs grow quadratically:

```
Turn 1:    1K tokens processed
Turn 2:    2K tokens processed
Turn 3:    3K tokens processed
...
Turn 100:  100K tokens processed

Total: ~5M tokens processed for a 100-turn conversation
```

## The Solution: Prefix Caching

The API caches a **prefix** of the input. If the beginning of a new
request matches a previous request, those tokens are served from cache
at reduced cost.

```
Turn 1:   [system prompt] + [msg1]
           └── cache MISS → process all, store in cache

Turn 2:   [system prompt] + [msg1] + [msg2]
           └── cache HIT ────────┘   └── new, full price

Turn 3:   [system prompt] + [msg1] + [msg2] + [msg3]
           └── cache HIT ──────────────────┘   └── new
```

Each turn, only the new content costs full price. Everything before it
is a cache hit.

## Critical Rule: Prefix Match Only

Caching works by matching from the **first character** forward. It is
NOT a substring search. Any change breaks the match at that point:

```
Last call:  [A][B][C][D][E]
New call:   [A][B][X][D][E]
                  ↑
            match breaks here

Cached:     [A][B]           ← cache hit (cheap)
Reprocess:       [X][D][E]  ← full price
```

Even though [D][E] is identical to the last call, it comes after the
mismatch point — no cache benefit.

## Cost Impact

| Provider | Cache write | Cache read | Minimum prefix |
|----------|-------------|------------|----------------|
| Anthropic | 1.25x normal | 0.1x normal (90% off) | 1,024 tokens |
| OpenAI | free | 0.5x normal (50% off) | 1,024 tokens |

### Example: 100-turn conversation

Without caching:
```
Total input tokens processed: ~5M
Cost: 5M × full price
```

With caching:
```
Turn 100: 100K tokens cached + 1K new tokens
Cost: 100K × cache price + 1K × full price
     = 100K × 0.1 + 1K × 1.0  (Anthropic)
     = 11K equivalent tokens
```

The marginal cost per turn stays roughly **constant** instead of growing
linearly. Long conversations become affordable.

## Design Rules for AI Agents

### 1. Keep the prefix stable

Put stable content first, changing content last:

```
Good:  [static system prompt] + [chat history] + [dynamic env info]
        └── always cached ──────────────────┘    └── small, changes ok

Bad:   [dynamic env info] + [static system prompt] + [chat history]
        └── changes → EVERYTHING reprocessed ──────────────────────┘
```

### 2. Append only — never rewrite history

Every time you modify or reorder earlier messages, the cache breaks from
that point forward.

```
Good:  messages.append(new_message)          ← prefix preserved
Bad:   messages[5] = summarize(messages[5])  ← cache breaks at msg 5
Bad:   messages = reorder(messages)          ← cache breaks entirely
```

### 3. Don't compact history prematurely

Compacting old messages saves context window space but **breaks the
cache**. This is a tradeoff:

```
Before compaction: 80K cached tokens × 0.1 = 8K equivalent cost
After compaction:  40K new tokens × 1.0    = 40K equivalent cost (worse!)
```

Only compact when approaching the context window limit — not "to save
tokens".

### 4. Put dynamic content at the end

Any content that changes between turns (timestamps, git status, env info)
must go at the end of the system prompt, not the beginning:

```
system_prompt = [
    "You are a helpful assistant...",     # static — cached
    "Use tools to help the user...",      # static — cached
    f"CWD: {cwd}\nDate: {today}",        # dynamic — at the end
]
```

## How Claude Code Does It

Claude Code splits the system prompt with a boundary marker:

```python
system_prompt = [
    # --- Static (cached across all turns) ---
    intro_section,          # identity
    system_section,         # rules and constraints
    doing_tasks_section,    # task execution guidance
    actions_section,        # action safety guidelines
    using_tools_section,    # tool usage guidance
    tone_section,           # communication style
    efficiency_section,     # output conciseness

    DYNAMIC_BOUNDARY,       # ← cache split marker

    # --- Dynamic (recomputed each turn) ---
    session_guidance,       # session-specific guidance
    memory,                 # user memories
    env_info,               # CWD, git status, OS
    mcp_instructions,       # MCP server info
    # ...
]
```

The static sections (~8-10K tokens) hit cache on every turn. Only the
dynamic sections (~1-2K tokens) are reprocessed.

### Context compaction

When approaching the context window limit, Claude Code uses "function
result clearing" (frc) — replacing old tool results with summaries.
This breaks the cache but is necessary to stay within limits.

```
Turns 1-80:   full history, cache covers ~95% → cheap
Turn 81:      compact old messages → cache breaks → expensive turn
Turns 82-160: new cache builds up → cheap again
```

## What This Means for Web Chat

Even on ChatGPT or Claude web, long conversations don't cost as much as
people think:

```
"I've been chatting for 2 hours, 100 messages, must be expensive"

Reality:
  Turn 100: [99 messages cached] + [1 new message]
  Cost ≈ cost of turn 1, not 100× turn 1
```

The marginal cost per turn is roughly constant. Caching makes the
per-turn cost almost independent of conversation length.

## What This Means for vibe-flow

Our `agent.py` already benefits from OpenAI's automatic prefix caching:

- `SYSTEM_PROMPT` is a fixed string — always cached
- Messages are append-only — prefix grows but stays stable
- No history rewriting — cache is never broken

No code changes needed. The design is already cache-friendly.

To make it explicit (like Claude Code), we could split the system prompt:

```python
SYSTEM_PROMPT_STATIC = "You are a helpful coding assistant..."
SYSTEM_PROMPT_DYNAMIC = f"CWD: {os.getcwd()}\nDate: {date.today()}"

messages = [
    {"role": "system", "content": SYSTEM_PROMPT_STATIC},
    {"role": "system", "content": SYSTEM_PROMPT_DYNAMIC},
] + conversation_messages
```

But since OpenAI caches automatically by prefix, the fixed string
approach works fine for now.
