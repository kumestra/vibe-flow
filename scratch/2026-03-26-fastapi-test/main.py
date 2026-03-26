"""JSON-RPC 2.0 server built with FastAPI."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# --- Method registry ---

METHODS: dict[str, Any] = {}


def method(func: Callable) -> Callable:
    """Register a function as a JSON-RPC method."""
    METHODS[func.__name__] = func
    return func


# --- Methods ---


@method
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@method
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"


@method
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        msg = "Division by zero"
        raise ValueError(msg)
    return a / b


# --- JSON-RPC models ---


class JsonRpcRequest(BaseModel):
    """JSON-RPC 2.0 request."""

    jsonrpc: str = "2.0"
    method: str
    params: list | dict = []
    id: int | str | None = None


class JsonRpcError(BaseModel):
    """JSON-RPC 2.0 error object."""

    code: int
    message: str


class JsonRpcResponse(BaseModel):
    """JSON-RPC 2.0 response."""

    jsonrpc: str = "2.0"
    result: Any = None
    error: JsonRpcError | None = None
    id: int | str | None = None


# --- Handler ---


def handle_request(req: JsonRpcRequest) -> JsonRpcResponse | None:
    """Process a single JSON-RPC request."""
    if req.method not in METHODS:
        return JsonRpcResponse(
            error=JsonRpcError(code=-32601, message=f"Method not found: {req.method}"),
            id=req.id,
        )

    try:
        if isinstance(req.params, list):
            result = METHODS[req.method](*req.params)
        else:
            result = METHODS[req.method](**req.params)
    except TypeError as e:
        return JsonRpcResponse(
            error=JsonRpcError(code=-32602, message=str(e)),
            id=req.id,
        )
    except Exception as e:  # noqa: BLE001
        return JsonRpcResponse(
            error=JsonRpcError(code=-32000, message=str(e)),
            id=req.id,
        )

    # Notification — no response
    if req.id is None:
        return None

    return JsonRpcResponse(result=result, id=req.id)


# --- Routes ---


@app.post("/")
def rpc(request: JsonRpcRequest) -> JsonRpcResponse | None:
    """Handle a single JSON-RPC request."""
    return handle_request(request)


@app.post("/batch")
def rpc_batch(requests: list[JsonRpcRequest]) -> list[JsonRpcResponse]:
    """Handle a batch of JSON-RPC requests."""
    return [r for req in requests if (r := handle_request(req)) is not None]
