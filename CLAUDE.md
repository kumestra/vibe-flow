# CLAUDE.md — Project Context for Claude Code

## What is this project?

vibe-flow is a **vibe coding playground** — not a serious product, not a business app, not a library. It exists purely for fun, learning, and experiencing AI-assisted coding. Each git branch is an independent experiment. There is no pressure to finish anything. The user wants to enjoy the journey, learn along the way, and explore every concept deeply. Even if an experiment doesn't succeed, that's fine — the learning is the goal.

## Who is the user?

- A solo developer doing this for fun
- Wrote frontend code about 10 years ago (Bootstrap era), now re-learning the modern web stack
- Familiar with basic React concepts (props, state, components) but learning modern patterns
- Currently learning Rust, Tailwind CSS, Next.js, TypeScript
- Prefers to **understand everything deeply** before moving on — don't just write code, explain it
- Prefers step-by-step approach: explain → write code → test → commit
- Likes writing docs as learning notes in markdown files in the `docs/` folder
- Does NOT want v0.dev for UI generation — prefers to learn and understand the tools
- Prefers raw Tailwind CSS over libraries that hide Tailwind details (wants to learn Tailwind itself)
- GitHub username: kumestra
- Git name: Evanara Kumestra

## Communication preferences

- Explain concepts thoroughly before writing code
- When writing code, explain what each part does
- Use step-by-step approach — don't write everything at once
- After each step, run and test the code before moving to the next
- The user often asks "why" questions — answer them patiently with context
- Compare new concepts to things the user already knows (Python, old CSS, npm)
- When the user asks about technology choices, research the internet for the latest 2026 information

## Git workflow

- Do NOT use `git -C /path/to/repo` — the working directory is already the repo
- Each branch is an experiment, branches are NOT meant to be merged
- Use numbered prefixes for doc files in folders (01-installation.md, 02-cargo-basics.md)
- Use `.gitkeep` files to track empty folders
- Clean ignored files (`git clean -Xfd`) before switching branches when needed
- Commit frequently with descriptive messages
- Push to GitHub after each commit

---

## Branch Overview

### `main`
Base branch. Contains only a README.md. All experiments branch from here.

### `tmp-proxy` — SOCKS5 Proxy in Rust (current active experiment)
**Goal**: Learn SOCKS5 protocol and Rust by implementing a proxy server from scratch.

**Plan**: Start with SOCKS5 (simplest proxy protocol), then potentially move to Shadowsocks.

**Protocol complexity ranking** (simplest to hardest):
```
HTTP < SOCKS5 < Shadowsocks < VLESS < VMess < Reality
```

**SOCKS5 implementation plan**:
1. TCP listener (accept client connections)
2. Read greeting → send method choice
3. Read connect request → parse address + port
4. Connect to target server
5. Send success response
6. Bidirectional copy: client ↔ target

**Tech stack**:
- Rust 1.94.0 (installed via rustup)
- Will use Tokio for async networking
- Cargo project already initialized

**File structure**:
```
docs/rust/01-installation.md  ← how to install Rust on Ubuntu
docs/rust/02-cargo-basics.md  ← Cargo init, run, dependencies
src/main.rs                   ← entry point (currently Hello World)
Cargo.toml                    ← project manifest
Cargo.lock                    ← dependency lockfile
```

**Status**: Rust installed, Cargo initialized, SOCKS5 protocol explained to user. Ready to start writing the proxy code.

### `chatui-new` — Next.js Chatbot UI (paused)
**Goal**: Build a web chatbot UI using Next.js, OpenAI API, and modern frontend tools.

**Based on commit**: `0ff16c0` from the deleted `chatbot-ui` branch.

**Tech stack**:
- Next.js 16.1.6 with App Router (NOT Pages Router)
- React 19 with React Compiler enabled
- TypeScript
- Tailwind CSS v4
- PostCSS
- ESLint for linting
- Prettier for formatting (will switch to Biome when ecosystem matures)
- react-markdown for rendering markdown responses
- @tailwindcss/typography (`prose` class) for styling rendered markdown
- OpenAI SDK (`gpt-4o-mini` model)
- Decision made: will use **shadcn/ui** as the component library (not yet installed)
  - Chosen because: no lock-in (you own the code), Vercel-backed, aligned with Next.js ecosystem, lowest risk

