"""
Tool execution pipeline — Phase 2: validation layers.

Steps wired in so far (mirrors Claude Code's runToolUse in query.ts):

    1. Lookup with alias fallback
    2. Abort check
    3. Schema validation (Pydantic)
    4. Semantic validate_input()
   10. tool.call()              (was the only step in Phase 1)

Remaining phases will add:
    Phase 3: permission resolution (between step 4 and 10)
    Phase 5: pre/post shell hooks (around step 10)
    Phase 6: large-result persistence (after step 10)
"""

from __future__ import annotations

import json

from src.tool_base import Tool, ToolResult, ToolUseContext

# ---------------------------------------------------------------------------
# Alias map — mirrors the aliases in Claude Code's tool-lookup layer.
# Keys are alternate names the model might use; values are canonical names.
# Extend this as we add more tools.
# ---------------------------------------------------------------------------
ALIASES: dict[str, str] = {
    # Claude Code aliases observed in the source:
    "str_replace_editor": "edit",
    "str_replace_based_edit_tool": "edit",
}


def _lookup_tool(
    name: str,
    tools_by_name: dict[str, Tool],
) -> Tool | None:
    """
    Look up a tool by name, falling back to the alias map.

    Returns None if neither the name nor any alias matches.
    """
    tool = tools_by_name.get(name)
    if tool is not None:
        return tool
    canonical = ALIASES.get(name)
    if canonical is not None:
        return tools_by_name.get(canonical)
    return None


def run_tool_use(
    tool_call,
    ctx: ToolUseContext,
    tools_by_name: dict[str, Tool],
) -> ToolResult:
    """
    Run a single tool call through the validation pipeline.

    Returns a ToolResult even on failure — the caller always has
    something to route back to the model.
    """
    name = tool_call.function.name

    # --- Step 1: Lookup with alias fallback --------------------------------
    tool = _lookup_tool(name, tools_by_name)
    if tool is None:
        available = ", ".join(sorted(tools_by_name)) or "(none)"
        return ToolResult.of(
            f"Error: unknown tool '{name}'. "
            f"Available tools: {available}"
        )

    # --- Step 2: Abort check -----------------------------------------------
    if ctx.abort_signal.is_set():
        return ToolResult.of(
            f"Error: tool call '{name}' aborted before execution."
        )

    # --- Parse raw JSON arguments ------------------------------------------
    # (must happen before schema or semantic validation)
    try:
        args = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError as exc:
        return ToolResult.of(
            f"Error: invalid JSON arguments for '{name}': {exc}"
        )

    # --- Step 3: Schema validation (Pydantic) ------------------------------
    schema_result = tool.validate_schema(args)
    if not schema_result.ok:
        return ToolResult.of(
            f"Error in '{name}' arguments: {schema_result.error}"
        )

    # --- Step 4: Semantic validate_input() ---------------------------------
    semantic_result = tool.validate_input(args, ctx)
    if not semantic_result.ok:
        return ToolResult.of(
            f"Error: cannot run '{name}': {semantic_result.error}"
        )

    # --- Step 10: The actual call ------------------------------------------
    # Phases 3 and 5 will insert permission + hooks between step 4 and here.
    try:
        return tool.call(args, ctx)
    except Exception as exc:
        return ToolResult.of(f"Error running '{name}': {exc}")
