"""Party model with positions vector."""

from sqlalchemy import Boolean, Column, Integer, String, JSON
from app.database import Base


class Party(Base):
    """Political party with ideological positions."""

    __tablename__ = "parties"

    id = Column(Integer, primary_key=True, index=True)
    abbreviation = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    logo_url = Column(String(500), nullable=True)
    color = Column(String(7), nullable=True)  # hex color
    positions = Column(JSON, nullable=True)  # ideological positions vector
    is_active = Column(Boolean, default=True, nullable=False)
