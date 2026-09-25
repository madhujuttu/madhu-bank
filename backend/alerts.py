"""System notification and alert dispatch service for Madhu Bank."""

from datetime import datetime
import secrets
from backend.database import system_alerts_collection, users_collection
from backend.email_otp import send_alert_email
from config.settings import SMTP_USERNAME


def dispatch_system_alert(
    alert_type: str,
    title: str,
    message: str,
    severity: str = "warning",
    metadata: dict = None,
    send_email: bool = True,
    target_email: str = None,
) -> dict:
    """Persistently store and dispatch an alert across all channels."""
    alert_id = f"ALT-{secrets.token_hex(4).upper()}"
    alert_doc = {
        "alert_id": alert_id,
        "type": alert_type,
        "title": title,
        "message": message,
        "severity": severity,
        "created_at": datetime.now(),
        "status": "Unread",
        "metadata": metadata or {},
        "email_sent": False,
    }

    if send_email:
        email_to = target_email
        if not email_to:
            admin_user = users_collection.find_one({"role": "admin"}) or {}
            email_to = admin_user.get("email") or SMTP_USERNAME

        if email_to:
            try:
                sent = send_alert_email(email_to, title, message)
                alert_doc["email_sent"] = sent
                alert_doc["recipient_email"] = email_to
            except Exception:
                alert_doc["email_sent"] = False

    try:
        system_alerts_collection.insert_one(alert_doc)
    except Exception:
        pass

    return alert_doc


def get_system_alerts(status_filter: str = "All", limit: int = 50) -> list:
    """Retrieve system alerts sorted newest first."""
    query = {}
    if status_filter and status_filter.lower() != "all":
        query["status"] = status_filter

    try:
        cursor = system_alerts_collection.find(query).sort("created_at", -1).limit(limit)
        return list(cursor)
    except Exception:
        return []


def get_unread_alerts_count() -> int:
    """Return count of unread alerts."""
    try:
        return system_alerts_collection.count_documents({"status": "Unread"})
    except Exception:
        return 0


def acknowledge_system_alert(alert_id: str) -> bool:
    """Mark an alert as Acknowledged."""
    try:
        res = system_alerts_collection.update_one(
            {"alert_id": alert_id},
            {"$set": {"status": "Acknowledged", "acknowledged_at": datetime.now()}}
        )
        return res.modified_count > 0
    except Exception:
        return False


def dismiss_system_alert(alert_id: str) -> bool:
    """Mark an alert as Dismissed."""
    try:
        res = system_alerts_collection.update_one(
            {"alert_id": alert_id},
            {"$set": {"status": "Dismissed", "dismissed_at": datetime.now()}}
        )
        return res.modified_count > 0
    except Exception:
        return False

