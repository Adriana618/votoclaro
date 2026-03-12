"""Mi Voto endpoints — save and retrieve strategic vote by DNI + dígito verificador.

Peruvian DNIs have 8 digits plus a verification digit (1 character, letter or number).
We require both for save/lookup to prevent unauthorized access to someone else's vote.
The key is hashed as SHA-256(dni + digito) so it's unique per person.
"""

import hashlib
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/mi-voto", tags=["mi-voto"])

# Simple file-based storage (no DB dependency)
VOTES_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "saved_votes.json"


def _validate_dni_digito(dni: str, digito: str) -> None:
    """Validate DNI (8 digits) and dígito verificador (1 alphanumeric char)."""
    if not dni or len(dni) != 8 or not dni.isdigit():
        raise HTTPException(status_code=400, detail="DNI debe tener 8 digitos.")
    if not digito or len(digito) != 1 or not digito.isalnum():
        raise HTTPException(
            status_code=400,
            detail="Digito verificador debe ser 1 caracter (numero o letra).",
        )


def _hash_key(dni: str, digito: str) -> str:
    """Hash DNI + dígito verificador with SHA-256 for privacy."""
    combined = f"{dni.strip()}-{digito.strip().upper()}"
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def _load_votes() -> dict:
    if VOTES_FILE.exists():
        return json.loads(VOTES_FILE.read_text())
    return {}


def _save_votes(votes: dict) -> None:
    VOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
    VOTES_FILE.write_text(json.dumps(votes, ensure_ascii=False))


@router.post("/save")
async def save_vote(request: Request):
    """Save a strategic vote result linked to hashed DNI + dígito verificador.

    Body: {dni, digito, region, recommended_party, rejected_parties}
    """
    body = await request.json()
    dni = body.get("dni", "")
    digito = body.get("digito", "")
    _validate_dni_digito(dni, digito)

    key = _hash_key(dni, digito)

    votes = _load_votes()
    votes[key] = {
        "region": body.get("region"),
        "recommended_party": body.get("recommended_party"),
        "rejected_parties": body.get("rejected_parties"),
        "saved_at": body.get("saved_at"),
    }
    _save_votes(votes)

    return {"success": True, "message": "Voto guardado exitosamente."}


@router.post("/lookup")
async def lookup_vote(request: Request):
    """Look up a saved strategic vote by DNI + dígito verificador.

    Body: {dni, digito}
    Returns the saved vote or 404.
    """
    body = await request.json()
    dni = body.get("dni", "")
    digito = body.get("digito", "")
    _validate_dni_digito(dni, digito)

    key = _hash_key(dni, digito)
    votes = _load_votes()
    vote = votes.get(key)

    if not vote:
        raise HTTPException(
            status_code=404,
            detail="No se encontro un voto guardado con este DNI y digito verificador.",
        )

    return vote
