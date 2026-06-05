from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

def search_places(destination: str, category: str) -> str:
    """Search for places/activities using Tavily"""
    try:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        
        query = f"best {category} places to visit in {destination} with estimated costs"
        response = client.search(query=query, max_results=5)
        
        results = []
        for r in response["results"]:
            results.append(f"- {r['title']}: {r['content'][:150]}")
        
        return "\n".join(results)

    except Exception as e:
        return f"Places search failed: {str(e)}"


def search_hotels(destination: str, budget_per_night: float) -> str:
    """Search for hotels within budget"""
    try:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        
        query = f"budget hotels in {destination} under ${budget_per_night} per night"
        response = client.search(query=query, max_results=3)
        
        results = []
        for r in response["results"]:
            results.append(f"- {r['title']}: {r['content'][:150]}")
        
        return "\n".join(results)

    except Exception as e:
        return f"Hotel search failed: {str(e)}"