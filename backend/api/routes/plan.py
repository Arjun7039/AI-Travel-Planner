"""Plan API routes — handles prompt enhancement and trip generation via SSE streaming."""

import json
import asyncio
import traceback
import os
from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from jose import jwt

from backend.api.schemas import PlanRequest, EnhanceRequest, EnhanceResponse
from backend.agents.prompt_enhancer import enhance_prompt
from backend.core.graph import build_graph
from backend.db.session import SessionLocal
from backend.db.models import User, Trip

router = APIRouter()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "voyagr-super-secret-key-change-in-production-2026")
ALGORITHM = "HS256"

# Track free trial usage: {ip: count}
_free_trials = {}


def _get_user_email(authorization: str) -> str | None:
    """Extract user email from JWT token."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except Exception:
        return None


@router.post("/enhance", response_model=EnhanceResponse)
async def enhance_user_prompt(request: EnhanceRequest):
    """Enhance a natural language travel prompt into structured parameters."""
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    result = enhance_prompt(request.prompt)
    return EnhanceResponse(**result)


@router.post("/stream")
async def plan_trip_stream(
    http_req: Request,
    request: PlanRequest,
    authorization: str = Header(None),
):
    """Stream trip planning progress via SSE."""

    async def event_generator():
        try:
            # 1. Check authentication & free trial limit
            email = _get_user_email(authorization)
            client_ip = http_req.client.host if http_req.client else "unknown"

            if not email:
                # Anonymous user — check free trial
                if _free_trials.get(client_ip, 0) >= 1:
                    yield _sse({
                        "agent": "system",
                        "status": "error",
                        "message": "Free trial used! Sign up for a free account to generate unlimited itineraries.",
                    })
                    return
                _free_trials[client_ip] = _free_trials.get(client_ip, 0) + 1

            # 2. Build initial state
            initial_state = {
                "destination": request.destination,
                "origin": request.origin,
                "start_date": str(request.start_date),
                "end_date": str(request.end_date),
                "num_travellers": request.num_travellers,
                "budget_inr": request.budget_inr,
                "transport_mode": request.transport_mode,
                "interests": request.interests,
                "user_prompt": request.user_prompt,
                "agent_logs": [],
                "replan_count": 0,
                "within_budget": True,
            }

            # 3. Stream agent progress
            yield _sse({
                "agent": "research",
                "status": "running",
                "message": "Gathering weather, attractions, and hotels...",
            })
            await asyncio.sleep(0.1)

            # Run the graph
            graph = build_graph()
            final_state = await asyncio.to_thread(graph.invoke, initial_state)

            # Stream agent completion messages
            for log in final_state.get("agent_logs", []):
                yield _sse({"agent": "system", "status": "update", "message": log})
                await asyncio.sleep(0.05)

            # Build result
            result = {
                "itinerary_markdown": final_state.get("itinerary_markdown", ""),
                "trip_title": final_state.get("trip_title", "Your Trip"),
                "budget_breakdown": final_state.get("budget_breakdown", {}),
                "total_cost": final_state.get("total_cost", 0),
                "within_budget": final_state.get("within_budget", True),
                "origin": request.origin,
                "destination": request.destination,
                "transport_mode": request.transport_mode,
            }

            # 4. Save trip if user is logged in
            if email:
                _save_trip(email, request, result)

            yield _sse({
                "agent": "complete",
                "status": "complete",
                "result": result,
            })

        except Exception as e:
            print(f"[Plan Error] {traceback.format_exc()}")
            yield _sse({
                "agent": "system",
                "status": "error",
                "message": f"Something went wrong: {str(e)}",
            })

    return StreamingResponse(event_generator(), media_type="text/event-stream")


def _sse(data: dict) -> str:
    """Format data as an SSE event."""
    return f"data: {json.dumps(data)}\n\n"


def _save_trip(email: str, request: PlanRequest, result: dict):
    """Save a generated trip to the database."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            trip = Trip(
                user_id=user.id,
                origin=request.origin,
                destination=request.destination,
                start_date=request.start_date,
                end_date=request.end_date,
                num_travellers=request.num_travellers,
                budget_inr=request.budget_inr,
                preferences={"interests": request.interests, "transport": request.transport_mode},
                result=result,
            )
            db.add(trip)
            db.commit()
    except Exception as e:
        print(f"[DB Error] Save trip failed: {e}")
    finally:
        db.close()
