from graph import build_graph

app = build_graph()

# Test input
initial_state = {
    "destination": "Bangkok, Thailand",
    "origin": "Bengaluru, India",
    "start_date": "2026-06-01",
    "end_date": "2026-06-04",
    "budget": 1000.0,
    "preferences": ["food", "culture", "adventure"],
    "travelers": 1,
    "suggested_places": [],
    "daily_itinerary": [],
    "weather_summary": "",
    "cost_breakdown": {},
    "total_estimated_cost": 0.0,
    "within_budget": True,
    "optimization_suggestions": [],
    "messages": [],
    "replanning_needed": False,
    "iteration_count": 0
}

print("🚀 Starting AI Travel Planner...\n")
result = app.invoke(initial_state)

print("\n" + "="*50)
print("✅ FINAL ITINERARY")
print("="*50)
print(result["daily_itinerary"][0]["raw"])

print("\n" + "="*50)
print("💰 BUDGET BREAKDOWN")
print("="*50)
for category, amount in result["cost_breakdown"].items():
    print(f"  {category}: ${amount}")
print(f"\n  TOTAL: ${result['total_estimated_cost']}")
print(f"  Within Budget: {result['within_budget']}")

if result["optimization_suggestions"]:
    print("\n💡 SUGGESTIONS:")
    for s in result["optimization_suggestions"]:
        print(f"  - {s}")