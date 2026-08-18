from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, index=True, nullable=False)
    mobile_number = Column(String(20), nullable=True, index=True)
    full_name = Column(String(150), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_mobile_verified = Column(Boolean, default=False)
    preferred_language = Column(String(10), default="en")
    
    # Legacy link tokens
    verification_token = Column(String(255), nullable=True)
    verification_token_expires_at = Column(DateTime, nullable=True)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires_at = Column(DateTime, nullable=True)
    
    # 5-Digit Email OTP Verification Fields
    email_verification_otp_hash = Column(String(255), nullable=True)
    email_verification_otp_expires_at = Column(DateTime, nullable=True)
    email_otp_attempts = Column(Integer, default=0)

    # Temporary Email Change Fields
    pending_email = Column(String(120), nullable=True)
    pending_email_otp_hash = Column(String(255), nullable=True)
    pending_email_otp_expires_at = Column(DateTime, nullable=True)
    pending_email_otp_attempts = Column(Integer, default=0)
    
    # 5-Digit Mobile OTP Verification Fields
    mobile_verification_otp_hash = Column(String(255), nullable=True)
    mobile_verification_otp_expires_at = Column(DateTime, nullable=True)
    mobile_otp_attempts = Column(Integer, default=0)
    mobile_otp_last_sent_at = Column(DateTime, nullable=True)

    # Temporary Mobile Change Fields
    pending_mobile_number = Column(String(20), nullable=True)
    pending_mobile_otp_hash = Column(String(255), nullable=True)
    pending_mobile_otp_expires_at = Column(DateTime, nullable=True)
    pending_mobile_otp_attempts = Column(Integer, default=0)

    # 5-Digit Password Reset OTP Fields
    password_reset_otp_hash = Column(String(255), nullable=True)
    password_reset_otp_expires_at = Column(DateTime, nullable=True)
    reset_otp_attempts = Column(Integer, default=0)

    # Cooldown & Rate Limiting
    otp_last_sent_at = Column(DateTime, nullable=True)
    
    # Travel preferences
    travel_style = Column(String(50), nullable=True)  # Budget, Balanced, Comfort, Premium, Backpacking
    food_preference = Column(String(100), nullable=True)  # Vegetarian, Non-Vegetarian, Vegan, Seafood
    budget_preference = Column(String(50), nullable=True)  # Low, Mid, High
    interests = Column(String(255), nullable=True)  # History, Nature, Food, Adventure, Shopping, Culture
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    trips = relationship("Trip", back_populates="user_rel", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user_rel", cascade="all, delete-orphan")
    history = relationship("TravelHistory", back_populates="user_rel", cascade="all, delete-orphan")


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    code = Column(String(10), unique=True, index=True, nullable=False)
    continent = Column(String(50), nullable=False)  # Asia, Europe, Americas, Oceania, Africa
    flag_emoji = Column(String(10), nullable=True)
    latitude = Column(Float, default=0.0)
    longitude = Column(Float, default=0.0)
    description = Column(Text, nullable=True)
    image = Column(String(255), nullable=True)

    destinations = relationship("Destination", back_populates="country_rel", cascade="all, delete-orphan")


class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(100), nullable=False, index=True)
    country = Column(String(100), default="India")
    state = Column(String(100), nullable=False)
    region = Column(String(50), nullable=True, index=True)  # North, South, West, East, Central, Northeast
    description = Column(Text, nullable=True)
    history = Column(Text, nullable=True)
    culture = Column(Text, nullable=True)
    best_time = Column(String(100), nullable=True)
    recommended_days = Column(Integer, default=3)
    approximate_budget = Column(Float, default=5000.0)
    image = Column(String(255), nullable=True)

    currency_code = Column(String(10), default="INR")  # EUR, USD, JPY, GBP, INR, AED, CHF, THB
    country_rel = relationship("Country", back_populates="destinations")
    places = relationship("Place", back_populates="destination", cascade="all, delete-orphan")
    stays = relationship("Stay", back_populates="destination", cascade="all, delete-orphan")
    food_spots = relationship("FoodSpot", back_populates="destination", cascade="all, delete-orphan")
    local_foods = relationship("LocalFood", back_populates="destination", cascade="all, delete-orphan")
    transports = relationship("Transport", back_populates="destination_rel", cascade="all, delete-orphan")


class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    history = Column(Text, nullable=True)
    location = Column(String(150), nullable=True)
    estimated_visit_time = Column(String(50), nullable=True)
    estimated_cost = Column(Float, default=0.0)
    currency_code = Column(String(10), default="INR")
    is_explicitly_free = Column(Boolean, default=False)
    recommended_time = Column(String(100), nullable=True)
    things_to_do = Column(Text, nullable=True)
    things_to_try = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    image = Column(String(255), nullable=True)

    destination = relationship("Destination", back_populates="places")


class WorldCity(Base):
    __tablename__ = "world_cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    normalized_name = Column(String(150), nullable=False, index=True)
    other_names = Column(Text, nullable=True)
    display_name = Column(String(255), nullable=True)
    country_code = Column(String(10), index=True, nullable=False)
    country_name = Column(String(100), index=True, nullable=False)
    state = Column(String(100), index=True, nullable=True)
    county = Column(String(100), nullable=True)
    population = Column(Integer, default=0, index=True)
    settlement_type = Column(String(50), default="city", index=True)  # city, town, village, hamlet
    latitude = Column(Float, default=0.0)
    longitude = Column(Float, default=0.0)
    bbox = Column(String(255), nullable=True)
    osm_type = Column(String(20), nullable=True)
    osm_id = Column(String(50), nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Stay(Base):
    __tablename__ = "stays"

    id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    area = Column(String(100), nullable=True)
    category = Column(String(50), nullable=True)  # Budget, Moderate, Premium, Hostel, Homestay
    approximate_price = Column(Float, default=0.0)
    rating = Column(Float, default=4.0)
    description = Column(Text, nullable=True)
    image = Column(String(255), nullable=True)

    destination = relationship("Destination", back_populates="stays")


class FoodSpot(Base):
    __tablename__ = "food_spots"

    id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    cuisine = Column(String(100), nullable=True)
    specialty = Column(String(150), nullable=True)
    approximate_price = Column(Float, default=0.0)
    location = Column(String(150), nullable=True)
    description = Column(Text, nullable=True)
    image = Column(String(255), nullable=True)

    destination = relationship("Destination", back_populates="food_spots")


class LocalFood(Base):
    __tablename__ = "local_foods"

    id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    is_must_try = Column(Boolean, default=False)
    image = Column(String(255), nullable=True)

    destination = relationship("Destination", back_populates="local_foods")


class Transport(Base):
    __tablename__ = "transports"

    id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False)
    origin = Column(String(100), nullable=True)
    destination = Column(String(100), nullable=True)
    transport_mode = Column(String(50), nullable=False)  # Flight, Train, Bus, Taxi, Metro, Rental
    approximate_cost = Column(Float, default=0.0)
    approximate_duration = Column(String(50), nullable=True)

    destination_rel = relationship("Destination", back_populates="transports")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(150), nullable=False)
    destination_name = Column(String(100), nullable=False)
    trip_type = Column(String(50), default="Solo")  # Solo, Friends, Family
    travel_style = Column(String(50), default="Budget")  # Budget, Comfort, Premium
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    number_of_days = Column(Integer, default=3)
    number_of_travelers = Column(Integer, default=1)
    total_budget = Column(Float, default=5000.0)
    status = Column(String(50), default="Upcoming")  # Upcoming, Active, Saved, Draft, Completed
    itinerary_json = Column(Text, nullable=True)
    packing_list_json = Column(Text, nullable=True)
    actual_expenses_json = Column(Text, nullable=True)
    interests_json = Column(Text, nullable=True)
    food_preferences = Column(String(255), nullable=True)
    special_requirements = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user_rel = relationship("User", back_populates="trips")


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    item_type = Column(String(50), nullable=False)  # destination, place, stay, food_spot
    item_id = Column(Integer, nullable=False)
    title = Column(String(150), nullable=False)
    subtitle = Column(String(150), nullable=True)
    image = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user_rel = relationship("User", back_populates="favorites")


class TravelHistory(Base):
    __tablename__ = "travel_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    item_type = Column(String(50), nullable=False)  # destination, place, food_spot
    item_id = Column(Integer, nullable=False)
    title = Column(String(150), nullable=False)
    viewed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user_rel = relationship("User", back_populates="history")
