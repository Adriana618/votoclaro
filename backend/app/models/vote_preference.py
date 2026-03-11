"""User's anti-vote preferences."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, func
from app.database import Base


class VotePreference(Base):
    """Stores a user's voting simulation preferences and results."""

    __tablename__ = "vote_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True)
    rejected_parties = Column(JSON, nullable=False)  # list of party abbreviations
    recommended_party_id = Column(Integer, ForeignKey("parties.id"), nullable=True)
    quiz_answers = Column(JSON, nullable=True)  # user's quiz responses
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
