from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.models import Destination, Place, Stay, FoodSpot, LocalFood, Transport, Country, WorldCity


def tool_search_destinations(db: Session, query: str) -> List[Dict[str, Any]]:
    if not query or not query.strip():
        return []
        
    q_clean = query.strip()
    
    # 1. Primary search: Exact / Partial match on Name or State FIRST
    dests = db.query(Destination).filter(
        or_(
            Destination.name.ilike(f"%{q_clean}%"),
            Destination.state.ilike(f"%{q_clean}%")
        )
    ).all()
    
    # 2. Secondary search: Country match
    if not dests:
        dests = db.query(Destination).filter(
            Destination.country.ilike(f"%{q_clean}%")
        ).all()
        
    # 3. Fallback search: Description match as last resort
    if not dests:
        dests = db.query(Destination).filter(
            Destination.description.ilike(f"%{q_clean}%")
        ).all()

    return [
        {
            "id": d.id,
            "name": d.name,
            "country": d.country,
            "state": d.state,
            "description": d.description,
            "best_time": d.best_time,
            "recommended_days": d.recommended_days,
            "approximate_budget": d.approximate_budget
        }
        for d in dests
    ]


def resolve_destination(query: str, db: Session) -> Optional[Destination]:
    """
    Returns primary Destination object matching the query or None.
    Maintains 100% backward compatibility.
    """
    dest_obj, _, _ = resolve_destination_two_layer(query, db)
    return dest_obj


def resolve_destination_two_layer(query: str, db: Session) -> Tuple[Optional[Destination], bool, Optional[WorldCity]]:
    """
    Two-Layer Destination System:
    Layer 1: WORLD LOCALITIES (WorldCity table derived from Geoapify OpenStreetMap dataset)
    Layer 2: TRAVEL CONTENT (Destination table with places, stays, food, transport)

    Returns:
    (Destination, has_full_travel_content, WorldCity)
    """
    if not query or not query.strip():
        return None, False, None

    clean_q = query.strip()
    
    # 1. Direct match on Destination Name
    dest = db.query(Destination).filter(Destination.name.ilike(clean_q)).first()
    if dest:
        return dest, True, None

    # 2. Direct match on Destination State
    dest = db.query(Destination).filter(Destination.state.ilike(clean_q)).first()
    if dest:
        return dest, True, None

    # 3. Token extraction (strip punctuation first)
    import re
    clean_q_no_punct = re.sub(r'[^\w\s]', ' ', clean_q)
    cleaned_words = re.sub(r'(?i)\b(plan|trip|to|in|for|a|an|the|days?|months?|make|budget|family|solo|friends|show|me|best|places|food|visit|where|can|i|what|should|eat|try|what\'s)\b', ' ', clean_q_no_punct)
    tokens = [t.strip() for t in cleaned_words.split() if len(t.strip()) >= 3 and not t.strip().isdigit()]

    # First pass: Check for city / destination name matches across all tokens
    for token in tokens:
        dest = db.query(Destination).filter(
            or_(
                Destination.name.ilike(f"%{token}%"),
                Destination.state.ilike(f"%{token}%")
            )
        ).first()
        if dest:
            return dest, True, None

    # Second pass: Check for Country matches only if no specific city was found
    for token in tokens:
        country = db.query(Country).filter(Country.name.ilike(f"%{token}%")).first()
        if country:
            dest = db.query(Destination).filter(Destination.country_id == country.id).first()
            if dest:
                return dest, True, None

    # 4. Check Layer 1 (WorldCity) if no Layer 2 travel content found
    for token in (tokens if tokens else [clean_q]):
        wc = db.query(WorldCity).filter(
            or_(
                WorldCity.name.ilike(f"%{token}%"),
                WorldCity.normalized_name.ilike(f"%{token.lower()}%"),
                WorldCity.state.ilike(f"%{token}%")
            )
        ).first()
        if wc:
            return None, False, wc

    return None, False, None


def tool_get_destination_details(db: Session, destination_id: int) -> Optional[Dict[str, Any]]:
    from app.core.currency import normalize_place_cost, get_country_currency
    d = db.query(Destination).filter(Destination.id == destination_id).first()
    if not d:
        return None

    curr_code = getattr(d, "currency_code", None) or get_country_currency(d.country)

    return {
        "id": d.id,
        "name": d.name,
        "country": d.country,
        "state": d.state,
        "currency_code": curr_code,
        "description": d.description,
        "history": d.history,
        "culture": d.culture,
        "best_time": d.best_time,
        "recommended_days": d.recommended_days,
        "approximate_budget": d.approximate_budget,
        "image": d.image or f"/static/images/{d.name.lower()}.jpg",
        "places": [
            {
                "name": p.name,
                "category": p.category,
                "description": p.description,
                "cost": normalize_place_cost(p.estimated_cost, currency_code=curr_code, is_explicitly_free=getattr(p, "is_explicitly_free", False), place_name=p.name, category=p.category)["display_amount"],
                "raw_cost": p.estimated_cost,
                "image": p.image or f"/static/images/{d.name.lower()}_place.jpg"
            }
            for p in d.places
        ],
        "stays": [{"name": s.name, "category": s.category, "price": s.approximate_price, "rating": s.rating, "image": s.image or f"/static/images/{d.name.lower()}_stay.jpg"} for s in d.stays],
        "food_spots": [{"name": f.name, "specialty": f.specialty, "price": f.approximate_price, "image": f.image or f"/static/images/{d.name.lower()}_food.jpg"} for f in d.food_spots],
        "local_foods": [{"name": lf.name, "category": lf.category, "is_must_try": lf.is_must_try, "image": lf.image or f"/static/images/{d.name.lower()}_food.jpg"} for lf in d.local_foods],
        "transports": [{"mode": t.transport_mode, "origin": t.origin, "cost": t.approximate_cost, "duration": t.approximate_duration} for t in d.transports]
    }


def tool_get_packing_list(destination_name: str, number_of_days: int) -> List[str]:
    base_items = [
        "Government issued ID proof / Passport",
        "Universal phone charger & power bank",
        "Prescribed medicines & basic first-aid kit",
        "Reusable water bottle"
    ]
    if number_of_days > 3:
        base_items.extend(["Comfortable walking/hiking shoes", "3-5 pairs of breathable cotton/linen clothes", "Laundry bag"])
    else:
        base_items.extend(["Comfortable walking shoes", "2-3 pairs of light clothes"])

    dest_lower = destination_name.lower()
    if "beach" in dest_lower or "goa" in dest_lower or "phuket" in dest_lower:
        base_items.extend(["Sunscreen SPF 50", "Sunglasses & hat", "Swimwear & beach towel"])
    elif "hill" in dest_lower or "munnar" in dest_lower or "manali" in dest_lower or "swiss" in dest_lower:
        base_items.extend(["Light jacket / sweater", "Rain jacket / umbrella", "Moisturizer"])

    return base_items
