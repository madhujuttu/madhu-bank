"""Password reset helpers for the Madhu Bank educational simulation."""

from backend.database import users_collection
from backend.security import hash_password, verify_password


def verify_reset_identity(username, account_number, security_answer=None):
    """Verify a customer's username/account number and optional security answer."""
    if not username or not account_number:
        return None

    try:
        numeric_account_number = int(str(account_number).strip())
    except (TypeError, ValueError):
        return None

    clean_username = str(username).strip()
    user = users_collection.find_one(
        {
            "username": clean_username,
            "account_number": numeric_account_number,
        }
    )

    if not user or str(user.get("status", "Active")).lower() == "disabled":
        return None

    # When an answer is supplied, verify it against the stored hash.
    if security_answer is not None:
        answer_hash = user.get("security_answer_hash")
        if not answer_hash:
            return None
        try:
            if not verify_password(str(security_answer).strip().lower(), answer_hash):
                return None
        except Exception:
            return None

    return user


def reset_password(username, new_password):
    """Replace the stored password hash for a verified customer."""
    if not username or not new_password:
        return False

    password_hash = hash_password(new_password)
    result = users_collection.update_one(
        {"username": str(username).strip()},
        {"$set": {"password": password_hash}},
    )
    return result.modified_count == 1
