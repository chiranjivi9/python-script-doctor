# Decisions

## Why "Script Doctor & Logger" over "Code Reviewer"?
- Produces a tangible artifact (fixed script + log file), not just text feedback
- Teaches 3 concepts in one: LLM calls, code execution, data logging
- Execution + logging is the entry point to MLOps
- More satisfying: you see something actually happen

## Pipeline vs Agent vs MCP Server vs LangGraph

| Term | What it means | How you trigger it |
|---|---|---|
| Pipeline | Fixed steps A→B→C, no decisions | `python src/agent.py` |
| Agent | Pipeline + retry loop, feeds errors back to LLM | `python src/agent.py` |
| MCP Server | Exposes your agent as tools Claude calls from chat | Claude calls it automatically |
| LangGraph | Same agent logic as a visual, traceable graph | `python langgraph-agent/src/graph.py` |

The logic is identical across all three. MCP only changes the interface. LangGraph adds structure and observability.

## Why two files (agent.py + mcp_server.py)?
- `agent.py` = CLI you run manually from terminal
- `mcp_server.py` = registered once, Claude Desktop calls it from chat
- Both share the same core functions: `fix_code`, `run_code`, `review_code`, `write_code_test`, `write_log`
- Separation keeps each file focused on one interface

## Why LangGraph over LangChain or CrewAI?
- LangGraph models the agent as a graph — nodes (steps) and edges (transitions) are explicit
- Conditional edges make the retry loop visual and easy to reason about
- LangSmith tracing works out of the box — every node's inputs/outputs are logged
- CrewAI is better for multi-agent collaboration with different roles; overkill for a single-script pipeline
- LangChain adds abstractions over LLM calls; LangGraph adds structure over agent flow — both useful, LangGraph is the right fit here

## Why nodes return only changed fields?
- LangGraph merges returned dicts back into the full state automatically
- Returning only what changed keeps each node focused — it only knows what it touched
- Returning the full state from every node would be redundant and error-prone

## Why FastMCP over the raw MCP SDK?
- One `@mcp.tool()` decorator per tool — that's all it takes
- Raw SDK requires ~50 lines of boilerplate for the same result
- FastMCP is what Anthropic recommends for new MCP servers

## Why NOT use a framework from the start?
- Frameworks hide how agents actually work
- Building raw first means you understand what the framework does for you later
- LangGraph was added after the raw agent was working — so you could see what it adds (structure + tracing)

## Why subprocess to run code?
- Python's built-in tool — no extra install
- Isolates executed code: if the script crashes, the agent keeps running
- Captures stdout and stderr separately
- Timeout support prevents infinite loops from hanging the agent

## Why `os.chdir(PROJECT_ROOT)` in mcp_server.py?
- Claude Desktop can launch the MCP server from any working directory
- Without it, relative paths like `logs/` and `samples/` would break
- Pinning to PROJECT_ROOT (derived from the file's own location) makes all paths predictable

## Why compute PROJECT_ROOT explicitly in langgraph nodes?
- The LangGraph files live in `langgraph-agent/src/`, two levels below the project root
- Calling `load_dotenv()` without an explicit path looks in the current working directory, which may not be the project root
- Explicit `PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))` is reliable regardless of where the script is run from

## Why create the venv with a quoted path?
- The project directory contains a space: `Python /skills-learning`
- Unquoted shell commands split on spaces — this created `bin` and `bin 2` as separate folders and broke the venv entirely
- Always quote paths with spaces: `python3.11 -m venv "/path with space/venv"`

## Why strip markdown fences from Claude's output?
- Claude sometimes wraps code in ```python ... ``` even when told not to
- Stripping them defensively makes the agent robust regardless of prompt variation

## Why LangSmith doesn't trace the CLI agent?
- LangSmith intercepts calls made through the LangChain/LangGraph stack
- `src/agent.py` calls `anthropic.Anthropic()` directly — there is no LangChain wrapper in the call path
- To trace the CLI agent, you would need to replace `anthropic.Anthropic()` with `langchain_anthropic.ChatAnthropic`

## Why claude-sonnet-4-6?
- Best balance of speed, cost, and quality for a learning project
- Haiku is cheaper but less reliable at code fixing
- Opus is overkill and more expensive
