"""
TUI entry point — agent wired into the chat layout.

Layout:
    ┌─────────────────────────┐
    │                         │
    │   message history       │
    │   (scrollable)          │
    │                         │
    ├─────────────────────────┤
    │ > input box             │
    └─────────────────────────┘

The agent runs as an async worker on textual's event loop.
Input is disabled during the call and re-enabled when the
response arrives.
"""

import os
import uuid

from rich.markdown import Markdown
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Input, RichLog

from vibe_flow.agent import query
from vibe_flow.logger import SessionLogger


class ChatApp(App):
    CSS = """
    RichLog {
        height: 1fr;
        border: solid $primary;
        padding: 0 1;
    }

    Input {
        dock: bottom;
    }
    """

    BINDINGS = [Binding("ctrl+c", "quit", "Quit", show=True, priority=True)]

    def __init__(self) -> None:
        super().__init__()
        self.session_id: str = str(uuid.uuid4())
        self.messages: list[dict] = []
        self.logger: SessionLogger = SessionLogger(
            self.session_id, os.getcwd()
        )

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield RichLog(wrap=True, markup=True)
        yield Input(placeholder="Type a message and press Enter...")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(RichLog).write(
            "[bold green]Assistant:[/] Hello! How can I help you?"
        )
        self.query_one(Input).focus()

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
        response: str = await query(
            user_input, self.messages, self.logger
        )
        self._show_response(response)

    def _show_response(self, response: str) -> None:
        log: RichLog = self.query_one(RichLog)
        log.write("[bold green]Assistant:[/]")
        log.write(Markdown(response))
        input_widget = self.query_one(Input)
        input_widget.disabled = False
        input_widget.focus()


def main() -> None:
    ChatApp().run()
