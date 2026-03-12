"""Mi Voto endpoints — save and retrieve strategic vote by DNI."""

import hashlib
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/mi-voto", tags=["mi-voto"])

# Simple file-based storage (no DB dependency)
VOTES_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "saved_votes.json"


def _hash_dni(dni: str) -> str:
    """Hash DNI with SHA-256 for privacy. Same DNI always produces same hash."""
    return hashlib.sha256(dni.strip().encode("utf-8")).hexdigest()


def _load_votes() -> dict:
    if VOTES_FILE.exists():
        return json.loads(VOTES_FILE.read_text())
    return {}


def _save_votes(votes: dict) -> None:
    VOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
    VOTES_FILE.write_text(json.dumps(votes, ensure_ascii=False))


@router.post("/save")
async def save_vote(request: Request):
    """Save a strategic vote result linked to a hashed DNI.

    Body: {dni, region, recommended_party, rejected_parties}
    """
    body = await request.json()
    dni = body.get("dni", "")
    if not dni or len(dni) != 8 or not dni.isdigit():
        raise HTTPException(status_code=400, detail="DNI debe tener 8 digitos.")

    dni_hash = _hash_dni(dni)

    votes = _load_votes()
    votes[dni_hash] = {
        "region": body.get("region"),
        "recommended_party": body.get("recommended_party"),
        "rejected_parties": body.get("rejected_parties"),
        "saved_at": body.get("saved_at"),
    }
    _save_votes(votes)

    return {"success": True, "message": "Voto guardado exitosamente."}


@router.post("/lookup")
async def lookup_vote(request: Request):
    """Look up a saved strategic vote by DNI.

    Body: {dni}
    Returns the saved vote or 404.
    """
    body = await request.json()
    dni = body.get("dni", "")
    if not dni or len(dni) != 8 or not dni.isdigit():
        raise HTTPException(status_code=400, detail="DNI debe tener 8 digitos.")

    dni_hash = _hash_dni(dni)
    votes = _load_votes()
    vote = votes.get(dni_hash)

    if not vote:
        raise HTTPException(
            status_code=404,
            detail="No se encontro un voto guardado con este DNI. Usa el simulador primero.",
        )

    return vote
