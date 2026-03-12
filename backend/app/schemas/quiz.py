"""Quiz schemas."""

from pydantic import BaseModel


class QuizOption(BaseModel):
    text: str
    value: int  # -2 to +2


class QuizQuestion(BaseModel):
    id: str
    question: str
    category: str
    emoji: str = ""
    options: list[QuizOption]
    context: str | None = None
    source: str | None = None


class QuizAnswer(BaseModel):
    question_id: str
    value: int  # -2 to +2 (0 = "no sé")


class QuizSubmission(BaseModel):
    answers: list[QuizAnswer]


class PartyAffinity(BaseModel):
    party: str
    name: str
    match_percentage: float


class QuizResult(BaseModel):
    rankings: list[PartyAffinity]
    affinities: list[PartyAffinity]
    top_match: str
    top_match_name: str
    top_match_percentage: float
