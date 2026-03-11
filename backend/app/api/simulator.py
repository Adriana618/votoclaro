"""Anti-vote and D'Hondt simulator endpoints."""

from fastapi import APIRouter, HTTPException

from app.schemas.simulator import (
    AntiVoteRequest,
    AntiVoteResult,
    DHondtRequest,
    DHondtResult,
    SeatAllocation,
)
from app.services.anti_vote import compute_anti_vote_strategy
from app.services.dhondt import dhondt_method

router = APIRouter(prefix="/simulator", tags=["simulator"])


@router.post("/anti-vote", response_model=AntiVoteResult)
async def anti_vote(request: AntiVoteRequest):
    """Calculate the optimal strategic (anti-vote) for a region.

    Given a region and a list of parties the user rejects, computes
    which party to vote for to minimize the rejected parties' seats
    using the D'Hondt allocation method.
    """
    if not request.rejected_parties:
        raise HTTPException(
            status_code=400,
            detail="Debes rechazar al menos un partido.",
        )

    try:
        result = compute_anti_vote_strategy(
            region_slug=request.region_slug,
            rejected_parties=request.rejected_parties,
            custom_votes=request.custom_votes,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return AntiVoteResult(
        recommended_party=result["recommended_party"],
        recommended_party_name=result["recommended_party_name"],
        explanation=result["explanation"],
        seat_allocation_without_strategy=[
            SeatAllocation(**s) for s in result["seat_allocation_without_strategy"]
        ],
        seat_allocation_with_strategy=[
            SeatAllocation(**s) for s in result["seat_allocation_with_strategy"]
        ],
        rejected_seats_before=result["rejected_seats_before"],
        rejected_seats_after=result["rejected_seats_after"],
        seats_saved=result["seats_saved"],
    )


@router.post("/dhondt", response_model=DHondtResult)
async def dhondt(request: DHondtRequest):
    """Run a raw D'Hondt allocation with custom votes and seats."""
    if request.seats <= 0:
        raise HTTPException(status_code=400, detail="El numero de escanos debe ser positivo.")

    allocation = dhondt_method(request.votes, request.seats)
    return DHondtResult(allocation=allocation)
