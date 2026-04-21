"""
Tool base class and execution.

Three types / functions:
  - ToolResult  — what a tool returns
  - Tool        — abstract base every tool extends
  - run_tool_use — look up, parse args, and call a tool
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
)


class PermissionDecision(str, Enum):
    ALLOW_ONCE = "allow_once"
    ALLOW_SESSION = "allow_session"
    DENY = "deny"


PermissionCallback = Callable[
    [str, dict[str, Any]], Awaitable[PermissionDecision]
]


@dataclass
class ToolResult:
    """
    Result of a tool call.

    `for_assistant` is what goes back to the model.
    `for_user` is what we show in the terminal.
    """

    for_assistant: str
    for_user: str

    @classmethod
    def of(cls, text: str) -> "ToolResult":
        """Convenience: same text for both views."""
        return cls(for_assistant=text, for_user=text)


class Tool(ABC):
    """
    Abstract base for every tool.

    Subclasses set `name`, `description`, `input_schema` as class
    attributes and implement `call()`.
    """

    name: str
    description: str
    input_schema: dict[str, Any]
    requires_permission: bool = False

    @abstractmethod
    async def call(self, args: dict[str, Any]) -> ToolResult:
        """Execute the tool. Must be implemented by every subclass."""
        ...


async def run_tool_use(
    tool_call: ChatCompletionMessageToolCall,
    tools_by_name: dict[str, Tool],
    on_permission: PermissionCallback | None = None,
    session_allowed: set[str] | None = None,
) -> ToolResult:
    """
    Run a single tool call. Returns a ToolResult even on failure
    so the caller can always route something back to the model.

    If the tool sets requires_permission=True and its name is not in
    session_allowed, on_permission is awaited. DENY short-circuits
    the call and returns a denial ToolResult. ALLOW_SESSION adds
    the name to session_allowed so later calls skip the prompt.
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

    # 3. Permission gate
    if (
        tool.requires_permission
        and on_permission is not None
        and (session_allowed is None or name not in session_allowed)
    ):
        decision: PermissionDecision = await on_permission(name, args)
        if decision == PermissionDecision.DENY:
            return ToolResult.of(
                f"Permission denied by user for tool '{name}'."
            )
        if (
            decision == PermissionDecision.ALLOW_SESSION
            and session_allowed is not None
        ):
            session_allowed.add(name)

    # 4. Call
    try:
        return await tool.call(args)
    except Exception as exc:
        return ToolResult.of(f"Error running '{name}': {exc}")
