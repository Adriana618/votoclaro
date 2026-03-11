"""Candidate listing and controversial ranking endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateOut, ControversialRankingOut

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("/controversial", response_model=ControversialRankingOut)
async def controversial_ranking(
    limit: int = Query(default=20, ge=1, le=100),
    region_id: int | None = None,
    party_id: int | None = None,
    db: Session = Depends(get_db),
):
    """Return candidates ranked by controversy score (descending).

    Optionally filter by region or party.
    """
    query = db.query(Candidate).order_by(Candidate.controversy_score.desc())

    if region_id is not None:
        query = query.filter(Candidate.region_id == region_id)
    if party_id is not None:
        query = query.filter(Candidate.party_id == party_id)

    total = query.count()
    candidates = query.limit(limit).all()

    return ControversialRankingOut(
        candidates=[CandidateOut.model_validate(c) for c in candidates],
        total=total,
    )
