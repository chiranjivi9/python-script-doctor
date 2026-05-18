# tests/test_agent.py
# Verifies every spec in SPEC.md. Run with: venv/bin/pytest tests/ -v

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Add src/ to the path so we can import agent.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from agent import fix_code, run_code, write_log, MAX_RETRIES


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_mock_response(text: str):
    """Build a fake Anthropic API response returning the given text."""
    mock = MagicMock()
    mock.content[0].text = text
    return mock


# ---------------------------------------------------------------------------
# fix_code — specs 1-4
# ---------------------------------------------------------------------------

def test_fix_code_returns_a_string():
    # Spec 1: returns a string
    with patch("anthropic.Anthropic") as MockClient:
        MockClient.return_value.messages.create.return_value = make_mock_response("print('hello')")
        result = fix_code("print 'hello'")
    assert isinstance(result, str)


def test_fix_code_strips_markdown_fences():
    # Spec 2: no markdown fences in output
    fenced = "```python\nprint('hello')\n```"
    with patch("anthropic.Anthropic") as MockClient:
        MockClient.return_value.messages.create.return_value = make_mock_response(fenced)
        result = fix_code("print 'hello'")
    assert not result.startswith("```")
    assert "print('hello')" in result


def test_fix_code_first_attempt_prompt_has_no_error():
    # Spec 3: first-attempt prompt does not include an error section
    with patch("anthropic.Anthropic") as MockClient:
        instance = MockClient.return_value
        instance.messages.create.return_value = make_mock_response("print('ok')")
        fix_code("broken code", error=None)
        prompt = instance.messages.create.call_args.kwargs["messages"][0]["content"]
    assert "ERROR" not in prompt


def test_fix_code_retry_prompt_includes_error():
    # Spec 4: retry prompt contains the real error traceback
    with patch("anthropic.Anthropic") as MockClient:
        instance = MockClient.return_value
        instance.messages.create.return_value = make_mock_response("print('fixed')")
        fix_code("some code", error="NameError: name 'x' is not defined")
        prompt = instance.messages.create.call_args.kwargs["messages"][0]["content"]
    assert "NameError" in prompt


# ---------------------------------------------------------------------------
# run_code — specs 5-9
# ---------------------------------------------------------------------------

def test_run_code_returns_true_on_success(tmp_path, monkeypatch):
    # Spec 5: (True, stdout) when script exits 0
    monkeypatch.chdir(tmp_path)
    success, output = run_code("print('hello')")
    assert success is True


def test_run_code_output_contains_printed_text(tmp_path, monkeypatch):
    # Spec 8: captured output matches what the script printed
    monkeypatch.chdir(tmp_path)
    success, output = run_code("print('expected text')")
    assert "expected text" in output


def test_run_code_returns_false_on_syntax_error(tmp_path, monkeypatch):
    # Spec 6: (False, stderr) on syntax error
    monkeypatch.chdir(tmp_path)
    success, output = run_code("def broken(")
    assert success is False
    assert output  # stderr should not be empty


def test_run_code_returns_false_on_runtime_error(tmp_path, monkeypatch):
    # Spec 7: (False, stderr) on runtime error
    monkeypatch.chdir(tmp_path)
    success, output = run_code("x = 1 / 0")
    assert success is False
    assert "ZeroDivisionError" in output


def test_run_code_cleans_up_temp_file(tmp_path, monkeypatch):
    # Spec 9: temp file is deleted after run
    monkeypatch.chdir(tmp_path)
    run_code("print('hello')")
    assert not os.path.exists(tmp_path / "_doctor_temp.py")


# ---------------------------------------------------------------------------
# write_log — specs 10-16
# ---------------------------------------------------------------------------

def test_write_log_creates_logs_directory(tmp_path, monkeypatch):
    # Spec 10: creates logs/ if it doesn't exist
    monkeypatch.chdir(tmp_path)
    write_log("myscript", "SUCCESS", "print('hi')", "hi\n", 1)
    assert os.path.isdir(tmp_path / "logs")


def test_write_log_returns_file_path(tmp_path, monkeypatch):
    # Spec 11: returns the path to the log file
    monkeypatch.chdir(tmp_path)
    log_path = write_log("myscript", "SUCCESS", "print('hi')", "hi\n", 1)
    assert os.path.exists(log_path)


def test_write_log_contains_script_name(tmp_path, monkeypatch):
    # Spec 12
    monkeypatch.chdir(tmp_path)
    log_path = write_log("myscript", "SUCCESS", "code", "output", 1)
    assert "myscript" in open(log_path).read()


def test_write_log_contains_status(tmp_path, monkeypatch):
    # Spec 13
    monkeypatch.chdir(tmp_path)
    log_path = write_log("myscript", "FAILED", "code", "error", 2)
    assert "FAILED" in open(log_path).read()


def test_write_log_contains_attempt_count(tmp_path, monkeypatch):
    # Spec 14: format is N/MAX_RETRIES
    monkeypatch.chdir(tmp_path)
    log_path = write_log("myscript", "SUCCESS", "code", "output", 2)
    assert f"2/{MAX_RETRIES}" in open(log_path).read()


def test_write_log_contains_fixed_code(tmp_path, monkeypatch):
    # Spec 15
    monkeypatch.chdir(tmp_path)
    log_path = write_log("myscript", "SUCCESS", "print('fixed')", "fixed\n", 1)
    assert "print('fixed')" in open(log_path).read()


def test_write_log_shows_no_output_when_empty(tmp_path, monkeypatch):
    # Spec 16: empty output is written as "(no output)"
    monkeypatch.chdir(tmp_path)
    log_path = write_log("myscript", "SUCCESS", "pass", "", 1)
    assert "(no output)" in open(log_path).read()
