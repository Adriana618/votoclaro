"""User schemas."""

import re

from pydantic import BaseModel, field_validator


class UserRegister(BaseModel):
    dni: str | None = None
    phone: str | None = None
    region_slug: str | None = None

    @field_validator("dni")
    @classmethod
    def validate_dni(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not re.fullmatch(r"\d{8}", v):
            raise ValueError("DNI debe ser exactamente 8 digitos numericos.")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not re.fullmatch(r"\+?\d{7,15}", v):
            raise ValueError("Numero de telefono invalido.")
        return v

    @field_validator("region_slug")
    @classmethod
    def validate_region_slug(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not re.fullmatch(r"[a-z0-9\-]{1,50}", v):
            raise ValueError("Slug de region invalido.")
        return v


class UserOut(BaseModel):
    id: int
    region_id: int | None = None

    model_config = {"from_attributes": True}
