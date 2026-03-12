"""Candidate listing and controversial ranking endpoints."""

from fastapi import APIRouter, Query

from app.data.candidates import CANDIDATES, CANDIDATES_BY_PARTY, CANDIDATES_BY_REGION

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("/controversial")
async def controversial_ranking(
    limit: int = Query(default=20, ge=1, le=100),
    region: str | None = None,
    party: str | None = None,
):
    """Return candidates ranked by controversy score (descending).

    Optionally filter by region slug or party slug.
    """
    candidates = list(CANDIDATES.values())

    # Filter
    if region:
        region_ids = set(CANDIDATES_BY_REGION.get(region, []))
        candidates = [c for c in candidates if c["id"] in region_ids]
    if party:
        party_ids = set(CANDIDATES_BY_PARTY.get(party, []))
        candidates = [c for c in candidates if c["id"] in party_ids]

    # Only include those with controversy_score > 0
    candidates = [c for c in candidates if c.get("controversy_score", 0) > 0]

    # Sort by score descending
    candidates.sort(key=lambda c: -c.get("controversy_score", 0))

    total = len(candidates)
    candidates = candidates[:limit]

    return {
        "candidates": [
            {
                "id": c["id"],
                "name": c["name"],
                "party_slug": c["party_slug"],
                "partido_jne": c.get("partido_jne", ""),
                "region_slug": c.get("region_slug"),
                "cargo": c["cargo"],
                "controversy_score": c["controversy_score"],
                "has_criminal_record": c.get("has_criminal_record", False),
                "voted_pro_crime": c.get("voted_pro_crime", False),
                "pro_crime_vote_count": c.get("pro_crime_vote_count", 0),
                "is_reelection": c.get("is_reelection", False),
                "investigations": c.get("investigations", 0),
                "party_changed_from": c.get("party_changed_from"),
                "foto_url": c.get("foto_url"),
            }
            for c in candidates
        ],
        "total": total,
    }
