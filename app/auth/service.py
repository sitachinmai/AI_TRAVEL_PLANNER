import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password, verify_password, create_access_token,
    generate_5digit_otp, hash_otp, verify_otp_hash, generate_secure_token
)
from app.core.email import LocalDevEmailService
from app.core.mobile_otp import LocalDevMobileOTPService
from app.database.models import User
from app.auth.schemas import (
    UserCreate, UserRegisterResponse, UserLogin, Token, ProfileUpdate,
    VerifyEmailOTPRequest, ResendOTPRequest, ForgotPasswordRequest,
    VerifyResetOTPRequest, ResetPasswordWithOTPRequest,
    SendMobileOTPRequest, VerifyMobileOTPRequest, ResendMobileOTPRequest
)

MAX_OTP_ATTEMPTS = 5
RESEND_COOLDOWN_SECONDS = 60


def register_new_user(db: Session, data: UserCreate) -> UserRegisterResponse:
    existing = db.query(User).filter(User.email == data.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=10)
    verification_context_token = generate_secure_token()

    email_otp = generate_5digit_otp()
    email_otp_hash = hash_otp(email_otp)

    mobile_otp = generate_5digit_otp()
    mobile_otp_hash = hash_otp(mobile_otp)

    has_mobile = bool(data.mobile_number and data.mobile_number.strip())

    user = User(
        email=data.email.lower(),
        mobile_number=data.mobile_number.strip() if has_mobile else None,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        is_active=True,
        is_verified=False,
        is_mobile_verified=not has_mobile,
        preferred_language="en",
        verification_token=verification_context_token,
        email_verification_otp_hash=email_otp_hash,
        email_verification_otp_expires_at=expires_at,
        email_otp_attempts=0,
        mobile_verification_otp_hash=mobile_otp_hash,
        mobile_verification_otp_expires_at=expires_at,
        mobile_otp_attempts=0,
        mobile_otp_last_sent_at=now,
        otp_last_sent_at=now
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    LocalDevEmailService.send_verification_otp_email(
        email=user.email,
        name=user.full_name,
        otp=email_otp
    )

    if user.mobile_number:
        LocalDevMobileOTPService.send_mobile_verification_otp(
            mobile_number=user.mobile_number,
            name=user.full_name,
            otp=mobile_otp
        )

    return UserRegisterResponse(
        id=user.id,
        email=user.email,
        mobile_number=user.mobile_number,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        is_mobile_verified=user.is_mobile_verified,
        verification_context_token=verification_context_token,
        message="Account created successfully. 5-digit OTPs sent to your email and mobile number."
    )


def verify_email_otp(db: Session, email: str, otp: str) -> dict:
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user:
        raise HTTPException(status_code=400, detail="User account not found.")

    if user.is_verified:
        return {"message": "Email is already verified.", "is_verified": True}

    if user.email_otp_attempts >= MAX_OTP_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Maximum verification attempts exceeded.")

    if not user.email_verification_otp_expires_at or not user.email_verification_otp_hash:
        raise HTTPException(status_code=400, detail="No active verification code found.")

    expires_at = user.email_verification_otp_expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=400, detail="Verification OTP has expired.")

    if not verify_otp_hash(otp, user.email_verification_otp_hash):
        user.email_otp_attempts += 1
        db.commit()
        remaining = MAX_OTP_ATTEMPTS - user.email_otp_attempts
        raise HTTPException(status_code=400, detail=f"Invalid 5-digit verification OTP. {remaining} attempt(s) remaining.")

    user.is_verified = True
    user.email_verification_otp_hash = None
    user.email_verification_otp_expires_at = None
    user.email_otp_attempts = 0
    db.commit()

    return {"message": "Email verified successfully!", "is_verified": True}


