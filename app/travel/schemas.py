from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class PlaceResponse(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    history: Optional[str] = None
    estimated_visit_time: Optional[str] = None
    estimated_cost: float
    image: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StayResponse(BaseModel):
    id: int
    name: str
    area: Optional[str] = None
    category: Optional[str] = None
    approximate_price: float
    rating: float
    description: Optional[str] = None
    image: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FoodSpotResponse(BaseModel):
    id: int
    name: str
    cuisine: Optional[str] = None
    specialty: Optional[str] = None
    approximate_price: float
    description: Optional[str] = None
    image: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class LocalFoodResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    image: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TransportResponse(BaseModel):
    id: int
    origin: Optional[str] = None
    destination: Optional[str] = None
    transport_mode: str
    approximate_cost: float
    approximate_duration: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DestinationResponse(BaseModel):
    id: int
    name: str
    country: str
    state: str
    description: Optional[str] = None
    best_time: Optional[str] = None
    recommended_days: int
    image: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DestinationDetailResponse(DestinationResponse):
    history: Optional[str] = None
    culture: Optional[str] = None
    places: List[PlaceResponse] = []
    stays: List[StayResponse] = []
    food_spots: List[FoodSpotResponse] = []
    local_foods: List[LocalFoodResponse] = []
    transports: List[TransportResponse] = []

    model_config = ConfigDict(from_attributes=True)
