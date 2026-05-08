"""Unit tests for token budget management."""

from vanta.llm.token_budget import count_tokens, trim_messages_to_budget


def test_count_tokens_basic():
    assert count_tokens("hello") >= 1
    assert count_tokens("") == 1  # min 1
    assert count_tokens("a" * 400) == 100


def test_trim_empty():
    assert trim_messages_to_budget([], 1000) == []


def test_trim_no_trimming_needed():
    msgs = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello"},
    ]
    result = trim_messages_to_budget(msgs, 10000)
    assert result == msgs


def test_trim_removes_middle_messages():
    msgs = [
        {"role": "system", "content": "System prompt"},
        {"role": "user", "content": "A" * 400},
        {"role": "assistant", "content": "B" * 400},
        {"role": "user", "content": "C" * 400},
        {"role": "user", "content": "Final question"},
    ]
    budget = 200  # Very tight budget
    result = trim_messages_to_budget(msgs, budget)
    # System and last message must always be present
    assert result[0]["role"] == "system"
    assert result[-1]["content"] == "Final question"


def test_trim_preserves_two_messages():
    msgs = [
        {"role": "system", "content": "System"},
        {"role": "user", "content": "Question"},
    ]
    result = trim_messages_to_budget(msgs, 1)
    assert len(result) == 2