def send_mobile_verification_otp(db: Session, mobile_number: str) -> dict:
    user = db.query(User).filter(User.mobile_number == mobile_number.strip()).first()
    if not user:
        raise HTTPException(status_code=400, detail="User account with this mobile number not found.")

    if user.is_mobile_verified:
        return {"message": "Mobile number is already verified.", "is_mobile_verified": True}

    now = datetime.now(timezone.utc)
    if user.mobile_otp_last_sent_at:
        last_sent = user.mobile_otp_last_sent_at
        if last_sent.tzinfo is None:
            last_sent = last_sent.replace(tzinfo=timezone.utc)
        elapsed = (now - last_sent).total_seconds()
        if elapsed < RESEND_COOLDOWN_SECONDS:
            wait_seconds = int(RESEND_COOLDOWN_SECONDS - elapsed)
            raise HTTPException(status_code=429, detail=f"Please wait {wait_seconds} seconds before requesting a new mobile OTP.")

    otp = generate_5digit_otp()
    user.mobile_verification_otp_hash = hash_otp(otp)
    user.mobile_verification_otp_expires_at = now + timedelta(minutes=10)
    user.mobile_otp_attempts = 0
    user.mobile_otp_last_sent_at = now
    db.commit()

    LocalDevMobileOTPService.send_mobile_verification_otp(
        mobile_number=user.mobile_number,
        name=user.full_name,
        otp=otp
    )

    return {"message": "A 5-digit Mobile OTP has been generated and logged (data/dev_mobile_otps.log)."}


def verify_mobile_otp(db: Session, mobile_number: str, otp: str) -> dict:
    user = db.query(User).filter(User.mobile_number == mobile_number.strip()).first()
    if not user:
        user = db.query(User).filter(User.email == mobile_number.lower()).first()

    if not user:
        raise HTTPException(status_code=400, detail="User account not found for mobile verification.")

    if user.is_mobile_verified:
        return {"message": "Mobile number is already verified.", "is_mobile_verified": True}

    if user.mobile_otp_attempts >= MAX_OTP_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Maximum mobile OTP attempts exceeded.")

    if not user.mobile_verification_otp_expires_at or not user.mobile_verification_otp_hash:
        raise HTTPException(status_code=400, detail="No active mobile verification code found.")

    expires_at = user.mobile_verification_otp_expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=400, detail="Mobile OTP has expired.")

    if not verify_otp_hash(otp, user.mobile_verification_otp_hash):
        user.mobile_otp_attempts += 1
        db.commit()
        remaining = MAX_OTP_ATTEMPTS - user.mobile_otp_attempts
        raise HTTPException(status_code=400, detail=f"Invalid 5-digit mobile OTP. {remaining} attempt(s) remaining.")

    user.is_mobile_verified = True
    user.mobile_verification_otp_hash = None
    user.mobile_verification_otp_expires_at = None
    user.mobile_otp_attempts = 0
    db.commit()

    return {"message": "Mobile number verified successfully!", "is_mobile_verified": True}


def resend_mobile_otp(db: Session, mobile_number: str) -> dict:
    return send_mobile_verification_otp(db, mobile_number)


def resend_verification_otp(db: Session, email: str) -> dict:
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user or user.is_verified:
        return {"message": "If an unverified account exists for this email, a new 5-digit OTP has been sent."}

    now = datetime.now(timezone.utc)
    if user.otp_last_sent_at:
        last_sent = user.otp_last_sent_at
        if last_sent.tzinfo is None:
            last_sent = last_sent.replace(tzinfo=timezone.utc)
        elapsed = (now - last_sent).total_seconds()
        if elapsed < RESEND_COOLDOWN_SECONDS:
            wait_seconds = int(RESEND_COOLDOWN_SECONDS - elapsed)
            raise HTTPException(status_code=429, detail=f"Please wait {wait_seconds} seconds before requesting a new OTP.")

    otp = generate_5digit_otp()
    user.email_verification_otp_hash = hash_otp(otp)
    user.email_verification_otp_expires_at = now + timedelta(minutes=10)
    user.email_otp_attempts = 0
    user.otp_last_sent_at = now
    db.commit()

    LocalDevEmailService.send_verification_otp_email(
        email=user.email,
        name=user.full_name,
        otp=otp
    )

    return {"message": "A new 5-digit verification code has been sent to your email."}


