import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_weather(destination: str) -> str:
    """Get weather forecast for destination"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": destination,
            "appid": api_key,
            "units": "metric",
            "cnt": 5  # next 5 forecasts
        }
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200:
            return f"Weather unavailable for {destination}"

        # Extract useful summary
        forecasts = []
        for item in data["list"][:3]:
            desc = item["weather"][0]["description"]
            temp = item["main"]["temp"]
            forecasts.append(f"{desc}, {temp}°C")

        return f"Weather in {destination}: " + " | ".join(forecasts)

    except Exception as e:
        return f"Weather fetch failed: {str(e)}"