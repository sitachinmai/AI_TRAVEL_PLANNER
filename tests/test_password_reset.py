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


def test_password_reset_otp_flow():
    """
    Complete lifecycle test for forgot password, 5-digit OTP verification, and Argon2 password update.
    """
    email = "reset_otp_user@example.com"
    cleanup_user(email)

    # 1. Register and verify user
    client.post("/auth/register", json={
        "email": email,
        "full_name": "Reset OTP User",
        "password": "oldpassword123",
        "confirm_password": "oldpassword123"
    })

    db: Session = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    user.is_verified = True
    user.otp_last_sent_at = None  # Reset cooldown for immediate test call
    db.commit()
    db.close()

    # 2. Request forgot password OTP
    forgot_res = client.post("/auth/forgot-password", json={"email": email})
    assert forgot_res.status_code == 200

    # Set known reset OTP hash
    db = SessionLocal()
    reset_user = db.query(User).filter(User.email == email).first()
    reset_user.password_reset_otp_hash = hash_otp("33333")
    reset_user.password_reset_otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    db.commit()
    db.close()

    # 3. Verify reset OTP
    verify_res = client.post("/auth/verify-reset-otp", json={
        "email": email,
        "otp": "33333"
    })
    assert verify_res.status_code == 200
    assert "reset_token" in verify_res.json()

    # 4. Submit password reset with new password
    reset_res = client.post("/auth/reset-password", json={
        "email": email,
        "otp": "33333",
        "new_password": "newsecurepassword456",
        "confirm_password": "newsecurepassword456"
    })
    assert reset_res.status_code == 200
    assert "Password reset successfully" in reset_res.json()["message"]

    # 5. Old password fails
    old_login = client.post("/auth/login/json", json={
        "email": email,
        "password": "oldpassword123"
    })
    assert old_login.status_code == 401

    # 6. New password succeeds
    new_login = client.post("/auth/login/json", json={
        "email": email,
        "password": "newsecurepassword456"
    })
    assert new_login.status_code == 200
    assert "access_token" in new_login.json()
