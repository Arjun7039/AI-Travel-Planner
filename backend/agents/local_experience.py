import os
from tavily import TavilyClient
from langsmith import traceable
from backend.core.state import TravelState
from backend.rag.retriever import retrieve_context

@traceable(name="local_experience_agent")
def local_experience_agent(state: TravelState) -> TravelState:
    """Enriches the itinerary with real local experiences, food, and hidden gems."""
    print("[Local Experience Agent] running...")
    
    if "local_experiences" in state and state["local_experiences"]:
        print("[Local Experience Agent] fast-path (already fetched)")
        return state
        
    if "agent_messages" not in state:
        state["agent_messages"] = []

    destination = state.get("destination", "Unknown")
    budget = state.get("budget_inr", 50000)
    
    # Retrieve local context from RAG
    query = f"Hidden gems, local food, cultural experiences, and insider tips for {destination}"
    rag_context = retrieve_context(query)
    state["rag_context"] = rag_context
    
    # Try Tavily for real local experiences
    api_key = os.getenv("TAVILY_API_KEY")
    if api_key:
        try:
            tavily = TavilyClient(api_key=api_key)
            
            # Search for local experiences
            exp_query = f"best local experiences things to do hidden gems street food in {destination} for tourists"
            response = tavily.search(query=exp_query, search_depth="basic", max_results=5)
            
            experiences = []
            for res in response.get("results", []):
                title = res.get("title", "").split(" - ")[0].split(" | ")[0].strip()
                content = res.get("content", "")
                if len(title) > 5 and len(content) > 20:
                    experiences.append({
                        "title": title[:80],
                        "description": content[:200],
                        "source": res.get("url", ""),
                        "estimated_cost_inr": 0
                    })
            
            state["local_experiences"] = experiences[:5]
            state["agent_messages"].append(f"Local Experience Agent: Found {len(experiences[:5])} experiences in {destination}.")
        except Exception as e:
            state["agent_messages"].append(f"Local Experience Agent search error: {str(e)}")
            state["local_experiences"] = []
    else:
        state["local_experiences"] = []
        state["agent_messages"].append("Local Experience Agent: Added RAG context (no Tavily key for live search).")
    
    return state
