from langsmith import traceable
from backend.core.state import TravelState

@traceable(name="supervisor_agent")
def supervisor_agent(state: TravelState) -> TravelState:
    """Parses user input, dispatches to sub-agents, handles replanning logic."""
    print("Supervisor Agent running...")
    
    if "agent_messages" not in state:
        state["agent_messages"] = []
        
    if "replan_count" not in state:
        state["replan_count"] = 0

    state["agent_messages"].append(f"Supervisor Agent: Iteration {state['replan_count']}")

    return state
