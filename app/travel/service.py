from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.database.models import Country, Destination, Place, Stay, FoodSpot, LocalFood, Transport, User, TravelHistory, Favorite
from app.core.images import resolve_destination_image, resolve_food_image, resolve_attraction_image, DEFAULT_PLACEHOLDER, clean_image_url
from app.core.research import get_research_url


def get_all_countries(db: Session) -> List[Dict[str, Any]]:
    """
    Returns list of all countries with flags, continent, coordinates, and destination count.
    """
    countries = db.query(Country).all()
    result = []
    for c in countries:
        img = c.image if c.image and c.image != 'None' else f"/static/images/countries/{c.code.lower()}.jpg"
        result.append({
            "id": c.id,
            "name": c.name,
            "code": c.code,
            "continent": c.continent,
            "flag_emoji": c.flag_emoji,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "description": c.description,
            "image": img,
            "destination_count": len(c.destinations)
        })
    return result


def get_country_by_id(db: Session, country_id: int) -> Optional[Dict[str, Any]]:
    """
    Returns country by ID with its associated destinations.
    """
    c = db.query(Country).filter(Country.id == country_id).first()
    if not c:
        return None

    c_img = c.image if c.image and c.image != 'None' else f"/static/images/countries/{c.code.lower()}.jpg"
    return {
        "id": c.id,
        "name": c.name,
        "code": c.code,
        "continent": c.continent,
        "flag_emoji": c.flag_emoji,
        "latitude": c.latitude,
        "longitude": c.longitude,
        "description": c.description,
        "image": c_img,
        "destinations": [
            {
                "id": d.id,
                "name": d.name,
                "state": d.state,
                "region": d.region,
                "description": d.description,
                "best_time": d.best_time,
                "recommended_days": d.recommended_days,
                "approximate_budget": d.approximate_budget,
                "image": d.image if d.image and d.image != 'None' else resolve_destination_image(d.name, c.name)
            }
            for d in c.destinations
        ]
    }


def get_destinations_by_country_id(db: Session, country_id: int) -> List[Destination]:
    return db.query(Destination).filter(Destination.country_id == country_id).all()


def get_all_destinations(
    db: Session,
    query: Optional[str] = None,
    region: Optional[str] = None,
    country: Optional[str] = None,
    category: Optional[str] = None,
    max_budget: Optional[float] = None
) -> List[Destination]:
    q = db.query(Destination)

    if query:
        search = f"%{query.strip()}%"
        q = q.filter(
            or_(
                Destination.name.ilike(search),
                Destination.state.ilike(search),
                Destination.country.ilike(search),
                Destination.region.ilike(search),
                Destination.description.ilike(search),
                Destination.culture.ilike(search)
            )
        )

    if country and country.lower() != "all":
        c_search = f"%{country.strip()}%"
        q = q.filter(Destination.country.ilike(c_search))

    if region and region.lower() != "all":
        q = q.filter(Destination.region.ilike(region.strip()))

    if category and category.lower() != "all":
        cat_search = f"%{category.strip()}%"
        q = q.filter(
            or_(
                Destination.description.ilike(cat_search),
                Destination.culture.ilike(cat_search),
                Destination.places.any(Place.category.ilike(cat_search))
            )
        )

    if max_budget and max_budget > 0:
        q = q.filter(Destination.approximate_budget <= max_budget)

    dests = q.all()
    for d in dests:
        if not d.image or d.image == 'None':
            d.image = resolve_destination_image(d.name, d.country)
        else:
            d.image = clean_image_url(d.image)
    return dests


def get_destination_by_id(db: Session, destination_id: int) -> Optional[Dict[str, Any]]:
    dest = (
        db.query(Destination)
        .options(
            joinedload(Destination.places),
            joinedload(Destination.stays),
            joinedload(Destination.food_spots),
            joinedload(Destination.local_foods),
            joinedload(Destination.transports)
        )
        .filter(Destination.id == destination_id)
        .first()
    )

    if not dest:
        return None

    d_img = clean_image_url(dest.image) if dest.image and dest.image != 'None' else resolve_destination_image(dest.name, dest.country)

    return {
        "id": dest.id,
        "name": dest.name,
        "state": dest.state,
        "region": dest.region,
        "country": dest.country,
        "country_id": dest.country_id,
        "description": dest.description,
        "history": dest.history,
        "culture": dest.culture,
        "best_time": dest.best_time,
        "recommended_days": dest.recommended_days,
        "approximate_budget": dest.approximate_budget,
        "image": d_img,
        "research_url": get_research_url(dest.name) or get_research_url(dest.country),
        "places": [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "description": p.description,
                "history": p.history,
                "location": p.location,
                "estimated_visit_time": p.estimated_visit_time,
                "estimated_cost": p.estimated_cost,
                "recommended_time": p.recommended_time,
                "things_to_do": p.things_to_do,
                "things_to_try": p.things_to_try,
                "image": clean_image_url(p.image) if (p.image and p.image != 'None' and p.image.startswith('http')) else (resolve_attraction_image(p.name, dest.name) if resolve_attraction_image(p.name, dest.name) != DEFAULT_PLACEHOLDER else DEFAULT_PLACEHOLDER),
                "research_url": get_research_url(p.name)
            }
            for p in dest.places
        ],
        "stays": [
            {
                "id": s.id,
                "name": s.name,
                "area": s.area,
                "category": s.category,
                "approximate_price": s.approximate_price,
                "rating": s.rating,
                "description": s.description,
                "image": clean_image_url(s.image) if s.image and s.image != 'None' else DEFAULT_PLACEHOLDER
            }
            for s in dest.stays
        ],
        "food_spots": [
            {
                "id": fs.id,
                "name": fs.name,
                "cuisine": fs.cuisine,
                "specialty": fs.specialty,
                "approximate_price": fs.approximate_price,
                "location": fs.location,
                "description": fs.description,
                "image": clean_image_url(fs.image) if fs.image and fs.image != 'None' else DEFAULT_PLACEHOLDER
            }
            for fs in dest.food_spots
        ],
        "local_foods": [
            {
                "id": lf.id,
                "name": lf.name,
                "description": lf.description,
                "category": lf.category,
                "is_must_try": lf.is_must_try,
                "image": clean_image_url(lf.image) if lf.image and lf.image != 'None' else resolve_food_image(lf.name)
            }
            for lf in dest.local_foods
        ],
        "transports": [
            {
                "id": t.id,
                "mode": t.transport_mode,
                "description": f"{t.origin or ''} to {t.destination or ''} via {t.transport_mode}",
                "cost": t.approximate_cost
            }
            for t in dest.transports
        ]
    }


