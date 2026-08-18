from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.auth.schemas import (
    UserCreate, UserRegisterResponse, UserResponse, UserLogin, Token, ProfileUpdate,
    VerifyEmailOTPRequest, ResendOTPRequest, ForgotPasswordRequest,
    VerifyResetOTPRequest, ResetPasswordWithOTPRequest,
    SendMobileOTPRequest, VerifyMobileOTPRequest, ResendMobileOTPRequest,
    ChangePasswordRequest, ChangePhoneRequest, VerifyPhoneChangeRequest,
    ChangeEmailRequest, VerifyEmailChangeRequest, LanguageUpdateRequest
)
from app.auth.service import (
    register_new_user, authenticate_user, verify_email_otp,
    resend_verification_otp, create_password_reset_otp_request,
    verify_password_reset_otp, reset_user_password_with_otp,
    update_user_profile, send_mobile_verification_otp,
    verify_mobile_otp, resend_mobile_otp,
    change_user_password, request_phone_change, verify_phone_change,
    request_email_change, verify_email_change, update_user_language
)
from app.database.models import User

router = APIRouter(prefix="/auth", tags=["Authentication & User Settings"])


@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return register_new_user(db, data)


@router.post("/verify-email-otp")
def verify_otp(data: VerifyEmailOTPRequest, db: Session = Depends(get_db)):
    return verify_email_otp(db, email=data.email, otp=data.otp)


@router.post("/resend-verification-otp")
def resend_otp(data: ResendOTPRequest, db: Session = Depends(get_db)):
    return resend_verification_otp(db, email=data.email)


@router.post("/send-mobile-otp")
def send_mobile_otp_endpoint(data: SendMobileOTPRequest, db: Session = Depends(get_db)):
    return send_mobile_verification_otp(db, mobile_number=data.mobile_number)


@router.post("/verify-mobile-otp")
def verify_mobile_otp_endpoint(data: VerifyMobileOTPRequest, db: Session = Depends(get_db)):
    return verify_mobile_otp(db, mobile_number=data.mobile_number, otp=data.otp)


@router.post("/resend-mobile-otp")
def resend_mobile_otp_endpoint(data: ResendMobileOTPRequest, db: Session = Depends(get_db)):
    return resend_mobile_otp(db, mobile_number=data.mobile_number)


@router.post("/forgot-password")
def forgot_password_otp(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return create_password_reset_otp_request(db, email=data.email)


@router.post("/verify-reset-otp")
def verify_reset_otp(data: VerifyResetOTPRequest, db: Session = Depends(get_db)):
    return verify_password_reset_otp(db, email=data.email, otp=data.otp)


@router.post("/reset-password")
def reset_password_with_otp(data: ResetPasswordWithOTPRequest, db: Session = Depends(get_db)):
    return reset_user_password_with_otp(db, email=data.email, otp=data.otp, new_password=data.new_password)


@router.put("/change-password")
def change_password_endpoint(data: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return change_user_password(db, current_user, data.current_password, data.new_password)


@router.post("/change-phone")
def change_phone_endpoint(data: ChangePhoneRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return request_phone_change(db, current_user, data.new_mobile_number)


@router.post("/verify-phone-change")
def verify_phone_change_endpoint(data: VerifyPhoneChangeRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return verify_phone_change(db, current_user, data.new_mobile_number, data.otp)


@router.post("/change-email")
def change_email_endpoint(data: ChangeEmailRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return request_email_change(db, current_user, data.new_email)


@router.post("/verify-email-change")
def verify_email_change_endpoint(data: VerifyEmailChangeRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return verify_email_change(db, current_user, data.new_email, data.otp)


@router.put("/language")
def update_language_endpoint(data: LanguageUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return update_user_language(db, current_user, data.language)


@router.post("/login", response_model=Token)
def login_form(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    token_obj = authenticate_user(db, form_data.username, form_data.password)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token_obj.access_token}",
        httponly=True,
        samesite="lax"
    )
    return token_obj


@router.post("/login/json", response_model=Token)
def login_json(data: UserLogin, response: Response, db: Session = Depends(get_db)):
    token_obj = authenticate_user(db, data.email, data.password)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token_obj.access_token}",
        httponly=True,
        samesite="lax"
    )
    return token_obj


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=UserResponse)
def update_profile(data: ProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return update_user_profile(db, current_user, data)
