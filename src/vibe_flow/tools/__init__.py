from typing import Any

from vibe_flow.tool_base import Tool
from vibe_flow.tools.bash import tool as bash_tool
from vibe_flow.tools.get_current_time import tool as get_current_time_tool
from vibe_flow.tools.read_file import tool as read_file_tool
from vibe_flow.tools.write_file import tool as write_file_tool

ALL_TOOLS: list[Tool] = [
    bash_tool,
    get_current_time_tool,
    read_file_tool,
    write_file_tool,
]
TOOLS_BY_NAME: dict[str, Tool] = {t.name: t for t in ALL_TOOLS}


def register_mcp_tools(tools: list[Tool]) -> None:
    """Add MCP tools to the registry at runtime."""
    for tool in tools:
        ALL_TOOLS.append(tool)
        TOOLS_BY_NAME[tool.name] = tool


def get_schemas() -> list[dict[str, Any]]:
    """Return OpenAI function-calling schemas for all tools."""
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.input_schema,
            },
        }
        for t in ALL_TOOLS
    ]
