from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.database import get_db
from app.database.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

# --- GLOBAL DEVELOPMENT AUTHENTICATION CONTROL ---
# Set AUTH_ENABLED = False to disable authentication requirements globally.
AUTH_ENABLED = False
DEV_AUTH_BYPASS = not AUTH_ENABLED
DEV_USER_EMAIL = "dev@aitravelplanner.local"


def get_token_from_request(request: Request, token_header: Optional[str] = Depends(oauth2_scheme)) -> Optional[str]:
    if token_header:
        return token_header
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        if cookie_token.startswith("Bearer "):
            return cookie_token[7:]
        return cookie_token
    return None


def get_or_create_dev_user(db: Session) -> User:
    user = db.query(User).filter(User.email == DEV_USER_EMAIL).first()
    if not user:
        from app.core.security import hash_password
        user = User(
            id=1,
            email=DEV_USER_EMAIL,
            full_name="Dev Traveler",
            mobile_number="+919876543210",
            hashed_password=hash_password("DevPassword123!"),
            is_active=True,
            is_verified=True,
            is_mobile_verified=True,
            preferred_language="en",
            travel_style="Comfort",
            food_preference="Local Specialties",
            budget_preference="Moderate",
            interests="Heritage, Nature, Beach, Food"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_current_user_optional(
    request: Request,
    token: Optional[str] = Depends(get_token_from_request),
    db: Session = Depends(get_db)
) -> Optional[User]:
    # 1. If a valid JWT token is provided in request headers or cookies, use that user
    if token:
        payload = decode_access_token(token)
        if payload:
            email: str = payload.get("sub")
            if email:
                user = db.query(User).filter(User.email == email).first()
                if user and user.is_active:
                    return user

    # 2. Otherwise fall back to Dev Traveler for guest/dev mode
    return get_or_create_dev_user(db)


def get_current_user(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    if user:
        return user
    return get_or_create_dev_user(db)


def require_web_authentication(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    if user:
        return user
    return get_or_create_dev_user(db)
