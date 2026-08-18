from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.database.models import User
from app.ai.agent import process_ai_chat_message
from app.ai.memory import AIMemory

router = APIRouter(prefix="/ai", tags=["AI Travel Assistant"])


class AIChatRequest(BaseModel):
    message: str
    trip_context: Optional[Dict[str, Any]] = None


class AIChatResponse(BaseModel):
    response: str
    trip_data: Optional[Dict[str, Any]] = None


@router.post("/chat", response_model=AIChatResponse)
def ai_chat_endpoint(
    data: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Processes natural-language travel queries using local SQLite retrieval tools
    and returns a structured natural-language response.
    """
    if not data.message or not data.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    current_state = data.trip_context or AIMemory.get_state(current_user.id)
    result = process_ai_chat_message(db, current_user, data.message, current_state)

    if result.get("trip_data"):
        AIMemory.set_state(current_user.id, result["trip_data"])

    return AIChatResponse(
        response=result["response"],
        trip_data=result.get("trip_data")
    )
