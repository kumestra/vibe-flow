from src.tool_base import Tool
from src.tools.get_current_time import tool as get_current_time_tool

ALL_TOOLS: list[Tool] = [get_current_time_tool]
TOOLS_BY_NAME: dict[str, Tool] = {t.name: t for t in ALL_TOOLS}


def get_schemas() -> list[dict]:
    """Return OpenAI function-calling schemas for all tools."""
    return [t.to_openai_schema() for t in ALL_TOOLS]
