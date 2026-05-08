"""File tools: read_file, write_file, patch_file, create_file, delete_file."""

from __future__ import annotations

from pathlib import Path

from vanta.tools.registry import tool
from vanta.utils.diff import apply_diff
from vanta.utils.fs import atomic_write


@tool("read_file", "Read file content, optionally sliced by line range.")
async def read_file(
    path: str,
    start_line: int | None = None,
    end_line: int | None = None,
    config=None,
    state=None,
) -> str:
    """
    Read the full text content of a file at the given path.

    Args:
        path: Absolute or relative (to cwd) file path.
        start_line: First line to read (1-indexed). None = start of file.
        end_line: Last line to read (inclusive). None = end of file.

    Returns:
        File content as string.

    Raises:
        FileNotFoundError: If path does not exist.
    """
    p = Path(path).resolve()
    if not p.exists():
        raise FileNotFoundError(f"read_file: {path} does not exist")
    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    if start_line is not None or end_line is not None:
        s = (start_line - 1) if start_line else 0
        e = end_line if end_line else len(lines)
        lines = lines[s:e]
    return "".join(lines)


@tool("write_file", "Write full content to a file. Creates parent dirs if needed.")
async def write_file(
    path: str,
    content: str,
    config=None,
    state=None,
) -> str:
    """
    Write content to a file, creating it (and parent dirs) if needed.
    Overwrites the full file content. Respects dry_run mode.

    Returns:
        Success message with bytes written, or dry-run notice.
    """
    p = Path(path).resolve()
    if config and config.dry_run:
        return f"[DRY RUN] Would write {len(content)} bytes to {p}"
    p.parent.mkdir(parents=True, exist_ok=True)
    await atomic_write(p, content)
    return f"Wrote {len(content)} bytes to {p}"


@tool("patch_file", "Apply a unified diff patch to an existing file.")
async def patch_file(
    path: str,
    patch: str,
    config=None,
    state=None,
) -> str:
    """
    Apply a unified diff patch to an existing file.

    Args:
        path: Target file path.
        patch: Unified diff string (--- a/... +++ b/... format).

    Returns:
        Success message or dry-run notice.

    Raises:
        FileNotFoundError: If file does not exist.
        RuntimeError: If patch application fails.
    """
    p = Path(path).resolve()
    if not p.exists():
        raise FileNotFoundError(f"patch_file: {path} not found")
    if config and config.dry_run:
        return f"[DRY RUN] Would apply patch to {p}"
    original = p.read_text(encoding="utf-8")
    patched = apply_diff(original, patch)
    if patched == original and patch.strip():
        raise RuntimeError("Patch application failed — check diff format and context lines.")
    await atomic_write(p, patched)
    orig_lines = len(original.splitlines())
    new_lines = len(patched.splitlines())
    return f"Patch applied to {p} ({abs(new_lines - orig_lines)} lines changed)"


@tool("create_file", "Create a new file. Fails if file already exists.")
async def create_file(
    path: str,
    content: str = "",
    config=None,
    state=None,
) -> str:
    """
    Create a new file with optional initial content.
    Fails if the file already exists (use write_file to overwrite).

    Returns:
        Confirmation or dry-run notice.

    Raises:
        FileExistsError: If file already exists.
    """
    p = Path(path).resolve()
    if p.exists():
        raise FileExistsError(
            f"create_file: {path} already exists. Use write_file to overwrite."
        )
    if config and config.dry_run:
        return f"[DRY RUN] Would create {p}"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Created {p} ({len(content)} bytes)"


@tool(
    "delete_file",
    "Delete a file. Prompts for confirmation unless force=True.",
)
async def delete_file(
    path: str,
    force: bool = False,
    config=None,
    state=None,
) -> str:
    """
    Delete a file. Always prompts for confirmation unless force=True.

    Args:
        path: File to delete.
        force: Skip confirmation prompt (use only programmatically).

    Returns:
        Confirmation or cancellation notice.

    Raises:
        FileNotFoundError: If file does not exist.
    """
    p = Path(path).resolve()
    if not p.exists():
        raise FileNotFoundError(f"delete_file: {path} not found")
    if config and config.dry_run:
        return f"[DRY RUN] Would delete {p}"
    if not force:
        # In non-TUI mode, prompt via stdin
        try:
            answer = input(f"Delete {p}? This cannot be undone. [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            answer = "n"
        if answer not in ("y", "yes"):
            return f"Deletion of {p} cancelled by user."
    p.unlink()
    return f"Deleted {p}"
