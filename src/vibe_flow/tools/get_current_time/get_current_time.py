from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from vibe_flow.tool_base import Tool, ToolResult


class GetCurrentTimeTool(Tool):
    name = "get_current_time"
    description = (
        "Return the current date and time as an ISO 8601 string. "
        "Optionally takes an IANA timezone name (e.g. 'UTC', "
        "'America/New_York'). Defaults to UTC."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "timezone": {
                "type": "string",
                "description": (
                    "IANA timezone name, e.g. 'UTC' or "
                    "'America/New_York'. Defaults to 'UTC'."
                ),
            },
        },
        "required": [],
    }

    async def call(self, args: dict[str, Any]) -> ToolResult:
        tz_name: str = args.get("timezone", "UTC")
        now = datetime.now(ZoneInfo(tz_name))
        return ToolResult.of(now.isoformat())


tool: GetCurrentTimeTool = GetCurrentTimeTool()
