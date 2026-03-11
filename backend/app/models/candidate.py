"""Candidate model with controversy score fields."""

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Boolean
from app.database import Base


class Candidate(Base):
    """Congressional candidate with controversy metrics."""

    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    party_id = Column(Integer, ForeignKey("parties.id"), nullable=False, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True, index=True)
    position_number = Column(Integer, nullable=True)
    has_criminal_record = Column(Boolean, default=False, nullable=False)
    voted_pro_crime = Column(Boolean, default=False, nullable=False)
    is_reelection = Column(Boolean, default=False, nullable=False)
    investigations = Column(Integer, default=0, nullable=False)
    controversy_score = Column(Float, default=0.0, nullable=False)
    party_changed_from = Column(String(10), nullable=True)
