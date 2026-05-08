"""Token counting and context window budget management."""

from __future__ import annotations


def count_tokens(text: str) -> int:
    """
    Approximate token count using the ~4 chars/token heuristic for English/code.
    """
    return max(1, len(text) // 4)


def trim_messages_to_budget(messages: list[dict], budget: int) -> list[dict]:
    """
    Trim conversation history to fit within the token budget.

    Strategy:
    - Always keeps: system message (index 0) and the last user message.
    - Removes oldest middle messages first until total tokens <= budget.

    Args:
        messages: List of {"role": ..., "content": ...} dicts.
        budget: Maximum allowed total tokens.

    Returns:
        Trimmed messages list.
    """
    if not messages:
        return messages

    total = sum(count_tokens(m.get("content", "")) for m in messages)
    if total <= budget:
        return messages

    if len(messages) <= 2:
        # Can't trim — only system + current user
        return messages

    result = [messages[0]]  # Always keep system prompt
    tail = [messages[-1]]   # Always keep current user message
    middle = list(messages[1:-1])

    while middle and total > budget:
        removed = middle.pop(0)
        total -= count_tokens(removed.get("content", ""))

    return result + middle + tail


def estimate_cost(prompt_tokens: int, completion_tokens: int, model: str = "groq") -> float:
    """
    Rough cost estimate in USD. Prices as of 2024 — update as needed.
    """
    rates: dict[str, tuple[float, float]] = {
        "groq": (0.0, 0.0),                   # Free tier

    }
    input_rate, output_rate = rates.get(model, (0.002, 0.006))
    return (prompt_tokens / 1000) * input_rate + (completion_tokens / 1000) * output_rate
