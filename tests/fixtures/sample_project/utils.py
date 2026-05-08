"""Sample project fixture: utils.py"""
from typing import Any


def add(a: int, b: int) -> int:
    """Return the sum of two integers."""
    return a + b


def subtract(a: int, b: int) -> int:
    """Return the difference of two integers."""
    return a - b


def multiply(a: int, b: int) -> int:
    """Return the product of two integers."""
    return a * b


def safe_divide(a: float, b: float) -> float | None:
    """Divide a by b. Returns None if b is zero."""
    if b == 0:
        return None
    return a / b


def flatten(nested: list[Any]) -> list[Any]:
    """Flatten a nested list one level deep."""
    result: list[Any] = []
    for item in nested:
        if isinstance(item, list):
            result.extend(item)
        else:
            result.append(item)
    return result
