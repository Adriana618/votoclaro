"""Candidate schemas."""

from pydantic import BaseModel


class CandidateOut(BaseModel):
    id: int
    name: str
    party_id: int
    region_id: int | None = None
    position_number: int | None = None
    has_criminal_record: bool = False
    voted_pro_crime: bool = False
    is_reelection: bool = False
    investigations: int = 0
    controversy_score: float = 0.0
    party_changed_from: str | None = None

    model_config = {"from_attributes": True}


class ControversialRankingOut(BaseModel):
    candidates: list[CandidateOut]
    total: int
