import os
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime, timezone

from app.core.config import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DEV_EMAIL_LOG_PATH = os.path.join(DATA_DIR, "dev_emails.log")


class LocalDevEmailService:
    """
    Email Service supporting both SMTP real inbox delivery and local log fallback for 5-Digit OTPs.
    - If SMTP_ENABLED=true, sends live emails over TLS via smtplib.
    - If SMTP delivery fails or SMTP_ENABLED=false, logs to data/dev_emails.log with notice.
    - Never exposes SMTP passwords.
    """

    @classmethod
    def get_email_status(cls) -> dict:
        return {
            "smtp_enabled": settings.SMTP_ENABLED,
            "configured": bool(settings.SMTP_ENABLED and settings.SMTP_HOST),
            "smtp_host": settings.SMTP_HOST if settings.SMTP_HOST else "Not Configured",
            "smtp_port": settings.SMTP_PORT,
            "smtp_from_email": settings.SMTP_FROM_EMAIL if settings.SMTP_FROM_EMAIL else "Not Configured",
            "dev_log_fallback": True,
            "dev_log_path": DEV_EMAIL_LOG_PATH
        }

    @classmethod
    def get_status(cls) -> dict:
        return cls.get_email_status()

    @classmethod
    def _send_smtp_message(cls, recipient: str, subject: str, body: str) -> bool:
        if not settings.SMTP_ENABLED or not settings.SMTP_HOST or not settings.SMTP_USERNAME:
            print(f"[SMTP NOTICE] SMTP is disabled or unconfigured. Writing email to dev log.")
            return False

        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            from_addr = settings.SMTP_FROM_EMAIL or settings.SMTP_USERNAME
            msg["From"] = f"{settings.SMTP_FROM_NAME} <{from_addr}>"
            msg["To"] = recipient
            msg.set_content(body)

            context = ssl.create_default_context()
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.starttls(context=context)
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)

            print(f"[SMTP EMAIL DELIVERED] Email successfully sent to {recipient}")
            return True
        except Exception as e:
            print(f"[SMTP DELIVERY ERROR] SMTP delivery to {recipient} failed ({e}). Fallback to local dev log.")
            return False

    @classmethod
    def send_verification_otp_email(cls, email: str, name: str, otp: str):
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        subject = "Verify your AI Travel Planner account - 5-Digit Code"
        body = (
            f"Hello {name or 'Traveler'},\n\n"
            f"Your 5-digit verification code is:\n\n"
            f"  {otp}\n\n"
            f"Please enter this code on the verification page to activate your account.\n"
            f"This verification code expires in 10 minutes.\n\n"
            f"Best regards,\n"
            f"AI Travel Planner Team"
        )

        email_log_entry = (
            f"===============================================================\n"
            f"[DEVELOPMENT EMAIL OTP NOTICE - ZERO EXTERNAL API KEYS REQUIRED]\n"
            f"TIMESTAMP: {timestamp}\n"
            f"TYPE: 5-DIGIT VERIFICATION OTP\n"
            f"TO: {name} <{email}>\n"
            f"SUBJECT: {subject}\n"
            f"OTP CODE: {otp}\n"
            f"---------------------------------------------------------------\n"
            f"{body}\n"
            f"===============================================================\n\n"
        )

        with open(DEV_EMAIL_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(email_log_entry)

        cls._send_smtp_message(recipient=email, subject=subject, body=body)

    @classmethod
    def send_password_reset_otp_email(cls, email: str, name: str, otp: str):
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        subject = "Reset your AI Travel Planner password - 5-Digit Code"
        body = (
            f"Hello {name or 'Traveler'},\n\n"
            f"Your 5-digit password reset code is:\n\n"
            f"  {otp}\n\n"
            f"Use this code to verify your identity and set a new password.\n"
            f"This code expires in 10 minutes.\n\n"
            f"If you did not request a password reset, please ignore this message.\n\n"
            f"Best regards,\n"
            f"AI Travel Planner Team"
        )

        email_log_entry = (
            f"===============================================================\n"
            f"TIMESTAMP: {timestamp}\n"
            f"TYPE: 5-DIGIT PASSWORD RESET OTP\n"
            f"TO: {name} <{email}>\n"
            f"SUBJECT: {subject}\n"
            f"OTP CODE: {otp}\n"
            f"---------------------------------------------------------------\n"
            f"{body}\n"
            f"===============================================================\n\n"
        )

        with open(DEV_EMAIL_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(email_log_entry)

        cls._send_smtp_message(recipient=email, subject=subject, body=body)

    # Aliases for backward compatibility
    @classmethod
    def send_verification_email(cls, email: str, name: str, token: str, host_url: str = None):
        cls.send_verification_otp_email(email=email, name=name, otp=token)

    @classmethod
    def send_password_reset_email(cls, email: str, name: str, token: str, host_url: str = None):
        cls.send_password_reset_otp_email(email=email, name=name, otp=token)
