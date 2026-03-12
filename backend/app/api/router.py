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
    """Frontend calls POST /simulador/calculate, backend has POST /simulator/anti-vote.

    Transforms backend response to match frontend AntiVoteResult interface:
    - region: Region object {id, name, seats}
    - rejected_parties: Party[] objects
    - recommended_party: Party object
    - dhondt_table: DhondtRow[] with quotients/divisors
    - wasted_vote_risk: number
    """
    from app.data.parties import PARTIES
    from app.data.regions import REGIONS
    from app.services.anti_vote import (
        DEFAULT_POLL_PERCENTAGES,
        compute_anti_vote_strategy,
        get_region_by_slug,
        percentages_to_votes,
    )
    from app.services.dhondt import dhondt_method

    body = await request.json()
    region_slug = body.get("region_id", "")
    raw_rejected = body.get("rejected_party_ids", [])

    # Normalize party IDs: frontend may send abbreviations ("fp") or
    # numeric IDs (1, 2, "1") from old fallback data. Convert to abbreviations.
    party_abbrs = list(PARTIES.keys())  # ordered list of party abbreviations
    rejected = []
    for pid in raw_rejected:
        pid_str = str(pid)
        if pid_str in PARTIES:
            # Already a valid abbreviation
            rejected.append(pid_str)
        elif isinstance(pid, int) or pid_str.isdigit():
            # Numeric ID — map to abbreviation by index (1-based)
            idx = int(pid_str) - 1
            if 0 <= idx < len(party_abbrs):
                rejected.append(party_abbrs[idx])
        # Skip unrecognized IDs

    try:
        result = compute_anti_vote_strategy(
            region_slug=region_slug,
            rejected_parties=rejected,
        )
    except ValueError as e:
        return JSONResponse(status_code=404, content={"detail": str(e)})

    # Build region object
    region_data = get_region_by_slug(region_slug)
    region_obj = {
        "id": region_slug,
        "name": region_data["name"] if region_data else region_slug,
        "seats": region_data["seats_diputados"] if region_data else 0,
    }

    # Build Party objects for rejected parties
    def _party_obj(abbr: str) -> dict:
        p = PARTIES.get(abbr, {})
        return {
            "id": abbr,
            "name": p.get("name", abbr),
            "abbreviation": p.get("abbreviation", abbr),
            "color": p.get("color"),
            "logo_url": p.get("logo_url"),
        }

    rejected_party_objs = [_party_obj(pid) for pid in rejected]

    rec_abbr = result.get("recommended_party", "")
    rec_party_obj = _party_obj(rec_abbr) if rec_abbr else {
        "id": "", "name": "Ninguno", "abbreviation": "", "color": None, "logo_url": None,
    }

    # Build D'Hondt table with quotients and divisors
    seats = region_obj["seats"]
    votes = percentages_to_votes(DEFAULT_POLL_PERCENTAGES)
    for rp in rejected:
        if rp not in votes:
            votes[rp] = 0

    dhondt_table = []
    allocation = dhondt_method(votes, seats)
    for party_abbr, vote_count in sorted(votes.items(), key=lambda x: -x[1]):
        if vote_count <= 0:
            continue
        divisors = list(range(1, seats + 1))
        quotients = [vote_count / d for d in divisors]
        dhondt_table.append({
            "party": PARTIES.get(party_abbr, {}).get("name", party_abbr),
            "votes": vote_count,
            "divisors": divisors,
            "quotients": quotients,
            "seats_won": allocation.get(party_abbr, 0),
        })

    # Wasted vote risk: if recommended party has very low votes, risk is higher
    rec_votes = votes.get(rec_abbr, 0)
    total_votes = sum(votes.values()) or 1
    rec_pct = (rec_votes / total_votes) * 100
    # Simple heuristic: risk is inverse of party strength, capped 0-100
    wasted_vote_risk = max(0, min(100, round(100 - rec_pct * 10)))

    return {
        "region": region_obj,
        "rejected_parties": rejected_party_objs,
        "recommended_party": rec_party_obj,
        "recommended_party_label": f"Vota por {rec_party_obj['name']}",
        "explanation": result.get("explanation", ""),
        "dhondt_table": dhondt_table,
        "wasted_vote_risk": wasted_vote_risk,
    }
