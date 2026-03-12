"""Notification subscription endpoints for VotoClaro.

Allows frontend clients to register/unregister Web Push subscriptions
and check subscription status.
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import web_push

router = APIRouter(prefix="/notifications", tags=["notifications"])


class PushSubscriptionRequest(BaseModel):
    """Browser PushSubscription JSON forwarded by the frontend."""

    user_id: str
    subscription: dict[str, Any]


class UnsubscribeRequest(BaseModel):
    user_id: str


@router.post("/subscribe")
async def subscribe(payload: PushSubscriptionRequest):
    """Save a Web Push subscription for a user."""
    web_push.subscribe(payload.user_id, payload.subscription)
    return {"status": "subscribed", "user_id": payload.user_id}


@router.post("/unsubscribe")
async def unsubscribe(payload: UnsubscribeRequest):
    """Remove a Web Push subscription."""
    removed = web_push.unsubscribe(payload.user_id)
    if not removed:
        raise HTTPException(status_code=404, detail="No subscription found for this user.")
    return {"status": "unsubscribed", "user_id": payload.user_id}


@router.get("/status")
async def subscription_status(user_id: str):
    """Check whether a user has an active push subscription."""
    active = web_push.has_subscription(user_id)
    return {"user_id": user_id, "subscribed": active}
