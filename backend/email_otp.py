"""OTP generation, expiry tracking, validation, and email sending helpers."""

from __future__ import annotations

import hashlib
import secrets
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config.settings import (
    SMTP_CONFIGURATION_ERROR,
    SMTP_FROM,
    SMTP_HOST,
    SMTP_PORT,
    SMTP_PASSWORD,
    SMTP_USERNAME,
)

OTP_STORE: dict[str, dict[str, object]] = {}
LAST_OTP_EMAIL_ERROR = ""


def get_last_otp_email_error() -> str:
    """Return the latest safe-to-display OTP delivery error message."""
    return LAST_OTP_EMAIL_ERROR


def _normalise_email(email: str) -> str:
    return str(email or "").strip().lower()


def _hash_otp(otp_code: str) -> str:
    return hashlib.sha256(str(otp_code).strip().encode("utf-8")).hexdigest()


def generate_otp(length: int = 6) -> str:
    """Generate a numeric OTP code as a fixed-length string."""
    if length <= 0:
        return ""
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


def send_otp_email(to_email: str, otp_code: str, subject: str = "Madhu Bank OTP Verification") -> bool:
    """Send a numeric OTP to the provided email address using Gmail SMTP."""
    global LAST_OTP_EMAIL_ERROR

    if not to_email or not otp_code:
        LAST_OTP_EMAIL_ERROR = "A recipient email address and OTP code are required."
        return False

    if SMTP_CONFIGURATION_ERROR:
        LAST_OTP_EMAIL_ERROR = SMTP_CONFIGURATION_ERROR

    if not SMTP_USERNAME or not SMTP_PASSWORD:
        return False

    try:
        message = MIMEMultipart()
        message["Subject"] = subject
        message["From"] = SMTP_FROM or SMTP_USERNAME
        message["To"] = to_email
        body = (
            "Your Madhu Bank OTP is: "
            f"{otp_code}\n\n"
            "This code is valid for one-time use only. Do not share it with anyone."
        )
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)
        LAST_OTP_EMAIL_ERROR = ""
        return True
    except smtplib.SMTPAuthenticationError:
        LAST_OTP_EMAIL_ERROR = (
            "Gmail rejected the SMTP login. Use a valid Gmail App Password, "
            "not your normal Gmail password."
        )
        return False
    except (smtplib.SMTPConnectError, TimeoutError, OSError):
        LAST_OTP_EMAIL_ERROR = (
            "Could not connect to Gmail SMTP. Check the internet connection, "
            "SMTP host, and port 587."
        )
        return False
    except smtplib.SMTPException:
        LAST_OTP_EMAIL_ERROR = "Gmail rejected the OTP email. Check the SMTP settings and sender address."
        return False
    except Exception:
        LAST_OTP_EMAIL_ERROR = "An unexpected error occurred while sending the OTP email."
        return False


def send_alert_email(to_email: str, subject: str, message_body: str) -> bool:
    """Send an administrative alert notification to the provided email address using Gmail SMTP."""
    global LAST_OTP_EMAIL_ERROR

    if not to_email or not message_body:
        LAST_OTP_EMAIL_ERROR = "A recipient email address and alert message are required."
        return False

    if SMTP_CONFIGURATION_ERROR:
        LAST_OTP_EMAIL_ERROR = SMTP_CONFIGURATION_ERROR

    if not SMTP_USERNAME or not SMTP_PASSWORD:
        return False

    try:
        message = MIMEMultipart()
        message["Subject"] = f"[MADHU BANK ALERT] {subject}"
        message["From"] = SMTP_FROM or SMTP_USERNAME
        message["To"] = to_email
        full_body = (
            "MADHU BANK SYSTEM NOTIFICATION\n"
            "==============================\n\n"
            f"Alert: {subject}\n\n"
            f"{message_body}\n\n"
            "This is an automated administrative notification dispatched by Madhu Bank Core System.\n"
        )
        message.attach(MIMEText(full_body, "plain"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)
        LAST_OTP_EMAIL_ERROR = ""
        return True
    except Exception as exc:
        LAST_OTP_EMAIL_ERROR = f"Alert email failed: {str(exc)}"
        return False


def store_otp(
    email: str,
    otp_code: str,
    expires_in_seconds: int = 300,
    expiry_seconds: int | None = None,
) -> str:
    """Persist a generated OTP in memory and return the hashed value for validation."""
    key = _normalise_email(email)
    if not key or not otp_code:
        raise ValueError("Email and OTP are required.")

    if expiry_seconds is not None:
        expires_in_seconds = expiry_seconds

    expires_at = time.time() + max(int(expires_in_seconds), 1)
    OTP_STORE[key] = {
        "otp_hash": _hash_otp(otp_code),
        "expires_at": expires_at,
    }
    return OTP_STORE[key]["otp_hash"]


def validate_otp(
    email: str,
    otp_code: str,
    expires_in_seconds: int | None = None,
    expiry_seconds: int | None = None,
) -> bool:
    """Validate an OTP against the one generated for a user, including expiry checks."""
    key = _normalise_email(email)
    record = OTP_STORE.get(key)
    if not record:
        return False

    if expiry_seconds is not None:
        expires_in_seconds = expiry_seconds

    if expires_in_seconds is not None:
        record["expires_at"] = time.time() + max(int(expires_in_seconds), 1)

    expires_at = float(record.get("expires_at", 0) or 0)
    if time.time() > expires_at:
        OTP_STORE.pop(key, None)
        return False

    expected_hash = record.get("otp_hash")
    if not isinstance(expected_hash, str):
        return False

    trimmed = str(otp_code or "").strip()
    if not trimmed:
        return False

    valid = secrets.compare_digest(expected_hash, _hash_otp(trimmed))
    if valid:
        OTP_STORE.pop(key, None)
    return valid


def generate_and_send_otp(
    to_email: str,
    length: int = 6,
    expires_in_seconds: int = 300,
    expiry_seconds: int | None = None,
) -> tuple[str, bool]:
    """Convenience helper: generate a fresh OTP, store it, and email it immediately."""
    if expiry_seconds is not None:
        expires_in_seconds = expiry_seconds

    otp = generate_otp(length=length)
    store_otp(to_email, otp, expires_in_seconds=expires_in_seconds)
    sent = send_otp_email(to_email, otp)
    return otp, sent
