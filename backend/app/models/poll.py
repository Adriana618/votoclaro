"""Poll data per region/party."""

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from app.database import Base


class Poll(Base):
    """Polling data for a party in a region."""

    __tablename__ = "polls"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True, index=True)
    party_id = Column(Integer, ForeignKey("parties.id"), nullable=False, index=True)
    percentage = Column(Float, nullable=False)
    sample_size = Column(Integer, nullable=True)
    pollster = Column(String(200), nullable=True)
    date = Column(Date, nullable=True)
