from pathlib import Path
from typing import Any

from vibe_flow.tool_base import Tool, ToolResult


class ReadFileTool(Tool):
    name = "read_file"
    description = (
        "Read text content from a file at an absolute path. "
        "Returns the full file contents as a string."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": (
                    "Absolute filesystem path of the file to read."
                ),
            },
        },
        "required": ["path"],
    }
    requires_permission: bool = False

    async def call(self, args: dict[str, Any]) -> ToolResult:
        path_str: str = args["path"]
        path: Path = Path(path_str)

        if not path.is_absolute():
            return ToolResult.of(
                f"Error: path must be absolute, got '{path_str}'."
            )
        if not path.exists():
            return ToolResult.of(
                f"Error: file does not exist: {path}"
            )
        if not path.is_file():
            return ToolResult.of(
                f"Error: not a regular file: {path}"
            )

        try:
            content: str = path.read_text()
        except UnicodeDecodeError:
            return ToolResult.of(
                f"Error: file is not valid UTF-8 text: {path}"
            )
        return ToolResult.of(content)


tool: ReadFileTool = ReadFileTool()
