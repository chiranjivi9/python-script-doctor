# CLAUDE.md

Instructions for Claude Code when working in this project.

## Project

Python Script Doctor & Logger — an agent that fixes broken Python scripts using Claude AI, runs them, and logs the result. Exposed as a CLI tool and as an MCP server.

## Key Commands

```bash
# Always run from the project root (code-review-agent/)

# Run tests
venv/bin/pytest tests/ -v

# Run the CLI agent
venv/bin/python src/agent.py samples/broken_example.py

# Start the MCP server manually (Claude Desktop starts it automatically)
venv/bin/python src/mcp_server.py
```

## Project Structure

```
src/agent.py         ← CLI agent (fix_code, run_code, write_log, run_doctor)
src/mcp_server.py    ← MCP server (imports from agent.py, exposes 3 tools)
tests/test_agent.py  ← 16 pytest tests, one per spec in SPEC.md
samples/             ← broken Python files for testing the agent
logs/                ← auto-generated, gitignored
```

## Conventions

- Venv is at `venv/` using Python 3.11 — always use `venv/bin/python`, not system python
- Secrets go in `.env` only — never `.env.example`, never hardcoded
- All paths with spaces must be quoted in shell commands
- Run commands from project root so relative paths (logs/, .env) resolve correctly
- Model: `claude-sonnet-4-6`
- Max retries: `MAX_RETRIES = 3` in agent.py

## Spec-Driven Development

- `SPEC.md` defines the behavioral contract for each function
- `tests/test_agent.py` has one test per spec line
- When changing agent.py, update SPEC.md and tests together

## What to Avoid

- Do not commit `.env` (contains real API key)
- Do not use system Python — always use `venv/bin/python`
- Do not hardcode usernames or absolute paths in docs
- Do not change `logs/` to a non-gitignored location

## Docs to Keep Updated

- `docs/status.md` — current phase and blockers
- `docs/progress.md` — log each session's work
- `docs/decision.md` — record why key choices were made
