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
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Input, Label, RichLog, Static

from vibe_flow.agent import query
from vibe_flow.mcp_client import load_mcp_tools
from vibe_flow.tool_base import PermissionDecision
from vibe_flow.tools import register_mcp_tools

_MCP_CONFIG: Path = Path(__file__).parent.parent.parent / "mcp.json"


class PermissionScreen(ModalScreen[PermissionDecision]):
    """Ask the user to allow/deny a tool call."""

    CSS = """
    PermissionScreen {
        align: center middle;
    }
    #dialog {
        width: 70;
        height: auto;
        border: thick $warning;
        background: $surface;
        padding: 1 2;
    }
    #dialog Label {
        margin-bottom: 1;
    }
    #buttons {
        height: auto;
        align-horizontal: center;
    }
    #buttons Button {
        margin: 0 1;
    }
    """

    BINDINGS = [Binding("escape", "deny", "Deny")]

    def __init__(self, tool_name: str, args: dict) -> None:
        super().__init__()
        self._tool_name: str = tool_name
        self._args: dict = args

    def compose(self) -> ComposeResult:
        args_str: str = ", ".join(
            f"{k}={v!r}" for k, v in self._args.items()
        )
        with Vertical(id="dialog"):
            yield Label(
                f"[bold]Allow tool call?[/]\n\n"
                f"[yellow]{self._tool_name}[/]({args_str})"
            )
            with Vertical(id="buttons"):
                yield Button("Allow once", id="once", variant="primary")
                yield Button("Allow for session", id="session")
                yield Button("Deny", id="deny", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        mapping: dict[str, PermissionDecision] = {
            "once": PermissionDecision.ALLOW_ONCE,
            "session": PermissionDecision.ALLOW_SESSION,
            "deny": PermissionDecision.DENY,
        }
        self.dismiss(mapping[event.button.id])

    def action_deny(self) -> None:
        self.dismiss(PermissionDecision.DENY)


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
        self._session_allowed: set[str] = set()

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

        async def on_permission(
            name: str, args: dict
        ) -> PermissionDecision:
            return await self.push_screen_wait(
                PermissionScreen(name, args)
            )

        response: str = await query(
            user_input, self.messages,
            on_token, on_tool_call, on_tool_result,
            on_permission=on_permission,
            session_allowed=self._session_allowed,
        )

        streaming.update("")
        log.write("[bold green]Assistant:[/]")
        log.write(Markdown(response))
        input_widget: Input = self.query_one(Input)
        input_widget.disabled = False
        input_widget.focus()


def main() -> None:
    ChatApp().run()
