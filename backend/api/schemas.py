from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class PlanRequest(BaseModel):
    """Request body for trip planning."""
    destination: str
    origin: str = ""
    start_date: date
    end_date: date
    num_travellers: int = 2
    budget_inr: float = 50000
    transport_mode: str = "Flight"
    interests: List[str] = ["sightseeing", "food"]
    user_prompt: str = ""


class EnhanceRequest(BaseModel):
    """Request body for prompt enhancement."""
    prompt: str


class EnhanceResponse(BaseModel):
    """Response from prompt enhancement."""
    destination: str
    origin: str
    start_date: str
    end_date: str
    num_travellers: int
    budget_inr: float
    transport_mode: str
    interests: List[str]
    enhanced_prompt: str
    trip_title: str


class UserCreate(BaseModel):
    name: str = ""
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    name: Optional[str] = ""
