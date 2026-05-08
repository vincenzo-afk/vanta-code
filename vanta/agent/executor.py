"""Executor — dispatches tool calls from plan steps."""

from __future__ import annotations

import asyncio
import json

from vanta.models import PlanStep, SessionState, ToolCall, ToolResult
from vanta.tools.registry import dispatch


class Executor:
    """
    Takes a plan (list of PlanStep) and executes each step by
    dispatching the appropriate tool call.

    Steps with no unresolved dependencies are run concurrently.
    """

    def __init__(self, config=None):
        self.config = config

    async def execute_plan(
        self, steps: list[PlanStep], state: SessionState
    ) -> list[ToolResult]:
        """Execute all steps respecting dependency ordering."""
        results: list[ToolResult] = []
        completed_ids: set[str] = set()

        remaining = list(steps)
        while remaining:
            # Find steps whose dependencies are all satisfied
            ready = [
                s for s in remaining
                if all(dep in completed_ids for dep in s.depends_on)
            ]
            if not ready:
                # Circular dependency or all blocked — run first step anyway
                ready = [remaining[0]]

            # Execute ready steps (concurrently if parallelizable)
            parallel = [s for s in ready if s.can_parallelize]
            sequential = [s for s in ready if not s.can_parallelize]

            if parallel:
                lock = asyncio.Lock()
                tasks = [self._run_step(s, state, lock) for s in parallel]
                batch = await asyncio.gather(*tasks, return_exceptions=True)
                for step, result in zip(parallel, batch):
                    if isinstance(result, Exception):
                        result = ToolResult(
                            success=False, output="", error=str(result),
                            tool_call_id=step.step_id
                        )
                    results.append(result)
                    state.results.append(result)
                    completed_ids.add(step.step_id)
                    step.status = "done" if result.success else "failed"

            for step in sequential:
                result = await self._run_step(step, state)
                results.append(result)
                state.results.append(result)
                completed_ids.add(step.step_id)
                step.status = "done" if result.success else "failed"

            for s in ready:
                remaining.remove(s)

        return results

    async def _run_step(
        self, step: PlanStep, state: SessionState, lock: asyncio.Lock | None = None
    ) -> ToolResult:
        """Execute a single plan step."""
        step.status = "running"
        call = ToolCall(tool=step.tool, params=step.params, step_id=step.step_id)
        result = await dispatch(call, config=self.config, state=state)
        if lock:
            async with lock:
                state.results.append(result)
        return result

    async def dispatch_raw(self, tool_name: str, params: dict, state: SessionState) -> ToolResult:
        """Dispatch a single tool call by name and params directly."""
        call = ToolCall(tool=tool_name, params=params)
        return await dispatch(call, config=self.config, state=state)
