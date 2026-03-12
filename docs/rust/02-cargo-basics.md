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

## cargo init vs uv init (Python comparison)

| | Rust (Cargo) | Python (uv) |
|---|---|---|
| Init current folder | `cargo init` | `uv init` |
| Run code | `cargo run` | `uv run main.py` |
| Add dependency | `cargo add tokio` | `uv add requests` |
| Manifest file | `Cargo.toml` | `pyproject.toml` |
| Lock file | `Cargo.lock` | `uv.lock` |
| Build output | `target/` | `.venv/` |
