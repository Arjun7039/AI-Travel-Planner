import requests
import json

url = "http://localhost:8000/api/plan/stream"
data = {
    "origin": "Bengaluru",
    "destination": "Goa",
    "start_date": "2026-10-10",
    "end_date": "2026-10-15",
    "num_travellers": 2,
    "budget_inr": 50000,
    "preferences": {
        "accommodation": "mid-range",
        "activities": ["sightseeing"],
        "cuisine": ["local"]
    }
}

try:
    response = requests.post(url, json=data, stream=True)
    print("Status Code:", response.status_code)
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))
except Exception as e:
    print("Request failed:", e)
