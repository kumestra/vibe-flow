"""
TUI entry point — hello world layout.

Layout:
    ┌─────────────────────────┐
    │                         │
    │   message history       │
    │   (scrollable)          │
    │                         │
    ├─────────────────────────┤
    │ > input box             │
    └─────────────────────────┘
"""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Input, RichLog


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

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield RichLog(wrap=True, markup=True)
        yield Input(placeholder="Type a message and press Enter...")
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one(RichLog)
        log.write("[bold green]Assistant:[/] Hello! How can I help you?")
        self.query_one(Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        user_input: str = event.value.strip()
        if not user_input:
            return

        log = self.query_one(RichLog)
        log.write(f"[bold blue]You:[/] {user_input}")
        log.write("[bold green]Assistant:[/] (agent not wired up yet)")

        event.input.clear()


def main() -> None:
    ChatApp().run()


if __name__ == "__main__":
    main()
