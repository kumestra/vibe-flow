"""
Tool base class.

Two types used throughout the pipeline:
  - Tool       — abstract base every tool extends
  - ToolResult — what a tool returns
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


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

