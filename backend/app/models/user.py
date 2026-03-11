"""User model with hashed DNI."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from app.database import Base


class User(Base):
    """Application user (optional registration)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    dni_hash = Column(String(64), nullable=True, unique=True, index=True)
    phone_hash = Column(String(64), nullable=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
