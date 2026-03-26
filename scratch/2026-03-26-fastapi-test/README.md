# JSON-RPC 2.0 Server (FastAPI)

A minimal JSON-RPC 2.0 server built with FastAPI to understand the protocol.

## References

- JSON-RPC 2.0 spec: https://www.jsonrpc.org/specification
- MCP (Model Context Protocol): https://modelcontextprotocol.io

## Run

```bash
uv run uvicorn scratch.2026-03-26-fastapi-test.main:app --reload
```

API docs: http://localhost:8000/docs

## Methods

| Method | Params | Description |
|--------|--------|-------------|
| `add` | `a`, `b` | Add two numbers |
| `greet` | `name` | Return a greeting |
| `divide` | `a`, `b` | Divide a by b |

## Test

```bash
# Single call
curl -s localhost:8000 -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"add","params":[3,5],"id":1}'

# Named params
curl -s localhost:8000 -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"greet","params":{"name":"World"},"id":2}'

# Error
curl -s localhost:8000 -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"divide","params":[1,0],"id":3}'

# Batch
curl -s localhost:8000/batch -H "Content-Type: application/json" \
  -d '[{"jsonrpc":"2.0","method":"add","params":[1,2],"id":1},{"jsonrpc":"2.0","method":"greet","params":{"name":"Batch"},"id":2}]'
```
