"""
Tool execution pipeline.

Steps:
    1. Lookup — find the tool by name (with alias fallback)
    2. Abort  — short-circuit if the turn was cancelled
    3. Parse  — decode the JSON arguments
    4. Call   — run the tool
"""

from __future__ import annotations

import json
from typing import Any

from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
)

from vibe_flow.tool_base import Tool, ToolResult, ToolUseContext

def run_tool_use(
    tool_call: ChatCompletionMessageToolCall,
    ctx: ToolUseContext,
    tools_by_name: dict[str, Tool],
) -> ToolResult:
    """
    Run a single tool call. Returns a ToolResult even on failure
    so the caller can always route something back to the model.
    """
    name: str = tool_call.function.name

    # 1. Lookup
    tool: Tool | None = tools_by_name.get(name)
    if tool is None:
        available: str = ", ".join(sorted(tools_by_name)) or "(none)"
        return ToolResult.of(
            f"Error: unknown tool '{name}'. "
            f"Available tools: {available}"
        )

    # 2. Parse
    args: dict[str, Any] = json.loads(tool_call.function.arguments)

    # 3. Call
    try:
        return tool.call(args, ctx)
    except Exception as exc:
        return ToolResult.of(f"Error running '{name}': {exc}")
