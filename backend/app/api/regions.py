"""Region listing endpoints."""

from fastapi import APIRouter

from app.data.regions import REGIONS, SENATE_SEATS

router = APIRouter(prefix="/regions", tags=["regions"])


@router.get("")
async def list_regions():
    """Return all electoral regions with their seat counts."""
    return [
        {
            "id": r["slug"],
            "name": r["name"],
            "slug": r["slug"],
            "seats": r["seats_diputados"],
            "seats_diputados": r["seats_diputados"],
        }
        for r in REGIONS
    ]


@router.get("/senate-info")
async def senate_info():
    """Return senate configuration (national single district)."""
    return {
        "type": "national",
        "seats": SENATE_SEATS,
        "description": "El Senado se elige en distrito unico nacional con 60 escanos.",
    }
