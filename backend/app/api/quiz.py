"""Quiz endpoints for ideological affinity calculation."""

from fastapi import APIRouter, HTTPException

from app.schemas.quiz import (
    QuizQuestion,
    QuizResult,
    QuizSubmission,
    PartyAffinity,
)
from app.services.quiz import calculate_affinity, get_quiz_questions

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.get("/questions", response_model=list[QuizQuestion])
async def list_questions():
    """Return all 15 quiz questions with options."""
    return get_quiz_questions()


@router.post("/submit", response_model=QuizResult)
async def submit_quiz(submission: QuizSubmission):
    """Calculate ideological affinity based on quiz answers.

    Accepts answers with values -2 to +2 (0 = "no sé").
    Returns affinity scores for all parties.
    """
    if not submission.answers:
        raise HTTPException(status_code=400, detail="Debes responder al menos una pregunta.")

    for answer in submission.answers:
        if answer.value < -2 or answer.value > 2:
            raise HTTPException(
                status_code=400,
                detail=f"La respuesta a {answer.question_id} debe estar entre -2 y 2.",
            )

    answers_dict = {a.question_id: a.value for a in submission.answers}
    affinities = calculate_affinity(answers_dict)

    if not affinities:
        raise HTTPException(status_code=500, detail="Error calculando afinidad.")

    top = affinities[0]

    affinity_list = [PartyAffinity(**a) for a in affinities]

    return {
        # Frontend expects 'rankings'
        "rankings": [a.model_dump() for a in affinity_list],
        # Also include original fields for backwards compat
        "affinities": [a.model_dump() for a in affinity_list],
        "top_match": top["party"],
        "top_match_name": top["name"],
        "top_match_percentage": top["match_percentage"],
    }
