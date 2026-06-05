"""Trips API routes — fetch saved trips for authenticated users."""

import os
from fastapi import APIRouter, Header, HTTPException
from jose import jwt
from backend.db.session import SessionLocal
from backend.db.models import User, Trip

router = APIRouter()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "voyagr-super-secret-key-change-in-production-2026")
ALGORITHM = "HS256"


@router.get("/")
async def get_user_trips(authorization: str = Header(None)):
    """Get all trips for the authenticated user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        trips = db.query(Trip).filter(Trip.user_id == user.id).order_by(Trip.created_at.desc()).all()
        return [
            {
                "id": str(trip.id),
                "destination": trip.destination,
                "origin": trip.origin,
                "start_date": str(trip.start_date) if trip.start_date else "",
                "end_date": str(trip.end_date) if trip.end_date else "",
                "budget_inr": float(trip.budget_inr) if trip.budget_inr else 0,
                "result": trip.result,
                "created_at": str(trip.created_at) if trip.created_at else "",
            }
            for trip in trips
        ]
    finally:
        db.close()
