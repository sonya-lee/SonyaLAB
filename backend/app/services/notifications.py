from datetime import datetime
from typing import Any

def build_notification_event(
    *,
    event_type: str,
    title: str,
    message: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    return {
        "event_type": event_type,
        "source": "sonya-lab",
        "created_at": datetime.now().astimezone().isoformat(),
        "title": title,
        "message": message,
        "data": data,
    }
