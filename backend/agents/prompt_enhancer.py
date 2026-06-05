"""Prompt Enhancer — Turns casual natural language into structured travel parameters.

This is the "wow" feature. User types something casual like:
  "take me to goa for 3 days, 15k budget, love beaches and nightlife"

And this agent:
1. Extracts structured parameters (destination, dates, budget, etc.)
2. Enhances the prompt with smart suggestions
3. Returns both the structured data AND an enhanced description
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()


def enhance_prompt(user_text: str) -> dict:
    """Take a natural language travel request and return structured parameters + enhanced prompt.
    
    Returns:
        {
            "destination": "Goa",
            "origin": "",
            "start_date": "2026-06-15",
            "end_date": "2026-06-18",
            "num_travellers": 2,
            "budget_inr": 15000,
            "transport_mode": "Flight",
            "interests": ["beaches", "nightlife"],
            "enhanced_prompt": "A 3-day beach and nightlife getaway to Goa...",
            "trip_title": "Goa Beach Getaway"
        }
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return _fallback_parse(user_text)

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=api_key,
        temperature=0.3,
        max_tokens=800,
    )

    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    system_prompt = f"""You are a travel query parser. Extract travel parameters from the user's natural language input.

RESPOND WITH ONLY VALID JSON — no markdown, no explanation, no extra text.

Today's date is {today}. If the user doesn't specify dates, suggest dates starting 7 days from today.

JSON STRUCTURE (fill in all fields):
{{
    "destination": "City/Place name",
    "origin": "Origin city if mentioned, else empty string",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "num_travellers": 2,
    "budget_inr": 50000,
    "transport_mode": "Flight or Train or Car",
    "interests": ["list", "of", "interests"],
    "enhanced_prompt": "A rich, enhanced 2-3 sentence description of what the user wants — expand on their interests, add context, make it vivid. This will be used to brief the AI planner.",
    "trip_title": "Short catchy title, 3-5 words max"
}}

RULES:
- If budget is mentioned in USD/dollars, convert to INR (1 USD = ₹84)
- If budget is not mentioned, estimate a reasonable budget based on destination and duration
- If number of days is mentioned (e.g., "3 days"), calculate end_date from start_date
- If transport mode is not mentioned, default to "Flight" for inter-city, "Car" for nearby destinations (<300km)
- interests should be lowercase keywords like ["beaches", "food", "culture", "adventure", "nightlife", "shopping", "temples", "nature", "trekking", "photography"]
- The enhanced_prompt should be vivid and detailed — transform a simple "goa 3 days" into "An exciting 3-day coastal adventure in Goa, exploring golden beaches, vibrant nightlife, fresh seafood, and the unique Portuguese-influenced culture of India's party paradise."
"""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Parse this travel request: {user_text}"),
        ])

        raw = response.content if isinstance(response.content, str) else str(response.content)

        # Extract JSON from response
        raw = raw.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            raw = raw[start:end]

        parsed = json.loads(raw)

        # Validate and clean
        result = {
            "destination": parsed.get("destination", "").strip(),
            "origin": parsed.get("origin", "").strip(),
            "start_date": parsed.get("start_date", tomorrow),
            "end_date": parsed.get("end_date", ""),
            "num_travellers": max(1, int(parsed.get("num_travellers", 2))),
            "budget_inr": max(1000, float(parsed.get("budget_inr", 50000))),
            "transport_mode": parsed.get("transport_mode", "Flight"),
            "interests": parsed.get("interests", ["sightseeing"]),
            "enhanced_prompt": parsed.get("enhanced_prompt", user_text),
            "trip_title": parsed.get("trip_title", f"Trip to {parsed.get('destination', 'Unknown')}"),
        }

        # Ensure end_date is after start_date
        if not result["end_date"] or result["end_date"] <= result["start_date"]:
            try:
                start = datetime.strptime(result["start_date"], "%Y-%m-%d")
                result["end_date"] = (start + timedelta(days=3)).strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                result["end_date"] = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")

        if not result["destination"]:
            result["destination"] = "Unknown Destination"

        return result

    except Exception as e:
        print(f"Prompt enhancement error: {e}")
        return _fallback_parse(user_text)


def _fallback_parse(text: str) -> dict:
    """Basic fallback parser when LLM is unavailable."""
    today = datetime.now()
    return {
        "destination": text.strip()[:50] if text else "Unknown",
        "origin": "",
        "start_date": (today + timedelta(days=7)).strftime("%Y-%m-%d"),
        "end_date": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
        "num_travellers": 2,
        "budget_inr": 50000,
        "transport_mode": "Flight",
        "interests": ["sightseeing", "food"],
        "enhanced_prompt": text,
        "trip_title": f"Trip to {text.strip()[:30]}",
    }
