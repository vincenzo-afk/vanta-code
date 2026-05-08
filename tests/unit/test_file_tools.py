"""Unit tests for file tools."""

import pytest
from pathlib import Path
from vanta.tools.file_tools import read_file, write_file, create_file, delete_file, patch_file


@pytest.mark.asyncio
async def test_write_and_read(tmp_path, default_config):
    default_config.dry_run = False
    default_config.agent.dry_run = False
    path = str(tmp_path / "test.py")
    await write_file(path, "x = 1\n", config=default_config)
    content = await read_file(path, config=default_config)
    assert content == "x = 1\n"


@pytest.mark.asyncio
async def test_read_file_not_found(default_config):
    with pytest.raises(FileNotFoundError):
        await read_file("/nonexistent/absolutely/missing/file.py", config=default_config)


@pytest.mark.asyncio
async def test_write_file_dry_run(tmp_path, default_config):
    """Dry run must NOT write the file."""
    default_config.dry_run = True
    path = str(tmp_path / "should_not_exist.py")
    result = await write_file(path, "x = 1", config=default_config)
    assert "[DRY RUN]" in result
    assert not (tmp_path / "should_not_exist.py").exists()


@pytest.mark.asyncio
async def test_create_file_fails_if_exists(tmp_path, default_config):
    default_config.dry_run = False
    default_config.agent.dry_run = False
    path = str(tmp_path / "existing.py")
    await write_file(path, "x = 1", config=default_config)
    with pytest.raises(FileExistsError):
        await create_file(path, "y = 2", config=default_config)


@pytest.mark.asyncio
async def test_read_file_line_range(tmp_path, default_config):
    default_config.dry_run = False
    default_config.agent.dry_run = False
    path = str(tmp_path / "lines.py")
    content = "\n".join([f"line{i}" for i in range(1, 11)])
    await write_file(path, content, config=default_config)
    result = await read_file(path, start_line=3, end_line=5, config=default_config)
    assert "line3" in result
    assert "line5" in result
    assert "line1" not in result


@pytest.mark.asyncio
async def test_delete_file_not_found(default_config):
    with pytest.raises(FileNotFoundError):
        await delete_file("/no/such/file.txt", force=True, config=default_config)


@pytest.mark.asyncio
async def test_delete_file_dry_run(tmp_path, default_config):
    default_config.dry_run = True
    path = tmp_path / "deleteme.py"
    path.write_text("x=1")
    result = await delete_file(str(path), force=True, config=default_config)
    assert "[DRY RUN]" in result
    assert path.exists()


@pytest.mark.asyncio
async def test_patch_file(tmp_path, default_config):
    default_config.dry_run = False
    default_config.agent.dry_run = False
    path = tmp_path / "patch_me.py"
    path.write_text("x = 1\ny = 2\nz = 3\n")
    patch = (
        "--- a/patch_me.py\n"
        "+++ b/patch_me.py\n"
        "@@ -1,3 +1,3 @@\n"
        " x = 1\n"
        "-y = 2\n"
        "+y = 99\n"
        " z = 3\n"
    )
    await patch_file(str(path), patch, config=default_config)
    result = path.read_text()
    assert "y = 99" in result
