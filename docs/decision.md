# Decisions

## Why "Script Doctor & Logger" over "Code Reviewer"?
- Produces a tangible artifact (fixed script + log file), not just text feedback
- Teaches 3 concepts in one: LLM calls, code execution, data logging
- Execution + logging is the entry point to MLOps
- More satisfying: you see something actually happen

## Pipeline vs Agent vs MCP Server

| Term | What it means | How you trigger it |
|---|---|---|
| Pipeline | Fixed steps A→B→C, no decisions | `python src/agent.py` |
| Agent | Pipeline + retry loop, feeds errors back to LLM | `python src/agent.py` |
| MCP Server | Exposes your agent as tools Claude calls from chat | Claude calls it automatically |

The logic is identical across all three. MCP only changes the interface — who triggers the run.

## Why two files (agent.py + mcp_server.py)?
- `agent.py` = CLI you run manually from terminal
- `mcp_server.py` = registered once, Claude Desktop calls it from chat
- Both share the same three functions: `fix_code`, `run_code`, `write_log`
- Separation keeps each file focused on one interface

## Why FastMCP over the raw MCP SDK?
- One `@mcp.tool()` decorator per tool — that's all it takes
- Raw SDK requires ~50 lines of boilerplate for the same result
- FastMCP is what Anthropic recommends for new MCP servers

## Why NOT use a framework (LangChain, CrewAI, AutoGen)?
- Frameworks hide how agents actually work
- Building raw first means you understand what the framework does for you later
- Add frameworks after you have the mental model — not before

## Why subprocess to run code?
- Python's built-in tool — no extra install
- Isolates executed code: if the script crashes, the agent keeps running
- Captures stdout and stderr separately
- Timeout support prevents infinite loops from hanging the agent

## Why `os.chdir(PROJECT_ROOT)` in mcp_server.py?
- Claude Desktop can launch the MCP server from any working directory
- Without it, relative paths like `logs/` and `samples/` would break
- Pinning to PROJECT_ROOT (derived from the file's own location) makes all paths predictable

## Why create the venv with a quoted path?
- The project directory contains a space: `Python /skills-learning`
- Unquoted shell commands split on spaces — this created `bin` and `bin 2` as separate folders and broke the venv entirely
- Always quote paths with spaces: `python3.11 -m venv "/path with space/venv"`

## Why strip markdown fences from Claude's output?
- Claude sometimes wraps code in ```python ... ``` even when told not to
- Stripping them defensively makes the agent robust regardless of prompt variation

## Why claude-sonnet-4-6?
- Best balance of speed, cost, and quality for a learning project
- Haiku is cheaper but less reliable at code fixing
- Opus is overkill and more expensive
