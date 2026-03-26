"""CLI chatbot that uses ChatGPT + MCP server for tools.

Flow:
  User → ChatGPT → tool call → MCP client → MCP server → result → ChatGPT → User

The MCP client (this file) connects to the MCP server over HTTP.
On startup it discovers available tools, then forwards tool calls from ChatGPT.
"""

import json
import os

import requests
from dotenv import load_dotenv

from vibe_flow.logger import logger

load_dotenv()

# --- ChatGPT config ---

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    msg = "OPENAI_API_KEY not found in .env"
    raise RuntimeError(msg)

CHAT_URL = "https://api.openai.com/v1/chat/completions"
CHAT_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}",
}
MODEL = "gpt-4o-mini"

# --- MCP client (no SDK) ---

MCP_URL = "http://localhost:8000"


def mcp_send(method: str, params: dict | None = None, req_id: int = 1) -> dict:
    """Send a JSON-RPC request to the MCP server."""
    payload: dict = {"jsonrpc": "2.0", "method": method, "id": req_id}
    if params:
        payload["params"] = params
    logger.debug(f"[mcp] >>> {json.dumps(payload)}")
    resp = requests.post(MCP_URL, json=payload, timeout=5)
    data = resp.json()
    logger.debug(f"[mcp] <<< {json.dumps(data, indent=2)}")
    return data


def mcp_initialize() -> dict:
    """Phase 1: Initialize handshake with MCP server."""
    resp = mcp_send(
        "initialize",
        {
            "protocolVersion": "2024-11-05",
            "clientInfo": {"name": "chatbot-mcp-client", "version": "0.1.0"},
            "capabilities": {},
        },
        req_id=1,
    )
    mcp_send("notifications/initialized", req_id=2)
    server_info = resp["result"]["serverInfo"]
    print(f"  [mcp] Connected to: {server_info['name']} v{server_info['version']}")
    return resp


def mcp_discover_tools() -> list[dict]:
    """Phase 2: Discover tools from MCP server."""
    resp = mcp_send("tools/list", req_id=3)
    return resp["result"]["tools"]


def mcp_call_tool(name: str, arguments: dict) -> str:
    """Phase 3: Call a tool on the MCP server, return the text result."""
    resp = mcp_send("tools/call", {"name": name, "arguments": arguments}, req_id=4)
    content = resp["result"]["content"]
    return content[0]["text"]


def mcp_tools_to_openai(mcp_tools: list[dict]) -> list[dict]:
    """Convert MCP tool definitions to OpenAI function calling format."""
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["inputSchema"],
            },
        }
        for t in mcp_tools
    ]


# --- ChatGPT ---


def chat(messages: list[dict], tools: list[dict]) -> dict:
    """Send messages to ChatGPT and return the response JSON."""
    body = {"model": MODEL, "messages": messages, "tools": tools}
    resp = requests.post(CHAT_URL, headers=CHAT_HEADERS, json=body, timeout=30)
    logger.debug(f"[chat] {resp.status_code} {json.dumps(resp.json(), indent=2)}")
    resp.raise_for_status()
    return resp.json()


# --- Main loop ---


def main() -> None:
    """Connect to MCP server, discover tools, then chat."""
    # Phase 1 & 2: Connect to MCP server and discover tools
    print("Connecting to MCP server...")
    mcp_initialize()
    mcp_tools = mcp_discover_tools()
    for t in mcp_tools:
        print(f"  [mcp] Tool: {t['name']} — {t['description']}")

    # Convert MCP tools to OpenAI format
    openai_tools = mcp_tools_to_openai(mcp_tools)

    print(f"\nChatbot ready (model: {MODEL}). Type 'quit' to exit.\n")

    messages = [{"role": "system", "content": "You are a helpful assistant."}]

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "quit":
            break

        messages.append({"role": "user", "content": user_input})
        data = chat(messages, openai_tools)
        assistant_msg = data["choices"][0]["message"]

        # Handle tool calls — forward to MCP server
        while assistant_msg.get("tool_calls"):
            messages.append(assistant_msg)
            for tool_call in assistant_msg["tool_calls"]:
                name = tool_call["function"]["name"]
                args = json.loads(tool_call["function"]["arguments"])
                print(f"  [tool] {name}({args})")

                # Phase 3: Call tool via MCP
                result = mcp_call_tool(name, args)
                print(f"  [tool] → {result}")

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": name,
                        "content": result,
                    },
                )

            data = chat(messages, openai_tools)
            assistant_msg = data["choices"][0]["message"]

        reply = assistant_msg["content"]
        messages.append({"role": "assistant", "content": reply})
        print(f"Bot: {reply}\n")


if __name__ == "__main__":
    main()
