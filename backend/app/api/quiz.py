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
    """Return all quiz questions."""
    return get_quiz_questions()


@router.post("/submit", response_model=QuizResult)
async def submit_quiz(submission: QuizSubmission):
    """Calculate ideological affinity based on quiz answers.

    Accepts a list of (question_id, value) pairs where value is 1-5
    on a Likert scale. Returns affinity scores for all parties.
    """
    if not submission.answers:
        raise HTTPException(status_code=400, detail="Debes responder al menos una pregunta.")

    # Validate answer values
    for answer in submission.answers:
        if answer.value < 1 or answer.value > 5:
            raise HTTPException(
                status_code=400,
                detail=f"La respuesta a {answer.question_id} debe estar entre 1 y 5.",
            )

    # Convert to dict format for the service
    answers_dict = {a.question_id: a.value for a in submission.answers}

    affinities = calculate_affinity(answers_dict)

    if not affinities:
        raise HTTPException(status_code=500, detail="Error calculando afinidad.")

    top = affinities[0]

    return QuizResult(
        affinities=[PartyAffinity(**a) for a in affinities],
        top_match=top["party"],
        top_match_name=top["name"],
        top_match_percentage=top["match_percentage"],
    )
