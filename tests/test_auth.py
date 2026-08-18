import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.database import SessionLocal
from app.database.models import User
from app.core.security import hash_otp

client = TestClient(app)


def cleanup_user(email: str):
    db: Session = SessionLocal()
    db.query(User).filter(User.email == email.lower()).delete()
    db.commit()
    db.close()


def test_user_registration_generates_5digit_otp():
    """
    Tests successful registration of a new user generating a 5-digit OTP hash.
    """
    email = "otp_reg_test@example.com"
    cleanup_user(email)

    user_data = {
        "email": email,
        "full_name": "OTP Test User",
        "password": "securepassword123",
        "confirm_password": "securepassword123"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert data["is_verified"] is False
    assert "verification_context_token" in data

    # Check database OTP hash
    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    assert user is not None
    assert user.email_verification_otp_hash is not None
    assert user.email_otp_attempts == 0
    db.close()


def test_unverified_login_blocked():
    """
    Verifies that unverified accounts are blocked from logging in with 403 Forbidden.
    """
    email = "unverified_block@example.com"
    cleanup_user(email)

    client.post("/auth/register", json={
        "email": email,
        "full_name": "Unverified User",
        "password": "password123",
        "confirm_password": "password123"
    })

    login_res = client.post("/auth/login/json", json={
        "email": email,
        "password": "password123"
    })
    assert login_res.status_code == 403
    assert "verify your email" in login_res.json()["detail"].lower()


def test_5digit_otp_verification_success():
    """
    Tests successful 5-digit OTP verification.
    """
    email = "otp_verify_success@example.com"
    cleanup_user(email)

    client.post("/auth/register", json={
        "email": email,
        "full_name": "Verify Success User",
        "password": "password123",
        "confirm_password": "password123"
    })

    # Set known OTP in DB for testing
    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    user.email_verification_otp_hash = hash_otp("48217")
    db.commit()
    db.close()

    # Submit correct 5-digit OTP
    verify_res = client.post("/auth/verify-email-otp", json={
        "email": email,
        "otp": "48217"
    })
    assert verify_res.status_code == 200
    assert verify_res.json()["is_verified"] is True

    # Login after verification must succeed
    login_res = client.post("/auth/login/json", json={
        "email": email,
        "password": "password123"
    })
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()


def test_invalid_otp_increments_attempts():
    """
    Tests that submitting an incorrect 5-digit OTP increments attempt counter.
    """
    email = "otp_invalid_test@example.com"
    cleanup_user(email)

    client.post("/auth/register", json={
        "email": email,
        "full_name": "Invalid OTP User",
        "password": "password123",
        "confirm_password": "password123"
    })

    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    user.email_verification_otp_hash = hash_otp("12345")
    db.commit()
    db.close()

    # Submit wrong OTP
    verify_res = client.post("/auth/verify-email-otp", json={
        "email": email,
        "otp": "99999"
    })
    assert verify_res.status_code == 400
    assert "Invalid 5-digit" in verify_res.json()["detail"]

    # Verify attempt counter in database
    db = SessionLocal()
    user_updated = db.query(User).filter(User.email == email).first()
    assert user_updated.email_otp_attempts == 1
    db.close()


def test_resend_otp_cooldown_rate_limit():
    """
    Tests resending OTP enforces 60-second rate-limiting cooldown.
    """
    email = "resend_cooldown@example.com"
    cleanup_user(email)

    client.post("/auth/register", json={
        "email": email,
        "full_name": "Cooldown User",
        "password": "password123",
        "confirm_password": "password123"
    })

    # Immediate resend attempt -> Must trigger 429 Too Many Requests
    resend_res = client.post("/auth/resend-verification-otp", json={"email": email})
    assert resend_res.status_code == 429
    assert "Please wait" in resend_res.json()["detail"]
