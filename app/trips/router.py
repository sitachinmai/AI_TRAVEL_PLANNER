import json
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.database.models import User, Trip
from app.ai.planner import build_itinerary_and_budget

router = APIRouter(prefix="/trips", tags=["Trip Management"])


from pydantic import BaseModel, Field


class TripCreateRequest(BaseModel):
    destination_name: str
    destination_id: Optional[int] = None
    title: Optional[str] = None
    trip_type: str = "Solo"  # Solo, Friends, Family
    travel_style: str = "Budget"  # Budget, Comfort, Premium
    number_of_days: int = Field(default=3, ge=1, le=365)
    number_of_travelers: int = Field(default=1, ge=1)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    interests: Optional[List[str]] = []
    food_preferences: Optional[str] = None
    special_requirements: Optional[str] = None


class TripUpdateRequest(BaseModel):
    title: Optional[str] = None
    trip_type: Optional[str] = None
    travel_style: Optional[str] = None
    number_of_days: Optional[int] = None
    number_of_travelers: Optional[int] = None
    status: Optional[str] = None


class ExpenseUpdateRequest(BaseModel):
    accommodation: Optional[float] = 0.0
    food: Optional[float] = 0.0
    local_transportation: Optional[float] = 0.0
    intercity_transportation: Optional[float] = 0.0
    activities: Optional[float] = 0.0
    shopping: Optional[float] = 0.0
    misc: Optional[float] = 0.0


class PackingListUpdateRequest(BaseModel):
    items: List[Dict[str, Any]]


@router.get("")
def list_user_trips(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns user-isolated list of trips. User A cannot access User B's trips.
    """
    return db.query(Trip).filter(Trip.user_id == current_user.id).order_by(Trip.created_at.desc()).all()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_trip(data: TripCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Build day-by-day itinerary and budget breakdown using planner
    plan = build_itinerary_and_budget(
        db=db,
        destination_name=data.destination_name,
        number_of_days=data.number_of_days,
        trip_type=data.trip_type,
        travel_style=data.travel_style,
        number_of_travelers=data.number_of_travelers,
        interests=data.interests,
        food_preferences=data.food_preferences,
        special_requirements=data.special_requirements
    )

    if not plan["found"]:
        raise HTTPException(status_code=400, detail=f"Destination '{data.destination_name}' not found in database.")

    title = data.title or f"{data.number_of_days}-Day {plan['destination_name']} Trip"
    total_budget = plan["budget_breakdown"]["total_estimated"]

    trip = Trip(
        user_id=current_user.id,
        destination_id=data.destination_id,
        destination_name=plan["destination_name"],
        title=title,
        trip_type=data.trip_type,
        travel_style=data.travel_style,
        start_date=data.start_date,
        end_date=data.end_date,
        number_of_days=data.number_of_days,
        number_of_travelers=data.number_of_travelers,
        total_budget=total_budget,
        status="Upcoming",
        itinerary_json=json.dumps(plan["itinerary"]),
        packing_list_json=json.dumps(plan["packing_list"]),
        actual_expenses_json=json.dumps(plan.get("actual_expenses", {})),
        interests_json=json.dumps(data.interests or []),
        food_preferences=data.food_preferences,
        special_requirements=data.special_requirements
    )

    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.get("/{trip_id}")
def read_trip(trip_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found or unauthorized.")
    
    return {
        "id": trip.id,
        "title": trip.title,
        "destination_name": trip.destination_name,
        "trip_type": trip.trip_type,
        "travel_style": trip.travel_style,
        "start_date": trip.start_date,
        "end_date": trip.end_date,
        "number_of_days": trip.number_of_days,
        "number_of_travelers": trip.number_of_travelers,
        "total_budget": trip.total_budget,
        "status": trip.status,
        "itinerary": json.loads(trip.itinerary_json) if trip.itinerary_json else [],
        "packing_list": json.loads(trip.packing_list_json) if trip.packing_list_json else [],
        "actual_expenses": json.loads(trip.actual_expenses_json) if trip.actual_expenses_json else {},
        "interests": json.loads(trip.interests_json) if trip.interests_json else [],
        "food_preferences": trip.food_preferences,
        "special_requirements": trip.special_requirements,
        "created_at": trip.created_at
    }


@router.put("/{trip_id}")
def update_trip(trip_id: int, data: TripUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found or unauthorized.")

    if data.title is not None:
        trip.title = data.title
    if data.trip_type is not None:
        trip.trip_type = data.trip_type
    if data.travel_style is not None:
        trip.travel_style = data.travel_style
    if data.status is not None:
        trip.status = data.status

    db.commit()
    db.refresh(trip)
    return trip


@router.put("/{trip_id}/expenses")
def update_trip_expenses(trip_id: int, data: ExpenseUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found or unauthorized.")

    expenses_dict = {
        "accommodation": data.accommodation or 0.0,
        "food": data.food or 0.0,
        "local_transportation": data.local_transportation or 0.0,
        "intercity_transportation": data.intercity_transportation or 0.0,
        "activities": data.activities or 0.0,
        "shopping": data.shopping or 0.0,
        "misc": data.misc or 0.0
    }

    trip.actual_expenses_json = json.dumps(expenses_dict)
    db.commit()
    db.refresh(trip)
    return {"message": "Actual expenses updated successfully!", "actual_expenses": expenses_dict}


@router.put("/{trip_id}/packing-list")
def update_trip_packing_list(trip_id: int, data: PackingListUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found or unauthorized.")

    trip.packing_list_json = json.dumps(data.items)
    db.commit()
    db.refresh(trip)
    return {"message": "Packing list updated successfully!", "packing_list": data.items}


@router.post("/{trip_id}/replan")
def replan_trip(trip_id: int, travel_style: str = "Budget", current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found or unauthorized.")

    interests_list = json.loads(trip.interests_json) if trip.interests_json else []

    plan = build_itinerary_and_budget(
        db=db,
        destination_name=trip.destination_name,
        number_of_days=trip.number_of_days,
        trip_type=trip.trip_type,
        travel_style=travel_style,
        number_of_travelers=trip.number_of_travelers,
        interests=interests_list,
        food_preferences=trip.food_preferences,
        special_requirements=trip.special_requirements
    )

    trip.travel_style = travel_style
    trip.total_budget = plan["budget_breakdown"]["total_estimated"]
    trip.itinerary_json = json.dumps(plan["itinerary"])
    trip.packing_list_json = json.dumps(plan["packing_list"])

    db.commit()
    db.refresh(trip)
    return {"message": "Trip re-planned successfully!", "trip": trip}


@router.delete("/{trip_id}")
def delete_trip(trip_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found or unauthorized.")

    db.delete(trip)
    db.commit()
    return {"message": "Trip deleted successfully."}
