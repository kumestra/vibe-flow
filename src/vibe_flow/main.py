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

import os
import uuid

from rich.markdown import Markdown
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Input, RichLog, Static

from vibe_flow.agent import query
from vibe_flow.logger import SessionLogger


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
        self.session_id: str = str(uuid.uuid4())
        self.messages: list[dict] = []
        self.logger: SessionLogger = SessionLogger(
            self.session_id, os.getcwd()
        )

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield RichLog(wrap=True, markup=True)
        yield Static("", id="streaming")
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
        streaming: Static = self.query_one("#streaming", Static)
        buffer: list[str] = []

        def on_token(token: str) -> None:
            buffer.append(token)
            streaming.update("".join(buffer))

        response: str = await query(
            user_input, self.messages, self.logger, on_token
        )

        streaming.update("")
        log: RichLog = self.query_one(RichLog)
        log.write("[bold green]Assistant:[/]")
        log.write(Markdown(response))
        input_widget: Input = self.query_one(Input)
        input_widget.disabled = False
        input_widget.focus()


def main() -> None:
    ChatApp().run()
