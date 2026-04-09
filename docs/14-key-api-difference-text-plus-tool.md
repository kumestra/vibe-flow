# The Key API Difference That Actually Matters for Agent Design

Most differences between the OpenAI and Anthropic APIs are trivial — different field names, different wrapping, different string formats. A thin adapter layer handles all of that in a few lines.

There is one difference that is **behavioral**, not cosmetic, and it forces a real design decision in every agent you build.

---

## The Difference

When the model decides to call a tool:

**Anthropic — text + tool call together:**

```json
{
  "stop_reason": "tool_use",
  "content": [
    {"type": "text",     "text": "I'll check the directory for you."},
    {"type": "tool_use", "id": "toolu_01Abc123", "name": "bash", "input": {...}}
  ]
}
```

**OpenAI — tool call only, no text:**

```json
{
  "finish_reason": "tool_calls",
  "message": {
    "content": null,
    "tool_calls": [{"id": "call_7Xk9mN", "name": "bash", "arguments": "..."}]
  }
}
```

Claude can return a `text` block **and** a `tool_use` block in the same response. GPT returns `content: null` — nothing to display, tool call only.

---

## Why This Matters

The text block Claude returns alongside a tool call is the model's **reasoning** — it's thinking out loud before acting:

> "I'll check the src/ directory for Python files."
> "Let me read that config file first to understand the structure."
> "I need to run this command to get the current state."

This is not the final answer. It's the model narrating what it's about to do. The final answer comes later, after the tool result, when `stop_reason` is `end_turn`.

GPT never does this — when it calls a tool, it goes silent.

---

## The Design Decision This Forces

Every time Claude calls a tool, you must decide what to do with the text block:

### Option A — Show it as a progress indicator

Display the text to the user in real time as the agent works.

```
User:  "How many Python files are in src/?"

Agent: "I'll check the src/ directory for Python files."   ← show this
       [runs: find src/ -name '*.py' | wc -l]
       [result: 7]

Agent: "There are 7 Python files in src/."                 ← show this too
```

**Good for:** CLI tools, chat interfaces where the user watches the agent work. Makes the agent feel transparent and trustworthy.

### Option B — Suppress it, show only the final reply

Buffer all intermediate text blocks silently. Only surface the `end_turn` response.

```
User:  "How many Python files are in src/?"
       [agent works silently...]
Agent: "There are 7 Python files in src/."
```

**Good for:** Automated pipelines, cases where intermediate reasoning is noise, or when the final answer is self-contained.

### Option C — Show it as a collapsible "thinking" section

Surface the reasoning but visually separate it from the answer.

```
User:  "How many Python files are in src/?"

▶ thinking  "I'll check the src/ directory for Python files."

Agent: "There are 7 Python files in src/."
```

**Good for:** Developer tools, debuggability, power users who want to see the agent's reasoning without it cluttering the main flow. Claude Code does something like this.

---

## The Trap: Dropping the Text Block from History

Whichever option you choose for display, **you must always store the full content array** — including the text block — when appending to message history.

```python
# CORRECT — append the full content array
messages.append({
    "role": "assistant",
    "content": response.content   # includes both text and tool_use blocks
})

# WRONG — dropping the text block
tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
messages.append({
    "role": "assistant",
    "content": tool_use_blocks    # stripped the text — now history is inconsistent
})
```

If you strip the text block before storing, the message history no longer matches what the model actually said. On the next request, the model sees a history that doesn't match its own output, which causes subtle degradation in reasoning quality.

**Display and storage are independent concerns.** Hide the text from the user if you want — but always keep it in the messages array.

---

## Summary

| | OpenAI (GPT) | Anthropic (Claude) |
|---|---|---|
| Tool call response | `content: null` + tool calls | `text` block + `tool_use` block |
| Intermediate reasoning | Never | Always (when it has something to say) |
| Design decision required | No | Yes — show, suppress, or style it |
| History storage | Straightforward | Must store full content array including text |

The other API differences — field names, JSON string vs object, which role carries tool results — are just syntax. This one changes how your agent feels to users and how you structure your rendering logic.
