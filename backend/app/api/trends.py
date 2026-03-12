"""Collective dashboard / trends endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.vote_preference import VotePreference

router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("")
async def trends_by_query(region_id: str = "", db: Session = Depends(get_db)):
    """Frontend calls GET /trends?region_id=X."""
    return await region_trends(region_id, db)


@router.get("/{region_slug}")
async def region_trends(region_slug: str, db: Session = Depends(get_db)):
    """Return aggregated trend data for a region.

    Shows which parties are most rejected and most recommended
    by VotoClaro users in the specified region.
    """
    from app.data.regions import REGIONS
    from app.data.parties import PARTY_NAMES

    # Find region
    region = None
    region_id = None
    for idx, r in enumerate(REGIONS, start=1):
        if r["slug"] == region_slug:
            region = r
            region_id = idx
            break

    if not region:
        return {
            "region": region_slug,
            "message": "Region no encontrada.",
            "total_simulations": 0,
            "most_rejected": [],
            "most_recommended": [],
        }

    # Count total simulations for this region
    total = (
        db.query(func.count(VotePreference.id))
        .filter(VotePreference.region_id == region_id)
        .scalar()
    ) or 0

    # If no data yet, return empty trends
    if total == 0:
        return {
            "region": region["name"],
            "region_slug": region_slug,
            "seats": region["seats_diputados"],
            "total_simulations": 0,
            "most_rejected": [],
            "most_recommended": [],
            "message": "Aun no hay suficientes datos para esta region. Se el primero en simular.",
        }

    # Get most recommended parties
    recommended_counts = (
        db.query(
            VotePreference.recommended_party_id,
            func.count(VotePreference.id).label("count"),
        )
        .filter(VotePreference.region_id == region_id)
        .filter(VotePreference.recommended_party_id.isnot(None))
        .group_by(VotePreference.recommended_party_id)
        .order_by(func.count(VotePreference.id).desc())
        .limit(5)
        .all()
    )

    return {
        "region": region["name"],
        "region_slug": region_slug,
        "seats": region["seats_diputados"],
        "total_simulations": total,
        "most_recommended": [
            {"party_id": r[0], "count": r[1]}
            for r in recommended_counts
        ],
    }
