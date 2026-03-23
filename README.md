# vibe-flow

## Project Structure

```
vibe-flow/
  pyproject.toml
  src/
    vibe_flow/
      __init__.py
      __main__.py           # python -m vibe_flow
      cli.py                # entry point
  tests/
    __init__.py
```

## Setup

After cloning the repo, run:

```bash
uv sync
```

`uv sync` installs all dependencies (including dev tools).

## Running

```bash
uv run vibe-flow
```

Alternative methods:

```bash
# Traditional: install in editable mode, then run
pip install -e .
vibe-flow

# Debug/development: run as module
python -m vibe_flow
```