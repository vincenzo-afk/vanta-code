"""Unit tests for shell tools."""

import pytest
from vanta.tools.shell_tools import run_shell, run_tests


@pytest.mark.asyncio
async def test_run_shell_echo(default_config):
    default_config.dry_run = False
    result = await run_shell("echo hello", config=default_config)
    assert result["stdout"].strip() == "hello"
    assert result["returncode"] == 0


@pytest.mark.asyncio
async def test_run_shell_dry_run(default_config):
    default_config.dry_run = True
    result = await run_shell("rm -rf /", config=default_config)
    assert "[DRY RUN]" in result["stdout"]
    assert result["returncode"] == 0


@pytest.mark.asyncio
async def test_run_shell_nonzero_exit(default_config):
    default_config.dry_run = False
    result = await run_shell("exit 1", config=default_config)
    assert result["returncode"] != 0


@pytest.mark.asyncio
async def test_run_shell_captures_stderr(default_config):
    default_config.dry_run = False
    result = await run_shell("echo error >&2", config=default_config)
    assert result["returncode"] == 0


@pytest.mark.asyncio
async def test_run_shell_timeout(default_config):
    default_config.dry_run = False
    result = await run_shell("sleep 10", timeout=1, config=default_config)
    assert result["returncode"] == -1
    assert "timed out" in result["stderr"].lower()
