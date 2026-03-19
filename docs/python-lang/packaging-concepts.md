# Python: Packaging Concepts

## Module

A single `.py` file.

```
math_utils.py  ← a module
```

```python
import math_utils
```

## Package

A folder of modules with `__init__.py` inside.

```
myapp/
  __init__.py
  utils.py
  models.py
```

```python
from myapp import utils
```

> **module = file, package = folder**

Packages can be nested (subpackages) — each folder needs its own `__init__.py` (Python 3.3+ also supports [namespace packages](https://docs.python.org/3/glossary.html#term-namespace-package) without `__init__.py`, but regular packages are the norm):

```
myapp/
  __init__.py
  auth/
    __init__.py
    login.py
  db/
    __init__.py
    models.py
```

```python
from myapp.auth import login
from myapp.db.models import User
```

In practice, rarely go more than 2-3 levels deep.

## How Python Resolves Imports

When you write `import something`, Python follows this order:

**1. `sys.modules` cache** — if already imported, return the cached version immediately.

**2. Finders in `sys.meta_path`** — Python asks each finder in order:

1. `BuiltinImporter` — built-in C modules (`sys`, `os`)
2. `FrozenImporter` — frozen modules (rarely relevant)
3. `PathFinder` — searches the filesystem via `sys.path`

**3. `sys.path` search** — the `PathFinder` walks these entries in order:

| Source | What it adds |
|---|---|
| Script location | Directory of the file being run (or `""` for CWD in REPL) |
| `PYTHONPATH` env var | Directories you set manually |
| Standard library | Built-in stdlib paths |
| `site-packages` | Where `pip install` puts things |

At each entry, Python looks for `<name>.py` (module) or `<name>/` with `__init__.py` (package).

**4. Not found** → `ModuleNotFoundError`

> **Gotcha:** A file named `random.py` in your project shadows the stdlib `random` module, because the current directory comes first in `sys.path`.

## App vs Library

**App** — has an entry point, meant to be run directly:

```python
if __name__ == "__main__":
    main()
```

`__name__` equals `"__main__"` only when the file is executed directly, not when imported. Modern projects use entry points instead of a standalone `main.py` (see [Modern Project Structure](#modern-project-structure)).

**Library** — no entry point, meant to be imported by other code:

```python
import requests  # used, not run
```

## Modern Project Structure

The modern standard uses `pyproject.toml` + `src/` layout + entry points.

```
myproject/
  pyproject.toml            ← single config file
  .gitignore
  src/
    myapp/                  ← package inside src/
      __init__.py
      __main__.py           ← enables: python -m myapp
      cli.py
      core.py
  tests/
    __init__.py
```

### `pyproject.toml`

The standard config file for Python projects, defined by PEPs 518/621. Not part of the language itself, but an official packaging standard governed by PyPA (Python Packaging Authority). Replaces the old `setup.py` + `requirements.txt` approach.

```toml
[build-system]                    # ← frontend (pip/uv) reads this
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]                         # ← build backend reads this
name = "myapp"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = []

[project.scripts]                 # ← creates CLI command after install
myapp = "myapp.cli:main"

[tool.ruff]                       # ← individual tools read their own section
line-length = 88
```

### Why `src/` layout?

Without it, Python can accidentally import the local folder instead of the installed package. The `src/` folder forces you to install the package first, catching import issues early.

### Entry points and `__main__.py`

Instead of a standalone `main.py`, modern projects declare entry points in `pyproject.toml` via `[project.scripts]`. After installation, you get a real command:

```bash
myapp serve                        # via entry point
python -m myapp serve              # via __main__.py
```

## Package Installers

### pip

Python's built-in package installer (bundled since Python 3.4). Downloads packages from PyPI and installs them into `site-packages/`.

```bash
pip install requests      # install from PyPI
pip uninstall requests    # remove
pip list                  # show installed
pip freeze                # show installed with exact versions
```

pip is an installer, not a full project manager — no lock files, no venv management.

### uv

A Rust rewrite of pip (by Astral, same team behind `ruff`). Not a wrapper — it reimplements package resolution, downloading, and installation from scratch. 10-100x faster than pip.

```bash
uv pip install requests   # drop-in pip replacement
uv venv                   # replaces python -m venv
uv lock                   # replaces pip-tools
uv python install 3.12    # replaces pyenv
```

### poetry

A higher-level workflow tool written in Python. Doesn't rewrite pip — it orchestrates on top of it. Adds lock files, venv management, building, and publishing.

```bash
poetry add requests       # install + update lock file
poetry install            # install from lock file
poetry build              # build .whl
poetry publish            # upload to PyPI
```

### Comparison

| Capability | pip | uv | poetry |
|---|---|---|---|
| Install packages | yes | yes (Rust) | yes (via pip) |
| Dependency resolution | yes | yes (Rust, faster) | yes (own solver) |
| Lock files | no | yes | yes |
| Venv management | no | yes | yes |
| Build packages | no | yes | yes |
| Written in | Python | Rust | Python |

### Package sources

All three download from [PyPI](https://pypi.org) by default (500k+ packages), but can install from other sources:

| Source | Example |
|---|---|
| **PyPI** | `pip install requests` |
| **Private index** | `pip install --index-url https://corp.jfrog.io/pypi mylib` |
| **Git repo** | `pip install git+https://github.com/user/repo.git` |
| **Local file** | `pip install ./mypackage.whl` |

Companies run private indexes (JFrog Artifactory, AWS CodeArtifact) for internal packages — same protocol as PyPI.

## Building and Distribution

### What "build" means

In compiled languages (C, Go, Rust), build means compiling to a binary. Python is interpreted, so **build means packaging source code + metadata into an installable artifact**:

1. Read `pyproject.toml` for metadata (name, version, dependencies, entry points)
2. Collect the right `.py` files
3. Generate metadata files
4. Zip it all into a `.whl` (a wheel is literally a renamed `.zip`)

No compilation — just packaging. For projects with C extensions (like `numpy`), the build also compiles C code into binaries.

```bash
pip install build        # the build tool
python -m build          # produces .whl + .tar.gz in dist/
```

### Frontends vs build backends (PEP 517)

Building has two independent, pluggable parts:

```
frontends (installers)              build backends
┌─────────────────────┐             ┌─────────────────────┐
│ pip install .       │             │ hatchling           │
│ uv build            │──calls──►   │ setuptools          │──► .whl
│ python -m build     │             │ poetry-core         │
└─────────────────────┘             │ flit-core           │
                                    └─────────────────────┘
```

The **frontend** reads `[build-system]` to know which backend to call. The **backend** reads `[project]` and packages the code. Any frontend works with any backend.

| Backend | Notes |
|---|---|
| **hatchling** | Modern, minimal, fast (recommended for new projects) |
| **setuptools** | Legacy default, the oldest |
| **poetry-core** | Used when you use Poetry |
| **flit-core** | Ultra-minimal, pure Python only |
| **maturin** | For Python packages with Rust extensions |

### Wheel vs source distribution

A **wheel** (`.whl`) is a pre-built, ready-to-install artifact. A **source distribution** (`.tar.gz`) contains raw source code that may need a build step.

```bash
pip install requests
# pip prefers the .whl (fast, no build needed)
# falls back to .tar.gz if no compatible wheel exists
```

Wheels are faster because they skip the build step — just unpack and go. Packages with C extensions especially benefit, since the wheel ships pre-compiled binaries.

```
requests-2.31.0-py3-none-any.whl
│         │      │   │    │
│         │      │   │    └─ platform (any = pure Python)
│         │      │   └─ ABI tag
│         │      └─ Python version
│         └─ package version
└─ package name
```

## Development Workflow

### Virtual environment (always use one)

```bash
python3 -m venv .venv         # create
source .venv/bin/activate     # activate (Linux/macOS)
pip install -e ".[dev]"       # install project + dev tools
deactivate                    # exit when done
```

Without a venv, `pip install` modifies your system-wide Python — packages leak across projects and are harder to clean up.

### `python file.py` vs `pip install -e .`

**`python file.py`** — runs the file directly. Imports resolved via `sys.path` (current directory). No install needed.

**`pip install -e .`** — editable install. Creates a link from `site-packages` to your source directory. Code stays where it is, changes take effect immediately. You need this when:
- Using `src/` layout (`src/` isn't in `sys.path` by default)
- You want CLI entry points from `[project.scripts]`

### For libraries (published to PyPI)

```
edit → run → test → git push → CI builds .whl → upload to PyPI
```

### For apps (not published — web apps, internal tools)

No build step. Just ship source code:

```bash
# Development
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
# edit → run → test (daily loop)

# Deployment
git clone <repo>
python3 -m venv .venv && source .venv/bin/activate
pip install .
```

Lock exact dependency versions for reproducible deploys:

```bash
pip freeze > requirements.lock
# on server:
pip install -r requirements.lock
```

### Common deployment methods

| Method | How it works |
|---|---|
| **Docker** | Copy source into container, `pip install`, run |
| **Systemd** | Clone on server, venv, run as a service |
| **PaaS** (Heroku, Railway) | Push code, platform handles install + run |

## Summary

| Concept | What it is |
|---|---|
| Module | A single `.py` file |
| Package | A folder of modules with `__init__.py` |
| Wheel | A pre-built `.whl` for fast installation |
| Source dist | A `.tar.gz` that may need building |
| App | Has an entry point, run directly |
| Library | No entry point, imported by other code |
| `pyproject.toml` | Standard project config (replaces setup.py) |
| `src/` layout | Prevents accidental local imports |
| Build | Packaging source into `.whl`/`.tar.gz` — not compilation |
| Build backend | hatchling/setuptools/poetry-core — reads `[project]`, produces `.whl` |
| pip | Python's built-in package installer |
| uv | Rust rewrite of pip — 10-100x faster |
| poetry | Workflow tool — installer + lock files + venv + build |
| PyPI | Default package registry (like npm for JS) |
| `pip install -e .` | Editable install — live link to source, no rebuild needed |
| venv | Isolates dependencies per project |
