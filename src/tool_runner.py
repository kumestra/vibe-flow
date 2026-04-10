"""
Tool execution pipeline — Phase 1 skeleton.

Mirrors Claude Code's `runToolUse` in query.ts. Right now it only does
lookup + call, but every future phase plugs in here:

    Phase 2: abort check, schema validation, semantic validation
    Phase 3: permission resolution
    Phase 5: pre/post hooks
    Phase 6: large-result persistence

Keeping this function as the single entry point means `agent.py` never
has to change again as we add layers.
"""

from __future__ import annotations

import json

from src.tool_base import Tool, ToolResult, ToolUseContext


def run_tool_use(
    tool_call,
    ctx: ToolUseContext,
    tools_by_name: dict[str, Tool],
) -> ToolResult:
    """
    Run a single tool call through the (currently minimal) pipeline.

    Returns a ToolResult even on failure, so the caller can always
    route something back to the model.
    """
    name = tool_call.function.name

    # --- Step 1: lookup (Phase 2 will add alias fallback) ---------------
    tool = tools_by_name.get(name)
    if tool is None:
        available = ", ".join(sorted(tools_by_name)) or "(none)"
        return ToolResult.of(
            f"Error: unknown tool '{name}'. Available tools: {available}"
        )

    # --- Parse arguments ------------------------------------------------
    try:
        args = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError as e:
        return ToolResult.of(f"Error: invalid JSON arguments for {name}: {e}")

    # --- Step 10: the actual call --------------------------------------
    # Phases 2/3/5 will sit between parsing and this call.
    try:
        return tool.call(args, ctx)
    except Exception as e:
        return ToolResult.of(f"Error running {name}: {e}")