**File structure**:
```
src/app/page.tsx              ← chat UI page ("use client")
src/app/layout.tsx            ← root layout
src/app/globals.css           ← Tailwind + typography plugin
src/app/api/chat/route.ts     ← API route, calls OpenAI (server-side)
src/components/MessageList.tsx ← renders chat messages with markdown
src/components/ChatInput.tsx   ← input box + send button
src/types/chat.ts             ← shared Message type
```

**Key architecture decisions**:
- API route handles OpenAI calls server-side (keeps API key safe)
- Message history stored in React useState on client
- Full history sent with each request so OpenAI has context
- MessageList uses react-markdown + prose for rendering
- No destructuring in component props (user prefers explicit `props.messages` style for readability)

**Environment setup needed**:
- Run `npm install` to restore node_modules
- Create `.env.local` with `OPENAI_API_KEY=<key>` (ask user for key, never store in git)
- Run `npm run dev` to start dev server

**Package.json scripts**:
- `npm run dev` — start dev server
- `npm run build` — production build
- `npm run lint` — run ESLint
- `npm run format` — run Prettier on src/

### `tmp-chatbot` — Python CLI Chatbot (paused)
**Goal**: Simple CLI chatbot using OpenAI API in Python.

**Tech stack**:
- Python project initialized with `uv`
- Dependencies: `python-dotenv`, `openai`

**File structure**:
```
main.py          ← CLI chatbot with conversation history
pyproject.toml   ← project manifest
uv.lock          ← dependency lockfile
.env.example     ← template for API key
```

**Environment setup needed**:
- Run `uv sync` to restore .venv and install dependencies
- Create `.env` with `OPENAI_API_KEY=<key>` (ask user for key)
- Run `uv run main.py` to start chatbot

---

## Technical Knowledge Established in Conversation

These concepts have been explained and understood by the user. No need to re-explain unless asked:

- **Git**: branching, staging, committing, pushing, .gitignore, .gitkeep, git clean -Xfd, git restore, stash -u vs -a
- **Python/uv**: uv init, uv add, uv sync, uv run, .venv auto-managed
- **Next.js**: App Router vs Pages Router, file-based routing, API routes (route.ts), layout.tsx wraps pages, "use client" for interactivity
- **React**: components, props, state (useState), form handling
- **TypeScript**: type definitions, `import type`, type annotations on function params
- **Tailwind CSS**: utility classes, Preflight (CSS reset), how it generates CSS at build time (no static CSS file), PostCSS pipeline, plugins
- **@tailwindcss/typography**: `prose` class styles HTML tags rendered from markdown
- **CSS modern syntax**: CSS variables (--var, var()), @media prefers-color-scheme, @import, @theme inline, @plugin
- **react-markdown**: converts markdown text to HTML tags, combined with prose for styling
- **PostCSS**: CSS transformer, runs Tailwind and Typography plugins at build time
- **Build pipeline**: TSX → TypeScript (strip types) → Turbopack (bundle JS, generate CSS via PostCSS) → Next.js server (SSR for server components) → browser (HTML + JS + CSS, hydration)
- **Proxy protocols**: SOCKS5 3-phase handshake, protocol comparison (HTTP, SOCKS5, Shadowsocks, VLESS, VMess, Reality)
- **Rust/Cargo**: rustup installation, cargo init/run/build/add, Cargo.toml, Cargo.lock, target/
- **shadcn/ui**: copy-paste approach, built on Radix UI + Tailwind, Vercel-backed, why it was chosen over MUI
- **Prettier vs Biome**: using Prettier now, will switch to Biome when ecosystem matures
- **.mjs files**: ES Module JavaScript, allows import/export syntax without setting "type": "module" in package.json
- **Import alias**: @/ maps to src/, configured in tsconfig.json, build-time transformation not standard JS

---

## Things NOT to do

- Do not write code without explaining what it does first
- Do not write all code at once — step by step, test after each step
- Do not use v0.dev to generate UI
- Do not use libraries that hide Tailwind internals when the user is trying to learn Tailwind
- Do not put API keys in committed files — always use .env.local or .env (gitignored)
- Do not use destructuring in component props unless the user asks for it
- Do not use `git -C` flag — we are already in the working directory
- Do not skip explaining "why" — the user values understanding over speed
