"""Quiz questions data and affinity calculation.

Takes a user's Likert-scale answers and computes cosine-similarity-style
affinity with each party's ideological position vector.
"""

import math

from app.data.parties import PARTY_NAMES, PARTY_POSITIONS
from app.data.quiz_questions import QUIZ_QUESTIONS


# The ideological dimensions used for affinity
DIMENSIONS = ["economy", "social", "authority", "corruption", "environment"]


def answers_to_vector(answers: dict[str, int]) -> dict[str, float]:
    """Convert quiz answers to a user ideological vector.

    Each answer is on a 1-5 Likert scale. We normalize to -2..+2 range
    (matching party positions) by subtracting 3.

    Then we apply each question's mapping to accumulate dimension scores.

    Args:
        answers: Dict mapping question_id to answer value (1-5).

    Returns:
        Dict mapping dimension name to accumulated score.
    """
    vector: dict[str, float] = {dim: 0.0 for dim in DIMENSIONS}
    dim_counts: dict[str, int] = {dim: 0 for dim in DIMENSIONS}

    for question in QUIZ_QUESTIONS:
        qid = question["id"]
        if qid not in answers:
            continue

        # Normalize answer from 1-5 to -2..+2
        normalized = answers[qid] - 3

        for dim, weight in question["mapping"].items():
            vector[dim] += normalized * weight
            dim_counts[dim] += 1

    # Average by number of questions contributing to each dimension
    for dim in DIMENSIONS:
        if dim_counts[dim] > 0:
            vector[dim] /= dim_counts[dim]

    return vector


def cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    """Compute cosine similarity between two ideological vectors.

    Args:
        vec_a: First vector (dimension -> value).
        vec_b: Second vector (dimension -> value).

    Returns:
        Cosine similarity in range [-1, 1].
    """
    dot_product = sum(vec_a.get(d, 0) * vec_b.get(d, 0) for d in DIMENSIONS)
    magnitude_a = math.sqrt(sum(vec_a.get(d, 0) ** 2 for d in DIMENSIONS))
    magnitude_b = math.sqrt(sum(vec_b.get(d, 0) ** 2 for d in DIMENSIONS))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def calculate_affinity(answers: dict[str, int]) -> list[dict]:
    """Calculate affinity between user answers and all parties.

    Args:
        answers: Dict mapping question_id to answer value (1-5).

    Returns:
        Sorted list of dicts with party, name, score, match_percentage.
        Sorted by match_percentage descending.
    """
    user_vector = answers_to_vector(answers)

    affinities = []
    for party_abbr, positions in PARTY_POSITIONS.items():
        # Convert party positions dict to float dict for cosine similarity
        party_vector = {dim: float(positions.get(dim, 0)) for dim in DIMENSIONS}
        similarity = cosine_similarity(user_vector, party_vector)

        # Convert from [-1, 1] to [0, 100] percentage
        match_pct = round((similarity + 1) / 2 * 100, 1)

        affinities.append({
            "party": party_abbr,
            "name": PARTY_NAMES[party_abbr],
            "score": round(similarity, 4),
            "match_percentage": match_pct,
        })

    affinities.sort(key=lambda x: -x["match_percentage"])
    return affinities


def get_quiz_questions() -> list[dict]:
    """Return quiz questions formatted for the API (without mappings)."""
    return [
        {
            "id": q["id"],
            "text": q["text"],
            "category": q["category"],
        }
        for q in QUIZ_QUESTIONS
    ]
