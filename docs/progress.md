# Progress Log

## 2026-05-17 — Session 1

### Done
- Decided on project: Python Script Doctor & Logger (pivoted from Code Reviewer)
- Built `agent.py` — 3-step pipeline: Fixer → Executor → Logger
- Created `broken_example.py` with 4 intentional syntax bugs
- Created `.env` + `.gitignore` — API key stored securely, never committed to git
- Created `.env.example` — safe template for sharing
- Installed anthropic and python-dotenv packages
- First test run: API key authenticated successfully
- Hit billing wall: account has $0 credits

### Key Learnings
- `.env` vs `.env.example`: real secrets in .env (gitignored), template in .env.example (safe to share)
- `load_dotenv()` reads .env and injects values into os.environ automatically
- A 400 "credit balance too low" error means the key works — billing issue, not a code issue

---

## 2026-05-17 — Session 2

### Done
- Upgraded pipeline → real agent by adding a retry loop
- `fix_code()` now accepts an optional `error` argument — real traceback feeds back to Claude on retry
- Added `broken_hard.py` — runtime errors that only appear after execution
- Log records number of attempts taken
- Created `requirements.txt`
- Restructured directories: src/, samples/, docs/

### Key Learnings
- Pipeline = fixed steps. Agent = loop + decisions based on output
- The one line that makes it agentic: `error = output` passed back into `fix_code()`

```
Attempt 1: fix(broken_code)      → run → FAILED
Attempt 2: fix(code, error)      → run → FAILED
Attempt 3: fix(code, error)      → run → SUCCESS
```

---

## 2026-05-17 — Session 3

### Done
- Built `mcp_server.py` using FastMCP — exposes the agent as 3 Claude tools
- Tools: `fix_and_run`, `list_logs`, `read_log`
- Fixed broken venv: original used Mac system Python 3.9 (too old for mcp); recreated with Anaconda Python 3.11 using quoted paths to handle space in project directory
- Registered MCP server in Claude Desktop config
- Tested MCP server starts cleanly
- Added explanatory comments to `agent.py` and `mcp_server.py`
- Wrote SPEC.md + 16 pytest tests (all passing)
- Created CLAUDE.md for Claude Code session conventions
- Created GitHub repo and pushed via SSH

### Key Learnings
- MCP changes the interface, not the logic — same fix_code/run_code/write_log, different caller
- `@mcp.tool()` decorator is all FastMCP needs to expose a function as a tool
- Paths with spaces must be quoted in shell commands — unquoted spaces split into separate arguments and break venv creation
- `os.chdir(PROJECT_ROOT)` in mcp_server.py pins the working directory so relative paths work regardless of where Claude Desktop launches the server
- `sys.executable` in subprocess.run ensures the same Python interpreter runs the fixed code
- Spec-driven development: write the spec first, then tests, then code

---

## 2026-05-25 — Session 4

### Done
- Added LangGraph multi-agent flow in `langgraph-agent/`
- Built 5 nodes: `fix_node`, `run_node`, `review_node`, `test_node`, `log_node`
- Shared `AgentState` TypedDict carries state between all nodes
- Wired conditional edge (retry loop) via `router()` function: retries fix→run if code fails, moves to review if it succeeds or max retries hit
- Enabled LangSmith tracing via `LANGCHAIN_TRACING_V2=true` + `LANGCHAIN_API_KEY` in `.env`
- Added `review_code()` and `write_code_test()` to `src/agent.py`
- Wired review and test steps into CLI `run_doctor()` — log files now contain all 4 sections
- Updated `write_log()` signature to accept `review` and `tests` parameters
- Tested LangGraph flow on broken_example.py, broken_hard.py — all pass in 1 attempt

### Key Learnings
- LangGraph nodes are plain Python functions: receive full state, return only changed fields
- LangSmith only traces LangChain/LangGraph calls — raw `anthropic` SDK calls are invisible to it
- Conditional edges use a `router()` function that reads state and returns a node name string
- `app.stream()` gives per-node diffs; `app.invoke()` gives the merged final state
- `PROJECT_ROOT` must be computed explicitly when running from a subdirectory — `load_dotenv()` with a relative path silently fails
