# Voyagr AI — Simplified System Spec v2

## Architecture
- 3-agent LangGraph pipeline: Research → Planner → Budget
- Prompt Enhancer for natural language input
- FastAPI backend with SSE streaming
- React + TypeScript frontend (ChatGPT-style UI)
- SQLite for auth & trip storage
- No RAG, no Redis, no Docker, no LangSmith

## Tech Stack
- **LLM:** Groq API — llama-3.3-70b-versatile
- **Agents:** LangGraph
- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Frontend:** React 19 + Vite + Vanilla CSS
- **APIs:** Tavily (search), OpenWeatherMap (weather)
- **Auth:** JWT (python-jose + bcrypt)

## Key Design Decisions
- Itinerary output is conversational markdown (not JSON)
- Single-page flow: input → enhance → confirm → generate → display
- Budget Agent uses pure regex extraction (no LLM call = fast)
- Research Agent runs 3 API calls in parallel (ThreadPoolExecutor)
- Free trial: 1 generation per IP, unlimited for signed-in users
