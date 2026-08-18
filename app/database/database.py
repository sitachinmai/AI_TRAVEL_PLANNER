import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "travel_planner.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Creates tables and performs safe, non-destructive ALTER TABLE migrations.
    Never wipes or resets data/travel_planner.db.
    """
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)

    # Migrations for users table
    if "users" in inspector.get_table_names():
        user_columns = [col["name"] for col in inspector.get_columns("users")]
        with engine.begin() as conn:
            if "preferred_language" not in user_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN preferred_language VARCHAR(10) DEFAULT 'en';"))
            if "pending_email" not in user_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN pending_email VARCHAR(120);"))
            if "pending_email_otp_hash" not in user_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN pending_email_otp_hash VARCHAR(255);"))
            if "pending_email_otp_expires_at" not in user_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN pending_email_otp_expires_at DATETIME;"))
            if "pending_email_otp_attempts" not in user_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN pending_email_otp_attempts INTEGER DEFAULT 0;"))
            if "pending_mobile_number" not in user_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN pending_mobile_number VARCHAR(20);"))
            if "pending_mobile_otp_hash" not in user_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN pending_mobile_otp_hash VARCHAR(255);"))
            if "pending_mobile_otp_expires_at" not in user_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN pending_mobile_otp_expires_at DATETIME;"))
            if "pending_mobile_otp_attempts" not in user_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN pending_mobile_otp_attempts INTEGER DEFAULT 0;"))

    # Migrations for destinations table
    if "destinations" in inspector.get_table_names():
        dest_columns = [col["name"] for col in inspector.get_columns("destinations")]
        with engine.begin() as conn:
            if "country_id" not in dest_columns:
                conn.execute(text("ALTER TABLE destinations ADD COLUMN country_id INTEGER REFERENCES countries(id);"))

    # Migrations for trips table
    if "trips" in inspector.get_table_names():
        trip_columns = [col["name"] for col in inspector.get_columns("trips")]
        with engine.begin() as conn:
            if "actual_expenses_json" not in trip_columns:
                conn.execute(text("ALTER TABLE trips ADD COLUMN actual_expenses_json TEXT;"))
            if "interests_json" not in trip_columns:
                conn.execute(text("ALTER TABLE trips ADD COLUMN interests_json TEXT;"))
            if "food_preferences" not in trip_columns:
                conn.execute(text("ALTER TABLE trips ADD COLUMN food_preferences VARCHAR(255);"))
            if "special_requirements" not in trip_columns:
                conn.execute(text("ALTER TABLE trips ADD COLUMN special_requirements TEXT;"))
