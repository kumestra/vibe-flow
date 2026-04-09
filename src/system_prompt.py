"""
System prompt assembly — mirrors Claude Code's static + dynamic pattern.

For now, just the static base prompt. Later this can grow to include
dynamic sections (environment info, tool guidelines, etc.).
"""

STATIC_PROMPT = (
    "You are a helpful coding assistant. "
    "Use the provided tools to help the user with their tasks. "
    "Be concise in your responses."
)


def build_system_prompt() -> str:
    """Assemble the full system prompt."""
    return STATIC_PROMPT
