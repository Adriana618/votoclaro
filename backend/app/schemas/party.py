"""Party schemas."""

from pydantic import BaseModel


class PartyBase(BaseModel):
    abbreviation: str
    name: str
    color: str | None = None
    logo_url: str | None = None
    positions: dict | None = None
    is_active: bool = True


class PartyOut(PartyBase):
    id: int

    model_config = {"from_attributes": True}


class PartyFilter(BaseModel):
    """Filter parameters for party listing."""
    filter_id: str | None = None  # spicy filter ID
    is_active: bool | None = None
