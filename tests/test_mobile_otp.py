import os
import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.database.models import User
from app.core.security import hash_password, generate_5digit_otp, hash_otp
from app.core.mobile_otp import DEV_MOBILE_OTP_LOG_PATH

client = TestClient(app)


def test_full_registration_email_and_mobile_otp_flow():
    """
    Tests the complete end-to-end user journey:
    Register -> Email OTP Verification -> Mobile OTP Verification -> Successful Login
    """
    db = SessionLocal()
    unique_email = f"mobile_test_{datetime.now().timestamp()}@example.com"
    unique_mobile = f"+9199{int(datetime.now().timestamp()) % 100000000}"

    # 1. Register new user
    reg_res = client.post("/auth/register", json={
        "full_name": "OTP Test User",
        "email": unique_email,
        "mobile_number": unique_mobile,
        "password": "Password123!",
        "confirm_password": "Password123!"
    })
    assert reg_res.status_code == 201

    user = db.query(User).filter(User.email == unique_email).first()
    assert user is not None
    assert user.is_verified is False
    assert user.is_mobile_verified is False
    assert user.mobile_verification_otp_hash is not None

    # Verify log output format
    assert os.path.exists(DEV_MOBILE_OTP_LOG_PATH)
    with open(DEV_MOBILE_OTP_LOG_PATH, "r", encoding="utf-8") as f:
        log_content = f.read()
        assert "[DEVELOPMENT MOBILE OTP NOTICE" in log_content

    # 2. Attempt login before email verification -> Blocked (403)
    login_res_1 = client.post("/auth/login/json", json={"email": unique_email, "password": "Password123!"})
    assert login_res_1.status_code == 403

    # 3. Manually verify Email OTP directly in DB to test Mobile restriction
    user.is_verified = True
    db.commit()

    # 4. Attempt login after email verification but BEFORE mobile verification -> Blocked (403)
    login_res_2 = client.post("/auth/login/json", json={"email": unique_email, "password": "Password123!"})
    assert login_res_2.status_code == 403
    assert "mobile" in login_res_2.json()["detail"].lower()

    # 5. Generate fresh Mobile OTP and verify
    raw_mobile_otp = "84920"
    user.mobile_verification_otp_hash = hash_otp(raw_mobile_otp)
    user.mobile_verification_otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    db.commit()

    # 6. Verify with wrong OTP -> Rejected
    verify_wrong = client.post("/auth/verify-mobile-otp", json={
        "mobile_number": unique_mobile,
        "otp": "00000"
    })
    assert verify_wrong.status_code == 400

    # 7. Verify with correct OTP -> Success
    verify_correct = client.post("/auth/verify-mobile-otp", json={
        "mobile_number": unique_mobile,
        "otp": raw_mobile_otp
    })
    assert verify_correct.status_code == 200
    assert verify_correct.json()["is_mobile_verified"] is True

    # 8. Attempt login after BOTH verifications -> Success!
    login_res_3 = client.post("/auth/login/json", json={"email": unique_email, "password": "Password123!"})
    assert login_res_3.status_code == 200
    assert "access_token" in login_res_3.json()

    db.close()


def test_mobile_otp_resend_cooldown_and_5_attempt_limit():
    """
    Tests 60-second cooldown on resends and 5-attempt rate limit locking.
    """
    db = SessionLocal()
    unique_email = f"cooldown_test_{datetime.now().timestamp()}@example.com"
    unique_mobile = f"+9198{int(datetime.now().timestamp()) % 100000000}"

    client.post("/auth/register", json={
        "full_name": "Cooldown User",
        "email": unique_email,
        "mobile_number": unique_mobile,
        "password": "Password123!",
        "confirm_password": "Password123!"
    })

    # Immediate second resend should fail with 429 Cooldown
    resend_res_1 = client.post("/auth/resend-mobile-otp", json={"mobile_number": unique_mobile})
    assert resend_res_1.status_code == 429

    # Test 5 failed attempts limit
    user = db.query(User).filter(User.email == unique_email).first()
    user.mobile_otp_attempts = 5
    db.commit()

    attempt_locked = client.post("/auth/verify-mobile-otp", json={
        "mobile_number": unique_mobile,
        "otp": "12345"
    })
    assert attempt_locked.status_code == 429

    db.close()
