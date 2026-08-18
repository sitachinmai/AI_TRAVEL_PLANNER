from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class UserRegister(BaseModel):
    email: EmailStr
    mobile_number: Optional[str] = Field(None, max_length=20, description="Optional mobile number for verification")
    full_name: Optional[str] = Field(None, max_length=150)
    password: str = Field(..., min_length=6, description="Minimum 6 characters")
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


UserCreate = UserRegister


class UserRegisterResponse(BaseModel):
    id: int
    email: EmailStr
    mobile_number: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_mobile_verified: bool
    verification_context_token: Optional[str] = None
    message: str = "Account created. Please verify your email and mobile number using 5-digit OTPs."

    model_config = ConfigDict(from_attributes=True)


class VerifyEmailOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=5, max_length=5, description="Exactly 5-digit numeric OTP")
    verification_token: Optional[str] = None


class ResendOTPRequest(BaseModel):
    email: EmailStr


class SendMobileOTPRequest(BaseModel):
    mobile_number: str


class VerifyMobileOTPRequest(BaseModel):
    mobile_number: str
    otp: str = Field(..., min_length=5, max_length=5, description="Exactly 5-digit numeric OTP")


class ResendMobileOTPRequest(BaseModel):
    mobile_number: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyResetOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=5, max_length=5, description="Exactly 5-digit numeric OTP")


class ResetPasswordWithOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=5, max_length=5, description="Exactly 5-digit numeric OTP")
    new_password: str = Field(..., min_length=6, description="Minimum 6 characters")
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def reset_passwords_match(cls, v: str, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)
    confirm_new_password: str

    @field_validator("confirm_new_password")
    @classmethod
    def new_passwords_match(cls, v: str, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("New passwords do not match")
        return v


class ChangePhoneRequest(BaseModel):
    new_mobile_number: str = Field(..., min_length=8, max_length=20)


class VerifyPhoneChangeRequest(BaseModel):
    new_mobile_number: str
    otp: str = Field(..., min_length=5, max_length=5)


class ChangeEmailRequest(BaseModel):
    new_email: EmailStr


class VerifyEmailChangeRequest(BaseModel):
    new_email: EmailStr
    otp: str = Field(..., min_length=5, max_length=5)


class LanguageUpdateRequest(BaseModel):
    language: str = Field(..., max_length=10, description="en, hi, or te")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    mobile_number: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_mobile_verified: bool
    preferred_language: Optional[str] = "en"
    travel_style: Optional[str] = None
    food_preference: Optional[str] = None
    budget_preference: Optional[str] = None
    interests: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=150)
    mobile_number: Optional[str] = Field(None, max_length=20)
    travel_style: Optional[str] = Field(None, max_length=50)
    food_preference: Optional[str] = Field(None, max_length=100)
    budget_preference: Optional[str] = Field(None, max_length=50)
    interests: Optional[str] = Field(None, max_length=255)
