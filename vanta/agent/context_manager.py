"""Context manager — sliding window context + memory injection."""

from __future__ import annotations

from vanta.llm.token_budget import count_tokens, trim_messages_to_budget
from vanta.agent.prompt_builder import build_system_prompt
from vanta.models import AgentMessage, MessageRole, SessionState


class ContextManager:
    """
    Manages the conversation context window for the agent.

    Responsibilities:
    - Assembles system prompt (base + project config + memory chunks)
    - Maintains a sliding window over session history
    - Injects relevant memory chunks as context
    """

    def __init__(self, config=None):
        self.config = config
        self.budget = config.llm.context_budget if config else 6000

    async def build_messages(
        self,
        state: SessionState,
        task: str,
        memory_results: list[dict] | None = None,
    ) -> list[dict]:
        """
        Build the full message list to send to the LLM.

        Returns:
            List of {"role": str, "content": str} dicts.
        """
        # 1. System prompt
        system_content = build_system_prompt(self.config)

        # 2. Inject memory context if available
        if memory_results:
            memory_ctx = "\n\n## Relevant Code Context\n"
            for chunk in memory_results[:5]:
                memory_ctx += (
                    f"\n### {chunk.get('file', 'unknown')} "
                    f"(lines {chunk.get('start_line', '?')}-{chunk.get('end_line', '?')})\n"
                    f"```\n{chunk.get('content', '')[:500]}\n```\n"
                )
            system_content += memory_ctx

        messages: list[dict] = [{"role": "system", "content": system_content}]

        # 3. Add session history
        for msg in state.history:
            messages.append({"role": msg.role.value, "content": msg.content})

        # 4. Add current task as user message (if not already last)
        if not state.history or state.history[-1].content != task:
            messages.append({"role": "user", "content": task})

        # 5. Trim to budget
        return trim_messages_to_budget(messages, self.budget)

    def add_user_message(self, state: SessionState, content: str) -> None:
        state.history.append(AgentMessage(role=MessageRole.user, content=content))

    def add_assistant_message(self, state: SessionState, content: str) -> None:
        state.history.append(AgentMessage(role=MessageRole.assistant, content=content))

    def add_tool_result(self, state: SessionState, content: str) -> None:
        state.history.append(AgentMessage(role=MessageRole.tool, content=content))
