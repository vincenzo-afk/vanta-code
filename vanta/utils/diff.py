"""Unified diff generation utility."""

from __future__ import annotations

import difflib


def generate_diff(
    original: str,
    modified: str,
    fromfile: str = "a/file",
    tofile: str = "b/file",
    context_lines: int = 3,
) -> str:
    """
    Generate a unified diff string between `original` and `modified` text.

    Args:
        original: Original file content.
        modified: Modified file content.
        fromfile: Label for the original file (shown in diff header).
        tofile: Label for the modified file (shown in diff header).
        context_lines: Number of context lines around each change.

    Returns:
        Unified diff as a string. Empty string if files are identical.
    """
    orig_lines = original.splitlines(keepends=True)
    mod_lines = modified.splitlines(keepends=True)
    diff = list(
        difflib.unified_diff(
            orig_lines,
            mod_lines,
            fromfile=fromfile,
            tofile=tofile,
            n=context_lines,
        )
    )
    return "".join(diff)


def apply_diff(original: str, patch_str: str) -> str:
    """
    Apply a unified diff patch to `original` text using difflib.
    Returns the patched content.
    Raises ValueError if the patch cannot be applied cleanly.
    """
    if not patch_str.strip():
        return original

    orig_lines = original.splitlines(keepends=True)
    patch_lines = patch_str.splitlines(keepends=True)

    result: list[str] = []
    orig_idx = 0

    i = 0
    while i < len(patch_lines):
        line = patch_lines[i]
        if line.startswith("---") or line.startswith("+++"):
            i += 1
            continue
        if line.startswith("@@"):
            # Parse hunk header: @@ -start,count +start,count @@
            import re

            m = re.match(r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
            if not m:
                i += 1
                continue
            orig_start = int(m.group(1)) - 1
            # Advance orig_idx to hunk start, copying unchanged lines
            while orig_idx < orig_start and orig_idx < len(orig_lines):
                result.append(orig_lines[orig_idx])
                orig_idx += 1
            i += 1
            continue
        if line.startswith("+"):
            result.append(line[1:])
        elif line.startswith("-"):
            orig_idx += 1
        else:
            # Context line
            if orig_idx < len(orig_lines):
                result.append(orig_lines[orig_idx])
                orig_idx += 1
        i += 1

    # Append remaining original lines
    while orig_idx < len(orig_lines):
        result.append(orig_lines[orig_idx])
        orig_idx += 1

    return "".join(result)
