"""Safe filesystem helpers: atomic writes, directory creation."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path


async def atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
    """
    Write content to `path` atomically using a temp file + rename.
    Guarantees no partial writes are visible.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        await asyncio.to_thread(_sync_write, tmp, content, encoding)
        await asyncio.to_thread(os.replace, str(tmp), str(path))
    except Exception:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise


def _sync_write(path: Path, content: str, encoding: str) -> None:
    with open(path, "w", encoding=encoding) as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())


def ensure_dir(path: str | Path) -> Path:
    """Create directory and all parents if they don't exist. Returns Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def safe_relative(path: str | Path, base: str | Path) -> str:
    """Return path relative to base, or the absolute path if not under base."""
    try:
        return str(Path(path).relative_to(base))
    except ValueError:
        return str(path)
