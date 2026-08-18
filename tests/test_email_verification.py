from datetime import datetime, timedelta, timezone
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


def test_full_5digit_otp_verification_lifecycle():
    """
    Complete lifecycle test for 5-digit OTP email verification.
    """
    email = "lifecycle_otp@example.com"
    cleanup_user(email)

    # 1. Register unverified user
    reg_res = client.post("/auth/register", json={
        "email": email,
        "full_name": "Lifecycle OTP User",
        "password": "password123",
        "confirm_password": "password123"
    })
    assert reg_res.status_code == 201

    # 2. Login before verification fails
    login_res = client.post("/auth/login/json", json={
        "email": email,
        "password": "password123"
    })
    assert login_res.status_code == 403

    # Set known OTP hash
    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    user.email_verification_otp_hash = hash_otp("54321")
    db.commit()
    db.close()

    # 3. Submit valid 5-digit OTP
    verify_res = client.post("/auth/verify-email-otp", json={
        "email": email,
        "otp": "54321"
    })
    assert verify_res.status_code == 200
    assert verify_res.json()["is_verified"] is True

    # 4. Login after verification succeeds
    login_ok = client.post("/auth/login/json", json={
        "email": email,
        "password": "password123"
    })
    assert login_ok.status_code == 200
    assert "access_token" in login_ok.json()


def test_expired_otp_rejection():
    """
    Tests that an expired OTP (> 10 mins) is rejected.
    """
    email = "expired_otp_user@example.com"
    cleanup_user(email)

    client.post("/auth/register", json={
        "email": email,
        "full_name": "Expired OTP User",
        "password": "password123",
        "confirm_password": "password123"
    })

    # Manually set expired timestamp in DB
    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    user.email_verification_otp_hash = hash_otp("88888")
    user.email_verification_otp_expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db.commit()
    db.close()

    # Attempt verification
    verify_res = client.post("/auth/verify-email-otp", json={
        "email": email,
        "otp": "88888"
    })
    assert verify_res.status_code == 400
    assert "expired" in verify_res.json()["detail"].lower()


def test_max_attempts_exceeded_blocks_otp():
    """
    Tests that exceeding 5 failed attempt limits blocks OTP verification.
    """
    email = "max_attempts@example.com"
    cleanup_user(email)

    client.post("/auth/register", json={
        "email": email,
        "full_name": "Max Attempts User",
        "password": "password123",
        "confirm_password": "password123"
    })

    # Set email_otp_attempts to 5
    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    user.email_verification_otp_hash = hash_otp("77777")
    user.email_otp_attempts = 5
    db.commit()
    db.close()

    verify_res = client.post("/auth/verify-email-otp", json={
        "email": email,
        "otp": "77777"
    })
    assert verify_res.status_code == 429
    assert "Maximum verification attempts exceeded" in verify_res.json()["detail"]
