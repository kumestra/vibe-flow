# Installing Rust on Ubuntu Minimal Server

## The Standard Way — rustup

The official and modern standard way to install Rust is via **rustup** — the Rust toolchain installer.

**Do NOT use `apt install rustc`** — the Ubuntu apt package is often outdated by several versions and lacks proper toolchain management.

---

## What is rustup?

rustup is to Rust what `nvm` is to Node.js or `pyenv` is to Python. It:
- Installs Rust and Cargo
- Manages multiple Rust versions (stable, beta, nightly)
- Lets you switch between versions
- Keeps Rust up to date with `rustup update`

---

## Installation Steps

### 1. Install dependencies (minimal Ubuntu server)

```bash
sudo apt update
sudo apt install -y curl build-essential
```

- `curl` — to download the rustup installer
- `build-essential` — C compiler and linker, required by Rust to link binaries

### 2. Download and run the rustup installer

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

Breaking down the flags:
- `--proto '=https'` — only allow HTTPS connections (security)
- `--tlsv1.2` — require TLS 1.2 minimum (security)
- `-sSf` — silent mode, show errors, fail on error

### 3. Follow the prompts

You will see:
```
1) Proceed with standard installation (default)
2) Customize installation
3) Cancel installation
```

Choose **option 1** for standard installation. This installs:
- `rustc` — the Rust compiler
- `cargo` — the Rust package manager and build tool
- `rustfmt` — code formatter
- `clippy` — linter
- The stable toolchain

### 4. Reload your shell environment

```bash
source ~/.cargo/env
```

This adds `~/.cargo/bin` to your PATH so you can run `rustc`, `cargo`, etc. This only needs to be done once for the current terminal session — future sessions load it automatically via `~/.bashrc` or `~/.profile`.

### 5. Verify installation

```bash
rustc --version
cargo --version
```

Expected output:
```
rustc 1.xx.x (xxxxxxxxx 20xx-xx-xx)
cargo 1.xx.x (xxxxxxxxx 20xx-xx-xx)
```

---

## What Gets Installed Where

```
~/.rustup/     ← rustup itself and toolchains
~/.cargo/
├── bin/       ← rustc, cargo, rustfmt, clippy, etc.
├── registry/  ← downloaded crate (package) cache
└── env        ← environment variables script
```

---

## Common Commands

```bash
# update rust to latest stable
rustup update

# check installed toolchains
rustup toolchain list

# install nightly toolchain (for experimental features)
rustup toolchain install nightly

# show active toolchain
rustup show
```

---

## rustup vs apt comparison

| | `apt install rustc` | `rustup` |
|---|---|---|
| Version | Outdated (Ubuntu ships old versions) | Always latest stable |
| Cargo included | Sometimes not | Always |
| Toolchain management | No | Yes |
| Updates | `apt upgrade` | `rustup update` |
| Multiple versions | No | Yes |
| Recommended by Rust team | No | Yes |

---

## Why build-essential is needed

Rust compiles to native machine code. The final linking step requires a C linker (`cc`/`gcc`) which comes from `build-essential`. Without it you get an error like:

```
error: linker `cc` not found
```
