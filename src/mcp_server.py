# mcp_server.py — exposes the Script Doctor as MCP tools Claude can call from chat
# This file uses the same fix_code / run_code / write_log logic as agent.py,
# but wrapped in MCP tools instead of a CLI interface.

import os
import sys
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# MCP servers can be launched from any working directory by Claude Desktop.
# We pin the working directory to the project root so all relative paths
# (logs/, .env, samples/) resolve correctly regardless of where Claude starts us.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# Add src/ to the import path so we can import from agent.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent import fix_code, run_code, write_log, MAX_RETRIES

# FastMCP creates the MCP server. The string "script-doctor" is the server name
# Claude Desktop uses to identify this server.
mcp = FastMCP("script-doctor")


@mcp.tool()
def fix_and_run(script_path: str) -> str:
    """
    Fix a broken Python script using Claude AI, run it, and save a log file.
    Retries up to MAX_RETRIES times, feeding each error back to Claude.
    Returns the final status, output, and log file path.
    """
    if not os.path.exists(script_path):
        return f"Error: file not found: {script_path}"

    script_name = os.path.splitext(os.path.basename(script_path))[0]

    with open(script_path, "r") as f:
        original_code = f.read()

    code = original_code
    error = None   # no error on first attempt
    success = False
    output = ""

    # Same agentic retry loop as agent.py — error feeds back into fix_code on each retry
    for attempt in range(1, MAX_RETRIES + 1):
        code = fix_code(code, error)
        success, output = run_code(code)

        if success:
            break
        error = output  # real traceback becomes input to the next fix attempt

    status = "SUCCESS" if success else "FAILED"
    log_path = write_log(script_name, status, code, output, attempt)

    return (
        f"Status   : {status}\n"
        f"Attempts : {attempt}/{MAX_RETRIES}\n"
        f"Log      : {log_path}\n"
        f"Output   :\n{output if output.strip() else '(no output)'}"
    )


@mcp.tool()
def list_logs() -> str:
    """List all Script Doctor log files, most recent first."""
    logs_dir = os.path.join(PROJECT_ROOT, "logs")

    if not os.path.exists(logs_dir):
        return "No logs yet. Run fix_and_run first."

    # Sort in reverse order so the newest log appears at the top
    files = sorted(os.listdir(logs_dir), reverse=True)
    return "\n".join(files) if files else "No logs yet."


@mcp.tool()
def read_log(filename: str) -> str:
    """Read the contents of a specific log file. Use list_logs to find filenames."""
    log_path = os.path.join(PROJECT_ROOT, "logs", filename)

    if not os.path.exists(log_path):
        return f"Log not found: {filename}"

    with open(log_path, "r") as f:
        return f.read()


if __name__ == "__main__":
    # mcp.run() starts the server using stdio transport — the standard way
    # Claude Desktop communicates with MCP servers.
    mcp.run()
