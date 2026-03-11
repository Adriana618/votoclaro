"""Party listing and filter endpoints."""

from fastapi import APIRouter

from app.data.parties import PARTIES
from app.data.spicy_filters import SPICY_FILTERS
from app.schemas.party import PartyOut

router = APIRouter(prefix="/parties", tags=["parties"])


@router.get("", response_model=list[PartyOut])
async def list_parties(filter_id: str | None = None, is_active: bool | None = None):
    """List all parties with optional filters.

    If filter_id is provided, it applies one of the spicy filters.
    In the MVP, spicy filters are informational only (candidate data
    is needed in the database for actual filtering). The full party
    list is returned with the filter metadata.
    """
    parties = []
    for idx, (abbr, data) in enumerate(PARTIES.items(), start=1):
        parties.append(
            PartyOut(
                id=idx,
                abbreviation=data["abbreviation"],
                name=data["name"],
                color=data.get("color"),
                logo_url=data.get("logo_url"),
                positions=data.get("positions"),
                is_active=True,
            )
        )

    if is_active is not None:
        parties = [p for p in parties if p.is_active == is_active]

    return parties


@router.get("/filters")
async def list_filters():
    """Return available spicy filter options."""
    return SPICY_FILTERS
