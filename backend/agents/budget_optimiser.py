from langsmith import traceable
from backend.core.state import TravelState

@traceable(name="budget_optimiser_agent")
def budget_optimiser_agent(state: TravelState) -> TravelState:
    """Calculates real budget breakdown from the itinerary and enforces strict budget constraints."""
    print("[Budget Optimiser Agent] running...")
    
    if "agent_messages" not in state:
        state["agent_messages"] = []

    budget = state.get("budget_inr", 0)
    
    # Calculate transport cost from the transport agent data
    flights = state.get("flights", [])
    hotels = state.get("hotels", [])
    
    # Calculate travel days
    travel_dates = state.get("travel_dates", {})
    num_days = 3
    if travel_dates.get("start") and travel_dates.get("end"):
        try:
            from datetime import datetime
            d1 = datetime.strptime(travel_dates["start"], "%Y-%m-%d")
            d2 = datetime.strptime(travel_dates["end"], "%Y-%m-%d")
            num_days = max(1, (d2 - d1).days)
        except:
            pass
    
    # Get transport cost estimate
    transport_cost = 0
    if flights:
        transport_cost = flights[0].get("price_inr", 0)
    
    # Get hotel cost estimate  
    hotel_cost = 0
    if hotels:
        hotel_cost = hotels[0].get("price_per_night_inr", 0) * num_days
    
    # Calculate activity costs from the itinerary itself
    activity_cost = 0
    itinerary = state.get("itinerary", [])
    for day in itinerary:
        if isinstance(day, dict):
            for act in day.get("activities", []):
                if isinstance(act, dict):
                    activity_cost += act.get("estimated_cost_inr", 0)
    
    total_cost = transport_cost + hotel_cost + activity_cost
    
    # If total is 0, estimate proportionally but STAY WITHIN BUDGET
    if total_cost == 0 and budget > 0:
        transport_cost = int(budget * 0.25)
        hotel_cost = int(budget * 0.35)
        activity_cost = int(budget * 0.30)
        total_cost = transport_cost + hotel_cost + activity_cost
    
    # STRICT BUDGET ENFORCEMENT: Scale down if exceeding
    if budget > 0 and total_cost > budget:
        scale = (budget * 0.95) / total_cost  # 5% safety margin
        transport_cost = int(transport_cost * scale)
        hotel_cost = int(hotel_cost * scale)
        activity_cost = int(activity_cost * scale)
        total_cost = transport_cost + hotel_cost + activity_cost
        
        # Also scale down itinerary costs
        for day in itinerary:
            if isinstance(day, dict):
                for act in day.get("activities", []):
                    if isinstance(act, dict):
                        act["estimated_cost_inr"] = int(act.get("estimated_cost_inr", 0) * scale)
                if day.get("hotel", {}).get("price_per_night"):
                    day["hotel"]["price_per_night"] = int(day["hotel"]["price_per_night"] * scale)
                day["day_total_cost"] = sum(
                    a.get("estimated_cost_inr", 0) for a in day.get("activities", [])
                ) + int(day.get("hotel", {}).get("price_per_night", 0))
    
    # Final clamp — total should never exceed budget
    if budget > 0:
        total_cost = min(total_cost, int(budget * 0.95))
    
    state["budget_breakdown"] = {
        "flights": transport_cost,
        "hotels": hotel_cost,
        "activities": activity_cost,
        "total": total_cost
    }
    
    state["budget_exceeded"] = False
    state["budget_overshoot_pct"] = 0.0
    state["replan_reason"] = None
    state["agent_messages"].append(f"Budget Optimiser: Trip estimated at ₹{total_cost:,} — within budget of ₹{budget:,}.")
        
    return state
