# Project Structure

## Overview

This project is a SOCKS5 proxy server written in Rust, with an HTTP server and HTTP client for testing.

Before writing the proxy, we first build:
1. A simple **HTTP server** — listens and responds to requests
2. A simple **HTTP client** — sends requests to the server

This serves two purposes:
- Learn Rust networking basics (TCP, async) in a simple context first
- Get working test tools — once the proxy is ready, route client → proxy → server to verify it works

---

## Package, Crate, Module

**Package** = the whole project (this git repo). Has one `Cargo.toml`.

**Crate** = a compilation unit that produces one binary or one library. There are two kinds:
- Binary crate — has `main()`, compiles into an executable
- Library crate — no `main()`, shared code used by other crates

**Module** = how you organize code inside a crate. One `.rs` file = one module.

```
Package (Cargo.toml)
└── Crate (src/main.rs, src/bin/*.rs)
    └── Modules (other .rs files)
        └── Functions, structs, types...
```

---

## Folder Structure

```
src/
├── main.rs              ← proxy server (main binary)
└── bin/
    ├── http_server.rs   ← HTTP server binary (for testing)
    └── http_client.rs   ← HTTP client binary (for testing)
```

Cargo automatically discovers `src/bin/*.rs` as binary crates — no extra config needed in `Cargo.toml`.

As each binary grows, it can be expanded into a folder:

```
src/
├── main.rs
└── bin/
    ├── http_server/
    │   ├── main.rs      ← entry point (required)
    │   └── handler.rs   ← module: request handling logic
    └── http_client/
        ├── main.rs      ← entry point (required)
        └── request.rs   ← module: build and send requests
```

Start with single files. Upgrade to folders when files get large enough to need splitting.

---

## Compile and Run

```bash
# run a specific binary
cargo run --bin http_server
cargo run --bin http_client
cargo run                      # runs src/main.rs (the proxy)

# build only (no run)
cargo build --bin http_server
cargo build --bin http_client
cargo build                    # builds all binaries at once
```

Compiled binaries are placed in:

```
target/debug/
├── vibe-flow       ← from src/main.rs
├── http_server     ← from src/bin/http_server.rs (or src/bin/http_server/main.rs)
└── http_client     ← from src/bin/http_client.rs (or src/bin/http_client/main.rs)
```

You can also run them directly after building:

```bash
./target/debug/http_server
./target/debug/http_client
```

Binary name = filename (or folder name) under `src/bin/`. The folder vs single-file choice does not affect the binary name or how you run it.

---

## Tech Stack

- **Rust** (via rustup)
- **Tokio** — async runtime for networking (will be added as a dependency)
- **Cargo** — build tool and package manager

---

## Development Plan

1. HTTP server — TCP listener, parse HTTP request, send response
2. HTTP client — connect, send GET request, print response
3. SOCKS5 proxy — sit between client and server, forward traffic
4. Test end-to-end — client → proxy → server
