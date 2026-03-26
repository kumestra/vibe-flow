"""Minimal MCP server over HTTP — no SDK, just FastAPI + JSON-RPC.

Same protocol as stdio version, but easier to test with curl.
"""

import random
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# --- Fake price tools ---


def get_gold_price(date: str) -> str:
    """Return a random gold price for a given date."""
    seed = hash(("gold", date))
    rng = random.Random(seed)  # noqa: S311
    price = round(rng.uniform(1800, 2400), 2)
    return f"Gold on {date}: ${price}/oz"


def get_bitcoin_price(date: str) -> str:
    """Return a random bitcoin price for a given date."""
    seed = hash(("bitcoin", date))
    rng = random.Random(seed)  # noqa: S311
    price = round(rng.uniform(50000, 100000), 2)
    return f"Bitcoin on {date}: ${price}"


DATE_PARAM = {
    "type": "string",
    "description": "Date in YYYY-MM-DD format, e.g. 2026-03-26",
}

# Tool definitions and dispatch
TOOLS = {
    "get_gold_price": {
        "func": get_gold_price,
        "definition": {
            "name": "get_gold_price",
            "description": "Get gold price per ounce in USD for a given date",
            "inputSchema": {
                "type": "object",
                "properties": {"date": DATE_PARAM},
                "required": ["date"],
            },
        },
    },
    "get_bitcoin_price": {
        "func": get_bitcoin_price,
        "definition": {
            "name": "get_bitcoin_price",
            "description": "Get bitcoin price in USD for a given date",
            "inputSchema": {
                "type": "object",
                "properties": {"date": DATE_PARAM},
                "required": ["date"],
            },
        },
    },
}


# --- MCP handlers ---


def handle_initialize(req_id: int | str) -> dict[str, Any]:
    """Respond with server info and capabilities."""
    return {
        "jsonrpc": "2.0",
        "result": {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "price-server", "version": "0.1.0"},
            "capabilities": {"tools": {}},
        },
        "id": req_id,
    }


def handle_tools_list(req_id: int | str) -> dict[str, Any]:
    """Return all available tools."""
    return {
        "jsonrpc": "2.0",
        "result": {"tools": [t["definition"] for t in TOOLS.values()]},
        "id": req_id,
    }


def handle_tools_call(req_id: int | str, params: dict[str, Any]) -> dict[str, Any]:
    """Execute a tool and return the result."""
    name = params.get("name", "")
    arguments = params.get("arguments", {})

    if name not in TOOLS:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": f"Tool not found: {name}"},
            "id": req_id,
        }

    result = TOOLS[name]["func"](**arguments)
    return {
        "jsonrpc": "2.0",
        "result": {"content": [{"type": "text", "text": result}]},
        "id": req_id,
    }


# --- Single endpoint for all JSON-RPC messages ---


@app.post("/")
async def rpc(request: Request) -> JSONResponse:
    """Handle all MCP JSON-RPC requests."""
    body = await request.json()
    method = body.get("method", "")
    req_id = body.get("id")
    params = body.get("params", {})

    # Notifications — no response
    if method in ("notifications/initialized", "notifications/cancelled"):
        return JSONResponse(content={})

    # Dispatch
    if method == "initialize":
        return JSONResponse(content=handle_initialize(req_id))
    if method == "tools/list":
        return JSONResponse(content=handle_tools_list(req_id))
    if method == "tools/call":
        return JSONResponse(content=handle_tools_call(req_id, params))

    return JSONResponse(
        content={
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": f"Method not found: {method}"},
            "id": req_id,
        },
    )
