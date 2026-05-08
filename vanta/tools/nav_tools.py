"""Navigation tools: list_directory, find_file."""

from __future__ import annotations

from pathlib import Path

from vanta.tools.registry import tool


@tool("list_directory", "List directory contents as a tree-formatted string.")
async def list_directory(
    path: str = ".",
    recursive: bool = False,
    max_depth: int = 3,
    show_hidden: bool = False,
    config=None,
    state=None,
) -> str:
    """
    List the contents of a directory with optional recursion.

    Args:
        path: Directory path (default: current directory).
        recursive: Recurse into subdirectories.
        max_depth: Maximum recursion depth (default 3).
        show_hidden: Include dotfiles.

    Returns:
        Tree-formatted directory listing as string.
    """
    root = Path(path).resolve()
    if not root.exists():
        raise FileNotFoundError(f"list_directory: {path} does not exist")
    if not root.is_dir():
        raise NotADirectoryError(f"list_directory: {path} is not a directory")

    lines: list[str] = [f"{root}/"]
    _build_tree(root, lines, prefix="", depth=0, max_depth=max_depth,
                recursive=recursive, show_hidden=show_hidden)
    return "\n".join(lines)


def _build_tree(
    directory: Path,
    lines: list[str],
    prefix: str,
    depth: int,
    max_depth: int,
    recursive: bool,
    show_hidden: bool,
) -> None:
    if depth >= max_depth:
        return
    try:
        entries = sorted(directory.iterdir(), key=lambda e: (e.is_file(), e.name.lower()))
    except PermissionError:
        return

    entries = [e for e in entries if show_hidden or not e.name.startswith(".")]
    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        icon = "📁 " if entry.is_dir() else "📄 "
        lines.append(f"{prefix}{connector}{icon}{entry.name}")
        if entry.is_dir() and recursive:
            extension = "    " if is_last else "│   "
            _build_tree(
                entry, lines, prefix + extension, depth + 1, max_depth, recursive, show_hidden
            )


@tool("find_file", "Find files matching a name pattern under a directory.")
async def find_file(
    pattern: str,
    path: str = ".",
    config=None,
    state=None,
) -> str:
    """
    Find files matching a glob pattern under the given directory.

    Args:
        pattern: Glob pattern (e.g. '*.py', '**/utils.py').
        path: Root directory to search under (default: '.').

    Returns:
        Newline-separated list of matching paths, or 'No files found.'
    """
    root = Path(path).resolve()
    matches = sorted(root.glob(pattern))
    if not matches:
        return "No files found."
    return "\n".join(str(m) for m in matches)