def create_password_reset_otp_request(db: Session, email: str) -> dict:
    user = db.query(User).filter(User.email == email.lower()).first()
    if user:
        now = datetime.now(timezone.utc)
        if user.otp_last_sent_at:
            last_sent = user.otp_last_sent_at
            if last_sent.tzinfo is None:
                last_sent = last_sent.replace(tzinfo=timezone.utc)
            elapsed = (now - last_sent).total_seconds()
            if elapsed < RESEND_COOLDOWN_SECONDS:
                wait_seconds = int(RESEND_COOLDOWN_SECONDS - elapsed)
                raise HTTPException(status_code=429, detail=f"Please wait {wait_seconds} seconds before requesting a new reset OTP.")

        otp = generate_5digit_otp()
        user.password_reset_otp_hash = hash_otp(otp)
        user.password_reset_otp_expires_at = now + timedelta(minutes=10)
        user.reset_otp_attempts = 0
        user.otp_last_sent_at = now
        db.commit()

        LocalDevEmailService.send_password_reset_otp_email(
            email=user.email,
            name=user.full_name,
            otp=otp
        )

    return {"message": "If an account exists for this email, a 5-digit password reset code has been sent."}


def verify_password_reset_otp(db: Session, email: str, otp: str) -> dict:
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user or not user.password_reset_otp_hash or not user.password_reset_otp_expires_at:
        raise HTTPException(status_code=400, detail="Invalid or expired reset request.")

    if user.reset_otp_attempts >= MAX_OTP_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Maximum reset attempts exceeded.")

    expires_at = user.password_reset_otp_expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=400, detail="Password reset OTP has expired.")

    if not verify_otp_hash(otp, user.password_reset_otp_hash):
        user.reset_otp_attempts += 1
        db.commit()
        remaining = MAX_OTP_ATTEMPTS - user.reset_otp_attempts
        raise HTTPException(status_code=400, detail=f"Invalid 5-digit reset OTP. {remaining} attempt(s) remaining.")

    reset_auth_token = generate_secure_token()
    user.reset_token = reset_auth_token
    user.reset_token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    db.commit()

    return {
        "message": "OTP verified successfully. You can now reset your password.",
        "reset_token": reset_auth_token
    }


def reset_user_password_with_otp(db: Session, email: str, otp: str, new_password: str) -> dict:
    verify_password_reset_otp(db, email, otp)
    user = db.query(User).filter(User.email == email.lower()).first()
    user.hashed_password = hash_password(new_password)
    user.password_reset_otp_hash = None
    user.password_reset_otp_expires_at = None
    user.reset_otp_attempts = 0
    user.reset_token = None
    user.reset_token_expires_at = None
    db.commit()

    return {"message": "Password reset successfully. You can now log in with your new password."}


def change_user_password(db: Session, user: User, current_password: str, new_password: str) -> dict:
    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password.")

    user.hashed_password = hash_password(new_password)
    db.commit()
    return {"message": "Password updated successfully!"}


def request_phone_change(db: Session, user: User, new_mobile_number: str) -> dict:
    new_mobile = new_mobile_number.strip()
    existing = db.query(User).filter(User.mobile_number == new_mobile, User.id != user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Another user account is already registered with this mobile number.")

    now = datetime.now(timezone.utc)
    otp = generate_5digit_otp()
    user.pending_mobile_number = new_mobile
    user.pending_mobile_otp_hash = hash_otp(otp)
    user.pending_mobile_otp_expires_at = now + timedelta(minutes=10)
    user.pending_mobile_otp_attempts = 0
    db.commit()

    LocalDevMobileOTPService.send_mobile_verification_otp(
        mobile_number=new_mobile,
        name=user.full_name,
        otp=otp
    )

    return {"message": "A 5-digit verification code has been sent to your new mobile number (logged to data/dev_mobile_otps.log)."}


def verify_phone_change(db: Session, user: User, new_mobile_number: str, otp: str) -> dict:
    if not user.pending_mobile_number or user.pending_mobile_number != new_mobile_number.strip():
        raise HTTPException(status_code=400, detail="Invalid pending mobile change request.")

    if user.pending_mobile_otp_attempts >= MAX_OTP_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Maximum attempts exceeded for mobile change.")

    if not user.pending_mobile_otp_expires_at or not user.pending_mobile_otp_hash:
        raise HTTPException(status_code=400, detail="No active mobile change request found.")

    expires_at = user.pending_mobile_otp_expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=400, detail="Mobile change OTP has expired.")

    if not verify_otp_hash(otp, user.pending_mobile_otp_hash):
        user.pending_mobile_otp_attempts += 1
        db.commit()
        remaining = MAX_OTP_ATTEMPTS - user.pending_mobile_otp_attempts
        raise HTTPException(status_code=400, detail=f"Invalid OTP code. {remaining} attempt(s) remaining.")

    user.mobile_number = user.pending_mobile_number
    user.is_mobile_verified = True
    user.pending_mobile_number = None
    user.pending_mobile_otp_hash = None
    user.pending_mobile_otp_expires_at = None
    user.pending_mobile_otp_attempts = 0
    db.commit()

    return {"message": "Mobile number updated and verified successfully!"}


