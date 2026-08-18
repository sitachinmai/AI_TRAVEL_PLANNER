import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from app.core.config import settings

# Initialize Argon2 password hasher
password_hash = PasswordHash((Argon2Hasher(),))


def hash_password(password: str) -> str:
    """
    Hashes raw plaintext password using Argon2 algorithm.
    """
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies raw plaintext password against stored Argon2 hash.
    """
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Encodes payload data into a signed JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes and verifies a signed JWT access token.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except Exception:
        return None


def generate_secure_token() -> str:
    """
    Generates a cryptographically secure random url-safe token string.
    """
    return secrets.token_urlsafe(32)


def generate_5digit_otp() -> str:
    """
    Generates a cryptographically secure 5-digit numeric OTP string (10000 - 99999).
    """
    return str(secrets.randbelow(90000) + 10000)


def hash_otp(otp: str) -> str:
    """
    Computes a SHA-256 hash string for a 5-digit OTP so plaintext is never stored.
    """
    return hashlib.sha256(otp.strip().encode("utf-8")).hexdigest()


def verify_otp_hash(plain_otp: str, stored_hash: str) -> bool:
    """
    Verifies a raw 5-digit OTP against its stored SHA-256 hash string.
    """
    if not plain_otp or not stored_hash:
        return False
    return secrets.compare_digest(hash_otp(plain_otp), stored_hash)
