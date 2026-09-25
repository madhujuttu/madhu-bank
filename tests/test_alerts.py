import pytest
from unittest.mock import patch
from backend.alerts import (
    dispatch_system_alert,
    get_system_alerts,
    get_unread_alerts_count,
    acknowledge_system_alert,
    dismiss_system_alert,
)


def test_dispatch_and_retrieve_alert():
    with patch("backend.alerts.send_alert_email", return_value=True):
        alert = dispatch_system_alert(
            alert_type="TEST_UNIT",
            title="Unit Test Alert",
            message="This is a unit test alert.",
            severity="warning",
            metadata={"source": "pytest"},
            send_email=False,
        )

        assert alert is not None
        assert alert["alert_id"].startswith("ALT-")
        assert alert["status"] == "Unread"
        assert alert["title"] == "Unit Test Alert"

        # Check retrieval
        alerts = get_system_alerts(status_filter="Unread", limit=10)
        found = any(a["alert_id"] == alert["alert_id"] for a in alerts)
        assert found, "Alert should be found in unread alerts"

        # Acknowledge
        ok = acknowledge_system_alert(alert["alert_id"])
        assert ok is True

        # Check status updated
        ack_alerts = get_system_alerts(status_filter="Acknowledged", limit=10)
        assert any(a["alert_id"] == alert["alert_id"] for a in ack_alerts)

        # Dismiss
        dismiss_ok = dismiss_system_alert(alert["alert_id"])
        assert dismiss_ok is True

        dismissed = get_system_alerts(status_filter="Dismissed", limit=10)
        assert any(a["alert_id"] == alert["alert_id"] for a in dismissed)

