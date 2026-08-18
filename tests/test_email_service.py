import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.email import LocalDevEmailService, DEV_EMAIL_LOG_PATH

client = TestClient(app)


def test_email_status_endpoint():
    """
    Verifies GET /email-status returns smtp_enabled and configured status without leaking secrets.
    """
    response = client.get("/email-status")
    assert response.status_code == 200
    data = response.json()
    assert "smtp_enabled" in data
    assert "configured" in data
    assert "password" not in data
    assert "username" not in data


def test_local_dev_email_logging_when_smtp_disabled():
    """
    Verifies that when SMTP is disabled, 5-digit OTP emails are safely logged to data/dev_emails.log.
    """
    original_enabled = settings.SMTP_ENABLED
    settings.SMTP_ENABLED = False

    try:
        test_email = "dev_log_otp_test@example.com"
        test_otp = "48217"

        LocalDevEmailService.send_verification_otp_email(
            email=test_email,
            name="Log Tester",
            otp=test_otp
        )

        assert os.path.exists(DEV_EMAIL_LOG_PATH)
        with open(DEV_EMAIL_LOG_PATH, "r", encoding="utf-8") as f:
            log_content = f.read()

        assert test_email in log_content
        assert test_otp in log_content
    finally:
        settings.SMTP_ENABLED = original_enabled


def test_smtp_delivery_attempt_when_enabled():
    """
    Mocks smtplib.SMTP to verify that when SMTP_ENABLED=True, real SMTP sending is attempted.
    """
    original_enabled = settings.SMTP_ENABLED
    original_host = settings.SMTP_HOST
    original_user = settings.SMTP_USERNAME
    original_pass = settings.SMTP_PASSWORD

    settings.SMTP_ENABLED = True
    settings.SMTP_HOST = "smtp.test.com"
    settings.SMTP_USERNAME = "testuser@test.com"
    settings.SMTP_PASSWORD = "testpassword123"

    try:
        with patch("smtplib.SMTP") as mock_smtp_cls:
            mock_server = MagicMock()
            mock_smtp_cls.return_value.__enter__.return_value = mock_server

            LocalDevEmailService.send_password_reset_otp_email(
                email="smtp_user@example.com",
                name="SMTP Tester",
                otp="98765"
            )

            assert mock_server.starttls.called
            mock_server.login.assert_called_once_with("testuser@test.com", "testpassword123")
            assert mock_server.send_message.called
    finally:
        settings.SMTP_ENABLED = original_enabled
        settings.SMTP_HOST = original_host
        settings.SMTP_USERNAME = original_user
        settings.SMTP_PASSWORD = original_pass


def test_smtp_failure_fallback_to_local_log():
    """
    Verifies that if SMTP server throws an exception, the app does NOT crash
    and continues logging the 5-digit OTP to dev_emails.log.
    """
    original_enabled = settings.SMTP_ENABLED
    settings.SMTP_ENABLED = True
    settings.SMTP_HOST = "failing.smtp.com"
    settings.SMTP_USERNAME = "failuser@test.com"

    try:
        with patch("smtplib.SMTP", side_effect=Exception("SMTP Connection Error")):
            LocalDevEmailService.send_verification_otp_email(
                email="fail_test@example.com",
                name="Fail Tester",
                otp="12345"
            )

        with open(DEV_EMAIL_LOG_PATH, "r", encoding="utf-8") as f:
            log_content = f.read()

        assert "fail_test@example.com" in log_content
        assert "12345" in log_content
    finally:
        settings.SMTP_ENABLED = original_enabled
