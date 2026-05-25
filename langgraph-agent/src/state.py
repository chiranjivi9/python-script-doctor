# state.py — defines the shared memory that travels through every node in the graph
#
# Every node receives the full AgentState and returns only the fields it changed.
# LangGraph merges the returned dict back into the state automatically.

from typing import Optional
from typing_extensions import TypedDict


class AgentState(TypedDict):
    original_code: str       # the broken code you passed in — never modified
    current_code: str        # the working copy — updated by fix_node each attempt
    error: Optional[str]     # traceback from the last failed run — fed back to Claude
    attempts: int            # how many fix attempts have been made
    success: bool            # did the last run succeed?
    output: str              # stdout (success) or stderr (failure) from last run
    review: str              # code quality feedback — added in Stage 3
    tests: str               # generated pytest tests  — added in Stage 3
    log_path: str            # path to the saved log file — added in Stage 4
