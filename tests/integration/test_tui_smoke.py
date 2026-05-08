"""Integration smoke test for TUI imports and structure."""

import pytest


def test_tui_imports():
    """TUI modules import without error."""
    from vanta.tui.app import VantaApp
    assert VantaApp is not None


def test_tui_panels_import():
    from vanta.tui.panels.chat_panel import ChatPanel
    from vanta.tui.panels.file_tree import FileTreePanel
    from vanta.tui.panels.terminal_panel import TerminalPanel
    assert ChatPanel and FileTreePanel and TerminalPanel


def test_tui_widgets_import():
    from vanta.tui.widgets.diff_viewer import DiffViewer
    from vanta.tui.widgets.status_bar import StatusBar
    from vanta.tui.widgets.input_bar import InputBar
    assert DiffViewer and StatusBar and InputBar


def test_themes_css_exist():
    from pathlib import Path
    themes_dir = Path(__file__).parent.parent.parent / "vanta" / "tui" / "themes"
    for theme in ["classic", "hacker", "sakura"]:
        css_file = themes_dir / f"{theme}.tcss"
        assert css_file.exists(), f"Missing theme: {css_file}"
        assert css_file.stat().st_size > 100, f"Theme too small: {theme}"


def test_theme_data_complete():
    from vanta.tui.themes import ALL_THEMES
    for name, data in ALL_THEMES.items():
        assert "banner" in data, f"Missing banner in {name}"
        assert "prefix" in data, f"Missing prefix in {name}"
        assert "spinner_chars" in data, f"Missing spinner_chars in {name}"
        assert len(data["spinner_chars"]) >= 2
