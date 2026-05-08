"""Unit tests for LLM router complexity scoring."""

from vanta.llm.router import score_complexity


def test_low_complexity():
    assert score_complexity("what is a decorator") < 0.5
    assert score_complexity("list all files") < 0.5
    assert score_complexity("explain asyncio") < 0.5
    assert score_complexity("summarize this function") < 0.5


def test_medium_complexity():
    score = score_complexity("implement a binary search function")
    assert 0.3 <= score <= 0.7
    score2 = score_complexity("fix bug in the login handler")
    assert 0.3 <= score2 <= 0.7


def test_high_complexity():
    assert score_complexity("refactor the entire codebase") >= 0.8
    assert score_complexity("architect a microservices migration") >= 0.8
    assert score_complexity("security audit of the authentication module") >= 0.8


def test_unknown_returns_low():
    score = score_complexity("do the thing")
    assert score == 0.2
