# Python Script Doctor & Logger

An agent that takes a broken Python script, fixes it with Claude AI, runs it automatically, and logs the result. Available as a CLI tool and as an MCP server so Claude can call it directly from chat.

## The 3-Step Pipeline

```
[ Your Broken Code ] ──> [ 1. Fixer Agent ] ──> [ 2. Executor ] ──> [ 3. Logger ]
```

| Step | What Happens |
|---|---|
| 1. Fixer | Sends broken code to Claude → gets fixed code back |
| 2. Executor | Runs the fixed code using Python's subprocess |
| 3. Logger | Writes a timestamped log file: status, attempts, output |

If execution fails, the real error is fed back to Claude and the cycle retries (up to 3 times). That feedback loop is what makes this an **agent**, not just a script.

## Two Ways to Use It

| Mode | How | When |
|---|---|---|
| CLI | `venv/bin/python src/agent.py yourfile.py` | Run manually from terminal |
| MCP Server | Say "Fix and run samples/file.py" in Claude Desktop | Claude runs it for you |

---

## How It Works — Sequence Diagrams

### CLI Flow (with retry loop)

```mermaid
sequenceDiagram
    participant You
    participant agent.py
    participant Claude API
    participant subprocess
    participant logs/

    You->>agent.py: python src/agent.py broken.py
    agent.py->>agent.py: read broken script

    loop Up to 3 attempts
        agent.py->>Claude API: fix_code(code, error)
        Claude API-->>agent.py: fixed code
        agent.py->>subprocess: run_code(fixed code)
        subprocess-->>agent.py: output or traceback

        alt Run succeeded
            agent.py->>logs/: write_log(SUCCESS, attempts)
        else Run failed
            agent.py->>agent.py: error = traceback → retry
        end
    end

    agent.py-->>You: print result + log path
```

---

### MCP Server Flow

```mermaid
sequenceDiagram
    participant You
    participant Claude Desktop
    participant mcp_server.py
    participant Claude API
    participant subprocess
    participant logs/

    You->>Claude Desktop: "Fix and run samples/broken.py"
    Claude Desktop->>mcp_server.py: call fix_and_run(script_path)

    loop Up to 3 attempts
        mcp_server.py->>Claude API: fix_code(code, error)
        Claude API-->>mcp_server.py: fixed code
        mcp_server.py->>subprocess: run_code(fixed code)
        subprocess-->>mcp_server.py: output or traceback

        alt Run succeeded
            mcp_server.py->>logs/: write_log(SUCCESS, attempts)
        else Run failed
            mcp_server.py->>mcp_server.py: error = traceback → retry
        end
    end

    mcp_server.py-->>Claude Desktop: status + output + log path
    Claude Desktop-->>You: "Fixed in 2 attempts. Output: ..."
```

---

## Setup

```bash
# 1. Create venv with Python 3.11 (quote the path if it contains spaces)
# Find your Python 3.11 path with: which python3.11
python3.11 -m venv venv

# 2. Install dependencies
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt

# 3. Create your .env file
cp .env.example .env
# Edit .env → add your real Anthropic API key

# 4. Add billing credits
# https://console.anthropic.com → Billing → Add credits ($5 minimum)
```

---

## CLI Usage

```bash
# Always run from the project root (code-review-agent/)

# Test with syntax bugs (should fix in 1 attempt)
venv/bin/python src/agent.py samples/broken_example.py

# Test with runtime errors (exercises the retry loop)
venv/bin/python src/agent.py samples/broken_hard.py

# Try on your own file
venv/bin/python src/agent.py samples/your_script.py

# Check logs
ls logs/
```

---

## MCP Server Usage

The server is registered in `~/Library/Application Support/Claude/claude_desktop_config.json`.

Restart Claude Desktop, then in any chat say:

| What you say | Tool called |
|---|---|
| "Fix and run samples/broken_example.py" | `fix_and_run` |
| "Show my script doctor logs" | `list_logs` |
| "Read the latest log" | `read_log` |

Verify it's connected: ask Claude "What MCP tools do you have?" — it should list all three.

---

## Project Structure

```
code-review-agent/
├── src/
│   ├── agent.py            ← CLI agent (agentic retry loop)
│   └── mcp_server.py       ← MCP server (same logic, exposed as tools)
├── samples/
│   ├── broken_example.py   ← 4 syntax bugs
│   └── broken_hard.py      ← runtime errors (exercises retry loop)
├── docs/
│   ├── status.md           ← current state
│   ├── progress.md         ← session-by-session log
│   └── decision.md         ← why key choices were made
├── logs/                   ← auto-created on first run
├── venv/                   ← Python 3.11 virtual environment (gitignored)
├── .env                    ← your real API key (gitignored)
├── .env.example            ← safe template to share
├── .gitignore
├── requirements.txt
└── README.md
```

## What You'll Learn

- How to call the Anthropic API from Python
- How AI agents use retry loops (the agentic loop)
- How to execute code programmatically with subprocess
- How to store secrets safely with .env files
- How to log structured data to files (the MLOps entry point)
- How MCP servers expose Python functions as tools Claude can call
- Why paths with spaces must always be quoted in shell commands
