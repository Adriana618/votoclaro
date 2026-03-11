"""Region model with seat counts."""

from sqlalchemy import Column, Integer, String
from app.database import Base


class Region(Base):
    """Peruvian electoral region."""

    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    seats_diputados = Column(Integer, nullable=False)
    department_code = Column(String(10), nullable=True)
