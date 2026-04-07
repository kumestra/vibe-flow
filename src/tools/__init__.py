from src.tools.bash import tool as bash_tool
from src.tools.read_file import tool as read_file_tool
from src.tools.write_file import tool as write_file_tool

ALL_TOOLS = [bash_tool, read_file_tool, write_file_tool]


def get_schemas() -> list[dict]:
    """Return OpenAI function-calling schemas for all tools."""
    return [t["schema"] for t in ALL_TOOLS]


def execute(name: str, arguments: dict) -> str:
    """Look up a tool by name and execute it."""
    for t in ALL_TOOLS:
        if t["name"] == name:
            return t["call"](arguments)
    return f"Unknown tool: {name}"
