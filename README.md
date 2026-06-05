# Voyagr AI — Multi-Agent Travel Planner

> An AI-powered travel planning assistant that takes your natural language requests and creates detailed, personalized itineraries using a multi-agent pipeline.

## ✨ Features

- **Natural Language Input** — Just type "Take me to Goa for 3 days, ₹15k budget" and get a complete itinerary
- **Smart Prompt Enhancement** — AI understands and enhances your casual travel request
- **3-Agent Pipeline** — Research Agent → Planner Agent → Budget Agent (powered by LangGraph)
- **Real-Time Streaming** — Watch your itinerary being created in real-time via SSE
- **ChatGPT-Style Display** — Beautiful conversational itinerary with rich formatting
- **Budget Optimization** — Automatic cost validation and budget enforcement
- **Auth System** — JWT-based login/signup with free trial for anonymous users
- **Modern UI** — Dark mode, glassmorphism, smooth animations

## 🏗️ Architecture

```
User Input (Natural Language)
        │
        ▼
  [Prompt Enhancer]  ← Groq LLM extracts & enhances
        │
        ▼
  ┌─────────────────────┐
  │  LangGraph Pipeline  │
  │                       │
  │  1. Research Agent    │ ← Tavily + OpenWeatherMap (parallel)
  │  2. Planner Agent     │ ← Groq llama-3.3-70b (markdown output)
  │  3. Budget Agent      │ ← Pure logic validation
  │                       │
  │  [Replan loop ×2]     │
  └─────────────────────┘
        │
        ▼
  SSE Stream → React Frontend
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | Groq API (llama-3.3-70b-versatile) |
| **Agent Orchestration** | LangGraph |
| **Backend** | FastAPI (Python) |
| **Frontend** | React 19 + TypeScript + Vite |
| **Search** | Tavily API |
| **Weather** | OpenWeatherMap API |
| **Database** | SQLite + SQLAlchemy |
| **Auth** | JWT (python-jose + bcrypt) |
| **Streaming** | Server-Sent Events (SSE) |

## 🚀 Quick Setup

### 1. Clone & Install Backend
```bash
git clone https://github.com/yourusername/ai-travel-planner.git
cd ai-travel-planner
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Add your API keys: GROQ_API_KEY, TAVILY_API_KEY, OPENWEATHER_API_KEY
```

### 3. Start Backend
```bash
uvicorn backend.main:app --reload --port 8000
```

### 4. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 5. Open
Visit `http://localhost:3000` and start planning!

## 📁 Project Structure

```
ai-travel-planner/
├── backend/
│   ├── agents/
│   │   ├── research_agent.py    # Weather + Places + Hotels (parallel)
│   │   ├── planner_agent.py     # LLM itinerary generation
│   │   ├── budget_agent.py      # Cost validation (no LLM)
│   │   └── prompt_enhancer.py   # NLP prompt parsing
│   ├── api/
│   │   ├── routes/
│   │   │   ├── plan.py          # /enhance + /stream endpoints
│   │   │   ├── auth.py          # JWT login/register
│   │   │   └── trips.py         # Saved trips
│   │   └── schemas.py
│   ├── core/
│   │   ├── graph.py             # LangGraph pipeline
│   │   └── state.py             # TravelState TypedDict
│   ├── db/
│   │   ├── models.py            # SQLAlchemy models
│   │   └── session.py           # DB session
│   └── main.py                  # FastAPI entry
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── ConversationView.tsx  # ChatGPT-style itinerary
│       │   ├── PlanningProgress.tsx  # Agent progress display
│       │   ├── Navbar.tsx
+       │   └── Footer.tsx
│       ├── pages/
│       │   ├── LandingPage.tsx      # Main page (all stages)
│       │   ├── LoginPage.tsx
│       │   └── SignupPage.tsx
│       ├── App.tsx
│       ├── App.css
│       └── index.css
├── requirements.txt
├── .env
└── README.md
```

## 📜 License

MIT License — feel free to use, modify, and share.
