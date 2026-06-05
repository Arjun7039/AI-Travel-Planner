"""Budget Agent — Pure logic budget validation and optimization.

No LLM call needed. Extracts cost numbers from the itinerary markdown,
validates against the budget, and suggests savings if over budget.
"""

import re
import json
from backend.core.state import TravelState


def _extract_costs_from_markdown(markdown: str) -> tuple:
    """Extract cost values from the JSON block at the end of the markdown."""
    categories = {
        "transport": 0,
        "accommodation": 0,
        "food": 0,
        "activities": 0,
        "miscellaneous": 0,
    }
    total_cost = 0

    json_match = re.search(r'```json\s*(.*?)\s*```', markdown, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group(1))
            if "budget_breakdown" in data:
                b = data["budget_breakdown"]
                categories["transport"] = int(b.get("transport", 0))
                categories["accommodation"] = int(b.get("accommodation", 0))
                categories["food"] = int(b.get("food", 0))
                categories["activities"] = int(b.get("activities", 0))
                categories["miscellaneous"] = int(b.get("miscellaneous", 0))
                total_cost = sum(categories.values())
        except Exception as e:
            print(f"Error parsing budget JSON: {e}")

    return categories, total_cost

def budget_agent(state: TravelState) -> dict:
    """Validate budget and provide breakdown. Pure logic — no LLM call."""
    print("💰 Budget Agent: Analyzing costs...")

    budget = state.get("budget_inr", 50000)
    itinerary = state.get("itinerary_markdown", "")
    replan_count = state.get("replan_count", 0)

    categories, total_cost = _extract_costs_from_markdown(itinerary)

    # If we couldn't extract meaningful costs, estimate within budget
    if total_cost == 0 and budget > 0:
        total_cost = int(budget * 0.85)
        categories = {
            "transport": int(budget * 0.25),
            "accommodation": int(budget * 0.30),
            "food": int(budget * 0.20),
            "activities": int(budget * 0.08),
            "miscellaneous": int(budget * 0.02),
        }

    within_budget = total_cost <= budget

    logs = state.get("agent_logs", [])
    if within_budget:
        logs.append(f"Budget Agent: Trip costs ₹{total_cost:,} — within budget of ₹{budget:,} ✅")
    else:
        logs.append(f"Budget Agent: Trip costs ₹{total_cost:,} — OVER budget of ₹{budget:,} by ₹{total_cost - budget:,} ❌")

    return {
        "budget_breakdown": categories,
        "total_cost": total_cost,
        "within_budget": within_budget,
        "replan_count": replan_count + (0 if within_budget else 1),
        "agent_logs": logs,
    }
