from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel

from src.tool_base import (
    Tool,
    ToolResult,
    ToolUseContext,
    ValidationResult,
)


class _Input(BaseModel):
    timezone: str = "UTC"


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

    InputModel = _Input

    def validate_input(
        self, args: dict, ctx: ToolUseContext
    ) -> ValidationResult:
        tz_name = args.get("timezone", "UTC")
        try:
            ZoneInfo(tz_name)
        except (ZoneInfoNotFoundError, KeyError):
            return ValidationResult.failure(
                f"Unknown timezone '{tz_name}'. "
                "Use an IANA name such as 'UTC' or 'America/New_York'."
            )
        return ValidationResult.success()

    def call(self, args: dict, ctx: ToolUseContext) -> ToolResult:
        tz_name = args.get("timezone", "UTC")
        now = datetime.now(ZoneInfo(tz_name))
        return ToolResult.of(now.isoformat())


tool = GetCurrentTimeTool()
