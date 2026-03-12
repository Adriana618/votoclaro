"""Party listing and filter endpoints."""

from fastapi import APIRouter

from app.data.parties import PARTIES
from app.data.spicy_filters import SPICY_FILTERS

router = APIRouter(prefix="/parties", tags=["parties"])


@router.get("")
async def list_parties():
    """List all parties."""
    return [
        {
            "id": abbr,
            "abbreviation": data["abbreviation"],
            "name": data["name"],
            "color": data.get("color"),
            "logo_url": data.get("logo_url"),
            "positions": data.get("positions"),
        }
        for abbr, data in PARTIES.items()
    ]


@router.get("/filters")
async def list_filters():
    """Return available spicy filter options."""
    return SPICY_FILTERS
