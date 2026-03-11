"""SQLAlchemy models for VotoClaro."""

from app.models.party import Party
from app.models.region import Region
from app.models.candidate import Candidate
from app.models.poll import Poll
from app.models.user import User
from app.models.vote_preference import VotePreference

__all__ = ["Party", "Region", "Candidate", "Poll", "User", "VotePreference"]
