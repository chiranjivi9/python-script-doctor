# Agent Specification

This document defines the expected behavior of each function in `src/agent.py`.
Tests in `tests/test_agent.py` verify every spec listed here.

---

## `fix_code(code, error=None) -> str`

**Purpose:** Send a Python script to Claude and return the fixed version.

| # | Spec |
|---|---|
| 1 | Returns a string |
| 2 | Returned string does not start with markdown fences (` ``` `) |
| 3 | When `error` is None, prompt asks Claude to fix bugs from reading the code |
| 4 | When `error` is provided, the error text is included in the prompt so Claude fixes based on the real traceback |

---

## `run_code(code) -> tuple[bool, str]`

**Purpose:** Execute a Python code string in a subprocess and return the result.

| # | Spec |
|---|---|
| 5 | Returns `(True, stdout)` when the script exits with code 0 |
| 6 | Returns `(False, stderr)` when the script has a syntax error |
| 7 | Returns `(False, stderr)` when the script raises a runtime error |
| 8 | Captured output contains the actual printed text from the script |
| 9 | Temp file `_doctor_temp.py` is deleted after execution, whether it succeeds or fails |

---

## `review_code(code) -> tuple[bool, str]`

**Purpose:** Send fixed code to Claude for a quality review.

| # | Spec |
|---|---|
| 17 | Returns `(True, review_text)` on success |
| 18 | Returns `(False, error_message)` on failure |
| 19 | Review text is a non-empty string when successful |

---

## `write_code_test(code) -> tuple[bool, str]`

**Purpose:** Ask Claude to generate pytest unit tests for the fixed code.

| # | Spec |
|---|---|
| 20 | Returns `(True, test_code)` on success |
| 21 | Returns `(False, error_message)` on failure |
| 22 | Generated tests are a non-empty string when successful |

---

## `write_log(script_name, status, fixed_code, output, attempts, review, tests) -> str`

**Purpose:** Save a structured log entry to a timestamped file in `logs/`.

| # | Spec |
|---|---|
| 10 | Creates the `logs/` directory if it does not exist |
| 11 | Returns the path to the created log file |
| 12 | Log file contains the script name |
| 13 | Log file contains the status (`SUCCESS` or `FAILED`) |
| 14 | Log file contains the attempt count in the format `N/MAX_RETRIES` |
| 15 | Log file contains the fixed code |
| 16 | Log file contains the output (or `(no output)` if empty) |
| 23 | Log file contains the review section (or `(no review)` if empty) |
| 24 | Log file contains the tests section (or `(no tests)` if empty) |
