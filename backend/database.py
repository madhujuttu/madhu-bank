"""MongoDB connection and centralized index management for Madhu Bank."""

import os
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment configuration if available
_BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def _sanitize_mongodb_uri(uri: str) -> str:
    """Ensure username and password in MongoDB URI are safely percent-encoded as per RFC 3986."""
    if not uri or "://" not in uri:
        return uri
    scheme, rest = uri.split("://", 1)
    if "@" not in rest:
        return uri
    userpass, host_and_rest = rest.rsplit("@", 1)
    if ":" in userpass:
        user, pwd = userpass.split(":", 1)
        escaped_user = urllib.parse.quote_plus(urllib.parse.unquote_plus(user))
        escaped_pwd = urllib.parse.quote_plus(urllib.parse.unquote_plus(pwd))
        return f"{scheme}://{escaped_user}:{escaped_pwd}@{host_and_rest}"
    return uri

MONGODB_URI = _sanitize_mongodb_uri(os.getenv("MONGODB_URI", "mongodb://localhost:27017/").strip())
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "madhu_bank").strip()

client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=4000,
    connectTimeoutMS=4000,
    socketTimeoutMS=10000,
    maxPoolSize=50,
    minPoolSize=2,
    maxIdleTimeMS=45000,
    retryWrites=True,
)
db = client[MONGODB_DB_NAME]


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
    try:
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
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Users & Deduplication Routine
# ---------------------------------------------------------------------------

def cleanup_duplicate_users(collection=None):
    """Find and remove duplicate customer records in users_collection.

    If multiple documents share the same username:
    - Retains the 'Active' account (or the most complete one with balance/account_number).
    - Removes stale 'Pending Verification' duplicate documents.
    """
    target = collection if collection is not None else users_collection
    try:
        pipeline = [
            {"$group": {"_id": "$username", "count": {"$sum": 1}, "docs": {"$push": "$$ROOT"}}},
            {"$match": {"count": {"$gt": 1}}},
        ]
        duplicates = list(target.aggregate(pipeline))
        for item in duplicates:
            docs = item.get("docs", [])
            if not docs or not item.get("_id"):
                continue

            def sort_key(d):
                status_str = str(d.get("status", "")).lower()
                is_active = 2 if status_str == "active" else 1 if status_str == "disabled" else 0
                has_balance = 1 if float(d.get("balance", 0) or 0) > 0 else 0
                has_acc = 1 if d.get("account_number") else 0
                created = str(d.get("created_at") or "")
                return (is_active, has_balance, has_acc, created)

            docs.sort(key=sort_key, reverse=True)
            keep_doc = docs[0]
            keep_id = keep_doc.get("_id")

            for dup in docs[1:]:
                dup_id = dup.get("_id")
                if dup_id and dup_id != keep_id:
                    target.delete_one({"_id": dup_id})
    except Exception:
        pass


import threading

_SETUP_INITIALIZED = False
_SETUP_LOCK = threading.Lock()


def init_database_indexes():
    """Ensure database indexes and perform one-time duplicate cleanup in the background."""
    global _SETUP_INITIALIZED
    with _SETUP_LOCK:
        if _SETUP_INITIALIZED:
            return
        _SETUP_INITIALIZED = True
        try:
            cleanup_duplicate_users(users_collection)
        except Exception:
            pass

        try:
            _ensure_index(
                users_collection,
                [("account_number", 1)],
                name="ux_users_account_number",
                unique=True,
                sparse=True,
            )
            _ensure_index(
                users_collection,
                [("username", 1)],
                name="ux_users_username",
                unique=True,
            )
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
        except Exception:
            pass


# Dispatch asynchronously in background so module import is instantaneous (<15ms)
threading.Thread(target=init_database_indexes, daemon=True, name="DBIndexInit").start()
