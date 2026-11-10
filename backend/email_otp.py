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
LAST_OTP_SIMULATION_CODE: dict[str, str] = {}


def get_last_otp_email_error() -> str:
    """Return the latest safe-to-display OTP delivery error message."""
    return LAST_OTP_EMAIL_ERROR


def get_last_simulated_otp(email: str) -> str | None:
    """Return the fallback simulated OTP if cloud host blocked outbound SMTP ports."""
    return LAST_OTP_SIMULATION_CODE.get(_normalise_email(email))


def clear_simulated_otp(email: str) -> None:
    """Clear simulated OTP once consumed or invalidated."""
    LAST_OTP_SIMULATION_CODE.pop(_normalise_email(email), None)


def _normalise_email(email: str) -> str:
    return str(email or "").strip().lower()


def _hash_otp(otp_code: str) -> str:
    return hashlib.sha256(str(otp_code).strip().encode("utf-8")).hexdigest()


def generate_otp(length: int = 6) -> str:
    """Generate a numeric OTP code as a fixed-length string."""
    if length <= 0:
        return ""
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


def _send_smtp_message(message: MIMEMultipart) -> tuple[bool, str]:
    """Attempt email dispatch using configured SMTP with automatic port 587/465 fallback."""
    if SMTP_CONFIGURATION_ERROR:
        return False, SMTP_CONFIGURATION_ERROR

    if not SMTP_USERNAME or not SMTP_PASSWORD:
        return False, "Gmail SMTP username and App Password are required."

    # Try configured port first, then attempt alternate secure port (465 SSL or 587 STARTTLS)
    ports_to_try = [SMTP_PORT]
    alternate = 465 if SMTP_PORT != 465 else 587
    if alternate not in ports_to_try:
        ports_to_try.append(alternate)

    last_error = ""
    for port in ports_to_try:
        try:
            if port == 465:
                with smtplib.SMTP_SSL(SMTP_HOST, port) as server:
                    server.login(SMTP_USERNAME, SMTP_PASSWORD)
                    server.send_message(message)
                return True, ""
            else:
                with smtplib.SMTP(SMTP_HOST, port) as server:
                    server.starttls()
                    server.login(SMTP_USERNAME, SMTP_PASSWORD)
                    server.send_message(message)
                return True, ""
        except smtplib.SMTPAuthenticationError:
            return False, (
                "Gmail rejected the SMTP login. Use a valid 16-character Gmail App Password, "
                "not your normal Gmail password."
            )
        except (smtplib.SMTPConnectError, TimeoutError, OSError) as e:
            last_error = f"Port {port}: {e}"
            continue
        except smtplib.SMTPException as e:
            return False, f"Gmail rejected the email: {e}"
        except Exception as e:
            return False, f"An unexpected error occurred while sending email: {e}"

    return False, (
        "Could not connect to Gmail SMTP. Outbound email ports (587 and 465) appear to be "
        f"blocked by the cloud network firewall ({last_error})."
    )


def send_otp_email(to_email: str, otp_code: str, subject: str = "Madhu Bank OTP Verification") -> bool:
    """Send a numeric OTP to the provided email address using Gmail SMTP."""
    global LAST_OTP_EMAIL_ERROR

    if not to_email or not otp_code:
        LAST_OTP_EMAIL_ERROR = "A recipient email address and OTP code are required."
        return False

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

    success, err_msg = _send_smtp_message(message)
    LAST_OTP_EMAIL_ERROR = err_msg
    return success


def send_alert_email(to_email: str, subject: str, message_body: str) -> bool:
    """Send an administrative alert notification to the provided email address using Gmail SMTP."""
    global LAST_OTP_EMAIL_ERROR

    if not to_email or not message_body:
        LAST_OTP_EMAIL_ERROR = "A recipient email address and alert message are required."
        return False

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

    success, err_msg = _send_smtp_message(message)
    LAST_OTP_EMAIL_ERROR = err_msg
    return success


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
        clear_simulated_otp(key)
    return valid


def generate_and_send_otp(
    to_email: str,
    length: int = 6,
    expires_in_seconds: int = 300,
    expiry_seconds: int | None = None,
) -> tuple[str, bool]:
    """Convenience helper: generate a fresh OTP, store it, and email it immediately.
    
    If outbound SMTP is blocked by the cloud hosting environment (e.g. cloud container
    firewall blocking email ports 587 and 465), falls back to simulation mode so the
    user can test the application.
    """
    if expiry_seconds is not None:
        expires_in_seconds = expiry_seconds

    otp = generate_otp(length=length)
    store_otp(to_email, otp, expires_in_seconds=expires_in_seconds)
    sent = send_otp_email(to_email, otp)

    # Always log OTP to server console (visible in Streamlit Cloud > Manage app > Logs)
    print(f"[MADHU BANK OTP] Generated OTP for {to_email}: {otp} (Sent via live email: {sent})")

    if not sent:
        last_err = get_last_otp_email_error()
        if "Could not connect to Gmail SMTP" in last_err or "blocked" in last_err:
            LAST_OTP_SIMULATION_CODE[_normalise_email(to_email)] = otp
            return otp, True

    return otp, sent
