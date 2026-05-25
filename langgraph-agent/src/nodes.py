# nodes.py — one function per node in the graph
#
# Each node receives the full AgentState and returns a dict of only the fields it changed.
# LangGraph merges those changes back into the state automatically.
#
# Stage 1: fix_node + run_node only

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Explicitly point to the project root .env (two levels up from langgraph-agent/src/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# Reuse the proven fix_code and run_code functions from the original agent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from agent import fix_code, run_code, review_code, write_code_test

from state import AgentState


def fix_node(state: AgentState) -> dict:
    """
    Calls Claude to fix the current code.
    On the first attempt, error is None — Claude reads the code and fixes what it sees.
    On retries (Stage 2), error contains the real traceback so Claude fixes with context.
    """
    print(f"\n[fix_node] Attempt {state['attempts'] + 1} — sending to Claude AI...")

    fixed = fix_code(state["current_code"], state["error"])

    print(f"[fix_node] Done.")

    # Return only the fields this node changed
    return {
        "current_code": fixed,
        "attempts": state["attempts"] + 1,
    }


def run_node(state: AgentState) -> dict:
    """
    Runs the current code in a subprocess.
    Returns success=True + stdout, or success=False + stderr.
    """
    print(f"[run_node] Running fixed code...")

    success, output = run_code(state["current_code"])

    status = "SUCCESS" if success else "FAILED"
    print(f"[run_node] {status}")

    return {
        "success": success,
        "output": output,
        "error": output if not success else None,
    }
    
def review_node(state: AgentState) -> dict:
    # Calls Claude to review the fixed code.
    
    success, output = review_code(state["current_code"])
    
    status = "SUCCESS" if success else "FAILED"
    
    print(f"[review_node] {status}")
    
    return {
        "review": output,
    }

def test_node(state: AgentState) -> dict:
    # Calls Claude to write python test for the reviewed code

    success, output = write_code_test(state["current_code"])

    status = "SUCCESS" if success else "FAILED"

    print(f"[test_node] {status}")

    return {
        "tests": output
    }


def log_node(state: AgentState) -> dict:
    # Saves fixed code, review, and generated tests to a timestamped log file.

    os.makedirs("logs", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join("logs", f"{timestamp}_langgraph.log")

    status = "SUCCESS" if state["success"] else "FAILED"

    with open(log_path, "w") as f:
        f.write("=== LangGraph Script Doctor Log ===\n")
        f.write(f"Date     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Status   : {status}\n")
        f.write(f"Attempts : {state['attempts']}\n")
        f.write("\n--- Fixed Code ---\n")
        f.write(state["current_code"])
        f.write("\n\n--- Review ---\n")
        f.write(state["review"] or "(no review)")
        f.write("\n\n--- Tests ---\n")
        f.write(state["tests"] or "(no tests)")

    print(f"[log_node] Saved → {log_path}")

    return {"log_path": log_path}