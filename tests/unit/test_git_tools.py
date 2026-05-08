"""Unit tests for git tools."""
import pytest
from unittest.mock import patch, MagicMock

from vanta.tools.git_tools import git_status, git_diff, git_commit

@pytest.mark.asyncio
@patch("vanta.tools.git_tools.Repo")
async def test_git_status(mock_repo_class):
    mock_repo = mock_repo_class.return_value
    mock_repo.git.status.return_value = "On branch main"
    
    result = await git_status()
    assert "On branch main" in result

@pytest.mark.asyncio
@patch("vanta.tools.git_tools.Repo")
async def test_git_diff(mock_repo_class):
    mock_repo = mock_repo_class.return_value
    mock_repo.git.diff.return_value = "diff --git"
    
    result = await git_diff(staged=False)
    assert "diff --git" in result

@pytest.mark.asyncio
@patch("vanta.tools.git_tools.Repo")
async def test_git_commit(mock_repo_class):
    mock_repo = mock_repo_class.return_value
    mock_repo.index.commit.return_value.hexsha = "12345678"
    
    result = await git_commit(message="Initial commit", files=["main.py"])
    assert "Committed 12345678: Initial commit" in result
