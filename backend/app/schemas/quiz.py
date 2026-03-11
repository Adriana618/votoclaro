"""Quiz schemas."""

from pydantic import BaseModel


class QuizQuestion(BaseModel):
    id: str
    text: str
    category: str


class QuizAnswer(BaseModel):
    question_id: str
    value: int  # 1-5 Likert scale


class QuizSubmission(BaseModel):
    answers: list[QuizAnswer]


class PartyAffinity(BaseModel):
    party: str
    name: str
    score: float
    match_percentage: float


class QuizResult(BaseModel):
    affinities: list[PartyAffinity]
    top_match: str
    top_match_name: str
    top_match_percentage: float
