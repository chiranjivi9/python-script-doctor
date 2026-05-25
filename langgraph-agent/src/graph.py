# graph.py — wires nodes together into a runnable graph
#
# Stage 2: fix → run → (retry loop) → review → test → END
# Conditional edge after run_node: retry if failed, move on if succeeded.

import os
import sys
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from langgraph.graph import StateGraph, END

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from state import AgentState
from nodes import fix_node, run_node, review_node, test_node, log_node

MAX_RETRIES = 3


def router(state: AgentState) -> str:
    """
    Decides what happens after run_node.
    Returns the name of the next node as a string.
    This is the conditional edge — the retry loop expressed as a graph decision.
    """
    if not state["success"] and state["attempts"] < MAX_RETRIES:
        return "fix"     # code failed and we have retries left → go back
    return "review"      # code succeeded or max retries hit → move on


def build_graph():
    graph = StateGraph(AgentState)

    # Register all nodes
    graph.add_node("fix", fix_node)
    graph.add_node("run", run_node)
    graph.add_node("review", review_node)
    graph.add_node("test", test_node)
    graph.add_node("log", log_node)

    # Wire them: fix → run → review → test → log → END
    graph.set_entry_point("fix")
    graph.add_edge("fix", "run")
    # Conditional edge: router() reads state and returns "fix" or "review"
    graph.add_conditional_edges("run", router, {"fix": "fix", "review": "review"})
    graph.add_edge("review", "test")
    graph.add_edge("test", "log")
    graph.add_edge("log", END)

    return graph.compile()


if __name__ == "__main__":
    script_path = sys.argv[1] if len(sys.argv) > 1 else "samples/broken_example.py"

    if not os.path.exists(script_path):
        print(f"Error: file not found: {script_path}")
        sys.exit(1)

    with open(script_path) as f:
        broken_code = f.read()

    print(f"\nScript Doctor — LangGraph (Stage 1)")
    print(f"{'=' * 40}")
    print(f"Script  : {script_path}")
    print(f"Flow    : fix → run → review → test → END\n")

    app = build_graph()

    initial_state = {
        "original_code": broken_code,
        "current_code": broken_code,
        "error": None,
        "attempts": 0,
        "success": False,
        "output": "",
        "review": "",
        "tests": "",
        "log_path": "",
    }

    # stream() shows each node's output as it runs — better than invoke() for debugging
    # Each event is a dict: { "node_name": { fields_that_changed } }
    print("Streaming node events:\n")
    result = None
    for event in app.stream(initial_state):
        node_name = list(event.keys())[0]
        node_output = event[node_name]
        print(f"  [{node_name}] → {list(node_output.keys())}")
        result = event[node_name]  # last event holds the final state updates

    # Get the full final state by invoking once more for the summary
    # (stream gives per-node diffs; invoke gives the merged final state)
    final = app.invoke(initial_state)

    print(f"\n{'=' * 40}")
    print(f"Result   : {'SUCCESS' if final['success'] else 'FAILED'}")
    print(f"Attempts : {final['attempts']}")
    print(f"Output   :\n{final['output'] if final['output'].strip() else '(no output)'}")
    print(f"Log      : {final['log_path']}")
    print(f"\nLangSmith trace: https://smith.langchain.com")
