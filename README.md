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

## Running

```bash
# Using uv
uv run vibe-flow

# Or install in editable mode and run directly
pip install -e .
vibe-flow

# Or run as a module
python -m vibe_flow
```