"""Controversy score calculator for candidates.

The controversy score is a composite metric that aggregates multiple
risk factors into a single 0-100 score for easy comparison.
"""


# Weights for each factor in the controversy score
WEIGHTS = {
    "has_criminal_record": 30,  # Criminal record is the heaviest factor
    "voted_pro_crime": 20,      # Voting against anti-corruption measures
    "is_reelection": 5,         # Mild factor - incumbency itself isn't bad
    "investigations": 15,       # Per investigation (capped)
    "party_changed": 10,        # Transfuguismo
}

MAX_INVESTIGATIONS_COUNTED = 3  # Cap investigations contribution
MAX_SCORE = 100.0


def calculate_controversy_score(
    has_criminal_record: bool = False,
    voted_pro_crime: bool = False,
    is_reelection: bool = False,
    investigations: int = 0,
    party_changed_from: str | None = None,
) -> float:
    """Calculate a controversy score for a candidate.

    Args:
        has_criminal_record: Whether the candidate has a criminal record.
        voted_pro_crime: Whether they voted for pro-impunity legislation.
        is_reelection: Whether they are seeking reelection.
        investigations: Number of active fiscal investigations.
        party_changed_from: Previous party abbreviation if they switched.

    Returns:
        Controversy score between 0.0 and 100.0.
    """
    score = 0.0

    if has_criminal_record:
        score += WEIGHTS["has_criminal_record"]

    if voted_pro_crime:
        score += WEIGHTS["voted_pro_crime"]

    if is_reelection:
        score += WEIGHTS["is_reelection"]

    # Cap investigations contribution
    inv_count = min(investigations, MAX_INVESTIGATIONS_COUNTED)
    score += inv_count * WEIGHTS["investigations"]

    if party_changed_from:
        score += WEIGHTS["party_changed"]

    return min(score, MAX_SCORE)


def calculate_party_controversy_average(candidates: list[dict]) -> float:
    """Calculate average controversy score across a party's candidates.

    Args:
        candidates: List of candidate dicts with controversy-relevant fields.

    Returns:
        Average controversy score for the party.
    """
    if not candidates:
        return 0.0

    total = sum(
        calculate_controversy_score(
            has_criminal_record=c.get("has_criminal_record", False),
            voted_pro_crime=c.get("voted_pro_crime", False),
            is_reelection=c.get("is_reelection", False),
            investigations=c.get("investigations", 0),
            party_changed_from=c.get("party_changed_from"),
        )
        for c in candidates
    )

    return total / len(candidates)
