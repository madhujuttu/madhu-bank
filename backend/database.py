"""MongoDB connection and centralized index management for Madhu Bank."""

from pymongo import MongoClient


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

client = MongoClient("mongodb://localhost:27017/")
db = client["madhu_bank"]


# ---------------------------------------------------------------------------
# Collections
# ---------------------------------------------------------------------------

users_collection = db["users"]
transactions_collection = db["transactions"]
cards_collection = db["cards"]
login_attempts_collection = db["login_attempts"]
account_review_requests_collection = db["account_review_requests"]
admin_action_sessions_collection = db["admin_action_sessions"]
system_alerts_collection = db["system_alerts"]


# ---------------------------------------------------------------------------
# Index helpers
# ---------------------------------------------------------------------------

def _normalise_keys(keys):
    """Return an index key specification as a list of (field, direction)."""
    if hasattr(keys, "items"):
        return list(keys.items())
    return list(keys or [])


def _same_index_options(
    index_info,
    *,
    unique=None,
    sparse=None,
    expire_after_seconds=None,
):
    """Check only options relevant to the requested index."""
    if unique is not None and bool(index_info.get("unique", False)) != bool(unique):
        return False

    if sparse is not None and bool(index_info.get("sparse", False)) != bool(sparse):
        return False

    if expire_after_seconds is not None:
        if index_info.get("expireAfterSeconds") != expire_after_seconds:
            return False

    return True


def _find_equivalent_index(
    collection,
    keys,
    *,
    unique=None,
    sparse=None,
    expire_after_seconds=None,
):
    """Find an existing equivalent index regardless of its name."""
    wanted = _normalise_keys(keys)

    for index_name, index_info in collection.index_information().items():
        existing = _normalise_keys(index_info.get("key", []))

        if existing != wanted:
            continue

        if _same_index_options(
            index_info,
            unique=unique,
            sparse=sparse,
            expire_after_seconds=expire_after_seconds,
        ):
            return index_name

    return None


def _ensure_index(
    collection,
    keys,
    *,
    name,
    unique=None,
    sparse=None,
    expire_after_seconds=None,
):
    """Create an index only when an equivalent one does not already exist."""
    existing = _find_equivalent_index(
        collection,
        keys,
        unique=unique,
        sparse=sparse,
        expire_after_seconds=expire_after_seconds,
    )

    if existing:
        return existing

    options = {"name": name}

    if unique is not None:
        options["unique"] = unique
    if sparse is not None:
        options["sparse"] = sparse
    if expire_after_seconds is not None:
        options["expireAfterSeconds"] = expire_after_seconds

    return collection.create_index(keys, **options)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

_ensure_index(
    users_collection,
    [("account_number", 1)],
    name="ux_users_account_number",
    unique=True,
    sparse=True,
)


# ---------------------------------------------------------------------------
# Login attempts
# ---------------------------------------------------------------------------

_ensure_index(
    login_attempts_collection,
    [("username", 1), ("created_at", -1)],
    name="ix_login_attempts_username_created",
)

_ensure_index(
    login_attempts_collection,
    [("ip_address", 1), ("created_at", -1)],
    name="ix_login_attempts_ip_created",
)


# ---------------------------------------------------------------------------
# Account Review
# ---------------------------------------------------------------------------

# No request_id index is created. MongoDB's built-in _id is the unique
# identifier for each account-review request.

_ensure_index(
    account_review_requests_collection,
    [("username", 1), ("status", 1)],
    name="ix_account_review_username_status",
)

_ensure_index(
    account_review_requests_collection,
    [("status", 1), ("created_at", -1)],
    name="ix_account_review_status_created",
)


# ---------------------------------------------------------------------------
# Admin action sessions
# ---------------------------------------------------------------------------

_ensure_index(
    admin_action_sessions_collection,
    [("username", 1), ("created_at", -1)],
    name="ix_admin_action_username_created",
)

_ensure_index(
    admin_action_sessions_collection,
    [("expires_at", 1)],
    name="ix_admin_action_expires",
    expire_after_seconds=0,
)


# ---------------------------------------------------------------------------
# System alerts
# ---------------------------------------------------------------------------

_ensure_index(
    system_alerts_collection,
    [("status", 1), ("created_at", -1)],
    name="ix_system_alerts_status_created",
)

_ensure_index(
    system_alerts_collection,
    [("alert_id", 1)],
    name="ux_system_alerts_alert_id",
    unique=True,
    sparse=True,
)
