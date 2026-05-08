"""Shell tools: run_shell, run_tests."""

from __future__ import annotations

import asyncio

from vanta.tools.registry import tool


@tool("run_shell", "Run a shell command and capture stdout/stderr/returncode.")
async def run_shell(
    command: str,
    cwd: str | None = None,
    timeout: int = 30,
    config=None,
    state=None,
) -> dict:
    """
    Execute a shell command in the project root directory.

    Args:
        command: Shell command string to execute.
        cwd: Working directory (default: config.project_root or '.').
        timeout: Max seconds to wait before killing process (default 30).

    Returns:
        dict with keys: stdout (str), stderr (str), returncode (int).
    """
    if config and config.dry_run:
        return {
            "stdout": f"[DRY RUN] Would run: {command}",
            "stderr": "",
            "returncode": 0,
        }
    work_dir = cwd or (config.project_root if config else ".")
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=work_dir,
    )
    try:
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(), timeout=timeout
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        return {
            "stdout": "",
            "stderr": f"Command timed out after {timeout}s",
            "returncode": -1,
        }
    return {
        "stdout": stdout_bytes.decode("utf-8", errors="replace"),
        "stderr": stderr_bytes.decode("utf-8", errors="replace"),
        "returncode": proc.returncode,
    }


@tool("run_tests", "Run pytest and return results. Triggers AutoDebug on failure.")
async def run_tests(
    path: str = "tests/",
    pattern: str = "test_*.py",
    verbose: bool = False,
    config=None,
    state=None,
) -> dict:
    """
    Run the project's test suite (pytest) and return structured results.

    Args:
        path: Test directory or file (default: 'tests/').
        pattern: File name glob pattern (default: 'test_*.py').
        verbose: Run with -v flag.

    Returns:
        dict with: passed (int), failed (int), errors (int), output (str).
    """
    flags = "-v" if verbose else "-q"
    result = await run_shell(
        f"python -m pytest {path} {flags} --tb=short",
        config=config,
        state=state,
    )
    output = result["stdout"] + result["stderr"]
    # Parse counts from pytest output
    passed = _count(output, "passed")
    failed = _count(output, "failed")
    errors = _count(output, "error")
    return {
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "output": output,
        "returncode": result["returncode"],
    }


def _count(text: str, keyword: str) -> int:
    """Count occurrences of '<n> keyword' in pytest output."""
    import re

    matches = re.findall(rf"(\d+)\s+{keyword}", text)
    return sum(int(m) for m in matches)
