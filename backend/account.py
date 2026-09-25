from datetime import datetime, timezone
import math

from backend.database import (
    users_collection,
    transactions_collection,
)

_CURRENCY = "INR"
_MAX_DECIMAL_PLACES = 4


def _normalize_amount(amount):
    """Return a finite amount rounded to two decimal places, or None."""
    try:
        value = float(amount)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(value) or value <= 0:
        return None

    return round(value, _MAX_DECIMAL_PLACES)


def current_balance(username):
    """Return the latest balance for a user from MongoDB."""
    if not username:
        return None

    user = users_collection.find_one(
        {"username": str(username).strip()},
        {"balance": 1},
    )

    if not user:
        return None

    return user.get("balance", 0)


def deposit_money(username, amount):
    """Atomically increase an active customer's balance and record the deposit.

    The balance update is conditional on the account being active.
    A transaction record is inserted only after the balance update succeeds.
    If transaction logging fails, the balance update is compensated.
    """
    username = str(username or "").strip()
    normalized_amount = _normalize_amount(amount)

    if not username or normalized_amount is None:
        return False

    result = users_collection.update_one(
        {
            "username": username,
            "status": "Active",
        },
        {
            "$inc": {"balance": normalized_amount},
        },
    )

    if result.modified_count != 1:
        return False

    transaction_id = f"TX-DEP-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}-{username}"

    try:
        transactions_collection.insert_one(
            {
                "transaction_id": transaction_id,
                "username": username,
                "type": "Deposit",
                "amount": normalized_amount,
                "currency": _CURRENCY,
                "status": "SUCCESS",
                "date": datetime.now(timezone.utc),
                "created_at": datetime.now(timezone.utc),
                "description": "Cash deposit (simulation)",
            }
        )
        return True

    except Exception:
        # Compensating rollback for the single-account operation.
        users_collection.update_one(
            {
                "username": username,
                "status": "Active",
                "balance": {"$gte": normalized_amount},
            },
            {
                "$inc": {"balance": -normalized_amount},
            },
        )
        return False


def withdraw_money(username, amount):
    """Atomically debit an active customer when sufficient funds exist.

    The conditional update prevents two concurrent withdrawals from both
    spending the same balance.
    """
    username = str(username or "").strip()
    normalized_amount = _normalize_amount(amount)

    if not username or normalized_amount is None:
        return False

    result = users_collection.update_one(
        {
            "username": username,
            "status": "Active",
            "balance": {"$gte": normalized_amount},
        },
        {
            "$inc": {"balance": -normalized_amount},
        },
    )

    if result.modified_count != 1:
        return False

    transaction_id = f"TX-WDL-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}-{username}"

    try:
        transactions_collection.insert_one(
            {
                "transaction_id": transaction_id,
                "username": username,
                "type": "Withdrawal",
                "amount": normalized_amount,
                "currency": _CURRENCY,
                "status": "SUCCESS",
                "date": datetime.now(timezone.utc),
                "created_at": datetime.now(timezone.utc),
                "description": "Cash withdrawal (simulation)",
            }
        )
        return True

    except Exception:
        # Compensating rollback if the history write fails.
        users_collection.update_one(
            {
                "username": username,
                "status": "Active",
            },
            {
                "$inc": {"balance": normalized_amount},
            },
        )
        return False
