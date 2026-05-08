"""Python AST helpers for code indexing."""

from __future__ import annotations

import ast
from pathlib import Path


def extract_python_symbols(source: str, file_path: str = "") -> dict:
    """
    Parse Python source and extract functions, classes, and imports.

    Returns:
        {
            "functions": [{"name": str, "start_line": int, "end_line": int}],
            "classes":   [{"name": str, "start_line": int, "end_line": int}],
            "imports":   [str],  # module names
        }
    """
    result: dict = {"functions": [], "classes": [], "imports": []}
    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError:
        return result

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result["functions"].append(
                {
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": node.end_lineno or node.lineno,
                }
            )
        elif isinstance(node, ast.ClassDef):
            result["classes"].append(
                {
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": node.end_lineno or node.lineno,
                }
            )
        elif isinstance(node, ast.Import):
            for alias in node.names:
                result["imports"].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                result["imports"].append(node.module)

    return result


def is_python_file(path: str | Path) -> bool:
    return Path(path).suffix == ".py"


def chunk_source(
    source: str, chunk_size: int = 512, overlap: int = 64
) -> list[tuple[int, int, str]]:
    """
    Split source into overlapping line-based chunks.

    Returns:
        List of (start_line, end_line, chunk_content) tuples (1-indexed).
    """
    lines = source.splitlines(keepends=True)
    chunks: list[tuple[int, int, str]] = []
    i = 0
    while i < len(lines):
        chunk_lines = lines[i : i + chunk_size]
        content = "".join(chunk_lines)
        start = i + 1
        end = i + len(chunk_lines)
        chunks.append((start, end, content))
        step = max(1, chunk_size - overlap)
        i += step
    return chunks
