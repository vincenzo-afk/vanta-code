"""LLM router: complexity scoring + model selection."""

from __future__ import annotations

COMPLEXITY_SIGNALS: dict[str, list[str]] = {
    "high": [
        "refactor",
        "architect",
        "design",
        "entire codebase",
        "migrate",
        "optimize performance",
        "security audit",
        "microservices",
    ],
    "medium": [
        "implement",
        "add feature",
        "fix bug",
        "write tests",
        "debug",
        "integrate",
        "build",
    ],
    "low": [
        "explain",
        "summarize",
        "list",
        "what is",
        "rename",
        "format",
        "add comment",
        "show",
        "print",
    ],
}


def score_complexity(task: str) -> float:
    """
    Score a task string on a complexity scale of 0.0 (trivial) to 1.0 (complex).
    """
    task_lower = task.lower()
    for word in COMPLEXITY_SIGNALS["high"]:
        if word in task_lower:
            return 0.9
    for word in COMPLEXITY_SIGNALS["medium"]:
        if word in task_lower:
            return 0.5
    return 0.2


async def route_query(
    task: str,
    complexity: str | None = None,
    config=None,
    system: str = "",
) -> str:
    """
    Route a task to the appropriate LLM based on complexity.

    Args:
        task: The task / prompt text.
        complexity: Explicit hint: 'low' | 'medium' | 'high'. If None, auto-scored.
        config: VantaConfig instance.
        system: Optional system prompt.

    Returns:
        LLM response string.
    """
    threshold = config.llm.complexity_threshold if config else 0.7
    score = score_complexity(task) if complexity is None else (
        0.9 if complexity == "high" else 0.5 if complexity == "medium" else 0.2
    )

    use_gemini = score >= threshold

    # Fallback: if primary key missing, try the other
    if use_gemini:
        try:
            from vanta.llm.gemini_client import GeminiClient
            client = GeminiClient(config=config)
            return await client.complete(task, system=system)
        except (ValueError, Exception):
            pass
        try:
            from vanta.llm.groq_client import GroqClient
            client = GroqClient(config=config)  # type: ignore[assignment]
            return await client.complete(task, system=system)
        except Exception as exc:
            raise RuntimeError(f"All LLM providers failed: {exc}") from exc
    else:
        try:
            from vanta.llm.groq_client import GroqClient
            client = GroqClient(config=config)
            return await client.complete(task, system=system)
        except (ValueError, Exception):
            pass
        try:
            from vanta.llm.gemini_client import GeminiClient
            client = GeminiClient(config=config)  # type: ignore[assignment]
            return await client.complete(task, system=system)
        except Exception as exc:
            raise RuntimeError(f"All LLM providers failed: {exc}") from exc
