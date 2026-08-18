from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.database import get_db
from app.database.models import WorldCity, Destination, Country

router = APIRouter(prefix="/locations", tags=["Global Locality Discovery"])


@router.get("/search")
def search_locations(
    q: str = Query(..., min_length=1, description="Locality or city search query"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Searches Geoapify WorldCity locality database.
    """
    search_str = f"%{q.strip()}%"
    cities = db.query(WorldCity).filter(
        or_(
            WorldCity.name.ilike(search_str),
            WorldCity.state.ilike(search_str),
            WorldCity.country_name.ilike(search_str),
            WorldCity.display_name.ilike(search_str)
        )
    ).order_by(WorldCity.population.desc()).limit(limit).all()

    return [
        {
            "id": c.id,
            "name": c.name,
            "display_name": c.display_name,
            "country_code": c.country_code,
            "country_name": c.country_name,
            "state": c.state,
            "population": c.population,
            "settlement_type": c.settlement_type,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "has_travel_content": db.query(Destination).filter(Destination.name.ilike(f"%{c.name}%")).first() is not None
        }
        for c in cities
    ]


@router.get("/countries/{country_code}")
def get_locations_by_country(
    country_code: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Returns localities belonging to a specific country code (e.g. IN, JP, FR, US).
    """
    cities = db.query(WorldCity).filter(
        WorldCity.country_code.ilike(country_code.strip())
    ).order_by(WorldCity.population.desc()).limit(limit).all()

    return [
        {
            "id": c.id,
            "name": c.name,
            "display_name": c.display_name,
            "state": c.state,
            "population": c.population,
            "settlement_type": c.settlement_type,
            "latitude": c.latitude,
            "longitude": c.longitude
        }
        for c in cities
    ]


@router.get("/cities")
def list_global_cities(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Paginated list of all global cities ordered by population.
    """
    cities = db.query(WorldCity).order_by(WorldCity.population.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "display_name": c.display_name,
            "country_name": c.country_name,
            "population": c.population,
            "settlement_type": c.settlement_type
        }
        for c in cities
    ]


@router.get("/nearby")
def get_nearby_locations(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius_km: float = Query(50.0, description="Radius in km"),
    db: Session = Depends(get_db)
):
    """
    Returns nearby localities based on latitude/longitude bounding box.
    """
    # Simple bounding box approximation: 1 deg lat approx 111km
    delta_lat = radius_km / 111.0
    delta_lng = radius_km / (111.0 * max(0.1, abs(lat / 90.0)))

    cities = db.query(WorldCity).filter(
        WorldCity.latitude.between(lat - delta_lat, lat + delta_lat),
        WorldCity.longitude.between(lng - delta_lng, lng + delta_lng)
    ).limit(20).all()

    return [
        {
            "id": c.id,
            "name": c.name,
            "display_name": c.display_name,
            "country_name": c.country_name,
            "latitude": c.latitude,
            "longitude": c.longitude
        }
        for c in cities
    ]
