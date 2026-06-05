from langgraph.graph import StateGraph, END
from backend.core.state import TravelState
from backend.agents.research_agent import research_agent
from backend.agents.planner_agent import planner_agent
from backend.agents.budget_agent import budget_agent


def should_replan(state: TravelState) -> str:
    """Decide whether to replan or finish. Max 2 replans."""
    if state.get("replan_count", 0) >= 2:
        return "finish"
    if not state.get("within_budget", True):
        return "replan"
    return "finish"


def build_graph():
    """Build the 3-agent LangGraph pipeline.
    
    Flow: research → planner → budget → (replan or finish)
    """
    graph = StateGraph(TravelState)

    graph.add_node("research", research_agent)
    graph.add_node("planner", planner_agent)
    graph.add_node("budget", budget_agent)

    # Linear flow
    graph.set_entry_point("research")
    graph.add_edge("research", "planner")
    graph.add_edge("planner", "budget")

    # Conditional: replan or finish
    graph.add_conditional_edges(
        "budget",
        should_replan,
        {
            "replan": "planner",
            "finish": END,
        },
    )

    return graph.compile()