def search_places(db: Session, query: Optional[str] = None, category: Optional[str] = None) -> List[Place]:
    q = db.query(Place)
    if query:
        q = q.filter(Place.name.ilike(f"%{query.strip()}%"))
    if category:
        q = q.filter(Place.category.ilike(f"%{category.strip()}%"))
    return q.all()


def search_stays(db: Session, query: Optional[str] = None, category: Optional[str] = None, max_price: Optional[float] = None) -> List[Stay]:
    q = db.query(Stay)
    if query:
        q = q.filter(Stay.name.ilike(f"%{query.strip()}%"))
    if category:
        q = q.filter(Stay.category.ilike(f"%{category.strip()}%"))
    if max_price:
        q = q.filter(Stay.approximate_price <= max_price)
    return q.all()


def search_food(db: Session, query: Optional[str] = None, cuisine: Optional[str] = None) -> Dict[str, Any]:
    q_lf = db.query(LocalFood)
    q_fs = db.query(FoodSpot)
    if query:
        q_lf = q_lf.filter(LocalFood.name.ilike(f"%{query.strip()}%"))
        q_fs = q_fs.filter(or_(FoodSpot.name.ilike(f"%{query.strip()}%"), FoodSpot.cuisine.ilike(f"%{query.strip()}%")))
    if cuisine:
        q_fs = q_fs.filter(FoodSpot.cuisine.ilike(f"%{cuisine.strip()}%"))
        
    return {
        "query": query or "",
        "local_foods": q_lf.all(),
        "food_spots": q_fs.all()
    }


def search_transports(db: Session, mode: Optional[str] = None, destination_id: Optional[int] = None) -> List[Transport]:
    q = db.query(Transport)
    if mode:
        q = q.filter(Transport.transport_mode.ilike(f"%{mode.strip()}%"))
    if destination_id:
        q = q.filter(Transport.destination_id == destination_id)
    return q.all()


def global_travel_search(db: Session, query: str) -> Dict[str, Any]:
    if not query:
        return {"query": "", "destinations": [], "countries": [], "places": [], "stays": [], "food_spots": []}

    search = f"%{query.strip()}%"
    dests = db.query(Destination).filter(
        or_(Destination.name.ilike(search), Destination.country.ilike(search))
    ).limit(10).all()

    countries = db.query(Country).filter(
        or_(Country.name.ilike(search), Country.code.ilike(search))
    ).limit(10).all()

    places = db.query(Place).filter(Place.name.ilike(search)).limit(10).all()
    stays = db.query(Stay).filter(Stay.name.ilike(search)).limit(10).all()
    food_spots = db.query(FoodSpot).filter(FoodSpot.name.ilike(search)).limit(10).all()

    return {
        "query": query,
        "destinations": [{"id": d.id, "name": d.name, "country": d.country, "image": d.image or resolve_destination_image(d.name, d.country)} for d in dests],
        "countries": [{"id": c.id, "name": c.name, "flag_emoji": c.flag_emoji, "image": c.image or DEFAULT_PLACEHOLDER} for c in countries],
        "places": [{"id": p.id, "name": p.name, "image": p.image or DEFAULT_PLACEHOLDER} for p in places],
        "stays": [{"id": s.id, "name": s.name, "image": s.image or DEFAULT_PLACEHOLDER} for s in stays],
        "food_spots": [{"id": fs.id, "name": fs.name, "image": fs.image or DEFAULT_PLACEHOLDER} for fs in food_spots]
    }


def get_personalized_recommendations(db: Session, user: Any) -> List[Dict[str, Any]]:
    dests = db.query(Destination).limit(6).all()
    return [
        {
            "id": d.id,
            "name": d.name,
            "country": d.country,
            "description": d.description,
            "approximate_budget": d.approximate_budget,
            "best_time": d.best_time,
            "recommendation_reason": f"Top recommended {d.region or 'cultural'} destination matching your travel style.",
            "image": d.image or resolve_destination_image(d.name, d.country)
        }
        for d in dests
    ]


def get_emergency_guidance(db: Session, destination_id: int) -> Dict[str, Any]:
    dest = db.query(Destination).filter(Destination.id == destination_id).first()
    dest_name = dest.name if dest else "Local Region"
    return {
        "destination_name": dest_name,
        "police_helpline": "112 / 100",
        "medical_emergency": "102 / 108",
        "tourist_helpline": "1363",
        "emergency_contacts": {
            "police": "112 / 100",
            "medical": "102 / 108",
            "tourist": "1363"
        },
        "travel_tips": [
            f"Keep digital copies of your passport and ID while exploring {dest_name}.",
            "Use authorized taxis or rideshare apps for night travel.",
            "Stay hydrated and carry local currency for small market purchases."
        ]
    }
