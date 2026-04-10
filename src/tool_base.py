"""
Tool base class and execution context — Phase 1 of the tool execution rewrite.

Mirrors Claude Code's Tool.ts and ToolUseContext:
  - Tool       — abstract base every tool extends
  - ToolUseContext — per-turn execution environment
  - ToolResult — what a tool returns (split into assistant/user views)
"""

from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    """
    Result of a tool call.

    `for_assistant` is what goes back to the model as the tool_result.
    `for_user` is what we show in the terminal.

    Today they're usually the same, but the split is where Phase 6
    (large-result persistence) will land: `for_assistant` becomes a
    short summary pointing at a file, while `for_user` stays rich.
    """

    for_assistant: str
    for_user: str

    @classmethod
    def of(cls, text: str) -> "ToolResult":
        """Convenience: same text for both views."""
        return cls(for_assistant=text, for_user=text)


@dataclass
class ToolUseContext:
    """
    Per-turn execution environment passed to every tool.

    Mirrors Claude Code's ToolUseContext. Phase 1 only uses `cwd` and
    `abort_signal`; later phases add hooks, permissions, budget, etc.
    """

    messages: list
    cwd: str
    abort_signal: threading.Event = field(default_factory=threading.Event)
    options: dict[str, Any] = field(default_factory=dict)


class Tool(ABC):
    """
    Abstract base for every tool.

    Subclasses set `name`, `description`, `input_schema` as class
    attributes and implement `call()`. Future phases will add optional
    methods (`validate_input`, `needs_permission`, `is_concurrency_safe`,
    etc.) here with sensible defaults.
    """

    name: str
    description: str
    input_schema: dict  # JSON Schema for the tool's arguments

    @abstractmethod
    def call(self, args: dict, ctx: ToolUseContext) -> ToolResult:
        """Execute the tool. Must be implemented by every subclass."""
        ...

    def to_openai_schema(self) -> dict:
        """Convert to an OpenAI function-calling schema entry."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }
