"""Anti-vote strategy calculator.

Wraps the D'Hondt engine with polling data and region context
to provide actionable strategic voting recommendations.
"""

from app.data.parties import PARTY_NAMES
from app.data.regions import REGIONS
from app.services.dhondt import calculate_anti_vote, dhondt_method


# Default simulated polling data (percentage per party, national average)
# In production this comes from the database
DEFAULT_POLL_PERCENTAGES: dict[str, float] = {
    "rp": 12.0,
    "fp": 15.0,
    "pm": 5.0,
    "jpp": 4.0,
    "ap": 8.0,
    "sc": 3.0,
    "pl": 6.0,
    "an": 3.0,
    "app": 10.0,
    "pod": 4.0,
    "fep": 2.0,
    "avp": 5.0,
}

# Total simulated electorate per region (rough proportional estimates)
DEFAULT_ELECTORATE = 100_000


def get_region_by_slug(slug: str) -> dict | None:
    """Find a region by its slug."""
    for region in REGIONS:
        if region["slug"] == slug:
            return region
    return None


def percentages_to_votes(
    percentages: dict[str, float], electorate: int = DEFAULT_ELECTORATE
) -> dict[str, int]:
    """Convert polling percentages to simulated vote counts."""
    return {
        party: int(pct / 100 * electorate)
        for party, pct in percentages.items()
    }


def compute_anti_vote_strategy(
    region_slug: str,
    rejected_parties: list[str],
    custom_votes: dict[str, int] | None = None,
) -> dict:
    """Compute the full anti-vote recommendation for a region.

    Args:
        region_slug: Slug of the electoral region.
        rejected_parties: Parties the user wants to minimize.
        custom_votes: Optional override vote distribution.

    Returns:
        Dictionary with recommendation details.
    """
    region = get_region_by_slug(region_slug)
    if region is None:
        raise ValueError(f"Region '{region_slug}' not found")

    seats = region["seats_diputados"]

    if custom_votes:
        votes = custom_votes
    else:
        votes = percentages_to_votes(DEFAULT_POLL_PERCENTAGES)

    # Ensure all rejected parties exist in votes
    for rp in rejected_parties:
        if rp not in votes:
            votes[rp] = 0

    recommended, original_alloc, strategy_alloc = calculate_anti_vote(
        votes, rejected_parties, seats
    )

    rejected_set = set(rejected_parties)
    rejected_before = sum(s for p, s in original_alloc.items() if p in rejected_set)
    rejected_after = sum(s for p, s in strategy_alloc.items() if p in rejected_set)

    if recommended:
        explanation = (
            f"En {region['name']} ({seats} escanos), votando por "
            f"{PARTY_NAMES.get(recommended, recommended)} puedes reducir "
            f"los escanos de los partidos que rechazas de {rejected_before} "
            f"a {rejected_after}."
        )
    else:
        explanation = "No se encontro una estrategia viable con los datos actuales."

    return {
        "recommended_party": recommended,
        "recommended_party_name": PARTY_NAMES.get(recommended, ""),
        "explanation": explanation,
        "seat_allocation_without_strategy": [
            {"party": p, "seats": s}
            for p, s in sorted(original_alloc.items(), key=lambda x: -x[1])
            if s > 0
        ],
        "seat_allocation_with_strategy": [
            {"party": p, "seats": s}
            for p, s in sorted(strategy_alloc.items(), key=lambda x: -x[1])
            if s > 0
        ],
        "rejected_seats_before": rejected_before,
        "rejected_seats_after": rejected_after,
        "seats_saved": rejected_before - rejected_after,
    }
