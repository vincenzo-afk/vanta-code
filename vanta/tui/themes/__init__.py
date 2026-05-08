"""Personality theme data: banners, prefixes, spinner chars."""

THEME_CLASSIC = {
    "banner": """
  ╔╗  ╔╗  ╔══╗  ╔╗  ╔╗  ╔════╗  ╔══╗
  ║╚╗╔╝║  ╠══╣  ║╚╗╔╝║  ╚══╗ ║  ╠══╣
  ╚══╝╚╝  ╚══╝  ╚══╝╚╝     ╚═╝  ╚══╝
    """,
    "prefix": "[→] ",
    "spinner_chars": ["◆", "◇", "◈", "◉"],
    "status_thinking": "Processing...",
    "status_done": "Done.",
    "status_error": "Error.",
    "pygments_style": "github-dark",
    "accent_color": "#58a6ff",
}

THEME_HACKER = {
    "banner": r"""
  ██╗   ██╗ █████╗ ███╗   ██╗████████╗ █████╗
  ██║   ██║██╔══██╗████╗  ██║╚══██╔══╝██╔══██╗
  ╚██╗ ██╔╝███████║██╔██╗ ██║   ██║   ███████║
   ╚████╔╝ ██╔══██║██║ ╚████║   ██║   ██╔══██║
    ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝
    """,
    "prefix": "[>] ",
    "spinner_chars": ["▓", "▒", "░", "▒"],
    "status_thinking": "EXECUTING...",
    "status_done": "DONE.",
    "status_error": "ERROR.",
    "pygments_style": "monokai",
    "accent_color": "#00ff41",
}

THEME_SAKURA = {
    "banner": """
  ✦ ˚ · .  V A N T A  C O D E  . · ˚ ✦
  ─────── the coding agent with a soul ───────
    """,
    "prefix": "✿ ",
    "spinner_chars": ["✿", "❀", "✾", "❁"],
    "status_thinking": "Thinking~",
    "status_done": "Done ✓",
    "status_error": "Oops! Error.",
    "pygments_style": "dracula",
    "accent_color": "#ff79c6",
}

ALL_THEMES: dict[str, dict] = {
    "classic": THEME_CLASSIC,
    "hacker": THEME_HACKER,
    "sakura": THEME_SAKURA,
}


def get_theme(name: str) -> dict:
    """Return theme data dict by name, falling back to classic."""
    return ALL_THEMES.get(name, THEME_CLASSIC)