def request_email_change(db: Session, user: User, new_email: str) -> dict:
    new_email_clean = new_email.lower().strip()
    existing = db.query(User).filter(User.email == new_email_clean, User.id != user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Another account is already registered with this email.")

    now = datetime.now(timezone.utc)
    otp = generate_5digit_otp()
    user.pending_email = new_email_clean
    user.pending_email_otp_hash = hash_otp(otp)
    user.pending_email_otp_expires_at = now + timedelta(minutes=10)
    user.pending_email_otp_attempts = 0
    db.commit()

    LocalDevEmailService.send_verification_otp_email(
        email=new_email_clean,
        name=user.full_name,
        otp=otp
    )

    return {"message": "A 5-digit verification code has been sent to your new email address."}


def verify_email_change(db: Session, user: User, new_email: str, otp: str) -> dict:
    if not user.pending_email or user.pending_email != new_email.lower().strip():
        raise HTTPException(status_code=400, detail="Invalid pending email change request.")

    if user.pending_email_otp_attempts >= MAX_OTP_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Maximum attempts exceeded for email change.")

    if not user.pending_email_otp_expires_at or not user.pending_email_otp_hash:
        raise HTTPException(status_code=400, detail="No active email change request found.")

    expires_at = user.pending_email_otp_expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=400, detail="Email change OTP has expired.")

    if not verify_otp_hash(otp, user.pending_email_otp_hash):
        user.pending_email_otp_attempts += 1
        db.commit()
        remaining = MAX_OTP_ATTEMPTS - user.pending_email_otp_attempts
        raise HTTPException(status_code=400, detail=f"Invalid OTP code. {remaining} attempt(s) remaining.")

    user.email = user.pending_email
    user.is_verified = True
    user.pending_email = None
    user.pending_email_otp_hash = None
    user.pending_email_otp_expires_at = None
    user.pending_email_otp_attempts = 0
    db.commit()

    return {"message": "Email address updated and verified successfully!"}


def update_user_language(db: Session, user: User, language: str) -> dict:
    lang = language.lower().strip()
    if lang not in ["en", "hi", "te"]:
        raise HTTPException(status_code=400, detail="Supported languages are: en, hi, te")
    user.preferred_language = lang
    db.commit()
    return {"message": "Language preference updated successfully!", "preferred_language": lang}


def authenticate_user(db: Session, email: str, password: str) -> Token:
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account.")

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email using the 5-digit OTP sent to your inbox before logging in."
        )

    if user.mobile_number and not user.is_mobile_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your mobile number using the 5-digit OTP sent to your phone before logging in."
        )

    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer")


def update_user_profile(db: Session, user: User, data: ProfileUpdate) -> User:
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.mobile_number is not None:
        user.mobile_number = data.mobile_number
    if data.travel_style is not None:
        user.travel_style = data.travel_style
    if data.food_preference is not None:
        user.food_preference = data.food_preference
    if data.budget_preference is not None:
        user.budget_preference = data.budget_preference
    if data.interests is not None:
        user.interests = data.interests

    db.commit()
    db.refresh(user)
    return user
