from typing import TypedDict, List, Optional, Annotated
from langgraph.graph import add_messages
class TripState(TypedDict):
    # User inputs
    destination: str
    origin: str
    start_date: str
    end_date: str
    budget: float
    budget_inr: float
    preferences: List[str]
    travelers: int
    transport_mode: str

    # Trip Planner outputs
    suggested_places: List[dict]
    daily_itinerary: List[dict]
    weather_summary: str

    # Budget Optimizer outputs
    cost_breakdown: dict
    total_estimated_cost: float
    within_budget: bool
    optimization_suggestions: List[str]

    # Control flow
    messages: Annotated[list, add_messages]
    replanning_needed: bool
    iteration_count: int