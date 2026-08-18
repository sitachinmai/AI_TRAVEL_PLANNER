from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.database.models import Country, Destination, Place, Stay, FoodSpot, LocalFood, Transport, User, TravelHistory, Favorite
from app.core.images import resolve_destination_image, resolve_food_image, resolve_attraction_image, resolve_hotel_image, DEFAULT_PLACEHOLDER, DEFAULT_PLACE_FALLBACK, DEFAULT_FOOD_FALLBACK, clean_image_url
from app.core.research import get_research_url


def get_all_countries(db: Session, only_with_destinations: bool = False) -> List[Dict[str, Any]]:
    """
    Returns list of all countries with flags, continent, coordinates, and destination count.
    If only_with_destinations is True, returns only countries that have destination records.
    """
    query = db.query(Country)
    if only_with_destinations:
        query = query.filter(Country.destinations.any())
    countries = query.all()
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


def is_generic_food_placeholder(name: str) -> bool:
    if not name:
        return True
    n_lower = name.lower().strip()
    generic_words = ["delicacy", "specialty", "delicacies", "specialties"]
    for word in generic_words:
        if word in n_lower and not any(real_food in n_lower for real_food in [
            "chole", "biryani", "sushi", "ramen", "pizza", "burger", "croissant", 
            "taco", "soup", "curry", "pie", "bug", "noodle", "rice", "cake", "bread", 
            "bbq", "seafood", "tart", "wine", "plat", "roll", "paan", "jalebi", "sweets",
            "pastry", "coffee", "tea", "dosa", "idli", "sambar", "chaat", "roti", "saag",
            "tagine", "couscous", "pastilla", "harira", "gelato", "suppli", "carciofi", "schnitzel",
            "torte", "nockerl", "mozart", "duck", "dumpling", "bao", "appam", "stew", "halwa",
            "kebab", "nihari", "haleem", "salan", "meetha", "falooda", "tikki", "gappe", "bhalla"
        ]):
            return True
    return False


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

    places = [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category or "Heritage & Sightseeing",
            "description": p.description,
            "history": p.history,
            "location": p.location or dest.name,
            "estimated_visit_time": p.estimated_visit_time or "2 Hours",
            "estimated_cost": p.estimated_cost or 0,
            "recommended_time": p.recommended_time or "Morning / Evening",
            "things_to_do": p.things_to_do,
            "things_to_try": p.things_to_try,
            "image": resolve_attraction_image(p.name, dest.name) if resolve_attraction_image(p.name, dest.name) != DEFAULT_PLACE_FALLBACK else (clean_image_url(p.image) if (p.image and p.image != 'None' and p.image.startswith('http')) else DEFAULT_PLACE_FALLBACK),
            "research_url": get_research_url(p.name)
        }
        for p in dest.places
    ]

    # Ensure at least 2 places
    if len(places) == 0:
        places.append({
            "id": 9001,
            "name": f"{dest.name} Historic Old Town",
            "category": "Heritage & Culture",
            "description": f"The historic heart of {dest.name} featuring traditional architecture, local artisan markets, and cultural landmarks.",
            "location": f"Central {dest.name}",
            "estimated_visit_time": "2-3 Hours",
            "estimated_cost": 0,
            "recommended_time": "Morning",
            "image": resolve_attraction_image(f"{dest.name} Old Town", dest.name),
            "research_url": get_research_url(dest.name)
        })
    if len(places) == 1:
        places.append({
            "id": 9002,
            "name": f"{dest.name} Scenic City Viewpoint",
            "category": "Sightseeing",
            "description": f"Panoramic viewpoint offering scenic vistas of the {dest.name} city skyline, natural landscapes, and surrounding hills.",
            "location": f"Upper {dest.name}",
            "estimated_visit_time": "1-2 Hours",
            "estimated_cost": 0,
            "recommended_time": "Sunset",
            "image": resolve_attraction_image(f"{dest.name} Viewpoint", dest.name),
            "research_url": get_research_url(dest.name)
        })

    stays = []
    for s in dest.stays:
        desc = s.description
        if not desc or str(desc).strip() in ['None', 'none', '']:
            if 'athénée' in (s.name or '').lower() or 'athenee' in (s.name or '').lower() or 'plaza' in (s.name or '').lower():
                desc = "Historic luxury palace hotel near Avenue Montaigne and the Champs-Élysées."
            else:
                desc = f"Comfortable hotel accommodation in {dest.name} featuring fine amenities and central location."
        
        st_img = resolve_hotel_image(s.name, dest.name)

        price_display = None
        if dest.name.lower() == "paris":
            if "generator" in s.name.lower():
                desc = "Design-focused hostel near Canal Saint-Martin."
                price_display = "€30–€60 / night (≈ ₹3,000–₹6,000)"
            elif "citizenm" in s.name.lower():
                desc = "Modern smart hotel near Gare de Lyon with compact rooms and technology-focused amenities."
                price_display = "€150–€220 / night (≈ ₹15,000–₹22,000)"
            elif "athénée" in s.name.lower() or "athenee" in s.name.lower() or "plaza" in s.name.lower():
                desc = "Historic luxury palace hotel near Avenue Montaigne and the Champs-Élysées."
                price_display = "€1,500–€2,500+ / night (≈ ₹1,50,000–₹2,50,000+)"
            elif "relais" in s.name.lower():
                desc = "Charming Left Bank boutique hotel near Saint-Germain-des-Prés."
                price_display = "€250–€400 / night (≈ ₹25,000–₹40,000)"
            elif "piaules" in s.name.lower():
                desc = "Trendy hostel in Belleville with social spaces and rooftop views."
                price_display = "€40–€80 / night (≈ ₹4,000–₹8,000)"
            elif "ritz" in s.name.lower():
                desc = "Historic luxury palace hotel on Place Vendôme."
                price_display = "€2,000–€4,000+ / night (≈ ₹2,00,000–₹4,00,000+)"

        stays.append({
            "id": s.id,
            "name": s.name,
            "area": s.area or dest.name,
            "category": s.category or "Hotel",
            "approximate_price": s.approximate_price or 2500.0,
            "price_display": price_display or (f"₹{s.approximate_price:,.0f} / night" if s.approximate_price else "₹2,500 / night"),
            "rating": s.rating or "4.5",
            "description": desc,
            "image": st_img
        })

    # Ensure at least 2 stays
    if len(stays) == 0:
        stays.append({
            "id": 8001,
            "name": f"Grand {dest.name} Heritage Hotel",
            "area": f"Central {dest.name}",
            "category": "Luxury Hotel",
            "approximate_price": 4500.0,
            "price_display": "₹4,500 / night",
            "rating": "4.7",
            "description": f"Premier luxury hotel in central {dest.name} offering world-class hospitality, fine dining, and executive suites.",
            "image": resolve_hotel_image(f"Grand {dest.name} Heritage Hotel", dest.name)
        })
    if len(stays) == 1:
        stays.append({
            "id": 8002,
            "name": f"{dest.name} Beachfront / Promenade Resort",
            "area": f"{dest.name} Promenade",
            "category": "Boutique Resort",
            "approximate_price": 2800.0,
            "price_display": "₹2,800 / night",
            "rating": "4.5",
            "description": f"Charming boutique resort in {dest.name} featuring comfortable sea/mountain view rooms and local cuisine.",
            "image": resolve_hotel_image(f"{dest.name} Promenade Resort", dest.name)
        })

    local_foods = [
        {
            "id": lf.id,
            "name": lf.name,
            "description": lf.description,
            "category": lf.category or "Local Specialty",
            "is_must_try": lf.is_must_try,
            "image": resolve_food_image(lf.name, dest.name, dest.country) if resolve_food_image(lf.name, dest.name, dest.country) != DEFAULT_FOOD_FALLBACK else (clean_image_url(lf.image) if (lf.image and lf.image != 'None' and lf.image.startswith('http')) else DEFAULT_FOOD_FALLBACK)
        }
        for lf in dest.local_foods
        if not is_generic_food_placeholder(lf.name)
    ]

    # Ensure at least 2 local foods
    if len(local_foods) == 0:
        local_foods.append({
            "id": 7001,
            "name": f"{dest.name} Signature Regional Cuisine",
            "category": "Must-Try Dish",
            "description": f"Authentic culinary creation of {dest.name} ({dest.country}) prepared using traditional local spices and recipes.",
            "is_must_try": True,
            "image": resolve_food_image(f"{dest.name} Special", dest.name, dest.country)
        })
    if len(local_foods) == 1:
        local_foods.append({
            "id": 7002,
            "name": f"{dest.name} Artisanal Street Snack",
            "category": "Local Street Food",
            "description": f"Popular savory street food delicacy enjoyed by locals across {dest.name}.",
            "is_must_try": True,
            "image": resolve_food_image(f"{dest.name} Snack", dest.name, dest.country)
        })

    if dest.name.lower() == "paris":
        transports = [
            {
                "id": 6101,
                "mode": "RER B Train",
                "transport_mode": "RER B Train",
                "origin": "CDG Airport",
                "destination": "Paris Gare du Nord",
                "approximate_cost": 1400.0,
                "cost_display": "€14.00 (≈ ₹1,400)",
                "description": "Charles de Gaulle Airport to Paris Gare du Nord via RER B Train",
                "cost": 1400.0
            },
            {
                "id": 6102,
                "mode": "Paris Métro",
                "transport_mode": "Paris Métro",
                "origin": "Châtelet",
                "destination": "Eiffel Tower / Montmartre",
                "approximate_cost": 255.0,
                "cost_display": "€2.55 (≈ ₹255)",
                "description": "Châtelet to Eiffel Tower / Montmartre via Paris Métro",
                "cost": 255.0
            },
            {
                "id": 6103,
                "mode": "RATP Bus",
                "transport_mode": "RATP Bus",
                "origin": "Louvre",
                "destination": "Bastille",
                "approximate_cost": 205.0,
                "cost_display": "€2.05 (≈ ₹205)",
                "description": "Louvre to Bastille via RATP Bus",
                "cost": 205.0
            },
            {
                "id": 6104,
                "mode": "Uber Green",
                "transport_mode": "Uber Green",
                "origin": "Opéra",
                "destination": "Le Marais",
                "approximate_cost": 2500.0,
                "cost_display": "€20–€30 estimated (≈ ₹2,000–₹3,000)",
                "description": "Opéra to Le Marais via Uber Green",
                "cost": 2500.0
            }
        ]
    else:
        transports = [
            {
                "id": t.id,
                "mode": t.transport_mode,
                "transport_mode": t.transport_mode,
                "origin": t.origin or f"{dest.name} Transit Station",
                "destination": t.destination or f"Central {dest.name}",
                "approximate_cost": t.approximate_cost or 200.0,
                "cost_display": f"₹{t.approximate_cost:,.0f}" if t.approximate_cost else "₹200",
                "description": f"{t.origin or 'City Center'} to {t.destination or 'Local Sights'} via {t.transport_mode}",
                "cost": t.approximate_cost or 200.0
            }
            for t in dest.transports
        ]

        if len(transports) == 0:
            transports.append({
                "id": 6001,
                "mode": "Airport & Railway Express Cab",
                "transport_mode": "Airport & Railway Express Cab",
                "origin": f"{dest.name} International / Central Hub",
                "destination": f"Central {dest.name} Hotels",
                "approximate_cost": 350.0,
                "cost_display": "₹350",
                "description": f"Direct express taxi connection from {dest.name} hub to major hotels.",
                "cost": 350.0
            })
        if len(transports) <= 1:
            transports.append({
                "id": 6002,
                "mode": "Local Metro, Bus & Auto-Rickshaw",
                "transport_mode": "Local Metro, Bus & Auto-Rickshaw",
                "origin": f"Central {dest.name}",
                "destination": "Attractions & Shopping Districts",
                "approximate_cost": 120.0,
                "cost_display": "₹120",
                "description": f"Frequent public transit and local cabs connecting major sightseeing spots in {dest.name}.",
                "cost": 120.0
            })

    hist_text = dest.history or f"Discover the rich historical heritage of {dest.name} ({dest.country}). From ancient trade routes and cultural dynasties to architectural monuments, {dest.name} has evolved into an iconic global travel destination."
    cult_text = dest.culture or f"Experience the living culture of {dest.name} through regional festivals, traditional performing arts, authentic gastronomy, and warm local hospitality."

    return {
        "id": dest.id,
        "name": dest.name,
        "state": dest.state,
        "region": dest.region,
        "country": dest.country,
        "country_id": dest.country_id,
        "description": dest.description,
        "history": hist_text,
        "culture": cult_text,
        "best_time": dest.best_time or "October to March",
        "recommended_days": dest.recommended_days or 3,
        "approximate_budget": dest.approximate_budget or 3500.0,
        "image": d_img,
        "research_url": get_research_url(dest.name) or get_research_url(dest.country) or f"https://en.wikipedia.org/wiki/{dest.name}",
        "places": places,
        "stays": stays,
        "food_spots": [
            {
                "id": fs.id,
                "name": fs.name,
                "cuisine": fs.cuisine,
                "specialty": fs.specialty,
                "approximate_price": fs.approximate_price,
                "location": fs.location,
                "description": fs.description,
                "image": clean_image_url(fs.image) if fs.image and fs.image != 'None' else DEFAULT_FOOD_FALLBACK
            }
            for fs in dest.food_spots
        ],
        "local_foods": local_foods,
        "transports": transports
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
