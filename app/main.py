import os
from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.database import init_db, get_db, SessionLocal
from app.database.seed import seed_data
from app.auth.router import router as auth_router
from app.travel.router import router as travel_router
from app.trips.router import router as trips_router
from app.favorites.router import router as favorites_router
from app.history.router import router as history_router
from app.ai.router import router as ai_router
from app.locations.router import router as locations_router
from app.debug.router import router as debug_router
from app.core.dependencies import require_web_authentication
from app.travel.service import get_all_destinations, get_destination_by_id, get_all_countries
from app.database.models import User, Destination, Place, Stay, FoodSpot, LocalFood, Transport, Country, Trip, Favorite, TravelHistory, WorldCity
from app.core.email import LocalDevEmailService

# Initialize Database Schema & Migrations
init_db()

# Seed Database
db = SessionLocal()
try:
    seed_data(db)
finally:
    db.close()

from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title="AI Travel Planner API",
    description="A complete pastel-themed Web UI and FastAPI platform for global travel planning.",
    version="8.0.0"
)

# Configure Production CORS
cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "..", "static")), name="static")

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "..", "templates"))

# Register API Routers First
app.include_router(auth_router)
app.include_router(travel_router)
app.include_router(trips_router)
app.include_router(favorites_router)
app.include_router(history_router)
app.include_router(ai_router)
app.include_router(locations_router)
app.include_router(debug_router)


# --- HTML Page Routes ---

@app.get("/")
def read_root(request: Request, current_user: User = Depends(require_web_authentication), db: Session = Depends(get_db)):
    return dashboard_page(request=request, current_user=current_user, db=db)


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


@app.get("/verify-otp")
def verify_otp_page(request: Request, email: str = "", mobile: str = ""):
    return templates.TemplateResponse(request=request, name="verify_otp.html", context={"email": email, "mobile": mobile})


@app.get("/verify-mobile-otp")
def verify_mobile_otp_page(request: Request, mobile: str = "", email: str = "", db: Session = Depends(get_db)):
    mobile_val = mobile
    if not mobile_val and email:
        user = db.query(User).filter(User.email == email.lower()).first()
        if user and user.mobile_number:
            mobile_val = user.mobile_number
    return templates.TemplateResponse(request=request, name="verify_mobile_otp.html", context={"mobile_number": mobile_val, "email": email})


@app.get("/forgot-password")
def forgot_password_page(request: Request):
    return templates.TemplateResponse(request=request, name="forgot_password.html")


@app.get("/verify-reset-otp")
def verify_reset_otp_page(request: Request):
    return templates.TemplateResponse(request=request, name="forgot_password.html")


@app.get("/reset-password")
def reset_password_page(request: Request):
    return templates.TemplateResponse(request=request, name="reset_password.html")


@app.get("/dashboard")
def dashboard_page(request: Request, current_user: User = Depends(require_web_authentication), db: Session = Depends(get_db)):
    countries = get_all_countries(db)
    destinations = get_all_destinations(db)
    user_trips = db.query(Trip).filter(Trip.user_id == current_user.id).order_by(Trip.created_at.desc()).all()
    user_favs = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    history = db.query(TravelHistory).filter(TravelHistory.user_id == current_user.id).order_by(TravelHistory.viewed_at.desc()).limit(10).all()

    return templates.TemplateResponse(request=request, name="dashboard.html", context={
        "user": current_user,
        "countries": countries,
        "destinations": destinations,
        "trips": user_trips,
        "favorites": user_favs,
        "history": history
    })


@app.get("/plan-trip")
def plan_trip_page(request: Request, current_user: User = Depends(require_web_authentication), db: Session = Depends(get_db)):
    destinations = get_all_destinations(db)
    countries = get_all_countries(db)
    return templates.TemplateResponse(request=request, name="plan_trip.html", context={
        "user": current_user,
        "destinations": destinations,
        "countries": countries
    })


