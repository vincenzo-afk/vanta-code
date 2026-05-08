"""Sample project fixture: main.py"""


def main() -> None:
    """Entry point for the sample project."""
    result = add(2, 3)
    print(f"2 + 3 = {result}")
    greet("Vanta")


def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def greet(name: str) -> str:
    """Return a greeting string."""
    msg = f"Hello, {name}!"
    print(msg)
    return msg


if __name__ == "__main__":
    main()
