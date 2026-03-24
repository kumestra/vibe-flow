# Scratch

Experimental code for learning, testing, and verification.

## Structure

Each experiment lives in its own dated folder:

```
scratch/
├── 2026-03-24-openai-streaming/
│   ├── main.py
│   └── helper.py
├── 2026-03-25-rag-chunk-test/
│   └── main.py
```

## How to run

```bash
uv run python scratch/<experiment>/main.py
```

This gives you:
- Project code via `from vibe_flow import ...`
- All third-party deps (openai, pydantic, etc.)
- Local file imports within the same experiment folder
