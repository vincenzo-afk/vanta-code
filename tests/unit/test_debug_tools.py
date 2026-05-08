"""Unit tests for AutoDebug traceback parser."""

from vanta.tools.debug_tools import parse_traceback


def test_parse_simple_traceback():
    tb = '''Traceback (most recent call last):
  File "src/main.py", line 42, in main
    result = compute(x)
  File "src/utils.py", line 17, in compute
    return a / b
ZeroDivisionError: division by zero'''

    parsed = parse_traceback(tb)
    assert parsed["error_type"] == "ZeroDivisionError"
    assert "division by zero" in parsed["error_message"]
    assert "src/utils.py" in parsed["file"]
    assert parsed["line"] == 17


def test_parse_import_error():
    tb = '''Traceback (most recent call last):
  File "main.py", line 1, in <module>
    import nonexistent_module
ModuleNotFoundError: No module named 'nonexistent_module'
'''
    parsed = parse_traceback(tb)
    assert parsed["error_type"] == "ModuleNotFoundError"
    assert "nonexistent_module" in parsed["error_message"]


def test_parse_empty_traceback():
    parsed = parse_traceback("")
    assert parsed["error_type"] == "UnknownError"
    assert parsed["file"] is None
    assert parsed["line"] is None


def test_parse_attribute_error():
    tb = '''Traceback (most recent call last):
  File "app.py", line 5, in run
    obj.missing_method()
AttributeError: 'NoneType' object has no attribute 'missing_method'
'''
    parsed = parse_traceback(tb)
    assert parsed["error_type"] == "AttributeError"
    assert parsed["line"] == 5
