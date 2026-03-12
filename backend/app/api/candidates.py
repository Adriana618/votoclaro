"""Candidate listing and controversial ranking endpoints."""

from fastapi import APIRouter, Query

from app.data.candidates import CANDIDATES, CANDIDATES_BY_PARTY, CANDIDATES_BY_REGION
from app.data.parties import PARTIES

router = APIRouter(prefix="/candidates", tags=["candidates"])


def _build_controversy_reason(c: dict) -> str:
    """Build a human-readable controversy reason string."""
    reasons = []
    if c.get("has_criminal_record"):
        reasons.append("antecedentes penales")
    if c.get("voted_pro_crime"):
        count = c.get("pro_crime_vote_count", 0)
        reasons.append(f"votó a favor de {count} leyes pro-crimen")
    if c.get("investigations", 0) > 0:
        reasons.append(f"{c['investigations']} investigación(es) en medios")
    if c.get("is_reelection"):
        reasons.append("busca reelección")
    if c.get("party_changed_from"):
        reasons.append(f"cambió de partido desde {c['party_changed_from']}")
    return ". ".join(reasons).capitalize() if reasons else ""


def _serialize_candidate(c: dict) -> dict:
    """Serialize a candidate to the format expected by the frontend."""
    party_slug = c.get("party_slug", "")
    party_data = PARTIES.get(party_slug, {})

    return {
        "id": str(c["id"]),
        "name": c["name"],
        # Frontend-compatible fields
        "party_id": party_slug,
        "party": {
            "id": party_slug,
            "name": party_data.get("name", c.get("partido_jne", "")),
            "abbreviation": party_data.get("abbreviation", party_slug.upper()),
            "color": party_data.get("color"),
        } if party_slug else None,
        "region_id": c.get("region_slug") or "",
        "position": c.get("position_number") or 0,
        "has_criminal_record": c.get("has_criminal_record", False),
        "controversy_score": c["controversy_score"],
        "controversy_reason": _build_controversy_reason(c),
        "photo_url": c.get("foto_url"),
        # Extra fields
        "party_slug": party_slug,
        "partido_jne": c.get("partido_jne", ""),
        "region_slug": c.get("region_slug"),
        "cargo": c.get("cargo", ""),
        "voted_pro_crime": c.get("voted_pro_crime", False),
        "pro_crime_vote_count": c.get("pro_crime_vote_count", 0),
        "is_reelection": c.get("is_reelection", False),
        "investigations": c.get("investigations", 0),
        "party_changed_from": c.get("party_changed_from"),
        "foto_url": c.get("foto_url"),
    }


@router.get("/controversial")
async def controversial_ranking(
    limit: int = Query(default=20, ge=1, le=100),
    region: str | None = None,
    region_id: str | None = None,
    party: str | None = None,
):
    """Return candidates ranked by controversy score (descending).

    Returns a flat array of candidates compatible with the frontend.
    """
    region_slug = region or region_id

    candidates = list(CANDIDATES.values())

    # Filter
    if region_slug:
        r_ids = set(CANDIDATES_BY_REGION.get(region_slug, []))
        candidates = [c for c in candidates if c["id"] in r_ids]
    if party:
        p_ids = set(CANDIDATES_BY_PARTY.get(party, []))
        candidates = [c for c in candidates if c["id"] in p_ids]

    # Only include those with controversy_score > 0
    candidates = [c for c in candidates if c.get("controversy_score", 0) > 0]

    # Sort by score descending
    candidates.sort(key=lambda c: -c.get("controversy_score", 0))

    candidates = candidates[:limit]

    return [_serialize_candidate(c) for c in candidates]
