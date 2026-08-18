from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user_optional
from app.database.models import User
from app.travel.service import (
    get_all_destinations, get_destination_by_id,
    get_all_countries, get_country_by_id, get_destinations_by_country_id,
    search_places, search_stays, search_food,
    search_transports, global_travel_search,
    get_personalized_recommendations, get_emergency_guidance
)

router = APIRouter(prefix="/travel", tags=["Travel Discovery"])


@router.get("/recommendations")
def list_recommendations(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Returns personalized destination recommendations based on user preferences and history.
    """
    class DummyUser:
        travel_style = "Budget"
        interests = "Culture, Nature, Food"

    user = current_user or DummyUser()
    return get_personalized_recommendations(db, user)


@router.get("/emergency/{destination_id}")
def read_emergency_info(destination_id: int, db: Session = Depends(get_db)):
    """
    Returns emergency safety contacts, police, tourist assistance, and travel tips for destination.
    """
    return get_emergency_guidance(db, destination_id)


@router.get("/countries")
def list_countries(db: Session = Depends(get_db)):
    """
    Returns list of all international countries for the 3D Globe and Country Explorer.
    """
    return get_all_countries(db)


@router.get("/countries/{country_id}")
def read_country(country_id: int, db: Session = Depends(get_db)):
    """
    Returns country details with associated destinations.
    """
    country = get_country_by_id(db, country_id)
    if not country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")
    return country


@router.get("/countries/{country_id}/destinations")
def list_country_destinations(country_id: int, db: Session = Depends(get_db)):
    """
    Returns destinations belonging to a specific country.
    """
    return get_destinations_by_country_id(db, country_id)


@router.get("/destinations")
def list_destinations(
    q: Optional[str] = Query(None, description="Search keyword"),
    region: Optional[str] = Query(None, description="Region filter"),
    country: Optional[str] = Query(None, description="Country filter"),
    category: Optional[str] = Query(None, description="Category filter"),
    max_budget: Optional[float] = Query(None, description="Maximum budget"),
    db: Session = Depends(get_db)
):
    return get_all_destinations(db, query=q, region=region, country=country, category=category, max_budget=max_budget)


@router.get("/destinations/{destination_id}")
def read_destination(destination_id: int, db: Session = Depends(get_db)):
    dest = get_destination_by_id(db, destination_id)
    if not dest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found")
    return dest


@router.get("/places")
def list_places(
    q: Optional[str] = Query(None, description="Search keyword"),
    category: Optional[str] = Query(None, description="Place category"),
    db: Session = Depends(get_db)
):
    return search_places(db, query=q, category=category)


@router.get("/stays")
def list_stays(
    q: Optional[str] = Query(None, description="Search keyword"),
    category: Optional[str] = Query(None, description="Category: Budget, Mid-range, Premium, Hostel, Homestay"),
    max_price: Optional[float] = Query(None, description="Maximum price per night"),
    db: Session = Depends(get_db)
):
    return search_stays(db, query=q, category=category, max_price=max_price)


@router.get("/food")
def list_food(
    q: Optional[str] = Query(None, description="Search keyword"),
    cuisine: Optional[str] = Query(None, description="Cuisine type"),
    db: Session = Depends(get_db)
):
    return search_food(db, query=q, cuisine=cuisine)


@router.get("/transport")
def list_transport(
    mode: Optional[str] = Query(None, description="Transport mode"),
    destination_id: Optional[int] = Query(None, description="Destination ID"),
    db: Session = Depends(get_db)
):
    return search_transports(db, mode=mode, destination_id=destination_id)


@router.get("/search")
def global_search(
    q: str = Query(..., min_length=1, description="Unified search query"),
    db: Session = Depends(get_db)
):
    return global_travel_search(db, query=q)
