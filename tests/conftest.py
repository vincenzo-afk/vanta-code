"""Shared test fixtures and configuration."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from vanta.models import SessionState, VantaConfig


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a minimal fake project for testing."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("def main():\n    print('hello')\n")
    (src / "utils.py").write_text("def add(a, b):\n    return a + b\n")
    return tmp_path


@pytest.fixture
def default_config(tmp_project: Path) -> VantaConfig:
    """Return a VantaConfig with dry_run=True for safe testing."""
    return VantaConfig(
        project_root=str(tmp_project),
        dry_run=True,
        agent=__import__("vanta.models", fromlist=["AgentConfig"]).AgentConfig(dry_run=True),
    )


@pytest.fixture
def session_state() -> SessionState:
    return SessionState()


@pytest.fixture
def mock_llm_response():
    """Mock route_query to return a canned response."""
    with patch("vanta.llm.router.route_query", new_callable=AsyncMock) as mock:
        mock.return_value = "Mocked LLM response"
        yield mock


@pytest.fixture
def mock_groq():
    """Mock Groq client to avoid real API calls."""
    with patch("vanta.llm.groq_client.GroqClient.complete", new_callable=AsyncMock) as mock:
        mock.return_value = '{"tool": "read_file", "params": {"path": "src/main.py"}}'
        yield mock
