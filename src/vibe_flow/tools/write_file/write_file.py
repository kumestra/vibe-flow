from pathlib import Path

from vibe_flow.tool_base import Tool, ToolResult, ToolUseContext


class WriteFileTool(Tool):
    name = "write_file"
    description = (
        "Write text content to a file. "
        "Creates the file if it does not exist; overwrites if it does."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file to write.",
            },
            "content": {
                "type": "string",
                "description": "Text content to write.",
            },
        },
        "required": ["path", "content"],
    }

    def call(self, args: dict, ctx: ToolUseContext) -> ToolResult:
        path: Path = Path(args["path"])
        content: str = args["content"]
        path.write_text(content, encoding="utf-8")
        return ToolResult.of(f"Wrote {len(content):,} chars to {path}")


tool: WriteFileTool = WriteFileTool()
