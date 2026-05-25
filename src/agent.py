# agent.py — CLI entry point for the Python Script Doctor
# Run: python src/agent.py samples/broken_example.py

import anthropic
import subprocess
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Reads ANTHROPIC_API_KEY from the .env file and puts it into os.environ
load_dotenv()

# How many times the agent will try to fix the code before giving up
MAX_RETRIES = 3


def fix_code(code: str, error: str = None) -> str:
    """
    Sends code to Claude and returns the fixed version.
    On the first attempt, error is None — Claude fixes syntax/logic bugs.
    On retry attempts, error contains the actual traceback from running the code,
    so Claude can fix based on what actually went wrong at runtime.
    """
    client = anthropic.Anthropic()  # Reads API key from os.environ automatically

    if error:
        # Retry prompt: include the real error so Claude has context
        content = (
            "You are a Python expert. This script ran and produced an error.\n"
            "Fix the code so it runs without errors.\n"
            "Return ONLY the fixed Python code. No explanations, no markdown, no code fences.\n\n"
            f"CODE:\n{code}\n\n"
            f"ERROR:\n{error}"
        )
    else:
        # First attempt: Claude reads the code and fixes what it can see
        content = (
            "You are a Python expert. Fix all bugs and syntax errors in this script.\n"
            "Return ONLY the fixed Python code. No explanations, no markdown, no code fences.\n\n"
            f"BROKEN CODE:\n{code}"
        )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": content}],
    )

    fixed = response.content[0].text.strip()

    # Claude sometimes wraps the output in ```python ... ``` even when told not to.
    # Strip the fences so we get raw, executable Python.
    if fixed.startswith("```"):
        lines = fixed.splitlines()
        fixed = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])

    return fixed

def review_code(code: str) -> str:
    client = anthropic.Anthropic()
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[
                {
                    "role": "user", 
                    "content": f"Review this python code for quality and best practices. Be concise.\n\n{code}"
                }
            ]
        )
        
        return (True, response.content[0].text)
    except:
        return (False, f"Script review_code failed")
         

def write_code_test(code: str) -> str:
    client = anthropic.Anthropic()
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[
                {
                    "role": "user", 
                    "content": f"Write unit test for this python code for quality and best practices. Be concise.\n\n{code}"
                }
            ]
        )
        
        return (True, response.content[0].text)
    except:
        return (False, f"write_code_test faile")

def run_code(code: str) -> tuple[bool, str]:
    """
    Writes code to a temporary file, runs it as a subprocess, and returns
    (success, output). Using a subprocess isolates the executed code from
    this script — if it crashes, our agent keeps running.
    """
    temp_file = "_doctor_temp.py"

    with open(temp_file, "w") as f:
        f.write(code)

    try:
        result = subprocess.run(
            [sys.executable, temp_file],  # sys.executable = the current Python interpreter
            capture_output=True,          # capture stdout and stderr separately
            text=True,                    # return strings, not bytes
            timeout=30,                   # kill the process if it runs longer than 30s
        )
        if result.returncode == 0:
            return True, result.stdout    # exit code 0 = success
        else:
            return False, result.stderr   # non-zero = error; return the traceback
    except subprocess.TimeoutExpired:
        return False, "Script timed out after 30 seconds."
    finally:
        # Always clean up the temp file, even if an exception was raised
        if os.path.exists(temp_file):
            os.remove(temp_file)


def write_log(script_name: str, status: str, fixed_code: str, output: str, attempts: int, review: str = "", tests: str = "") -> str:
    """
    Saves the result of a run to a timestamped log file in the logs/ folder.
    This is the MLOps part — tracking what ran, when, and what happened.
    """
    os.makedirs("logs", exist_ok=True)  # create logs/ if it doesn't exist yet

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join("logs", f"{timestamp}_{script_name}.log")

    with open(log_path, "w") as f:
        f.write("=== Python Script Doctor Log ===\n")
        f.write(f"Date     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Script   : {script_name}\n")
        f.write(f"Status   : {status}\n")
        f.write(f"Attempts : {attempts}/{MAX_RETRIES}\n")
        f.write("\n--- Fixed Code ---\n")
        f.write(fixed_code)
        f.write("\n\n--- Output ---\n")
        f.write(output if output.strip() else "(no output)")
        f.write("\n\n--- Review ---\n")
        f.write(review if review.strip() else "(no review)")
        f.write("\n\n--- Tests ---\n")
        f.write(tests if tests.strip() else "(no tests)")

    return log_path


def run_doctor(script_path: str):
    """
    Orchestrates the full agent loop:
    1. Read the broken script
    2. Ask Claude to fix it
    3. Run the fixed code
    4. If it fails, feed the error back to Claude and retry
    5. Log the final result
    """
    if not os.path.exists(script_path):
        print(f"Error: file not found: {script_path}")
        sys.exit(1)

    # Extract just the filename (without extension) for use in the log
    script_name = os.path.splitext(os.path.basename(script_path))[0]

    with open(script_path, "r") as f:
        original_code = f.read()

    print(f"\nPython Script Doctor")
    print(f"{'=' * 40}")
    print(f"Script : {script_path}")
    print(f"Max retries : {MAX_RETRIES}\n")

    code = original_code
    error = None   # no error on the first attempt
    success = False
    output = ""

    # The agentic loop — keeps trying until success or max retries
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"--- Attempt {attempt}/{MAX_RETRIES} ---")

        print("  Fix    Sending to Claude AI...")
        code = fix_code(code, error)  # error is None on attempt 1, real traceback on retries
        print("         Done.")

        print("  Run    Executing fixed code...")
        success, output = run_code(code)

        if success:
            print(f"  Result SUCCESS\n")
            break
        else:
            error = output  # pass the real error to Claude on the next attempt
            if attempt < MAX_RETRIES:
                print(f"  Result FAILED — sending error back to Claude...\n")
            else:
                print(f"  Result FAILED — max retries reached.\n")

    status = "SUCCESS" if success else "FAILED"

    review = ""
    tests = ""
    if success:
        print("  Review  Sending to Claude AI...")
        _, review = review_code(code)
        print("          Done.")

        print("  Tests   Generating unit tests...")
        _, tests = write_code_test(code)
        print("          Done.")

    print("Logging result...")
    log_path = write_log(script_name, status, code, output, attempt, review, tests)
    print(f"Saved  : {log_path}\n")

    print(f"{'=' * 40}")
    print(f"Result   : {status} (attempt {attempt}/{MAX_RETRIES})")
    print(f"Output   :\n{output if output.strip() else '(no output)'}")
    print(f"Log      : {log_path}")


if __name__ == "__main__":
    # sys.argv is the list of command-line arguments
    # sys.argv[0] = "src/agent.py", sys.argv[1] = the script path you pass in
    if len(sys.argv) != 2:
        print("Usage: python src/agent.py <path_to_script.py>")
        sys.exit(1)

    run_doctor(sys.argv[1])
