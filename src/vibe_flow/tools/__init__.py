from vibe_flow.tool_base import Tool
from vibe_flow.tools.get_current_time import tool as get_current_time_tool

ALL_TOOLS: list[Tool] = [
    get_current_time_tool,
]
TOOLS_BY_NAME: dict[str, Tool] = {t.name: t for t in ALL_TOOLS}


def get_schemas() -> list[dict]:
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
