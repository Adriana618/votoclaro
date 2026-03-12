"""WhatsApp sharing and OG image generation endpoints."""

from urllib.parse import quote, urlencode

from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.data.shareable_facts import SHAREABLE_FACTS
from app.services.notifications import (
    build_anti_vote_share_message,
    build_fact_share_message,
    build_quiz_share_message,
    generate_whatsapp_url,
)

router = APIRouter(prefix="/share", tags=["share"])


def _og_url(path: str, params: dict) -> str:
    """Build a full OG image URL from path and query params."""
    qs = urlencode(params)
    return f"{settings.BASE_URL}/api/og/{path}?{qs}"


@router.get("/whatsapp/{share_type}")
async def whatsapp_share(
    share_type: str,
    party: str | None = None,
    region: str | None = None,
    seats_saved: int | None = None,
    match_pct: float | None = None,
    fact_id: str | None = None,
):
    """Generate a WhatsApp share URL for different content types.

    share_type can be:
      - 'anti-vote': share anti-vote result
      - 'quiz': share quiz result
      - 'fact': share a specific fact
    """
    og_image_url: str | None = None

    if share_type == "anti-vote":
        if not party or not region:
            raise HTTPException(
                status_code=400,
                detail="Se necesita 'party' y 'region' para compartir anti-voto.",
            )
        message = build_anti_vote_share_message(
            recommended_party=party,
            region_name=region,
            seats_saved=seats_saved or 0,
        )
        og_image_url = _og_url(
            "anti-vote",
            {"region": region, "rejected": "partido rechazado", "recommended": party},
        )
    elif share_type == "quiz":
        if not party or match_pct is None:
            raise HTTPException(
                status_code=400,
                detail="Se necesita 'party' y 'match_pct' para compartir quiz.",
            )
        message = build_quiz_share_message(
            top_party=party,
            match_percentage=match_pct,
        )
        og_image_url = _og_url(
            "quiz",
            {"match": party, "percent": match_pct},
        )
    elif share_type == "fact":
        if fact_id:
            fact = next((f for f in SHAREABLE_FACTS if f["id"] == fact_id), None)
            if not fact:
                raise HTTPException(status_code=404, detail="Fact not found.")
            message = build_fact_share_message(fact["text"])
        else:
            # Return a random-ish fact (first one for determinism)
            message = build_fact_share_message(SHAREABLE_FACTS[0]["text"])
    else:
        raise HTTPException(status_code=400, detail=f"Tipo '{share_type}' no soportado.")

    return {
        "share_type": share_type,
        "message": message,
        "whatsapp_url": generate_whatsapp_url(message),
        "og_image_url": og_image_url,
    }


@router.get("/facts")
async def list_facts(
    category: str | None = None,
    limit: int = Query(default=5, ge=1, le=20),
):
    """Return shareable facts, optionally filtered by category."""
    facts = SHAREABLE_FACTS

    if category:
        facts = [f for f in facts if f["category"] == category]

    return facts[:limit]
