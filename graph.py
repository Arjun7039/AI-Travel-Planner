from langgraph.graph import StateGraph, END
from agents.trip_planner import trip_planner_node
from agents.budget_optimizer import budget_optimizer_node
from utils.state import TripState

def should_replan(state: TripState) -> str:
    """Decide whether to replan or finish"""
    if not state.get("within_budget", True) and state.get("iteration_count", 0) < 3:
        print(f"🔄 Over budget! Replanning... (attempt {state['iteration_count']})")
        return "replan"
    return "end"

def build_graph():
    graph = StateGraph(TripState)

    # Add nodes
    graph.add_node("trip_planner", trip_planner_node)
    graph.add_node("budget_optimizer", budget_optimizer_node)

    # Set entry point
    graph.set_entry_point("trip_planner")

    # Trip planner always goes to budget optimizer
    graph.add_edge("trip_planner", "budget_optimizer")

    # Budget optimizer either replans or ends
    graph.add_conditional_edges(
        "budget_optimizer",
        should_replan,
        {
            "replan": "trip_planner",
            "end": END
        }
    )

    return graph.compile()