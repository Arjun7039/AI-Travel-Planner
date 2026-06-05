"""Planner Agent — Generates a beautiful conversational markdown itinerary.

Uses Groq LLM (llama-3.3-70b-versatile) to create a ChatGPT-style travel
itinerary with rich formatting, emojis, and practical details.
The output is human-readable markdown, NOT JSON.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from backend.core.state import TravelState

load_dotenv()


def planner_agent(state: TravelState) -> dict:
    """Generate a conversational, markdown-formatted travel itinerary."""
    print("✈️ Planner Agent: Crafting your itinerary...")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {
            "itinerary_markdown": "❌ Cannot generate itinerary: Missing GROQ_API_KEY.",
            "trip_title": "Error",
            "agent_logs": state.get("agent_logs", []) + ["Planner Agent: No API key."],
        }

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=api_key,
        temperature=0.5,
        max_tokens=4000,
    )

    # Gather all context
    destination = state.get("destination", "Unknown")
    origin = state.get("origin", "")
    start_date = state.get("start_date", "")
    end_date = state.get("end_date", "")
    budget = state.get("budget_inr", 50000)
    travellers = state.get("num_travellers", 1)
    transport = state.get("transport_mode", "Flight")
    interests = state.get("interests", [])
    user_prompt = state.get("user_prompt", "")
    weather = state.get("weather_data", "No weather data")
    places = state.get("places_data", "No places data")
    hotels = state.get("hotels_data", "No hotel data")
    replan_count = state.get("replan_count", 0)

    # Calculate days
    num_days = 3
    if start_date and end_date:
        try:
            from datetime import datetime
            d1 = datetime.strptime(start_date, "%Y-%m-%d")
            d2 = datetime.strptime(end_date, "%Y-%m-%d")
            num_days = max(1, (d2 - d1).days + 1)
        except (ValueError, TypeError):
            pass

    budget_note = ""
    if replan_count > 0:
        budget_note = f"""
⚠️ BUDGET ALERT: The previous itinerary exceeded the budget of ₹{budget:,}.
You MUST cut costs this time. Use cheaper hotels, free activities, street food, 
and budget transport options. The total MUST stay under ₹{budget:,}."""

    system_prompt = f"""You are Yatri AI — a friendly, knowledgeable Indian travel assistant.
You write in a warm, conversational style like a helpful friend who knows every hidden gem.

YOUR TASK: Create a complete day-by-day travel itinerary in a clean, readable format.

FORMATTING RULES (CRITICAL — follow exactly):
- Start with a 2-3 sentence overview of the trip vibe
- Use "## 🗓️ Day X: [Theme]" for each day heading
- Use bullet points (•) for each activity/event
- Use emojis strategically: 🚗 for driving, 🍽️ for food, 🏛️ for sightseeing, 🌊 for beach, 🛏️ for hotel, ⏰ for timings, 💰 for costs
- **Bold** place names and important details
- Include (parenthetical tips) in italic for insider advice
- For each activity include: time, place name, what to do, and cost in ₹
- End each day with: 🛏️ Stay: [Hotel name] — ₹[price]/night
- At the very end, add a "## 💰 Budget Summary" section with a line-by-line breakdown

STRICT RULES FOR INDIAN PRICING AND BUDGET:
1. ALL prices in ₹ (INR) only. Never use $ or USD. 1 USD ≈ ₹84.
2. If the budget is tight, force the itinerary to be cheap: use local transport (bus/auto ₹20-150), street food/dhabas (₹50-200/meal), and budget stays/hostels (₹500-1500/night). DO NOT hallucinate high prices. India is very affordable.
3. Stay STRICTLY within ₹{budget:,} total budget for {travellers} traveller(s). If you must, suggest fewer paid activities and more free ones (temples, beaches, walks).
4. Use REAL place names from the research data provided.
5. Transport mode is "{transport}" — ONLY mention this mode.
6. AT THE VERY END OF YOUR RESPONSE, you MUST output a valid JSON block containing the specific places visited AND the estimated total costs for the trip. Provide rough latitude/longitude coordinates for each place. Use this EXACT format, wrapped in ```json ... ```:
```json
{{
  "waypoints": [{{"name": "Baga Beach", "lat": 15.5553, "lng": 73.7517}}],
  "budget_breakdown": {{"transport": 2000, "accommodation": 4500, "food": 3000, "activities": 0, "miscellaneous": 0}}
}}
```
{budget_note}

RESEARCH DATA (use these real places and hotels):
{weather}

{places}

HOTELS:
{hotels}"""

    user_message = f"""Create a {num_days}-day itinerary:

**From:** {origin if origin else 'Not specified'} → **To:** {destination}
**Dates:** {start_date} to {end_date}
**Travellers:** {travellers}
**Budget:** ₹{budget:,} (strict limit)
**Transport:** {transport}
**Interests:** {', '.join(interests) if interests else 'General sightseeing'}
**User's request:** {user_prompt if user_prompt else f'Plan a trip to {destination}'}

Please write the itinerary now. Make it feel like a conversation — friendly, detailed, and actionable."""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ])

        itinerary = response.content if isinstance(response.content, str) else str(response.content)

        # Generate a catchy trip title
        title_response = llm.invoke([
            SystemMessage(content="Generate a short, catchy trip title (max 6 words). Just the title, nothing else. Example: 'Goa Beach Getaway' or 'Royal Rajasthan Adventure'"),
            HumanMessage(content=f"Trip to {destination} for {num_days} days, interests: {', '.join(interests)}"),
        ])
        trip_title = title_response.content.strip().strip('"').strip("'")
        if len(trip_title) > 60:
            trip_title = f"{destination} Adventure"

    except Exception as e:
        itinerary = f"❌ Could not generate itinerary: {str(e)}"
        trip_title = "Planning Error"

    logs = state.get("agent_logs", [])
    logs.append(f"Planner Agent: Generated {num_days}-day itinerary for {destination}.")

    return {
        "itinerary_markdown": itinerary,
        "trip_title": trip_title,
        "agent_logs": logs,
    }
