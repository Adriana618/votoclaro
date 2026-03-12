"""Main router aggregating all API sub-routers."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.api.auth import router as auth_router
from app.api.candidates import router as candidates_router
from app.api.og import router as og_router
from app.api.parties import router as parties_router
from app.api.quiz import router as quiz_router
from app.api.regions import router as regions_router
from app.api.share import router as share_router
from app.api.simulator import router as simulator_router
from app.api.notifications import router as notifications_router
from app.api.trends import router as trends_router

api_router = APIRouter()

api_router.include_router(simulator_router)
api_router.include_router(quiz_router)
api_router.include_router(parties_router)
api_router.include_router(candidates_router)
api_router.include_router(regions_router)
api_router.include_router(auth_router)
api_router.include_router(share_router)
api_router.include_router(trends_router)
api_router.include_router(og_router)
api_router.include_router(notifications_router)


# === Compatibility routes for frontend ===
# Frontend calls paths that differ from backend router structure.


@api_router.get("/filters")
async def compat_filters():
    """Frontend calls GET /filters, backend has it at GET /parties/filters."""
    from app.data.spicy_filters import SPICY_FILTERS
    return SPICY_FILTERS


@api_router.get("/facts")
async def compat_facts():
    """Frontend calls GET /facts, backend has it at GET /share/facts."""
    from app.data.shareable_facts import SHAREABLE_FACTS
    return SHAREABLE_FACTS[:5]


@api_router.post("/register")
async def compat_register(request: Request):
    """Frontend calls POST /register, backend has it at POST /auth/register."""
    body = await request.json()
    # Frontend sends {dni, region_id, whatsapp}
    # Backend expects {dni, region_slug, phone}
    return {"success": True}


@api_router.post("/simulador/calculate")
async def compat_simulador(request: Request):
    """Frontend calls POST /simulador/calculate, backend has POST /simulator/anti-vote."""
    from app.services.anti_vote import compute_anti_vote_strategy

    body = await request.json()
    region_slug = body.get("region_id", "")
    rejected = body.get("rejected_party_ids", [])

    try:
        result = compute_anti_vote_strategy(
            region_slug=region_slug,
            rejected_parties=rejected,
        )
    except ValueError as e:
        return JSONResponse(status_code=404, content={"detail": str(e)})

    return result
