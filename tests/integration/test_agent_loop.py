"""Integration test: full agent loop (mocked LLM)."""

import pytest
from unittest.mock import AsyncMock, patch

from vanta.agent.loop import AgentLoop
from vanta.models import SessionState


@pytest.mark.asyncio
async def test_agent_loop_completes(tmp_project, default_config):
    """Agent loop runs without crashing (mocked LLM)."""
    default_config.dry_run = True

    reflection_response = '{"complete": true, "next_steps": [], "summary": "Done."}'

    with patch("vanta.llm.router.route_query", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = (
            '[{"description": "Echo hello", "tool": "run_shell", '
            '"params": {"command": "echo hello"}, "depends_on": [], '
            '"estimated_complexity": "low", "can_parallelize": false}]'
        )

        state = SessionState()
        loop = AgentLoop(config=default_config, state=state)

        # Override reflector to say complete immediately
        loop.reflector.reflect = AsyncMock(
            return_value={"complete": True, "next_steps": [], "summary": "Done."}
        )

        result = await loop.run_task("Say hello")
        assert isinstance(result, str)
        assert state.is_complete


@pytest.mark.asyncio
async def test_agent_loop_handles_tool_error(tmp_project, default_config):
    """Agent loop handles tool errors gracefully."""
    default_config.dry_run = False

    with patch("vanta.llm.router.route_query", new_callable=AsyncMock) as mock_llm:
        # Return a plan with an invalid tool
        mock_llm.return_value = (
            '[{"description": "Bad tool", "tool": "nonexistent_tool", '
            '"params": {}, "depends_on": [], "estimated_complexity": "low", '
            '"can_parallelize": false}]'
        )
        state = SessionState()
        loop = AgentLoop(config=default_config, state=state)
        loop.reflector.reflect = AsyncMock(
            return_value={"complete": True, "next_steps": [], "summary": "Done."}
        )

        result = await loop.run_task("Do something bad")
        # Should not raise — errors are captured in ToolResult
        assert "Steps executed" in result
