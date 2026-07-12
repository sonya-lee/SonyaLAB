"""Notification event contracts.

Delivery to another Sonya service intentionally does not live in this repository.
Business jobs persist outbox-style events in notification_events. A future relay
may deliver them without coupling Sonya Lab to another repository or database.
"""

from datetime import datetime
from typing import Any


def build_notification_event(*, event_type: str, title: str, message: str, data: dict[str, Any], severity: str = "info") -> dict[str, Any]:
    return {"event_type": event_type, "source": "sonya-lab", "severity": severity, "created_at": datetime.now().astimezone().isoformat(), "title": title, "message": message, "data": data}
