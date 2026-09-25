"""Transaction PIN helpers for the Madhu Bank educational simulation."""

import hashlib

from backend.database import users_collection
from backend.security import hash_password, verify_password


def hash_transaction_pin(pin: str) -> str:
    """Hash a 6-digit transaction PIN for storage and comparison."""
    clean_pin = str(pin or "").strip()
    if not clean_pin.isdigit() or len(clean_pin) != 6:
        raise ValueError("Transaction PIN must be a 6-digit number.")
    return hashlib.sha256(clean_pin.encode("utf-8")).hexdigest()


def verify_transaction_pin_hash(pin: str, stored_hash: str) -> bool:
    """Verify a raw PIN against a stored hash (supports both bcrypt and sha256)."""
    if not isinstance(pin, str) or not isinstance(stored_hash, str):
        return False
    if not pin or not stored_hash:
        return False
    if stored_hash.startswith(("$2a$", "$2b$", "$2y$")):
        return verify_password(pin, stored_hash)
    return hash_transaction_pin(pin) == stored_hash



def set_transaction_pin(username, pin):
    """Store a hashed 6-digit transaction PIN for a user."""
    clean_pin = str(pin or "").strip()

    if not clean_pin.isdigit() or len(clean_pin) != 6:
        return False

    # Reject PINs where all digits are identical.
    if len(set(clean_pin)) == 1:
        return False

    result = users_collection.update_one(
        {"username": str(username).strip()},
        {"$set": {"transaction_pin_hash": hash_transaction_pin(clean_pin)}},
    )

    return result.matched_count == 1


def verify_transaction_pin(username, pin):
    """Verify a user's 6-digit transaction PIN."""
    clean_pin = str(pin or "").strip()

    if not clean_pin.isdigit() or len(clean_pin) != 6:
        return False

    user = users_collection.find_one(
        {"username": str(username).strip()},
        {"transaction_pin_hash": 1},
    )

    pin_hash = user.get("transaction_pin_hash") if user else None

    if not pin_hash:
        return False

    try:
        return verify_transaction_pin_hash(clean_pin, pin_hash)
    except Exception:
        return False
