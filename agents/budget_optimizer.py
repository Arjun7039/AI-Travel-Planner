from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from utils.state import TripState
import os
import json
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

def budget_optimizer_node(state: TripState) -> TripState:
    """Budget Optimizer Agent — analyzes and optimizes trip cost"""

    print("💰 Budget Optimizer Agent working...")

    itinerary = state["daily_itinerary"][0]["raw"] if state["daily_itinerary"] else "No itinerary yet"

    system_prompt = """You are an expert travel budget optimizer.
    Analyze the itinerary and return ONLY a JSON object, nothing else.
    No explanation, no markdown, just raw JSON.
    
    Return this exact structure:
    {
        "cost_breakdown": {
            "accommodation": 0,
            "food": 0,
            "activities": 0,
            "transport": 0,
            "miscellaneous": 0
        },
        "total_estimated_cost": 0,
        "within_budget": true,
        "optimization_suggestions": ["suggestion 1", "suggestion 2"],
        "savings_tips": ["tip 1", "tip 2"]
    }"""

    user_prompt = f"""
    Analyze this itinerary and estimate costs:

    ITINERARY:
    {itinerary}

    CONSTRAINTS:
    - Total budget: ${state["budget"]}
    - Travelers: {state["travelers"]}
    - Origin: {state["origin"]}
    - Destination: {state["destination"]}

    If total cost exceeds budget, set within_budget to false and 
    provide specific cheaper alternatives in optimization_suggestions.
    """

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    # Groq always returns a string, but handle both cases safely
    if isinstance(response.content, list):
        raw = response.content[0].get("text", "") if isinstance(response.content[0], dict) else response.content[0].text
    else:
        raw = response.content

    # Parse JSON
    try:
        raw = raw.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end != 0:
            raw = raw[start:end]
        budget_data = json.loads(raw.strip())

    except Exception as e:
        print(f"JSON parse error: {e}")
        print(f"Raw response was: {raw[:200]}")
        budget_data = {
            "cost_breakdown": {
                "accommodation": 0,
                "food": 0,
                "activities": 0,
                "transport": 0,
                "miscellaneous": 0
            },
            "total_estimated_cost": 0,
            "within_budget": True,
            "optimization_suggestions": ["Could not parse budget data"],
            "savings_tips": []
        }

    within_budget = budget_data.get("within_budget", True)
    total_cost = budget_data.get("total_estimated_cost", 0)

    print(f"   Total estimated: ${total_cost}")
    print(f"   Within budget: {within_budget}")

    return {
        **state,
        "cost_breakdown": budget_data.get("cost_breakdown", {}),
        "total_estimated_cost": total_cost,
        "within_budget": within_budget,
        "optimization_suggestions": budget_data.get("optimization_suggestions", []),
        "messages": state["messages"] + [
            {"role": "assistant", "content": f"Budget analysis complete. Total: ${total_cost}. Within budget: {within_budget}"}
        ]
    }