"""Research Agent — Fetches weather, places, and hotels in parallel.

This single agent replaces the old flight_agent + weather_agent + hotel_agent
+ local_experience_agent. It runs all API calls concurrently using ThreadPoolExecutor,
completing in ~2 seconds instead of ~12 seconds sequentially.
"""

import os
import requests
import concurrent.futures
from backend.core.state import TravelState


def _fetch_weather(destination: str) -> str:
    """Fetch 5-day weather forecast from OpenWeatherMap."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Weather data unavailable."

    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {"q": destination, "appid": api_key, "units": "metric", "cnt": 24}
        resp = requests.get(url, params=params, timeout=8)
        data = resp.json()

        if resp.status_code != 200:
            return f"Weather unavailable for {destination}."

        # Group by date and summarize
        daily = {}
        for item in data.get("list", []):
            date = item["dt_txt"].split(" ")[0]
            if date not in daily:
                daily[date] = {"temps": [], "conditions": []}
            daily[date]["temps"].append(item["main"]["temp"])
            daily[date]["conditions"].append(item["weather"][0]["description"])

        lines = []
        for date, info in list(daily.items())[:5]:
            avg_temp = round(sum(info["temps"]) / len(info["temps"]), 1)
            condition = max(set(info["conditions"]), key=info["conditions"].count)
            lines.append(f"  {date}: {condition}, {avg_temp}°C")

        return f"Weather forecast for {destination}:\n" + "\n".join(lines)

    except Exception as e:
        return f"Weather fetch failed: {str(e)}"


def _search_tavily(query: str, max_results: int = 5) -> str:
    """Search using Tavily API and return formatted results."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Search unavailable (no API key)."

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        response = client.search(query=query, search_depth="basic", max_results=max_results)

        results = []
        for r in response.get("results", []):
            title = r.get("title", "").split(" - ")[0].split(" | ")[0].strip()
            content = r.get("content", "")[:200]
            if title and content:
                results.append(f"  • {title}: {content}")

        return "\n".join(results) if results else "No results found."

    except Exception as e:
        return f"Search failed: {str(e)}"


def _fetch_places(destination: str) -> str:
    """Search for attractions and restaurants."""
    attractions = _search_tavily(
        f"best tourist attractions places to visit in {destination} with timings and entry fees in INR",
        max_results=5,
    )
    restaurants = _search_tavily(
        f"best restaurants local food street food in {destination} with prices in INR",
        max_results=5,
    )
    return f"TOP ATTRACTIONS:\n{attractions}\n\nBEST FOOD & RESTAURANTS:\n{restaurants}"


def _fetch_hotels(destination: str, budget_per_night: float) -> str:
    """Search for hotels within budget."""
    if budget_per_night < 1500:
        tier = "budget guest house hostel OYO"
    elif budget_per_night < 5000:
        tier = "mid-range 3-star hotel"
    else:
        tier = "luxury 4-star 5-star hotel"

    return _search_tavily(
        f"best {tier} in {destination} prices per night in INR reviews",
        max_results=4,
    )

def _fetch_flights(origin: str, destination: str) -> str:
    """Search for average flight prices."""
    if not origin:
        return "Flight search skipped (no origin)."
    return _search_tavily(
        f"average flight price from {origin} to {destination} return economy INR",
        max_results=3,
    )


def research_agent(state: TravelState) -> dict:
    """Fetch weather, places, and hotels in parallel (~2s total)."""
    print("🔍 Research Agent: Gathering data...")

    destination = state.get("destination", "Unknown")
    origin = state.get("origin", "")
    budget = state.get("budget_inr", 50000)
    start_date = state.get("start_date", "")
    end_date = state.get("end_date", "")

    # Calculate budget per night for hotel tier
    num_days = 3
    if start_date and end_date:
        try:
            from datetime import datetime
            d1 = datetime.strptime(start_date, "%Y-%m-%d")
            d2 = datetime.strptime(end_date, "%Y-%m-%d")
            num_days = max(1, (d2 - d1).days)
        except (ValueError, TypeError):
            pass

    hotel_budget_per_night = (budget * 0.30) / max(num_days, 1)

    # Run all 4 searches in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        weather_future = executor.submit(_fetch_weather, destination)
        places_future = executor.submit(_fetch_places, destination)
        hotels_future = executor.submit(_fetch_hotels, destination, hotel_budget_per_night)
        flights_future = executor.submit(_fetch_flights, origin, destination)

        weather_data = weather_future.result(timeout=15)
        places_data = places_future.result(timeout=15)
        hotels_data = hotels_future.result(timeout=15)
        flights_data = flights_future.result(timeout=15)

    logs = state.get("agent_logs", [])
    logs.append(f"Research Agent: Gathered weather, places, and hotels for {destination}.")

    return {
        "weather_data": weather_data,
        "places_data": places_data,
        "hotels_data": hotels_data,
        "flights_data": flights_data,
        "agent_logs": logs,
    }
