"""Region listing endpoints."""

from fastapi import APIRouter

from app.data.regions import REGIONS, SENATE_SEATS
from app.schemas.region import RegionOut

router = APIRouter(prefix="/regions", tags=["regions"])


@router.get("", response_model=list[RegionOut])
async def list_regions():
    """Return all electoral regions with their seat counts."""
    return [
        RegionOut(
            id=idx,
            name=r["name"],
            slug=r["slug"],
            seats_diputados=r["seats_diputados"],
            department_code=r.get("department_code"),
        )
        for idx, r in enumerate(REGIONS, start=1)
    ]


@router.get("/senate-info")
async def senate_info():
    """Return senate configuration (national single district)."""
    return {
        "type": "national",
        "seats": SENATE_SEATS,
        "description": "El Senado se elige en distrito unico nacional con 60 escanos.",
    }
