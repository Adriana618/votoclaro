"""Region schemas."""

from pydantic import BaseModel


class RegionOut(BaseModel):
    id: int
    name: str
    slug: str
    seats_diputados: int
    department_code: str | None = None

    model_config = {"from_attributes": True}
