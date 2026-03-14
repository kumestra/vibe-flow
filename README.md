# vibe-flow

A vibe coding playground — each branch is an independent learning experiment. No pressure to finish anything. The journey is the goal.

## Current Branch: `tmp-proxy`

Building a SOCKS5 proxy server in Rust from scratch, starting from the basics up.

**Progression plan:**
1. HTTP server (axum + tokio) ✅
2. HTTP client (reqwest) ✅
3. SOCKS5 proxy server (in progress)
4. End-to-end test: client → proxy → server

## Project Structure

```
src/
├── main.rs              ← proxy server (in progress)
└── bin/
    ├── http_server.rs   ← HTTP server for testing
    └── http_client.rs   ← HTTP client for testing
docs/
├── rust/                ← Rust language notes
└── project/             ← project architecture notes
```

## How to Run

```bash
# HTTP server (keep running in a separate terminal)
cargo run --bin http_server

# HTTP client (test the server)
cargo run --bin http_client

# Proxy server
cargo run
```

## Tech Stack

- Rust (via rustup)
- [axum](https://github.com/tokio-rs/axum) — HTTP server framework
- [tokio](https://tokio.rs) — async runtime
- [reqwest](https://github.com/seanmonstar/reqwest) — HTTP client

## All Branches

| Branch | Description | Status |
|--------|-------------|--------|
| `main` | Base branch, contains only this README | — |
| `tmp-proxy` | SOCKS5 proxy server in Rust | Active |
| `chatui-new` | Next.js chatbot UI with OpenAI | Paused |
| `tmp-chatbot` | Python CLI chatbot with OpenAI | Paused |
| `tmp-rust-learning` | Rust learning experiments | Paused |
