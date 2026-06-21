import os
import json
import re
from langchain_core.messages import HumanMessage, SystemMessage
from langsmith import traceable
from backend.core.state import TravelState
from backend.rag.retriever import retrieve_context
from backend.core.llm_provider import get_llm, get_text_content


def extract_json_from_text(text: str):
    """Extract JSON array or object from LLM text that may contain markdown fences."""
    # Try to find JSON in code blocks first
    code_block = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', text)
    if code_block:
        text = code_block.group(1).strip()
    
    # Try parsing as-is
    try:
        parsed = json.loads(text)
        # If it's a dict with a "days" key, extract that
        if isinstance(parsed, dict) and "days" in parsed:
            return parsed["days"]
        if isinstance(parsed, list):
            return parsed
        return [parsed]
    except json.JSONDecodeError:
        pass
    
    # Try to find a JSON array in the text
    match = re.search(r'\[[\s\S]*\]', text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    
    # Try to find a JSON object
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, dict) and "days" in parsed:
                return parsed["days"]
            return [parsed]
        except json.JSONDecodeError:
            pass
    
    return None


@traceable(name="trip_planner_agent")
def trip_planner_agent(state: TravelState) -> TravelState:
    """Generates day-by-day itinerary using LLM and context from prior agents."""
    print("Trip Planner Agent running...")
    
    if "agent_messages" not in state:
        state["agent_messages"] = []

    llm = get_llm(temperature=0.4, max_tokens=4000)
    if not llm:
        state["agent_messages"].append("Trip Planner Agent skipped: No LLM API key.")
        state["error"] = "Missing LLM API key"
        return state

    # Gather context from state
    weather_data = state.get("weather_forecast", [])
    weather_info = json.dumps(weather_data[:15], indent=1) if weather_data else "No weather data available"
    flight_info = json.dumps(state.get("flights", []), indent=1)
    hotel_data = state.get("hotels", [])
    hotel_info = json.dumps(hotel_data, indent=1)
    local_exp = state.get("local_experiences", [])
    local_info = json.dumps(local_exp, indent=1) if local_exp else "No local experience data"
    transport_mode = state.get("transport_mode", "Flight")
    budget = state.get("budget_inr", 50000)
    origin = state.get("origin", "")
    destination = state.get("destination", "")
    travel_dates = state.get("travel_dates", {})
    num_travellers = state.get("num_travellers", 1)
    
    # Calculate number of days
    start_date = travel_dates.get("start", "")
    end_date = travel_dates.get("end", "")
    num_days = 3  # default
    if start_date and end_date:
        try:
            from datetime import datetime
            d1 = datetime.strptime(start_date, "%Y-%m-%d")
            d2 = datetime.strptime(end_date, "%Y-%m-%d")
            num_days = max(1, (d2 - d1).days + 1)
        except:
            pass
    
    # Budget per day for reference
    budget_per_day = int(budget / num_days)
    
    # Retrieve RAG context based on destination and preferences
    prefs = str(state.get("preferences", {}))
    rag_query = f"Travel guide and tips for {destination} focusing on {prefs}"
    rag_context = retrieve_context(rag_query, n_results=5)

    system_prompt = f"""You are "Yatri-AI," an elite Indian travel architect who creates incredibly detailed, magazine-quality travel itineraries.
You MUST respond with ONLY valid JSON. No markdown, no explanation, no extra text.

CRITICAL BUDGET RULE:
- The ABSOLUTE MAXIMUM total budget is ₹{budget} for {num_travellers} traveller(s) for the ENTIRE trip.
- Add up ALL estimated_cost_inr values across ALL days. The sum MUST be LESS than ₹{budget}.
- Budget per day should average around ₹{budget_per_day}. Stay well within this.
- If the budget is tight (e.g., ₹3000 or less), suggest FREE and very cheap options: free temples, parks, street food (₹30-50), walking tours, etc.
- NEVER exceed the total budget. Double-check your math.

TRANSPORT RULE:
- The user's transport mode is "{transport_mode}" — DO NOT mention any other transport mode.
- If transport is "Flight", you MUST include the real flight name, airline, flight numbers, and exact prices from the Transport Info as an activity on Day 1 (Category: transport). Do not make up fake flight names. Extract the exact data provided.
- If transport is "Car", plan for road trip / driving. NEVER mention flights.
- If transport is "Train", plan for train journeys. NEVER mention flights.

QUALITY RULES:
- Use REAL, SPECIFIC place names (actual restaurant names, temple names, market names, etc.)
- Give vivid, engaging 1-2 sentence descriptions for each activity (keep it concise and fast)
- Include practical tips (best time to visit, what to wear, etc.)
- Reference the weather data to give weather-appropriate suggestions
- Use the REAL hotel names from the hotel data provided
- Include local food recommendations with specific dish names

CONTEXT DATA:
Weather Forecast: {weather_info}
Transport: {transport_mode} ONLY
Transport Info: {flight_info}
Hotels Found: {hotel_info}
Local Experiences: {local_info}
Local Tips (RAG): {rag_context}
"""

    user_prompt = f"""Create a {num_days}-day itinerary for {destination} from {origin}.
Travel dates: {start_date} to {end_date}
Travellers: {num_travellers}
Budget: ₹{budget} TOTAL (ABSOLUTE MAX — never exceed this!)
Transport: {transport_mode} ONLY

Respond with this EXACT JSON structure and nothing else:
{{
  "days": [
    {{
      "day": 1,
      "date": "{start_date}",
      "theme": "Arrival & Heritage Exploration",
      "weather": {{
        "temp_high": 34,
        "temp_low": 22,
        "condition": "Partly Cloudy",
        "humidity": 45,
        "advice": "Carry sunscreen and a light hat. Stay hydrated."
      }},
      "hotel": {{
        "name": "Actual Hotel Name from data",
        "area": "Neighborhood/Area",
        "stars": 3,
        "price_per_night": 800,
        "check_in": "2:00 PM"
      }},
      "activities": [
        {{
          "time": "06:30 AM",
          "title": "Sunrise at Specific Place Name",
          "description": "Vivid 2-3 sentence description of the experience. What makes it special, what to expect, insider knowledge.",
          "location": "Exact Place Name, Area",
          "category": "sightseeing",
          "estimated_cost_inr": 0,
          "tips": "Best visited early morning before crowds. Wear comfortable shoes."
        }},
        {{
          "time": "08:30 AM",
          "title": "Breakfast at Specific Restaurant Name",
          "description": "Description of the food experience. Mention specific dishes to try.",
          "location": "Restaurant Name, Street/Area",
          "category": "food",
          "estimated_cost_inr": 150,
          "tips": "Try the signature dish. Cash preferred."
        }}
      ],
      "local_experience": {{
        "title": "Unique Local Experience",
        "description": "A special, authentic local experience for this day",
        "estimated_cost_inr": 0
      }},
      "day_total_cost": 500
    }}
  ]
}}

IMPORTANT: 
- Categories must be one of: "sightseeing", "food", "transport", "shopping", "adventure", "culture", "relaxation", "nightlife"
- Sum of ALL day_total_cost values MUST be less than ₹{budget}
- Each day_total_cost = hotel price_per_night + sum of activity costs for that day
- Use real place names from {destination}
- Weather data should reference the actual forecast data provided"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        raw_text = get_text_content(response)
        
        # Parse the JSON from the response
        parsed = extract_json_from_text(raw_text)
        
        if parsed and isinstance(parsed, list) and len(parsed) > 0:
            # Validate and normalize each day
            valid_days = []
            running_total = 0
            
            for day in parsed:
                if isinstance(day, dict):
                    valid_day = {
                        "day": day.get("day", len(valid_days) + 1),
                        "date": day.get("date", ""),
                        "theme": day.get("theme", "Exploration"),
                        "weather": day.get("weather", {
                            "temp_high": 30,
                            "temp_low": 20,
                            "condition": "Pleasant",
                            "humidity": 50,
                            "advice": "Comfortable weather for sightseeing."
                        }),
                        "hotel": day.get("hotel", {}),
                        "local_experience": day.get("local_experience", {}),
                        "activities": [],
                        "day_total_cost": 0
                    }
                    
                    day_cost = 0
                    for act in day.get("activities", []):
                        if isinstance(act, dict):
                            cost = int(act.get("estimated_cost_inr", 0))
                            day_cost += cost
                            valid_day["activities"].append({
                                "time": act.get("time", "TBD"),
                                "title": act.get("title", act.get("description", "Activity")[:50]),
                                "description": act.get("description", ""),
                                "location": act.get("location", ""),
                                "category": act.get("category", "sightseeing"),
                                "estimated_cost_inr": cost,
                                "tips": act.get("tips", "")
                            })
                    
                    # Add hotel cost
                    hotel_cost = int(valid_day.get("hotel", {}).get("price_per_night", 0))
                    day_cost += hotel_cost
                    valid_day["day_total_cost"] = day_cost
                    running_total += day_cost
                    valid_days.append(valid_day)
            
            # BUDGET ENFORCEMENT: If total exceeds budget, scale down all costs
            if running_total > budget and budget > 0:
                scale_factor = budget / running_total * 0.95  # 5% safety margin
                for day in valid_days:
                    for act in day["activities"]:
                        act["estimated_cost_inr"] = int(act["estimated_cost_inr"] * scale_factor)
                    if day.get("hotel", {}).get("price_per_night"):
                        day["hotel"]["price_per_night"] = int(day["hotel"]["price_per_night"] * scale_factor)
                    # Recalculate day total
                    day["day_total_cost"] = sum(a["estimated_cost_inr"] for a in day["activities"]) + int(day.get("hotel", {}).get("price_per_night", 0))
            
            if valid_days:
                state["itinerary"] = valid_days
                total = sum(d["day_total_cost"] for d in valid_days)
                state["agent_messages"].append(f"Trip Planner Agent: Generated {len(valid_days)}-day detailed itinerary. Estimated total: ₹{total:,}")
            else:
                state["itinerary"] = [{"day": 1, "theme": "Your Trip", "weather": {}, "hotel": {}, "activities": [{"time": "All Day", "title": "Explore", "description": raw_text[:500], "estimated_cost_inr": 0, "category": "sightseeing", "location": "", "tips": ""}], "day_total_cost": 0}]
                state["agent_messages"].append("Trip Planner Agent: Generated itinerary (basic format).")
        else:
            # Final fallback — wrap raw text as a single activity
            state["itinerary"] = [{"day": 1, "theme": "Your Trip", "weather": {}, "hotel": {}, "activities": [{"time": "All Day", "title": "Trip Plan", "description": raw_text[:500], "estimated_cost_inr": 0, "category": "sightseeing", "location": "", "tips": ""}], "day_total_cost": 0}]
            state["agent_messages"].append("Trip Planner Agent: Generated itinerary (text format).")

    except Exception as e:
        state["agent_messages"].append(f"Trip Planner Agent exception: {str(e)}")
        state["error"] = str(e)
        state["itinerary"] = [{"day": 1, "theme": "Error", "weather": {}, "hotel": {}, "activities": [{"time": "", "title": "Planning Error", "description": f"Could not generate itinerary: {str(e)}", "estimated_cost_inr": 0, "category": "sightseeing", "location": "", "tips": ""}], "day_total_cost": 0}]

    return state
