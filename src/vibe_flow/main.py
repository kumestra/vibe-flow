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

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Input, RichLog
from openai.types.chat import ChatCompletionMessageParam

from vibe_flow.agent import query


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
        self.messages: list[ChatCompletionMessageParam] = []

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
        response: str = await query(user_input, self.messages)
        self._show_response(response)

    def _show_response(self, response: str) -> None:
        self.query_one(RichLog).write(
            f"[bold green]Assistant:[/] {response}"
        )
        input_widget = self.query_one(Input)
        input_widget.disabled = False
        input_widget.focus()


def main() -> None:
    ChatApp().run()


if __name__ == "__main__":
    main()
