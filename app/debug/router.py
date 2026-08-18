from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.database import get_db
from app.database.models import Country, Destination, Place, FoodSpot, Stay, Transport, WorldCity, User, Trip, Favorite

router = APIRouter(prefix="/debug", tags=["Developer Diagnostics"])


@router.get("/travel-data")
def debug_travel_data(db: Session = Depends(get_db)):
    """
    Developer diagnostic endpoint to verify database integrity, table row counts,
    and missing data link metrics across the application.
    """
    total_countries = db.query(Country).count()
    total_destinations = db.query(Destination).count()
    total_places = db.query(Place).count()
    total_food_spots = db.query(FoodSpot).count()
    total_stays = db.query(Stay).count()
    total_transports = db.query(Transport).count()
    total_world_cities = db.query(WorldCity).count()
    total_users = db.query(User).count()
    total_trips = db.query(Trip).count()
    total_favorites = db.query(Favorite).count()

    # Missing metrics calculations
    destinations_without_images = db.query(Destination).filter(
        (Destination.image == None) | (Destination.image == "")
    ).count()

    destinations_without_places = db.query(Destination).filter(
        ~Destination.places.any()
    ).count()

    destinations_without_food = db.query(Destination).filter(
        ~Destination.food_spots.any() & ~Destination.local_foods.any()
    ).count()

    destinations_without_stays = db.query(Destination).filter(
        ~Destination.stays.any()
    ).count()

    return {
        "status": "healthy",
        "database": "travel_planner.db",
        "counts": {
            "world_cities": total_world_cities,
            "countries": total_countries,
            "destinations": total_destinations,
            "places": total_places,
            "food_spots": total_food_spots,
            "stays": total_stays,
            "transports": total_transports,
            "users": total_users,
            "trips": total_trips,
            "favorites": total_favorites
        },
        "quality_metrics": {
            "destinations_without_images": destinations_without_images,
            "destinations_without_places": destinations_without_places,
            "destinations_without_food": destinations_without_food,
            "destinations_without_stays": destinations_without_stays
        }
    }
