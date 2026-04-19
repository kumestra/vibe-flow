"""
TUI entry point — agent wired into the chat layout.

Layout:
    ┌─────────────────────────┐
    │                         │
    │   message history       │
    │   (scrollable)          │
    │                         │
    ├─────────────────────────┤
    │ streaming response      │
    ├─────────────────────────┤
    │ > input box             │
    └─────────────────────────┘

The agent runs as an async worker on textual's event loop.
Tokens stream into the Static widget as they arrive; when the
response is complete it moves to RichLog as rendered markdown.
"""

import json
from contextlib import AsyncExitStack
from pathlib import Path

from rich.markdown import Markdown
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Input, RichLog, Static

from vibe_flow.agent import query
from vibe_flow.mcp_client import load_mcp_tools
from vibe_flow.tools import register_mcp_tools

_MCP_CONFIG: Path = Path(__file__).parent.parent.parent / "mcp.json"


class ChatApp(App):
    CSS = """
    RichLog {
        height: 1fr;
        border: solid $primary;
        padding: 0 1;
    }

    #streaming {
        padding: 0 1;
        color: $text-muted;
    }

    Input {
        dock: bottom;
    }
    """

    BINDINGS = [Binding("ctrl+c", "quit", "Quit", show=True, priority=True)]

    def __init__(self) -> None:
        super().__init__()
        self.messages: list[dict] = []
        self._mcp_stack: AsyncExitStack = AsyncExitStack()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield RichLog(wrap=True, markup=True)
        yield Static("", id="streaming")
        yield Input(placeholder="Type a message and press Enter...")
        yield Footer()

    async def on_mount(self) -> None:
        self.query_one(RichLog).write(
            "[bold green]Assistant:[/] Hello! How can I help you?"
        )
        self.query_one(Input).focus()
        await self._init_mcp()

    async def _init_mcp(self) -> None:
        if not _MCP_CONFIG.exists():
            return
        config: dict = json.loads(_MCP_CONFIG.read_text())
        for server in config.get("servers", []):
            tools = await load_mcp_tools(
                server["url"], self._mcp_stack
            )
            register_mcp_tools(tools)

    async def on_unmount(self) -> None:
        await self._mcp_stack.aclose()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        user_input: str = event.value.strip()
        if not user_input:
            return

        self.query_one(RichLog).write(f"[bold blue]You:[/] {user_input}")
        event.input.clear()
        event.input.disabled = True
        self._run_agent(user_input)

    @work
    async def _run_agent(self, user_input: str) -> None:
        streaming: Static = self.query_one("#streaming", Static)
        log: RichLog = self.query_one(RichLog)
        buffer: list[str] = []

        def on_token(token: str) -> None:
            buffer.append(token)
            streaming.update("".join(buffer))

        def on_tool_call(name: str, args: dict) -> None:
            args_str: str = ", ".join(
                f"{k}={v!r}" for k, v in args.items()
            )
            log.write(f"[bold yellow]→ Tool:[/] {name}({args_str})")

        def on_tool_result(name: str, output: str) -> None:
            preview: str = output[:120] + "…" if len(output) > 120 else output
            log.write(f"[dim]← {name}: {preview}[/dim]")

        response: str = await query(
            user_input, self.messages,
            on_token, on_tool_call, on_tool_result,
        )

        streaming.update("")
        log.write("[bold green]Assistant:[/]")
        log.write(Markdown(response))
        input_widget: Input = self.query_one(Input)
        input_widget.disabled = False
        input_widget.focus()


def main() -> None:
    ChatApp().run()
