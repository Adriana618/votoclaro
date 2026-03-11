"""User schemas."""

from pydantic import BaseModel


class UserRegister(BaseModel):
    dni: str | None = None
    phone: str | None = None
    region_slug: str | None = None


class UserOut(BaseModel):
    id: int
    region_id: int | None = None

    model_config = {"from_attributes": True}
