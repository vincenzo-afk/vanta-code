"""Main agent loop: Plan → Act → Observe → Reflect."""

from __future__ import annotations

import asyncio

from rich.console import Console

from vanta.agent.context_manager import ContextManager
from vanta.agent.executor import Executor
from vanta.agent.planner import Planner
from vanta.agent.reflector import Reflector
from vanta.models import SessionState
from vanta.utils.logger import get_logger

console = Console()
log = get_logger("vanta.agent")


class AgentLoop:
    """
    The core Plan → Act → Observe → Reflect loop.

    Each call to `run_task()` executes one full autonomous task cycle.
    """

    def __init__(self, config=None, state: SessionState | None = None):
        self.config = config
        self.state = state or SessionState()
        self.planner = Planner(config=config)
        self.executor = Executor(config=config)
        self.reflector = Reflector(config=config)
        self.ctx_manager = ContextManager(config=config)
        self.max_steps = config.agent.max_steps if config else 50
        self._step_count = 0

    async def run_task(self, task: str) -> str:
        """
        Run the full agent loop for the given task.

        Returns:
            Summary string of what was accomplished.
        """
        self.state.task = task
        self.state.is_complete = False
        self._step_count = 0

        log.info(f"Starting task: {task[:80]}...")
        self.ctx_manager.add_user_message(self.state, task)

        # Optional: inject memory context
        memory_results: list[dict] = []
        if self.config and self.config.memory.enabled:
            try:
                from vanta.memory.retriever import Retriever
                retriever = Retriever(config=self.config)
                memory_results = await retriever.query(task, top_k=3)
            except Exception:
                pass

        # Iterative loop
        current_task = task
        iteration = 0
        max_iterations = 5

        while not self.state.is_complete and iteration < max_iterations:
            iteration += 1
            log.info(f"Iteration {iteration}: planning...")

            # 1. Plan
            steps = await self.planner.plan(current_task)
            self.state.current_plan = steps
            log.info(f"Plan: {len(steps)} step(s)")

            if self._step_count + len(steps) > self.max_steps:
                log.warning("Max steps reached — stopping.")
                break

            # 2. Act
            results = await self.executor.execute_plan(steps, self.state)
            self._step_count += len(steps)

            # 3. Observe — add results to context
            for result in results:
                result_msg = (
                    f"Tool result: {'SUCCESS' if result.success else 'ERROR'}\n"
                    f"{result.output or result.error or ''}"
                )
                self.ctx_manager.add_tool_result(self.state, result_msg[:500])

            # 4. Reflect
            reflection = await self.reflector.reflect(task, results, self.state)
            summary = reflection.get("summary", "")
            self.ctx_manager.add_assistant_message(self.state, summary)

            if reflection["complete"]:
                self.state.is_complete = True
                log.info("Task complete.")
                break

            # Not complete — plan next steps
            next_steps = reflection.get("next_steps", [])
            if next_steps:
                current_task = "\n".join(
                    s.get("description", "") for s in next_steps
                )
            else:
                # No clear next steps — stop
                break

        return self._final_summary()

    def _final_summary(self) -> str:
        """Build a human-readable summary of what happened."""
        total = len(self.state.results)
        success = sum(1 for r in self.state.results if r.success)
        failed = total - success
        parts = [
            f"Task: {self.state.task[:60]}",
            f"Steps executed: {total} ({success} succeeded, {failed} failed)",
        ]
        if self.state.results:
            last = self.state.results[-1]
            parts.append(f"Last output: {(last.output or last.error or '')[:200]}")
        return "\n".join(parts)


async def run_plain_mode(config=None) -> None:
    """
    Plain-text interactive mode (no TUI). Used as fallback or --plain flag.
    """
    console.print(
        "[bold cyan]Vanta Code[/bold cyan] — plain mode. Type your task, or 'exit' to quit.\n"
    )
    state = SessionState()
    loop = AgentLoop(config=config, state=state)

    while True:
        try:
            task = input("❯ ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye.[/dim]")
            break
        if not task:
            continue
        if task.lower() in ("exit", "quit", "/exit", "/quit"):
            console.print("[dim]Goodbye.[/dim]")
            break

        try:
            with console.status("[cyan]Working...[/cyan]", spinner="dots"):
                result = await loop.run_task(task)
            console.print(f"\n[green]{result}[/green]\n")
        except Exception as exc:
            console.print(f"[red]Error: {exc}[/red]")
