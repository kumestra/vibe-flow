"""Tool router — routes tool calls to the right provider.

The chat loop only calls:
  router.get_openai_tools()  → list of tools for OpenAI API
  router.call(name, args)    → execute a tool, returns string
"""

import json
import logging

import requests

logger = logging.getLogger(__name__)

MCP_URL = "http://localhost:8000"


class ToolRouter:
    """Route tool calls to MCP servers or local functions."""

    def __init__(self) -> None:
        """Initialize with empty tool registry."""
        self._tools: dict[str, dict] = {}
        self._mcp_tools: set[str] = set()
        self._mcp_urls: list[str] = []

    def add_local(
        self,
        name: str,
        description: str,
        parameters: dict,
        func: callable,
    ) -> None:
        """Register a local function as a tool."""
        self._tools[name] = {
            "description": description,
            "parameters": parameters,
            "func": func,
        }

    def connect_mcp(self, url: str) -> None:
        """Connect to an MCP server and discover its tools."""
        # Phase 1: Initialize
        self._mcp_send(
            url,
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "clientInfo": {"name": "tool-router", "version": "0.1.0"},
                "capabilities": {},
            },
            req_id=1,
        )
        self._mcp_send(url, "notifications/initialized", req_id=2)
        self._mcp_urls.append(url)

        # Phase 2: Discover tools
        self._refresh_mcp(url)

    def refresh_all_mcp(self) -> None:
        """Re-fetch tool lists from all connected MCP servers."""
        # Clear old MCP tools, keep local tools
        for name in list(self._mcp_tools):
            del self._tools[name]
        self._mcp_tools.clear()

        for url in self._mcp_urls:
            self._refresh_mcp(url)

    def _refresh_mcp(self, url: str) -> None:
        """Fetch tool list from a single MCP server."""
        resp = self._mcp_send(url, "tools/list", req_id=3)
        for t in resp["result"]["tools"]:
            name = t["name"]
            self._tools[name] = {
                "description": t["description"],
                "parameters": t["inputSchema"],
                "mcp_url": url,
            }
            self._mcp_tools.add(name)
            logger.info("[mcp] Registered tool: %s", name)

    def get_openai_tools(self) -> list[dict]:
        """Return all tools in OpenAI function calling format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": info["description"],
                    "parameters": info["parameters"],
                },
            }
            for name, info in self._tools.items()
        ]

    def call(self, name: str, arguments: dict) -> str:
        """Call a tool by name. Returns result string or error."""
        if name not in self._tools:
            return f"Error: unknown tool '{name}'"

        tool = self._tools[name]

        try:
            if name in self._mcp_tools:
                return self._call_mcp(tool["mcp_url"], name, arguments)
            return str(tool["func"](**arguments))
        except Exception as e:
            logger.exception("Tool '%s' failed", name)
            return f"Error: {e}"

    def _call_mcp(self, url: str, name: str, arguments: dict) -> str:
        """Phase 3: Call a tool on an MCP server."""
        resp = self._mcp_send(
            url,
            "tools/call",
            {
                "name": name,
                "arguments": arguments,
            },
            req_id=4,
        )

        if "error" in resp:
            return f"Error: {resp['error']['message']}"

        return resp["result"]["content"][0]["text"]

    def _mcp_send(
        self,
        url: str,
        method: str,
        params: dict | None = None,
        req_id: int = 1,
    ) -> dict:
        """Send a JSON-RPC request to an MCP server."""
        payload: dict = {"jsonrpc": "2.0", "method": method, "id": req_id}
        if params:
            payload["params"] = params
        logger.debug("[mcp] >>> %s", json.dumps(payload))
        resp = requests.post(url, json=payload, timeout=5)
        data = resp.json()
        logger.debug("[mcp] <<< %s", json.dumps(data))
        return data
