from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.database.models import User, Favorite

router = APIRouter(prefix="/favorites", tags=["Favorites"])


class FavoriteCreate(BaseModel):
    item_type: str  # destination, place, stay, food_spot
    item_id: int
    title: str
    subtitle: Optional[str] = None
    image: Optional[str] = None


@router.get("")
def list_user_favorites(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns user-isolated list of favorite places, destinations, stays, and foods.
    """
    favs = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    return favs


@router.post("", status_code=status.HTTP_201_CREATED)
def add_favorite(data: FavoriteCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.item_type == data.item_type,
        Favorite.item_id == data.item_id
    ).first()

    if existing:
        return existing

    fav = Favorite(
        user_id=current_user.id,
        item_type=data.item_type,
        item_id=data.item_id,
        title=data.title,
        subtitle=data.subtitle,
        image=data.image
    )
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return fav


@router.delete("/{favorite_id}")
def delete_favorite(favorite_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    fav = db.query(Favorite).filter(Favorite.id == favorite_id, Favorite.user_id == current_user.id).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite item not found.")
    db.delete(fav)
    db.commit()
    return {"message": "Favorite item removed successfully."}
