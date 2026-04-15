from pathlib import Path

from vibe_flow.tool_base import Tool, ToolResult, ToolUseContext


class ReadFileTool(Tool):
    name = "read_file"
    description = "Read the text content of a file and return it."
    input_schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file to read.",
            },
        },
        "required": ["path"],
    }

    def call(self, args: dict, ctx: ToolUseContext) -> ToolResult:
        path: Path = Path(args["path"])
        content: str = path.read_text(
            encoding="utf-8", errors="replace"
        )
        return ToolResult.of(content)


tool: ReadFileTool = ReadFileTool()