@app.get("/explore")
def explore_page(request: Request, q: str = None, region: str = "All", category: str = "All", country: str = "All", db: Session = Depends(get_db)):
    destinations = get_all_destinations(db, query=q, region=region, category=category, country=country)
    countries = get_all_countries(db)

    regions = ["All", "North", "South", "West", "East", "Central", "Northeast"]
    categories = ["All", "Monument", "Heritage Site", "Beach", "Hill Fort", "UNESCO Temple", "Waterfall", "Park"]

    return templates.TemplateResponse(request=request, name="explore.html", context={
        "destinations": destinations,
        "countries": countries,
        "selected_query": q,
        "selected_region": region,
        "selected_category": category,
        "selected_country": country,
        "regions": regions,
        "categories": categories
    })


@app.get("/destinations/{destination_id}")
@app.get("/destination/{destination_id}")
def destination_detail_page(destination_id: int, request: Request, db: Session = Depends(get_db)):
    destination = get_destination_by_id(db, destination_id)
    if not destination:
        return templates.TemplateResponse(request=request, name="explore.html", context={"destinations": get_all_destinations(db)})
    return templates.TemplateResponse(request=request, name="destination_detail.html", context={"destination": destination})


@app.get("/my-trips")
def trips_page(request: Request, current_user: User = Depends(require_web_authentication), db: Session = Depends(get_db)):
    user_trips = db.query(Trip).filter(Trip.user_id == current_user.id).order_by(Trip.created_at.desc()).all()
    return templates.TemplateResponse(request=request, name="dashboard.html", context={
        "user": current_user,
        "trips": user_trips,
        "countries": get_all_countries(db),
        "destinations": get_all_destinations(db),
        "favorites": db.query(Favorite).filter(Favorite.user_id == current_user.id).all(),
        "history": db.query(TravelHistory).filter(TravelHistory.user_id == current_user.id).all()
    })


@app.get("/my-favorites")
def favorites_page(request: Request, current_user: User = Depends(require_web_authentication), db: Session = Depends(get_db)):
    user_favs = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    return templates.TemplateResponse(request=request, name="dashboard.html", context={
        "user": current_user,
        "favorites": user_favs,
        "countries": get_all_countries(db),
        "destinations": get_all_destinations(db),
        "trips": db.query(Trip).filter(Trip.user_id == current_user.id).all(),
        "history": db.query(TravelHistory).filter(TravelHistory.user_id == current_user.id).all()
    })


@app.get("/profile")
def profile_page(request: Request, current_user: User = Depends(require_web_authentication), db: Session = Depends(get_db)):
    user_trips = db.query(Trip).filter(Trip.user_id == current_user.id).all()
    user_favs = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    user_history = db.query(TravelHistory).filter(TravelHistory.user_id == current_user.id).all()

    return templates.TemplateResponse(request=request, name="profile.html", context={
        "user": current_user,
        "trips": user_trips,
        "favorites": user_favs,
        "history": user_history
    })


@app.get("/chat")
def chat_page(request: Request, destination: str = None, country: str = None, current_user: User = Depends(require_web_authentication), db: Session = Depends(get_db)):
    init_prompt = None
    if destination:
        init_prompt = f"Plan a trip to {destination}" + (f", {country}" if country else "")
    return templates.TemplateResponse(request=request, name="chat.html", context={
        "user": current_user,
        "initial_prompt": init_prompt,
        "app_name": "AI Travel Planner"
    })


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "no_external_api_keys_required": True,
        "app": "AI Travel Planner"
    }


@app.get("/email-status")
def email_status_endpoint():
    return LocalDevEmailService.get_status()


@app.get("/database-status")
def database_status(db: Session = Depends(get_db)):
    return {
        "database": "connected",
        "world_cities": db.query(WorldCity).count(),
        "countries": db.query(Country).count(),
        "destinations": db.query(Destination).count(),
        "places": db.query(Place).count(),
        "stays": db.query(Stay).count(),
        "food_spots": db.query(FoodSpot).count(),
        "local_foods": db.query(LocalFood).count(),
        "transports": db.query(Transport).count(),
        "users": db.query(User).count(),
        "trips": db.query(Trip).count(),
        "favorites": db.query(Favorite).count()
    }
