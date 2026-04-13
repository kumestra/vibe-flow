"""
Tool base class and execution context — Phases 1 & 2.

Mirrors Claude Code's Tool.ts and ToolUseContext:
  - ValidationResult — outcome of a validation step (Phase 2)
  - Tool             — abstract base every tool extends
  - ToolUseContext   — per-turn execution environment
  - ToolResult       — what a tool returns (split into assistant/user views)
"""

from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, ValidationError


@dataclass
class ValidationResult:
    """
    Outcome of a validation step.

    Used by both `Tool.validate_schema` (Pydantic) and
    `Tool.validate_input` (semantic checks). A failed result carries
    a human-readable `error` that `run_tool_use` forwards to the model.
    """

    ok: bool
    error: str | None = None

    @classmethod
    def success(cls) -> "ValidationResult":
        return cls(ok=True)

    @classmethod
    def failure(cls, error: str) -> "ValidationResult":
        return cls(ok=False, error=error)


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
    attributes and implement `call()`.

    Optional overrides added in Phase 2:
      - `InputModel` — a Pydantic BaseModel; if set, `validate_schema`
        uses it automatically.
      - `validate_input()` — semantic checks beyond schema (e.g. file
        must exist, timezone must be valid).

    Later phases will add:
      - `needs_permission()` (Phase 3)
      - `is_concurrency_safe()` (Phase 4)
    """

    name: str
    description: str
    input_schema: dict  # JSON Schema for the tool's arguments

    # Subclasses may set this to a Pydantic model class.
    # If set, validate_schema() uses it automatically.
    InputModel: type[BaseModel] | None = None

    @abstractmethod
    def call(self, args: dict, ctx: ToolUseContext) -> ToolResult:
        """Execute the tool. Must be implemented by every subclass."""
        ...

    def validate_schema(
        self, args: dict
    ) -> ValidationResult:
        """
        Validate args against this tool's Pydantic InputModel.

        If no InputModel is declared, always returns success — the
        OpenAI layer already validated the basic JSON structure.
        """
        if self.InputModel is None:
            return ValidationResult.success()
        try:
            self.InputModel.model_validate(args)
            return ValidationResult.success()
        except ValidationError as exc:
            lines = [
                f"  {e['loc'][0] if e['loc'] else '(root)'}: "
                f"{e['msg']}"
                for e in exc.errors()
            ]
            return ValidationResult.failure(
                "Schema validation failed:\n" + "\n".join(lines)
            )

    def validate_input(
        self, args: dict, ctx: ToolUseContext
    ) -> ValidationResult:
        """
        Semantic validation beyond schema checks.

        Default: always OK. Override in tools that need deeper checks
        (e.g. path exists, timezone name is valid, etc.).
        """
        return ValidationResult.success()

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
