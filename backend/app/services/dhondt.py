"""D'Hondt method implementation for seat allocation.

The D'Hondt method (also known as Jefferson method) is used in Peru
to allocate congressional seats proportionally. For each party, quotients
are calculated as votes/1, votes/2, ..., votes/seats. The highest
quotients across all parties win seats.
"""


def dhondt_method(votes: dict[str, int], seats: int) -> dict[str, int]:
    """Standard D'Hondt method for seat allocation.

    Args:
        votes: Dictionary mapping party abbreviation to vote count.
        seats: Number of seats to allocate.

    Returns:
        Dictionary mapping party abbreviation to number of seats won.
    """
    if seats <= 0:
        return {party: 0 for party in votes}

    # Filter out parties with zero or negative votes
    active_votes = {p: v for p, v in votes.items() if v > 0}

    if not active_votes:
        return {party: 0 for party in votes}

    # Build list of (quotient, party) for all divisors
    quotients: list[tuple[float, str]] = []
    for party, vote_count in active_votes.items():
        for divisor in range(1, seats + 1):
            quotients.append((vote_count / divisor, party))

    # Sort by quotient descending, then by party name for deterministic tie-breaking
    quotients.sort(key=lambda x: (-x[0], x[1]))

    # Allocate seats to the top quotients
    allocation: dict[str, int] = {party: 0 for party in votes}
    for i in range(min(seats, len(quotients))):
        _, party = quotients[i]
        allocation[party] += 1

    return allocation


def calculate_anti_vote(
    votes: dict[str, int],
    rejected_parties: list[str],
    seats: int,
) -> tuple[str, dict[str, int], dict[str, int]]:
    """Given rejected parties, find which remaining party to vote for
    that minimizes rejected parties' seats.

    The strategy: simulate adding a block of strategic votes to each
    non-rejected party and see which allocation hurts the rejected
    parties the most.

    Args:
        votes: Current vote distribution (party -> votes).
        rejected_parties: List of party abbreviations the user rejects.
        seats: Number of seats in the district.

    Returns:
        Tuple of (recommended_party, original_allocation, best_allocation).
    """
    rejected_set = set(rejected_parties)
    non_rejected = [p for p in votes if p not in rejected_set and votes[p] > 0]

    if not non_rejected:
        # All parties are rejected or have no votes - no recommendation possible
        original = dhondt_method(votes, seats)
        return "", original, original

    # Calculate original allocation
    original_allocation = dhondt_method(votes, seats)
    original_rejected_seats = sum(
        s for p, s in original_allocation.items() if p in rejected_set
    )

    # Strategic vote block size: approximate 1% of total votes
    # This simulates what happens if a meaningful group votes strategically
    total_votes = sum(votes.values())
    strategic_block = max(1, total_votes // 100)

    best_party = non_rejected[0]
    best_rejected_seats = original_rejected_seats
    best_allocation = original_allocation

    for candidate_party in non_rejected:
        # Simulate adding strategic votes to this party
        simulated_votes = dict(votes)
        simulated_votes[candidate_party] += strategic_block

        allocation = dhondt_method(simulated_votes, seats)
        rejected_seats = sum(
            s for p, s in allocation.items() if p in rejected_set
        )

        # Prefer the party that minimizes rejected seats
        # On tie, prefer the party that already has fewer seats (spread power)
        if rejected_seats < best_rejected_seats or (
            rejected_seats == best_rejected_seats
            and allocation.get(candidate_party, 0)
            < best_allocation.get(best_party, 0)
        ):
            best_party = candidate_party
            best_rejected_seats = rejected_seats
            best_allocation = allocation

    return best_party, original_allocation, best_allocation
