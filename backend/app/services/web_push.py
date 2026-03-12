"""Web Push notification service for VotoClaro.

Manages push subscriptions and sends notifications via the Web Push protocol.
Falls back to logging when pywebpush is not installed.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

try:
    from pywebpush import webpush, WebPushException  # type: ignore[import-untyped]

    _WEBPUSH_AVAILABLE = True
except ImportError:
    _WEBPUSH_AVAILABLE = False
    logger.info("pywebpush not installed — push notifications will be logged only")

# In-memory subscription store.
# In production this should be backed by a database table.
_subscriptions: dict[str, dict[str, Any]] = {}


def subscribe(user_id: str, subscription_info: dict[str, Any]) -> None:
    """Store a push subscription for a user.

    Args:
        user_id: Unique identifier for the user.
        subscription_info: PushSubscription JSON from the browser
            (contains endpoint, keys.p256dh, keys.auth).
    """
    _subscriptions[user_id] = {
        "subscription_info": subscription_info,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    logger.info("Push subscription saved for user %s", user_id)


def unsubscribe(user_id: str) -> bool:
    """Remove a push subscription.

    Returns:
        True if a subscription was removed, False if none existed.
    """
    removed = _subscriptions.pop(user_id, None)
    if removed:
        logger.info("Push subscription removed for user %s", user_id)
    return removed is not None


def has_subscription(user_id: str) -> bool:
    """Check whether a user has an active push subscription."""
    return user_id in _subscriptions


def get_all_subscriptions() -> dict[str, dict[str, Any]]:
    """Return all stored subscriptions (for batch sending)."""
    return dict(_subscriptions)


def send_push_notification(
    user_id: str,
    title: str,
    body: str,
    url: str | None = None,
) -> bool:
    """Send a Web Push notification to a single user.

    Args:
        user_id: Target user.
        title: Notification title.
        body: Notification body text.
        url: Optional URL to open when the notification is clicked.

    Returns:
        True if the notification was sent (or logged) successfully.
    """
    record = _subscriptions.get(user_id)
    if not record:
        logger.warning("No push subscription for user %s", user_id)
        return False

    import json

    payload = json.dumps({"title": title, "body": body, "url": url or ""})

    if _WEBPUSH_AVAILABLE and settings.VAPID_PRIVATE_KEY:
        try:
            webpush(
                subscription_info=record["subscription_info"],
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": settings.VAPID_CLAIMS_EMAIL},
            )
            logger.info("Push notification sent to user %s", user_id)
            return True
        except WebPushException as exc:
            logger.error("Push failed for user %s: %s", user_id, exc)
            return False
    else:
        # Fallback: just log the notification
        logger.info(
            "PUSH (logged) to=%s title=%r body=%r url=%r",
            user_id,
            title,
            body,
            url,
        )
        return True
