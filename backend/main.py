from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import plan, auth, trips
from backend.db.session import engine
from backend.db.models import Base

# Create DB tables (SQLite — zero config)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Voyagr AI Travel Planner",
    description="Multi-agent AI travel planning with natural language input",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plan.router, prefix="/api/plan", tags=["Planning"])
app.include_router(auth.router, prefix="/api/user", tags=["Auth"])
app.include_router(trips.router, prefix="/api/trips", tags=["Trips"])


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": "2.0.0"}
