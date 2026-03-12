"""Quiz affinity calculation — spec-compliant implementation.

Uses normalized Euclidean distance to match user answers against
party positions on 15 specific questions. Values range -2 to +2.
Answers of 0 ("no sé") are skipped.
"""

from app.data.parties import PARTY_NAMES
from app.data.quiz_questions import QUIZ_QUESTIONS, PARTY_POSITIONS


def calculate_affinity(user_answers: dict[str, int]) -> list[dict]:
    """Calculate affinity between user answers and all parties.

    Uses the spec's distance formula:
    - max_distance = answered_questions * 4  (max diff per question = |-2 - 2| = 4)
    - actual_distance = sum of abs differences
    - match = (1 - actual/max) * 100

    Args:
        user_answers: Dict mapping question_id to selected value (-2 to +2).

    Returns:
        Sorted list of dicts with party, name, match_percentage.
        Sorted by match_percentage descending.
    """
    affinities = []

    for party_abbr, party_positions in PARTY_POSITIONS.items():
        common = set(user_answers.keys()) & set(party_positions.keys())
        if not common:
            affinities.append({
                "party": party_abbr,
                "name": PARTY_NAMES.get(party_abbr, party_abbr),
                "match_percentage": 0.0,
            })
            continue

        # Only count questions where user gave a real answer (not 0 / "no sé")
        answered = [q for q in common if user_answers[q] != 0]
        if not answered:
            affinities.append({
                "party": party_abbr,
                "name": PARTY_NAMES.get(party_abbr, party_abbr),
                "match_percentage": 50.0,  # neutral if all "no sé"
            })
            continue

        max_distance = len(answered) * 4
        actual_distance = sum(
            abs(user_answers[q] - party_positions[q])
            for q in answered
        )

        match_pct = round((1 - actual_distance / max_distance) * 100, 1)

        affinities.append({
            "party": party_abbr,
            "name": PARTY_NAMES.get(party_abbr, party_abbr),
            "match_percentage": match_pct,
        })

    affinities.sort(key=lambda x: -x["match_percentage"])
    return affinities


def get_quiz_questions() -> list[dict]:
    """Return quiz questions formatted for the API."""
    return [
        {
            "id": q["id"],
            "question": q["question"],
            "category": q["category"],
            "emoji": q.get("emoji", ""),
            "options": q["options"],
            "context": q.get("context"),
            "source": q.get("source"),
        }
        for q in QUIZ_QUESTIONS
    ]
