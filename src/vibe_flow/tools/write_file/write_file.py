from pathlib import Path
from typing import Any

from vibe_flow.tool_base import Tool, ToolResult


class WriteFileTool(Tool):
    name = "write_file"
    description = (
        "Write text content to a file at an absolute path. "
        "Creates parent directories if missing. Overwrites the "
        "file if it already exists."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": (
                    "Absolute filesystem path of the file to write."
                ),
            },
            "content": {
                "type": "string",
                "description": "Text content to write to the file.",
            },
        },
        "required": ["path", "content"],
    }
    requires_permission: bool = True

    async def call(self, args: dict[str, Any]) -> ToolResult:
        path_str: str = args["path"]
        content: str = args["content"]

        path: Path = Path(path_str)
        if not path.is_absolute():
            return ToolResult.of(
                f"Error: path must be absolute, got '{path_str}'."
            )

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return ToolResult.of(
            f"Wrote {len(content)} bytes to {path}"
        )


tool: WriteFileTool = WriteFileTool()
