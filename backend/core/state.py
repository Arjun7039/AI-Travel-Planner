from typing import TypedDict, Optional, List


class TravelState(TypedDict):
    """Simplified shared state for the 3-agent LangGraph pipeline."""

    # User input (extracted from natural language by prompt enhancer)
    destination: str
    origin: str
    start_date: str              # "YYYY-MM-DD"
    end_date: str                # "YYYY-MM-DD"
    num_travellers: int
    budget_inr: float
    transport_mode: str          # "Flight" | "Train" | "Car"
    interests: List[str]         # ["beaches", "food", "adventure", ...]
    user_prompt: str             # Original natural language prompt

    # Research Agent outputs
    weather_data: Optional[str]
    places_data: Optional[str]
    hotels_data: Optional[str]

    # Planner Agent outputs
    itinerary_markdown: Optional[str]   # Rich markdown itinerary (ChatGPT-style)
    trip_title: Optional[str]           # e.g. "Goa Beach Getaway"

    # Budget Agent outputs
    budget_breakdown: Optional[dict]
    total_cost: Optional[float]
    within_budget: bool

    # Control
    agent_logs: List[str]
    replan_count: int
    error: Optional[str]
