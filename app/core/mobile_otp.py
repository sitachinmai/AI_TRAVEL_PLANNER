import os
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DEV_MOBILE_OTP_LOG_PATH = os.path.join(DATA_DIR, "dev_mobile_otps.log")


class LocalDevMobileOTPService:
    """
    Local Development Mobile OTP Service.
    - Zero external SMS API keys required.
    - Safely logs generated 5-digit mobile OTPs to data/dev_mobile_otps.log with timestamp.
    - Clearly labels output as DEVELOPMENT MOBILE OTP.
    - Does not falsely claim SMS delivery.
    """

    @classmethod
    def send_mobile_verification_otp(cls, mobile_number: str, name: str, otp: str):
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        log_entry = (
            f"===============================================================\n"
            f"[DEVELOPMENT MOBILE OTP NOTICE - NO EXTERNAL SMS API USED]\n"
            f"TIMESTAMP: {timestamp}\n"
            f"TO USER: {name or 'Traveler'}\n"
            f"MOBILE NUMBER: {mobile_number or 'Unspecified'}\n"
            f"5-DIGIT MOBILE OTP: {otp}\n"
            f"EXPIRATION: 10 minutes\n"
            f"---------------------------------------------------------------\n"
            f"Enter code '{otp}' on the Mobile Verification Page to activate.\n"
            f"===============================================================\n\n"
        )

        # Write to log file
        with open(DEV_MOBILE_OTP_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(log_entry)

        # Also print clear development console log
        print(f"[DEVELOPMENT MOBILE OTP] Code '{otp}' generated for mobile '{mobile_number}'. Saved to data/dev_mobile_otps.log")
