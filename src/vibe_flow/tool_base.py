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
from dataclasses import dataclass
from typing import Any

from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
)


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

    @abstractmethod
    def call(self, args: dict[str, Any]) -> ToolResult:
        """Execute the tool. Must be implemented by every subclass."""
        ...


def run_tool_use(
    tool_call: ChatCompletionMessageToolCall,
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
        return tool.call(args)
    except Exception as exc:
        return ToolResult.of(f"Error running '{name}': {exc}")
