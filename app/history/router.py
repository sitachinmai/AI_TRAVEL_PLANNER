from typing import List, Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.database.models import User, TravelHistory

router = APIRouter(prefix="/history", tags=["Travel History"])


class HistoryCreate(BaseModel):
    item_type: str
    item_id: int
    title: str


@router.get("")
def list_user_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns user-isolated recently viewed destinations and places.
    """
    history = db.query(TravelHistory).filter(TravelHistory.user_id == current_user.id).order_by(TravelHistory.viewed_at.desc()).limit(20).all()
    return history


@router.post("", status_code=status.HTTP_201_CREATED)
def record_history(data: HistoryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = TravelHistory(
        user_id=current_user.id,
        item_type=data.item_type,
        item_id=data.item_id,
        title=data.title
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("")
def clear_user_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(TravelHistory).filter(TravelHistory.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Travel history cleared successfully."}
