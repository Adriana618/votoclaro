"""Static data for VotoClaro."""

from app.data.parties import PARTIES, PARTY_NAMES
from app.data.regions import REGIONS, SENATE_SEATS

# Candidatos se importan condicionalmente (pueden no existir aun)
try:
    from app.data.candidates import (
        CANDIDATES,
        CANDIDATES_BY_PARTY,
        CANDIDATES_BY_REGION,
    )
except ImportError:
    CANDIDATES: dict = {}
    CANDIDATES_BY_PARTY: dict = {}
    CANDIDATES_BY_REGION: dict = {}
