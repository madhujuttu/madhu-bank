"""Disabled-account review requests and authorized admin actions."""

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import secrets
from uuid import uuid4

from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from backend.database import (
    account_review_requests_collection,
    users_collection,
    transactions_collection,
    admin_action_sessions_collection,
)


MAX_REASON_LENGTH = 1000
ADMIN_ACTION_TOKEN_MINUTES = 30


def _clean_username(username):
    return str(username or "").strip()


def _clean_reason(reason):
    return " ".join(str(reason or "").split())


def _token_hash(token):
    return sha256(str(token).encode("utf-8")).hexdigest()


def create_admin_action_token(admin_username):
    """Create a short-lived server-side token after the existing admin login succeeds."""
    username = _clean_username(admin_username)
    if not username:
        raise ValueError("Administrator username is required.")

    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=ADMIN_ACTION_TOKEN_MINUTES)

    admin_action_sessions_collection.insert_one(
        {
            "token_hash": _token_hash(token),
            "username": username,
            "created_at": now,
            "expires_at": expires_at,
            "active": True,
        }
    )

    return token


def revoke_admin_action_token(token):
    if not token:
        return

    admin_action_sessions_collection.update_one(
        {"token_hash": _token_hash(token), "active": True},
        {"$set": {"active": False}},
    )


def _get_authorized_admin(token):
    if not token:
        return None

    session = admin_action_sessions_collection.find_one(
        {
            "token_hash": _token_hash(token),
            "active": True,
        },
        {"username": 1, "expires_at": 1},
    )

    if not session:
        return None

    expires_at = session.get("expires_at")
    if not expires_at:
        return None

    now = datetime.now(timezone.utc)
    try:
        expired = expires_at <= now
    except TypeError:
        expired = expires_at.replace(tzinfo=None) <= now

    if expired:
        admin_action_sessions_collection.update_one(
            {"token_hash": _token_hash(token), "active": True},
            {"$set": {"active": False}},
        )
        return None

    return _clean_username(session.get("username")) or None


def create_review_request(username, reason):
    """Create a pending reactivation request for a disabled customer."""
    clean_username = _clean_username(username)
    clean_reason = _clean_reason(reason)

    if not clean_username:
        return False, "Username is required."

    if not clean_reason:
        return False, "Please provide a reason for account review."

    if len(clean_reason) < 10:
        return False, "Please provide a more detailed reason (at least 10 characters)."

    if len(clean_reason) > MAX_REASON_LENGTH:
        return False, f"Reason must be {MAX_REASON_LENGTH} characters or fewer."

    user = users_collection.find_one({"username": clean_username})
    if not user:
        return False, "Account could not be found."

    status = str(user.get("status", "Active")).strip().lower()
    if status not in {"disabled", "frozen", "suspended"}:
        return False, "A review request can only be submitted for a disabled account."

    existing_pending = account_review_requests_collection.find_one(
        {"username": clean_username, "status": "Pending"},
        {"request_id": 1},
    )
    if existing_pending:
        return False, "A review request is already pending for this account."

    request = {
        "request_id": uuid4().hex,
        "username": clean_username,
        "account_number": user.get("account_number"),
        "name": user.get("name", ""),
        "reason": clean_reason,
        "status": "Pending",
        "created_at": datetime.now(timezone.utc),
        "reviewed_at": None,
        "reviewed_by": None,
    }

    try:
        account_review_requests_collection.insert_one(request)
    except DuplicateKeyError:
        return False, "A review request is already pending for this account."

    return True, request


def get_pending_review_requests(limit=100):
    try:
        return list(
            account_review_requests_collection.find(
                {"status": "Pending"},
                {"_id": 0},
            )
            .sort("created_at", -1)
            .limit(int(limit))
        )
    except (TypeError, ValueError):
        return []


def get_review_request_history(username, limit=20):
    clean_username = _clean_username(username)
    if not clean_username:
        return []

    try:
        return list(
            account_review_requests_collection.find(
                {"username": clean_username},
                {"_id": 0},
            )
            .sort("created_at", -1)
            .limit(int(limit))
        )
    except (TypeError, ValueError):
        return []


def get_pending_review_count():
    return account_review_requests_collection.count_documents(
        {"status": "Pending"}
    )


def get_review_transactions(username, account_number=None, limit=1000):
    """Return the customer's transaction history for administrator review."""
    clean_username = _clean_username(username)
    if not clean_username:
        return []

    clauses = [{"username": clean_username}]

    if account_number not in (None, "", "N/A"):
        try:
            numeric_account_number = int(str(account_number).strip())
            clauses.append({"account_number": numeric_account_number})
        except (TypeError, ValueError):
            pass

    try:
        return list(
            transactions_collection.find(
                {"$or": clauses}
            )
            .sort("date", -1)
            .limit(int(limit))
        )
    except (TypeError, ValueError):
        return []


def approve_review_request(request_id, admin_action_token):
    """Approve a pending request using a server-issued admin action token."""
    clean_request_id = str(request_id or "").strip()
    admin_username = _get_authorized_admin(admin_action_token)

    if not clean_request_id:
        return False, "Invalid review request."

    if not admin_username:
        return False, "Administrator authorization failed. Please log in again."

    request = account_review_requests_collection.find_one_and_update(
        {"request_id": clean_request_id, "status": "Pending"},
        {"$set": {"status": "Reviewing", "reviewed_by": admin_username}},
        return_document=ReturnDocument.AFTER,
    )

    if not request:
        return False, "This request is no longer pending."

    try:
        from backend.admin import enable_account
        enabled = bool(enable_account(request.get("username")))
    except (ImportError, TypeError, ValueError):
        enabled = False

    if not enabled:
        account_review_requests_collection.update_one(
            {"request_id": clean_request_id, "status": "Reviewing"},
            {"$set": {"status": "Pending", "reviewed_by": None}},
        )
        return False, "The account could not be enabled. The request remains pending."

    result = account_review_requests_collection.update_one(
        {"request_id": clean_request_id, "status": "Reviewing"},
        {
            "$set": {
                "status": "Approved",
                "reviewed_at": datetime.now(timezone.utc),
                "reviewed_by": admin_username,
            }
        },
    )

    if result.modified_count != 1:
        return False, "The request status could not be updated after enabling the account."

    # Once the administrator approves the request, clear all previous
    # review-request records for this customer. If the account is disabled
    # again later, the customer starts a fresh review cycle.
    account_review_requests_collection.delete_many(
        {"username": request.get("username")}
    )

    return True, "Account enabled successfully."


def reject_review_request(request_id, admin_action_token, rejection_reason):
    """Reject a pending request and store the administrator's reason."""
    clean_request_id = str(request_id or "").strip()
    clean_reason = _clean_reason(rejection_reason)
    admin_username = _get_authorized_admin(admin_action_token)

    if not clean_request_id:
        return False, "Invalid review request."

    if not admin_username:
        return False, "Administrator authorization failed. Please log in again."

    if len(clean_reason) < 10:
        return False, "Please provide a rejection reason of at least 10 characters."

    if len(clean_reason) > MAX_REASON_LENGTH:
        return False, f"Rejection reason must be {MAX_REASON_LENGTH} characters or fewer."

    result = account_review_requests_collection.update_one(
        {"request_id": clean_request_id, "status": "Pending"},
        {
            "$set": {
                "status": "Rejected",
                "reviewed_at": datetime.now(timezone.utc),
                "reviewed_by": admin_username,
                "rejection_reason": clean_reason,
            }
        },
    )

    if result.modified_count != 1:
        return False, "This request is no longer pending."

    return True, "Request rejected. The customer may submit a new request."
