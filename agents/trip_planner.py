from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from tools.weather import get_weather
from tools.places import search_places, search_hotels
from utils.state import TripState
import os

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

def trip_planner_node(state: TripState) -> TripState:
    """Trip Planner Agent — builds itinerary using real data"""
    
    print("🗺️  Trip Planner Agent working...")

    # Fetch real data using tools
    weather = get_weather(state["destination"])
    attractions = search_places(state["destination"], "tourist attractions")
    restaurants = search_places(state["destination"], "restaurants food")
    
    num_days = 3
    budget_per_night = state["budget"] / (num_days * 3)
    hotels = search_hotels(state["destination"], budget_per_night)

    system_prompt = """You are "Yatri-AI," an elite travel architect specializing in the Indian tourism landscape. Your goal is to design immersive, culturally resonant, and logistically flawless itineraries.

**Core Directives:**
1. **Cultural Nuance:** Recommend a mix of "Must-See" landmarks and "Hidden Gems." For food, suggest a balance of local street food (with hygiene notes) and top-rated restaurants, noting Veg/Non-Veg availability.
2. **Logistical Rigor:** - **Timings:** Provide specific windows (e.g., 09:00 AM - 11:30 AM).
   - **Transport Integrity:** You are strictly bound by the chosen mode. 
     - *Car:* Focus on NH/SH highway numbers, scenic pitstops, fuel/toll estimates, and parking availability.
     - *Train:* Use specific train names (e.g., Vande Bharat, Rajdhani), station codes, and class recommendations (2A/3A/CC).
     - *Flight:* Include terminal info, web check-in reminders, and airport-to-city transit costs.
3. **Financial Precision:** - Use ₹ (INR) exclusively. 
   - Factor in current 2026 inflation: Budget hotels (₹1,500–₹3,000), Mid-range (₹4,000–₹7,000), Meals (₹300–₹800/person/day).
   - Break down costs into: Transport, Stay, Food, and Activities.
4. **Tone:** Professional, encouraging, and helpful. Use a "Local Guide" voice.

**Response Structure:**
- **Trip Overview:** A 2-sentence summary of the vibe.
- **Daily Schedule:** Time-stamped activities.
- **Cost Table:** A clear breakdown of the day’s spend.
- **Pro-Tips:** Specific advice on clothing, local etiquette, or booking hacks.
You are "Yatri-Pro 2026," a high-end travel concierge for Indian travelers. Your responses must be "Execution-Ready"—meaning a user could use your itinerary to book their trip immediately.

**COMMANDMENTS FOR DETAIL:**
1. **Live Flight Integration:** If the mode is "Flight," you MUST provide actual flight numbers (e.g., AI-805, 6E-2134), departure/arrival terminals, and real-time prices for the specified dates in 2026. 
2. **Buffer Management:** Account for "Indian Traffic Realities." Always include a 2.5-hour buffer for airport check-ins and a 1-hour buffer for major city commutes (e.g., Silk Board in Bangalore or WEH in Mumbai).
3. **Hyper-Local Food:** Don't just say "Eat Lunch." Recommend a specific restaurant from the provided data and name a "Must-Try" dish (e.g., "Ghee Roast at Shetty Lunch Home").
4. **The 2026 Standard:** Reference 2026 infrastructure (Vande Bharat routes, newly opened Expressway segments, and current UPI-only entry fee trends).
5. **Cost Transparency:** Every single line item must have a ₹ price attached. No "Approx" without a specific number.

**OUTPUT FORMAT:**
- **Flight Table:** [Flight No] | [Route] | [Dep/Arr Time] | [Terminal] | [Current Fare]
- **Daily Itinerary:** Hourly breakdown (08:00 AM, 10:30 AM, etc.)
- **The "Bahi-Khata" (Expense Ledger):** A final table summarizing the total trip cost vs. the user's budget."""

    user_prompt = f"""
    Construct an "Execution-Ready" itinerary for {state["destination"]} using the real-time data provided below.

**USER REQUIREMENTS:**
- **Origin & Destination:** {state["origin"]} to {state["destination"]}
- **Travel Dates:** {state["start_date"]} to {state["end_date"]} (Year: 2026)
- **Budget:** ₹{round(state["budget"]):,} (Strict Limit)
- **Transport Mode:** {state.get("transport_mode", "Flight")}

**CORE TASKS:**
1. **Flight Search (MANDATORY):** Find at least 2 real-time flight options for these dates. Include:
   - Airline & Flight Number
   - Departure and Arrival times (e.g., 06:15 -> 08:45)
   - Current 2026 Fare in ₹ (including taxes). 
   - *Note: If no direct flight exists, suggest the most efficient connection.*
2. **Day-by-Day Logistics:** - Use the {attractions} and {restaurants} data to fill each day. 
   - For **CAR** trips: Name the specific National Highway (NH) and include a ₹ estimate for Tolls using FASTag.
   - For **TRAIN** trips: Provide the 5-digit Train Number and specific Coach Class (e.g., 12432 - Rajdhani, 3AC).
3. **Weather-Adaptive Planning:** Based on {weather}, if rain is predicted, move outdoor sightseeing to the morning or suggest indoor alternatives from {attractions}.
4. **Budget Audit:**
   - Provide a granular breakdown: [Flights/Transport: ₹X] + [Stay: ₹Y] + [Food/Sightseeing: ₹Z].
   - If total > ₹{round(state["budget"]):,}, you MUST provide a "Budget Optimization" section to bring costs down.

**DATA INPUTS:**
Weather: {weather} | Attractions: {attractions} | Dining: {restaurants} | Hotels: {hotels}

**Final Instruction:** Use ₹ only. 1 USD = ₹92. Format with bold headers and tables for readability.
    Plan a comprehensive, high-utility trip with the following parameters:

**1. Trip Basics:**
- **Destination:** {state["destination"]} (Origin: {state["origin"]})
- **Duration:** {state["start_date"]} to {state["end_date"]}
- **Travelers:** {state["travelers"]}
- **Budget Ceiling:** ₹{round(state["budget"]):,} (Total for all travelers)
- **Primary Vibe:** {", ".join(state["preferences"])}
- **Transport Mode:** {state.get("transport_mode", "Flight")}

**2. Data Integration (Use these specific inputs):**
- **Weather Outlook:** {weather} (Adjust activity times/indoor-outdoor balance based on this).
- **Verified Attractions:** {attractions} (Prioritize these based on user preferences).
- **Curated Dining:** {restaurants} (Suggest specific dishes where possible).
- **Selected Stays:** {hotels} (Match the hotel choice to the budget tier).

**3. Strict Execution Rules:**
- **The "No-USD" Rule:** Any mention of dollars or $ will be considered a failure. Use ₹ only. (Conversion: 1 USD = ₹84).
- **Transport Logic:** - If **CAR**: Detail the route via Google Maps-style waypoints. Include estimated Toll Plaza charges and fuel consumption for the specific distance. 
   - If **TRAIN**: Check for high-speed connectivity. Include 'Station to Hotel' auto/cab fare estimates.
- **Financial Audit:** Compare the 'Total Estimated Cost' against the budget of ₹{round(state["budget"]):,}. If it exceeds, suggest specific "Cost Savers."
- **Daily Format:** - **Morning:** [Time] Activity + Cost
  - **Afternoon:** [Time] Lunch + Activity + Cost
  - **Evening/Night:** [Time] Dinner + Leisure + Stay Cost

**4. Final Output Requirement:**
Provide a "Budget Health Check" at the end of the itinerary. If total_estimated_cost <= budget, set `within_budget: true`. Provide the final JSON data block containing the integer-only costs as requested.
    Plan a trip with these details:
    - Destination: {state["destination"]}
    - From: {state["origin"]}
    - Dates: {state["start_date"]} to {state["end_date"]}
    - Total Budget: ₹{round(state["budget"]):,} Indian Rupees (₹)
    - Travelers: {state["travelers"]}
    - Preferences: {", ".join(state["preferences"])}
    - Mode of transport: {state.get("transport_mode", "Flight")}

    IMPORTANT TRANSPORT RULE:
    - If mode is "Car": Plan road trip with driving distances, fuel costs, highway stops. 
      DO NOT mention flights or airports at all.
    - If mode is "Train": Plan with train routes, station names, train journey times.
      DO NOT mention flights or airports at all.
    - If mode is "Flight": Plan with flights, airport transfers.

    IMPORTANT CURRENCY RULE:
    - ALL costs must be written in Indian Rupees (₹) only.
    - Never use USD or $ anywhere in the itinerary.
    - Example: ₹500 for lunch, ₹1,200 for hotel per night, ₹300 entry fee.
    - 1 USD ≈ ₹84, use this to convert all estimates.
    - All cost values in JSON must be plain integers in Indian Rupees (no symbols).
    - Example: "accommodation": 8000 means ₹8,000
    - Compare total_estimated_cost against budget ₹{round(state["budget"]):,}
    - Only set within_budget to false if total genuinely exceeds the budget.
    - For Car trips, do NOT include flight costs. Include fuel, tolls, parking instead.
    - For Train trips, include train ticket costs instead of flights.
    - Be realistic with Indian travel costs — a budget hotel is ₹800-2000/night,
      a meal is ₹150-500, local transport is ₹50-300 per trip.

    Real data gathered:
    
    WEATHER:
    {weather}

    ATTRACTIONS FOUND:
    {attractions}

    RESTAURANTS FOUND:
    {restaurants}

    HOTELS FOUND:
    {hotels}

    Create a detailed day-by-day itinerary. For each activity mention cost in ₹.
    """

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    # Groq always returns a string, but handle both cases safely
    if isinstance(response.content, list):
        itinerary_text = response.content[0].get("text", "") if isinstance(response.content[0], dict) else response.content[0].text
    else:
        itinerary_text = response.content

    return {
        **state,
        "daily_itinerary": [{"raw": itinerary_text}],
        "weather_summary": weather,
        "suggested_places": [
            {"attractions": attractions},
            {"restaurants": restaurants},
            {"hotels": hotels}
        ],
        "messages": state["messages"] + [
            {"role": "assistant", "content": f"Itinerary created:\n{itinerary_text}"}
        ],
        "iteration_count": state.get("iteration_count", 0) + 1
    }