# Cargo Basics — Init and Run a Rust Project

## What is Cargo?

Cargo is Rust's official build tool and package manager. It handles:
- Creating new projects
- Building code
- Running code
- Managing dependencies (called **crates**)
- Running tests

Think of it like `npm` for Node.js or `uv` for Python.

---

## Initialize Current Folder as a Rust Project

```bash
cargo init
```

This creates the following files in the current directory:

```
.
├── Cargo.toml    ← project manifest (like package.json)
└── src/
    └── main.rs   ← entry point
```

### What if you want a new folder instead?

```bash
cargo new my-project
```

This creates a new folder `my-project/` with the same structure. Use `cargo init` for existing folders, `cargo new` for new folders.

---

## Cargo.toml — The Project Manifest

```toml
[package]
name = "vibe-flow"
version = "0.1.0"
edition = "2021"

[dependencies]
```

- `name` — project name
- `version` — current version
- `edition` — Rust edition (2021 is the modern standard)
- `[dependencies]` — external crates go here (like npm dependencies)

---

## src/main.rs — The Entry Point

```rust
fn main() {
    println!("Hello, world!");
}
```

Every Rust binary starts from the `main()` function in `src/main.rs`.

---

## Running the Project

```bash
cargo run
```

This does two things:
1. Compiles the code
2. Runs the resulting binary

On first run it will download and compile dependencies (if any). Subsequent runs are faster due to caching.

Expected output:
```
   Compiling vibe-flow v0.1.0
    Finished dev [unoptimized + debuginfo] target(s) in 0.50s
     Running `target/debug/vibe-flow`
Hello, world!
```

---

## Other Common Cargo Commands

```bash
# only compile, don't run
cargo build

# compile in release mode (optimized, slower to compile but faster binary)
cargo build --release

# check for errors without producing a binary (faster than build)
cargo check

# run tests
cargo test

# add a dependency
cargo add tokio
```

---

## Adding Dependencies

Edit `Cargo.toml` manually:
```toml
[dependencies]
tokio = { version = "1", features = ["full"] }
```

Or use the `cargo add` command:
```bash
cargo add tokio --features full
```

Next time you run `cargo build` or `cargo run`, Cargo automatically downloads and compiles the new dependency.

---

## What Gets Generated

```
.
├── Cargo.toml        ← project manifest
├── Cargo.lock        ← exact dependency versions (like package-lock.json)
├── src/
│   └── main.rs       ← your code
└── target/           ← build output (gitignored)
    └── debug/
        └── vibe-flow ← compiled binary
```

### Cargo.lock
Like `package-lock.json` in npm — records exact versions of all dependencies. Should be committed to git for binary projects so builds are reproducible.

### target/
Build output folder — can be very large (GBs for big projects). Always gitignored.

---

## Two Types of Crates

There are two types of crates in the Rust ecosystem:

```
lib crate    → code library, cannot run alone, used by your code
binary crate → executable tool, can run directly
```

**Two ways to install:**

```bash
cargo install ripgrep    # installs binary tool globally to ~/.cargo/bin/
cargo add serde          # adds lib crate as dependency to current project
```

- `cargo install` — for tools you want to run (circom, ripgrep, cargo-watch)
- `cargo add` — for libraries your code uses (serde, tokio, axum)

In both cases, cargo always fetches **source code** and compiles it locally. This is different from most package managers:

| Package Manager | What it fetches |
|---|---|
| **cargo** (Rust) | Source code → compiles locally |
| **npm** (JavaScript) | Pre-built JavaScript files |
| **pip** (Python) | Pre-built wheels (or source) |
| **apt** (Ubuntu) | Pre-built binaries |

**Why Rust always compiles locally:**

- Rust does heavy compile-time optimizations that require knowing your specific target architecture
- Generic types in libraries must be compiled for your specific types — this can't be done ahead of time
- The compiler needs to see all source code to guarantee memory safety

---

## cargo init vs uv init (Python comparison)

| | Rust (Cargo) | Python (uv) |
|---|---|---|
| Init current folder | `cargo init` | `uv init` |
| Run code | `cargo run` | `uv run main.py` |
| Add dependency | `cargo add tokio` | `uv add requests` |
| Manifest file | `Cargo.toml` | `pyproject.toml` |
| Lock file | `Cargo.lock` | `uv.lock` |
| Build output | `target/` | `.venv/` |
