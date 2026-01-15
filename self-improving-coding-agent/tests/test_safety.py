from src.utils.safety import Safety


def test_safety_allows_simple_code():
    ok, reason = Safety.check("print('hello')")
    assert ok is True
    assert reason == "Safe"


def test_safety_blocks_blacklisted_import():
    ok, reason = Safety.check("import os\nprint(os.getcwd())")
    assert ok is False
    assert "Importing" in reason


def test_safety_blocks_blacklisted_call():
    ok, reason = Safety.check("eval('1+1')")
    assert ok is False
    assert "Calling" in reason

