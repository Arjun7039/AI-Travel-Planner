import os
from tavily import TavilyClient
from langsmith import traceable
from backend.core.state import TravelState

@traceable(name="flight_agent")
def flight_agent(state: TravelState) -> TravelState:
    """Searches for real-time transport options using Tavily."""
    print("[Transport Agent] running...")
    
    if "flights" in state and state["flights"]:
        print("[Transport Agent] fast-path (already fetched)")
        return state
        
    if "agent_messages" not in state:
        state["agent_messages"] = []

    origin = state.get("origin", "Unknown")
    dest = state.get("destination", "Unknown")
    date = state.get("travel_dates", {}).get("start", "Unknown Date")
    transport_mode = state.get("transport_mode", "Flight")

    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        state["agent_messages"].append("Transport Agent skipped: No TAVILY_API_KEY.")
        budget = state.get("budget_inr", 50000)
        state["flights"] = [{"airline": f"{transport_mode} from {origin} to {dest}", "price_inr": int(budget * 0.3)}]
        return state

    try:
        tavily = TavilyClient(api_key=api_key)
        
        if transport_mode.lower() == "car":
            query = f"driving distance and estimated fuel cost from {origin} to {dest} in INR"
        elif transport_mode.lower() == "train":
            query = f"trains from {origin} to {dest} on {date} ticket prices INR"
        else:
            query = f"direct flights from {origin} to {dest} on {date} airlines flight numbers prices INR"

        response = tavily.search(query=query, search_depth="basic", max_results=3)
        
        # Summarize the results
        summary = " ".join([res.get("content", "") for res in response.get("results", [])])
        
        # Estimate transport cost as ~30% of budget
        budget = state.get("budget_inr", 50000)
        estimated_price = int(budget * 0.3)
        
        state["flights"] = [{
            "transport_type": transport_mode,
            "airline": f"{transport_mode} from {origin} to {dest}",
            "flight_no": "",
            "duration": "Varies",
            "stops": 0,
            "price_inr": estimated_price,
            "details": summary[:1500] + "..."
        }]
        
        state["agent_messages"].append(f"Transport Agent: Searched for {transport_mode} via Tavily.")

    except Exception as e:
        state["agent_messages"].append(f"Transport Agent error: {str(e)}")
        budget = state.get("budget_inr", 50000)
        state["flights"] = [{"airline": f"{transport_mode} from {origin} to {dest}", "price_inr": int(budget * 0.3)}]

    return state
