"""AutoDebug tool: parse tracebacks and attempt automated fixes."""

from __future__ import annotations

import asyncio
import re

from vanta.tools.registry import tool


def parse_traceback(tb: str) -> dict:
    """Extract structured info from a Python traceback string."""
    file_matches = re.findall(r'File "(.+?)", line (\d+)', tb)
    error_match = re.search(r"(\w+Error|\w+Exception): (.+)$", tb, re.MULTILINE)
    last_file, last_line = file_matches[-1] if file_matches else (None, None)
    return {
        "error_type": error_match.group(1) if error_match else "UnknownError",
        "error_message": (
            error_match.group(2) if error_match else tb.strip().splitlines()[-1]
        ),
        "file": last_file,
        "line": int(last_line) if last_line else None,
        "frames": file_matches,
    }


async def _generate_fix(parsed: dict, context_code: str, attempt: int, config) -> str:
    from vanta.llm.router import route_query

    prompt = f"""You are an expert Python debugger. Fix the following error.

Error Type: {parsed['error_type']}
Error Message: {parsed['error_message']}
File: {parsed['file']}, Line: {parsed['line']}
Attempt: {attempt + 1}/3

Offending code:
```python
{context_code}
```

Return ONLY the fixed code block for the function or section that contains the bug.
Do not include explanation. Do not include any text outside the code block.
"""
    return await route_query(task=prompt, complexity="medium", config=config)


def _splice_fix(original: str, fix_code: str, error_line: int | None) -> str:
    """Replace code around error_line with fix_code (best-effort)."""
    # Strip markdown code fences if present
    fix_code = re.sub(r"```(?:python)?\n?", "", fix_code).strip()
    if not error_line:
        return fix_code  # Can't splice — replace whole file
    lines = original.splitlines(keepends=True)
    fix_lines = fix_code.splitlines(keepends=True)
    # Find function start by walking back from error_line
    start = max(0, error_line - 1)
    for i in range(start, -1, -1):
        if lines[i].startswith("def ") or lines[i].startswith("async def "):
            start = i
            break
    # Find function end
    end = min(len(lines), error_line + 20)
    result = lines[:start] + fix_lines + lines[end:]
    return "".join(result)


@tool(
    "auto_debug",
    "Parse a traceback, generate a fix, apply it, and re-run tests. Retries up to 3 times.",
)
async def auto_debug(
    traceback: str,
    context_files: list | None = None,
    max_attempts: int = 3,
    config=None,
    state=None,
) -> dict:
    """
    Automatically diagnose and fix a Python traceback.

    Args:
        traceback: Full error traceback string.
        context_files: Additional files to include as context.
        max_attempts: Maximum fix attempts (default 3).

    Returns:
        dict with fixed (bool), attempts (int), patch_applied (str|None), message (str).
    """
    from vanta.tools.file_tools import read_file, write_file
    from vanta.tools.shell_tools import run_tests

    parsed = parse_traceback(traceback)
    context_code = ""

    if parsed["file"] and parsed["line"]:
        start = max(1, parsed["line"] - 5)
        end = parsed["line"] + 10
        try:
            context_code = await read_file(
                parsed["file"], start_line=start, end_line=end, config=config, state=state
            )
        except FileNotFoundError:
            pass

    for attempt in range(max_attempts):
        backoff = 2**attempt  # 1s, 2s, 4s
        await asyncio.sleep(backoff)

        try:
            fix_code = await _generate_fix(parsed, context_code, attempt, config)
        except Exception as exc:
            continue

        # Apply fix
        if parsed["file"]:
            try:
                original = await read_file(parsed["file"], config=config, state=state)
                patched = _splice_fix(original, fix_code, parsed["line"])
                await write_file(parsed["file"], patched, config=config, state=state)
            except Exception:
                continue

        # Validate
        test_result = await run_tests(config=config, state=state)
        if test_result["failed"] == 0 and test_result["errors"] == 0:
            return {
                "fixed": True,
                "attempts": attempt + 1,
                "patch_applied": fix_code,
                "message": f"Fixed on attempt {attempt + 1}",
            }

    return {
        "fixed": False,
        "attempts": max_attempts,
        "patch_applied": None,
        "message": (
            f"AutoDebug exhausted {max_attempts} attempts. Manual intervention required."
        ),
    }
