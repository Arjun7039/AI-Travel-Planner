import os
import requests
from langsmith import traceable
from backend.core.state import TravelState

@traceable(name="weather_agent")
def weather_agent(state: TravelState) -> TravelState:
    """Fetches weather forecast for the destination covering the full trip duration."""
    print("Weather Agent running...")
    
    if "weather_forecast" in state and state["weather_forecast"]:
        print("[Weather Agent] fast-path (already fetched)")
        return state
        
    if "agent_messages" not in state:
        state["agent_messages"] = []

    api_key = os.getenv("OPENWEATHER_API_KEY")
    destination = state.get("destination", "")
    
    if not api_key or not destination:
        state["agent_messages"].append("Weather Agent skipped: No API key or destination.")
        # Provide reasonable defaults so the trip planner has something to work with
        state["weather_forecast"] = _get_default_weather(destination)
        return state

    try:
        # Use 5-day forecast API (free tier gives up to 5 days / 3-hour intervals)
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": destination,
            "appid": api_key,
            "units": "metric",
            "cnt": 40  # Max: 5 days × 8 intervals = 40
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if response.status_code != 200:
            state["agent_messages"].append(f"Weather Agent error: {data.get('message', 'Unknown error')}")
            state["weather_forecast"] = _get_default_weather(destination)
            return state

        # Group forecasts by date to create daily summaries
        daily = {}
        for item in data.get("list", []):
            date = item["dt_txt"].split(" ")[0]
            if date not in daily:
                daily[date] = {"temps": [], "conditions": [], "humidity": [], "rain_prob": [], "wind": []}
            daily[date]["temps"].append(item["main"]["temp"])
            daily[date]["conditions"].append(item["weather"][0]["description"])
            daily[date]["humidity"].append(item["main"]["humidity"])
            daily[date]["rain_prob"].append(item.get("pop", 0) * 100)
            daily[date]["wind"].append(item.get("wind", {}).get("speed", 0))
        
        forecasts = []
        for date, info in daily.items():
            temps = info["temps"]
            conditions = info["conditions"]
            # Find most common condition
            condition = max(set(conditions), key=conditions.count)
            avg_humidity = int(sum(info["humidity"]) / len(info["humidity"]))
            max_rain = max(info["rain_prob"]) if info["rain_prob"] else 0
            avg_wind = round(sum(info["wind"]) / len(info["wind"]), 1)
            
            # Generate packing/activity advice
            temp_high = round(max(temps), 1)
            temp_low = round(min(temps), 1)
            advice = _get_weather_advice(temp_high, condition, max_rain)
            
            forecasts.append({
                "date": date,
                "temp_high": temp_high,
                "temp_low": temp_low,
                "condition": condition.title(),
                "humidity": avg_humidity,
                "rain_probability": round(max_rain, 0),
                "wind_speed_kmh": round(avg_wind * 3.6, 1),
                "advice": advice
            })
            
        state["weather_forecast"] = forecasts
        state["agent_messages"].append(f"Weather Agent: Fetched {len(forecasts)}-day forecast for {destination}.")
        
    except Exception as e:
        state["agent_messages"].append(f"Weather Agent exception: {str(e)}")
        state["weather_forecast"] = _get_default_weather(destination)

    return state


def _get_weather_advice(temp_high, condition, rain_prob):
    """Generate practical weather advice."""
    tips = []
    if temp_high > 35:
        tips.append("Very hot — carry water, sunscreen, and wear light clothing.")
    elif temp_high > 30:
        tips.append("Warm day — stay hydrated and use sunscreen.")
    elif temp_high > 20:
        tips.append("Pleasant weather, perfect for sightseeing.")
    elif temp_high > 10:
        tips.append("Cool weather — carry a light jacket.")
    else:
        tips.append("Cold — dress in warm layers.")
    
    cond_lower = condition.lower()
    if "rain" in cond_lower or rain_prob > 50:
        tips.append("Carry an umbrella or raincoat.")
    if "cloud" in cond_lower:
        tips.append("Overcast skies — good for outdoor photos without harsh shadows.")
    if "clear" in cond_lower:
        tips.append("Clear skies — great for photography and outdoor activities.")
    
    return " ".join(tips)


def _get_default_weather(destination):
    """Return reasonable default weather when API is unavailable."""
    return [
        {"date": "Day 1", "temp_high": 32, "temp_low": 24, "condition": "Partly Cloudy",
         "humidity": 55, "rain_probability": 20, "wind_speed_kmh": 12,
         "advice": "Warm and pleasant. Carry sunscreen and stay hydrated."},
        {"date": "Day 2", "temp_high": 33, "temp_low": 23, "condition": "Sunny",
         "humidity": 50, "rain_probability": 10, "wind_speed_kmh": 10,
         "advice": "Sunny day — perfect for sightseeing. Use sunscreen."},
        {"date": "Day 3", "temp_high": 31, "temp_low": 25, "condition": "Light Rain",
         "humidity": 65, "rain_probability": 60, "wind_speed_kmh": 15,
         "advice": "Possible rain — carry an umbrella. Indoor activities recommended in afternoon."},
    ]
