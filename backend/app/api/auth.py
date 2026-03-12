"""Optional DNI-based registration endpoints."""

import hashlib
import hmac

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])


def _hash_value(value: str) -> str:
    """Hash a sensitive value (DNI or phone) using HMAC-SHA256 with secret salt.

    Uses a keyed hash (HMAC) so that the same DNI always produces the same
    hash within this deployment, but the hash cannot be reversed or brute-forced
    without knowing the SECRET_KEY.
    """
    return hmac.new(
        key=settings.SECRET_KEY.encode("utf-8"),
        msg=value.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


@router.post("/register", response_model=UserOut)
async def register(data: UserRegister, db: Session = Depends(get_db)):
    """Register a user (optional, for tracking preferences).

    DNI and phone are stored only as hashes for privacy.
    """
    dni_hash = _hash_value(data.dni) if data.dni else None
    phone_hash = _hash_value(data.phone) if data.phone else None

    # Check if user already exists by DNI hash
    if dni_hash:
        existing = db.query(User).filter(User.dni_hash == dni_hash).first()
        if existing:
            return UserOut.model_validate(existing)

    # Find region_id from slug if provided
    region_id = None
    if data.region_slug:
        from app.data.regions import REGIONS

        for idx, r in enumerate(REGIONS, start=1):
            if r["slug"] == data.region_slug:
                region_id = idx
                break

    user = User(
        dni_hash=dni_hash,
        phone_hash=phone_hash,
        region_id=region_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserOut.model_validate(user)
