"""Root Textual App — VantaApp with 3-panel layout and theme switching."""

from __future__ import annotations

import asyncio
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal

from vanta.tui.panels.chat_panel import ChatPanel
from vanta.tui.panels.file_tree import FileTreePanel
from vanta.tui.panels.terminal_panel import TerminalPanel
from vanta.tui.widgets.input_bar import InputBar
from vanta.tui.widgets.status_bar import StatusBar

_THEMES_DIR = Path(__file__).parent / "themes"


class VantaApp(App):
    """The Vanta Code terminal UI application."""

    TITLE = "Vanta Code"
    CSS_PATH = str(_THEMES_DIR / "classic.tcss")

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+t", "toggle_theme", "Theme"),
        Binding("ctrl+f", "focus_file_tree", "Files"),
        Binding("ctrl+l", "clear_chat", "Clear"),
        Binding("ctrl+k", "show_shortcuts", "Keys"),
        Binding("ctrl+p", "command_palette", "Commands"),
        Binding("ctrl+z", "undo_last", "Undo"),
        Binding("f1", "toggle_memory_panel", "Memory"),
        Binding("f2", "toggle_terminal", "Terminal"),
        Binding("enter", "send_message", "Send"),
    ]

    def __init__(self, config=None, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self._theme_cycle = ["classic", "hacker", "sakura"]
        self._theme_idx = 0
        self._agent_loop = None

        if config:
            theme = config.tui.theme
            if theme in self._theme_cycle:
                self._theme_idx = self._theme_cycle.index(theme)
            self.CSS_PATH = str(_THEMES_DIR / f"{theme}.tcss")

    def compose(self) -> ComposeResult:
        from textual.widgets import Header, Footer

        yield Header(show_clock=True)
        with Horizontal():
            project_root = self.config.project_root if self.config else "."
            yield FileTreePanel(project_root=project_root, id="file-tree")
            yield ChatPanel(id="chat")
            yield TerminalPanel(id="terminal")
        yield InputBar(id="input")
        yield StatusBar(id="status")
        yield Footer()

    async def on_mount(self) -> None:
        """Initialize the agent loop on startup."""
        from vanta.agent.loop import AgentLoop
        from vanta.models import SessionState

        state = SessionState()
        self._agent_loop = AgentLoop(config=self.config, state=state)
        self.query_one("#input").focus()

        # Show banner
        chat = self.query_one(ChatPanel)
        from vanta.tui.themes import get_theme
        theme_data = get_theme(self.config.tui.theme if self.config else "classic")
        chat.add_message("agent", theme_data["banner"] + "\nReady. Type a task to begin.")

    async def action_send_message(self) -> None:
        """Handle Enter key — submit input and run agent."""
        input_bar = self.query_one(InputBar)
        task = input_bar.submit()
        if not task:
            return

        chat = self.query_one(ChatPanel)
        terminal = self.query_one(TerminalPanel)
        status = self.query_one(StatusBar)

        # Handle slash commands
        if task.startswith("/"):
            await self._handle_slash_command(task)
            return

        chat.add_message("user", task)
        status.set_state("planning")
        terminal.write_info(f"Task: {task[:60]}")

        try:
            assert self._agent_loop is not None
            status.set_state("acting")
            result = await asyncio.get_event_loop().run_in_executor(
                None, lambda: asyncio.run(self._agent_loop.run_task(task))
            )
            chat.add_message("agent", result)
            status.set_state("idle")
            terminal.write_success("Done.")
        except Exception as exc:
            chat.add_message("agent", f"**Error:** {exc}")
            status.set_state("idle")
            terminal.write_error(str(exc))

    async def _handle_slash_command(self, cmd: str) -> None:
        """Process /command shortcuts."""
        chat = self.query_one(ChatPanel)
        parts = cmd.split()
        command = parts[0].lower()

        if command in ("/help", "/h"):
            chat.add_message("agent", (
                "**Slash Commands:**\n"
                "- `/help` — this message\n"
                "- `/clear` — clear chat\n"
                "- `/plan` — show current plan\n"
                "- `/theme <name>` — switch theme (classic|hacker|sakura)\n"
                "- `/dry-run toggle` — toggle dry-run mode\n"
                "- `/exit` — quit"
            ))
        elif command == "/clear":
            chat.clear()
        elif command == "/theme" and len(parts) > 1:
            await self._switch_theme(parts[1])
        elif command in ("/exit", "/quit"):
            self.exit()
        elif command == "/plan":
            if self._agent_loop and self._agent_loop.state.current_plan:
                plan_str = "\n".join(
                    f"{i+1}. [{s.status}] {s.description}"
                    for i, s in enumerate(self._agent_loop.state.current_plan)
                )
                chat.add_message("agent", f"**Current Plan:**\n```\n{plan_str}\n```")
            else:
                chat.add_message("agent", "No active plan.")
        else:
            chat.add_message("agent", f"Unknown command: `{cmd}`. Type `/help` for list.")

    async def _switch_theme(self, theme_name: str) -> None:
        css_path = _THEMES_DIR / f"{theme_name}.tcss"
        if css_path.exists():
            self.stylesheet.read(str(css_path))
            self.refresh(layout=True)
            if theme_name in self._theme_cycle:
                self._theme_idx = self._theme_cycle.index(theme_name)
        else:
            self.query_one(ChatPanel).add_message("agent", f"Unknown theme: `{theme_name}`")

    def action_toggle_theme(self) -> None:
        self._theme_idx = (self._theme_idx + 1) % len(self._theme_cycle)
        theme = self._theme_cycle[self._theme_idx]
        self.run_worker(self._switch_theme(theme), exclusive=False)

    def action_focus_file_tree(self) -> None:
        self.query_one("#file-tree").focus()

    def action_clear_chat(self) -> None:
        self.query_one(ChatPanel).clear()

    def action_toggle_terminal(self) -> None:
        terminal = self.query_one("#terminal")
        terminal.display = not terminal.display

    def action_show_shortcuts(self) -> None:
        chat = self.query_one(ChatPanel)
        shortcuts = (
            "**Keyboard Shortcuts:**\n"
            "- `Ctrl+Q` — Quit\n"
            "- `Ctrl+T` — Cycle theme\n"
            "- `Ctrl+F` — Focus file tree\n"
            "- `Ctrl+L` — Clear chat\n"
            "- `F2` — Toggle terminal panel\n"
            "- `Enter` — Send message\n"
            "- `↑/↓` — Input history\n"
        )
        chat.add_message("agent", shortcuts)

    def action_undo_last(self) -> None:
        self.query_one(TerminalPanel).write_info("Undo not yet implemented.")

    def action_toggle_memory_panel(self) -> None:
        self.query_one(TerminalPanel).write_info("Memory panel toggle not yet implemented.")
