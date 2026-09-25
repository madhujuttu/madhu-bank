"""User registration and authentication services."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
import bcrypt

from backend.database import users_collection, login_attempts_collection
from backend.security import PasswordPolicyError, hash_password, verify_password


MAX_FAILED_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def _clean_username(username):
    if not isinstance(username, str):
        return ""
    return username.strip()


def _is_locked(username):
    record = login_attempts_collection.find_one(
        {"username": username},
        {"locked_until": 1},
    )
    if not record:
        return False

    locked_until = record.get("locked_until")
    if not locked_until:
        return False

    # MongoDB normally returns an aware/naive datetime consistently with the
    # connection configuration. Keep comparison tolerant for both forms.
    now = datetime.now(timezone.utc)
    try:
        return locked_until > now
    except TypeError:
        return locked_until.replace(tzinfo=None) > now


def _record_failed_login(username):
    now = datetime.now(timezone.utc)

    record = login_attempts_collection.find_one_and_update(
        {"username": username},
        {
            "$inc": {"failed_attempts": 1},
            "$set": {"last_failed_at": now, "updated_at": now},
            "$setOnInsert": {"username": username},
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )

    failed_attempts = int((record or {}).get("failed_attempts", 1))

    if failed_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
        locked_until = now + timedelta(minutes=LOCKOUT_MINUTES)
        login_attempts_collection.update_one(
            {"username": username},
            {
                "$set": {
                    "locked_until": locked_until,
                    "updated_at": now,
                }
            },
        )
        try:
            from backend.alerts import dispatch_system_alert
            dispatch_system_alert(
                alert_type="SECURITY_LOGIN_LOCKOUT",
                title=f"Security Lockout: {username}",
                message=f"User '{username}' triggered security lockout after {failed_attempts} consecutive failed login attempts. Locked for {LOCKOUT_MINUTES} minutes.",
                severity="danger",
                metadata={"username": username, "failed_attempts": failed_attempts, "lockout_minutes": LOCKOUT_MINUTES},
                send_email=True,
            )
        except Exception:
            pass


def _clear_login_failures(username):
    login_attempts_collection.delete_one({"username": username})


# =========================================================
# REGISTER USER
# =========================================================


def register_user(
    name,
    username,
    password,
    dob,
    account_type,
    security_question=None,
    security_answer=None,
    email=None,
):
    """Create a customer account and, when supplied, persist its recovery question atomically."""
    clean_username = _clean_username(username)
    clean_name = str(name or "").strip()
    clean_email = str(email or "").strip().lower()

    if not clean_name or not clean_username:
        return False

    # This is authoritative backend validation; the Streamlit form is not
    # considered a security boundary. PasswordPolicyError is intentionally
    # allowed to propagate so the UI can report the real validation failure
    # instead of incorrectly showing "Username already exists."
    hashed_password = hash_password(password)

    user = {
        "name": clean_name,
        "username": clean_username,
        "password": hashed_password,
        "dob": dob,
        "account_type": account_type,
        "balance": 0,
        "status": "Pending Verification" if clean_email else "Active",
        "role": "user",
        "created_at": datetime.now(timezone.utc),
    }

    if clean_email:
        user["email"] = clean_email
        user["email_verified"] = False

    # Save recovery data in the same insert as the customer account.
    # This prevents registration from succeeding while the security question
    # is accidentally omitted by a later Streamlit rerun.
    clean_question = str(security_question or "").strip()
    clean_answer = str(security_answer or "").strip().lower()
    if clean_question and clean_answer:
        user["security_question"] = clean_question
        # Security answers are not passwords and must not be subject to the password policy.
        user["security_answer_hash"] = bcrypt.hashpw(
            clean_answer.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

    try:
        users_collection.insert_one(user)
    except DuplicateKeyError as exc:
        # Treat both username and email collisions as ordinary registration
        # conflicts so the UI can present a friendly validation message.
        key_pattern = (exc.details or {}).get("keyPattern", {}) if getattr(exc, "details", None) else {}
        if "username" in key_pattern or "email" in key_pattern:
            return False
        raise RuntimeError("Registration failed because of a database uniqueness conflict.") from exc

    return True


# =========================================================
# LOGIN WITH STATUS
# =========================================================


def login_with_status(username, password):
    """Authenticate a customer and distinguish active vs disabled accounts."""
    clean_username = _clean_username(username)

    if (
        not clean_username
        or not isinstance(password, str)
        or not password
    ):
        return "invalid", None

    if _is_locked(clean_username):
        return "invalid", None

    existing_user = users_collection.find_one(
        {"username": clean_username}
    )

    if not existing_user:
        _record_failed_login(clean_username)
        return "invalid", None

    stored_password = existing_user.get("password")

    if not stored_password or not verify_password(password, stored_password):
        _record_failed_login(clean_username)
        return "invalid", None

    status = str(
        existing_user.get("status", "Active")
    ).strip().lower()

    _clear_login_failures(clean_username)

    if status in {"disabled", "frozen", "suspended"}:
        return "disabled", existing_user

    if status != "active":
        return "invalid", None

    return "active", existing_user


# =========================================================
# LOGIN
# =========================================================


def login(username, password):
    """Backward-compatible boolean authentication wrapper."""
    status, _user = login_with_status(username, password)
    return status == "active"


# =========================================================
# GET USER
# =========================================================


def get_user(username):
    """Return a user record without password data."""
    clean_username = _clean_username(username)
    if not clean_username:
        return None

    return users_collection.find_one(
        {"username": clean_username},
        {
            "_id": 0,
            "password": 0,
        },
    )
