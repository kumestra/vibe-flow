# Skills Design: The General Idea

## The One-Line Summary

A skill is just a long prompt with a name and a description — cheap to advertise, expensive to load, fetched only when Claude decides it's needed.

---

## The Problem Skills Solve

An agent's system prompt is a **shared resource with a hard budget**. Every token you put in it:

1. 💰 Costs money on **every single API call** (even turns where it's irrelevant)
2. 📏 Eats into the **context window** available for real work
3. 🎯 Competes for the model's **attention** — more instructions means each one gets less focus

But a useful agent needs to know *a lot* of procedural knowledge:

- How to write a good commit message
- How to format a PR description
- How to debug a flaky test
- How to run the project's specific deploy pipeline
- How to review code for security issues
- How to write database migrations safely
- ...

This list grows without bound as the agent is used for more workflows.

### The naive approach (and why it fails)

Stuff everything into the system prompt.

```
system_prompt = base_instructions + commit_guide + pr_guide +
                debug_guide + deploy_guide + security_guide + ...
```

This fails fast:

- Token cost explodes — you pay for the `deploy_guide` on turns that have nothing to do with deploying.
- The prompt becomes unreadable and unmaintainable.
- The model's attention gets diluted across instructions that are **irrelevant to 99% of turns**.
- Adding a new workflow requires editing the base prompt, which risks regressing everything else.

### The key insight

Most procedural knowledge is **conditionally relevant**. You only need the commit guide when you're committing. You only need the flaky-test guide when a test is flaky. So **why pay for it always**?

---

## The Core Mechanism: Progressive Disclosure

Skills implement a **two-level loading strategy**:

```
┌─────────────────────────────────────────────────────────┐
│  Level 1 — always in context (cheap)                    │
│                                                          │
│  skill name + one-line description                      │
│                                                          │
│    commit       → "Create a well-formatted git commit"  │
│    review-pr    → "Review a GitHub PR for correctness"  │
│    debug-flaky  → "Diagnose and fix flaky tests"        │
│    ...                                                   │
└─────────────────────────────────────────────────────────┘
                          │
                          │ Claude decides: "I need skill X"
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Level 2 — loaded on demand (expensive)                 │
│                                                          │
│  the full skill body — instructions, examples,         │
│  templates, step-by-step procedures                     │
│                                                          │
│  only paid for when Claude actually picks this skill    │
└─────────────────────────────────────────────────────────┘
```

You pay the cheap cost (name + description) **always**, and the expensive cost (full body) **only when relevant**.

This is the same pattern as:

| System | Level 1 (cheap, always) | Level 2 (expensive, on demand) |
|---|---|---|
| **File system** | `ls` lists filenames | `cat` reads file contents |
| **Library imports** | You know `numpy` exists | You pay to `import numpy` |
| **Tool definitions** | Schema in context | Execution result |
| **Skills** | Name + description | Full prompt body |

Skills are **"knowledge imports"** — lazy-loaded procedural manuals.

---

## The Symmetry With Tools

Once you see skills as "a prompt fragment with lazy loading," the parallel with tools becomes obvious:

|                          | Tool                              | Skill                         |
| ------------------------ | --------------------------------- | ----------------------------- |
| **Always in context**    | name + description + input schema | name + description            |
| **Loaded on demand**     | execution result (from code)      | body text (from a file)       |
| **Trigger**              | Claude emits a `tool_use` block   | Claude emits "use skill X"    |
| **Cost model**           | pay per call                      | pay per load                  |
| **What it gives Claude** | *data / side effects*             | *instructions*                |
| **Runtime**              | runs code                         | reads a file                  |

The **only real difference** is what sits on the other end of the request:

- **Tool** → code runs, returns data
- **Skill** → a file is read, returns text that becomes part of the prompt

That's a beautifully small difference. It's why skills feel natural in a system that already has tools — they reuse the exact same "name + description + on-demand fetch" pattern. No new mental model needed.

---

## The Hard Part: Routing

The tricky part isn't *storing* skills — it's the **routing decision**. How does Claude know which skill to load?

| Approach | Pro | Con |
|---|---|---|
| User explicitly invokes (`/commit`) | Zero ambiguity | Requires user to know what exists |
| Claude reads descriptions and picks | Automatic | Descriptions must be discriminating; risk of wrong pick |
| Keyword/regex matching in the harness | Fast, deterministic | Brittle, can't handle paraphrase |
| Embedding / semantic retrieval | Scales to many skills | Adds infrastructure, latency |

A mature design uses **a mix**:

- **Short descriptions in context + Claude chooses** for automatic invocation
- **Slash commands** for explicit user invocation (`/commit`, `/review-pr`)

### The description is the API contract

This is the most important practical lesson:

> A skill with a perfect body and a vague description is **dead weight** — Claude will never load it.

The description is the only thing Claude sees at decision time. If it's vague, generic, or buried, the skill won't be picked. If it's specific and discriminating, the skill will be loaded exactly when it should be.

This mirrors tool design exactly: the tool schema is for the runtime, the description is for the model.

---

## Two Wins At Once

Skills give you two distinct benefits, and it's worth separating them:

### Win #1 — 💰 Cost

You don't pay for instructions you're not using. A project with 30 skills doesn't pay for 30 prompts per turn — it pays for 30 one-liners per turn, and the full body of whichever one (if any) Claude actually loads.

### Win #2 — 🎯 Attention

Even if tokens were free, stuffing 50 workflows into the base system prompt would **hurt performance**. The model has to attend to all of them on every turn and decide which (if any) applies. By only loading the relevant skill, you remove distractors. The model isn't just paying less — it's also **thinking more clearly**, because the instructions it's reading are all relevant to the current task.

This is the same reason you'd rather have 5 focused tools than 50 tools where 45 are irrelevant to your task.

---

## Design Trade-offs

### Skill granularity

- **Too fine** → Claude has to chain many skills; routing overhead dominates.
- **Too coarse** → each skill is huge, loses the "only pay for what you need" benefit.
- **Sweet spot** → one skill per **coherent workflow or playbook**.

### Skill autonomy

- **Pure instructions (markdown)** → simple, portable, no runtime requirements.
- **Instructions + scripts/resources** → more powerful, but now skills have runtime dependencies.
- A good system supports both, with pure markdown as the default.

### Skill discovery scope

- **Project-local** (e.g. `.claude/skills/`) → version-controlled with code, team-shared.
- **User-global** (e.g. `~/.claude/skills/`) → personal workflows across all projects.
- **Both**, with project overriding user — same pattern as `CLAUDE.md`.

### Model-invocable vs user-invocable

- **User-invocable** — triggered explicitly via slash command. The user knows what they want.
- **Model-invocable** — Claude picks autonomously when the task matches the description.
- Some skills are both (the user *can* invoke `/commit`, and Claude *can* also pick it up when the user says "commit these changes").

---

## Skills vs Tools vs Sub-Agents

This is the interesting architectural question. All three are ways to **extend the base agent**, but they're fundamentally different primitives:

| Primitive      | Question it answers            | Mechanism                                         |
| -------------- | ------------------------------ | ------------------------------------------------- |
| **Tool**       | "I need to **do** something"   | Atomic action with structured input/output        |
| **Sub-agent**  | "I need to **delegate** something" | Recursive isolated agent loop with its own context |
| **Skill**      | "I need to **know** something" | Loaded instructions, executed in current context  |

The crucial distinction for skills:

- Skills **don't fork context**. A sub-agent runs in isolation; a skill is text added to *this* conversation.
- Skills **don't execute anything**. A tool runs code; a skill just injects prompt text.
- Skills **don't return results**. They change *how Claude thinks* going forward, not *what Claude knows about the world*.

```
base agent (small system prompt)
  ├── tools       → actions       (do things)
  ├── sub-agents  → delegation    (fork a conversation)
  └── skills      → knowledge     (lazy-load instructions)
```

These three primitives are **orthogonal**. You can combine them: a sub-agent can load skills; a skill can instruct Claude to use specific tools; a tool's output can trigger Claude to load a skill.

---

## What Writing a Good Skill Looks Like

Since a skill is "just a long prompt," **writing a good skill = writing a good prompt**. All the usual prompt engineering applies:

- Be specific about inputs, outputs, and constraints.
- Give concrete examples.
- Show the exact format you want.
- State failure modes and how to handle them.
- Don't assume context the model won't have.

There is no magic skill syntax that makes mediocre instructions work. A skill is as good as the prompt inside it.

The **description**, separately, must be written for a different reader: the model at routing time, which only sees that one line. It should answer "**when should I use this?**" not "**what does this do?**".

- ❌ "A skill for commits" (vague, doesn't say *when*)
- ❌ "Git commit helper utility" (too terse, feels like a library name)
- ✅ "Create a well-formatted git commit following the project's conventional-commit style — use when the user asks to commit changes"

---

## Why Skills Matter For The Python Rewrite

For `vibe-flow`, we've been building the first two legs of the stool:

- ✅ **Tools** — `bash`, `read_file`, `write_file`
- 🚧 **Sub-agents** — documented, not yet implemented
- ❌ **Skills** — not yet touched

Without skills, every workflow we want the agent to do well must go into the system prompt → bloat. With skills, we can keep the base prompt small and **scale knowledge horizontally** by adding markdown files. That's a very attractive property for a learning project: we can grow capabilities without rewriting the core.

A minimal Python implementation of skills would look roughly like:

```python
# 1. Discovery: scan a directory for skill files
skills = load_skills_from("./skills/")   # returns [{name, description, body_path}, ...]

# 2. Advertisement: inject names + descriptions into system prompt
system_prompt += format_skill_list(skills)

# 3. Routing: expose a "load_skill" tool that reads the body
def load_skill(name: str) -> str:
    return read_file(skills[name].body_path)

# 4. Claude picks the skill, harness loads the body, body becomes part of the conversation.
```

That's the whole mechanism. Everything else — frontmatter, slash commands, scoping, permissions — is plumbing around this core idea.

---

## Summary

> **A skill is a long prompt with a name and description. The description is always in context (cheap). The body is loaded only when Claude picks it (expensive). That's it.**

Everything else follows from this:

- Two-level loading → progressive disclosure → cheap + sharp
- Description is the API contract → must answer "when to use this"
- Symmetric with tools → reuses the "name + desc + lazy fetch" pattern
- Orthogonal to sub-agents → skills inject text, sub-agents fork context
- Writing a skill = writing a prompt → all prompt engineering applies

Next: go read the Claude Code source and see how this actually looks in production — file layout, frontmatter schema, discovery, routing, and the loading mechanism.
