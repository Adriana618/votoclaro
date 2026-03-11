"""Tests for quiz affinity calculation."""

import pytest

from app.services.quiz import (
    answers_to_vector,
    calculate_affinity,
    cosine_similarity,
    get_quiz_questions,
    DIMENSIONS,
)


class TestAnswersToVector:
    def test_neutral_answers(self):
        """All neutral (3) answers should produce zero vector."""
        answers = {f"q{i}": 3 for i in range(1, 16)}
        vector = answers_to_vector(answers)
        for dim in DIMENSIONS:
            assert vector[dim] == pytest.approx(0.0, abs=0.01)

    def test_extreme_agree(self):
        """All strongly agree (5) should produce non-zero vector."""
        answers = {f"q{i}": 5 for i in range(1, 16)}
        vector = answers_to_vector(answers)
        # At least some dimensions should be non-zero
        assert any(abs(v) > 0.1 for v in vector.values())

    def test_missing_answers(self):
        """Partial answers should still work."""
        answers = {"q1": 1, "q2": 5}
        vector = answers_to_vector(answers)
        assert isinstance(vector, dict)
        assert all(dim in vector for dim in DIMENSIONS)


class TestCosineSimilarity:
    def test_identical_vectors(self):
        vec = {"economy": 1, "social": 1, "authority": 1, "corruption": 1, "environment": 1}
        assert cosine_similarity(vec, vec) == pytest.approx(1.0, abs=0.001)

    def test_opposite_vectors(self):
        vec_a = {"economy": 1, "social": 1, "authority": 1, "corruption": 1, "environment": 1}
        vec_b = {"economy": -1, "social": -1, "authority": -1, "corruption": -1, "environment": -1}
        assert cosine_similarity(vec_a, vec_b) == pytest.approx(-1.0, abs=0.001)

    def test_orthogonal_vectors(self):
        vec_a = {"economy": 1, "social": 0, "authority": 0, "corruption": 0, "environment": 0}
        vec_b = {"economy": 0, "social": 1, "authority": 0, "corruption": 0, "environment": 0}
        assert cosine_similarity(vec_a, vec_b) == pytest.approx(0.0, abs=0.001)

    def test_zero_vector(self):
        vec_a = {"economy": 0, "social": 0, "authority": 0, "corruption": 0, "environment": 0}
        vec_b = {"economy": 1, "social": 1, "authority": 1, "corruption": 1, "environment": 1}
        assert cosine_similarity(vec_a, vec_b) == pytest.approx(0.0, abs=0.001)


class TestCalculateAffinity:
    def test_returns_all_parties(self):
        """Should return affinity for every party."""
        answers = {f"q{i}": 3 for i in range(1, 16)}
        result = calculate_affinity(answers)
        assert len(result) == 12  # 12 parties

    def test_sorted_by_match(self):
        """Results should be sorted by match_percentage descending."""
        answers = {f"q{i}": 4 for i in range(1, 16)}
        result = calculate_affinity(answers)
        percentages = [r["match_percentage"] for r in result]
        assert percentages == sorted(percentages, reverse=True)

    def test_match_percentage_range(self):
        """Match percentages should be between 0 and 100."""
        answers = {f"q{i}": 1 for i in range(1, 16)}
        result = calculate_affinity(answers)
        for r in result:
            assert 0 <= r["match_percentage"] <= 100

    def test_right_wing_answers_favor_right_parties(self):
        """Strongly right-wing answers should favor conservative parties.

        We selectively answer: agree with pro-market, pro-authority,
        pro-extractivism questions; disagree with progressive ones.
        """
        answers = {
            "q1": 1,   # disagree: state price controls (left)
            "q2": 5,   # agree: private > state (right)
            "q3": 1,   # disagree: equal marriage (conservative)
            "q4": 1,   # disagree: sex ed (conservative)
            "q5": 5,   # agree: death penalty (authoritarian)
            "q6": 5,   # agree: military power (authoritarian)
            "q7": 5,   # agree: mining > environment (extractivist)
            "q8": 1,   # disagree: bar investigated politicians (pro-corruption)
            "q9": 5,   # agree: foreign investment (right)
            "q10": 1,  # disagree: community veto on mining (authoritarian)
            "q11": 5,  # agree: recentralize (authoritarian)
            "q12": 1,  # disagree: legal abortion (conservative)
            "q13": 1,  # disagree: expand social programs (right)
            "q14": 1,  # disagree: new constitution (conservative)
            "q15": 5,  # agree: jobs > labor rights (right)
        }
        result = calculate_affinity(answers)
        top = result[0]
        assert top["party"] in ("rp", "fp", "fep", "an", "avp", "app")

    def test_left_wing_answers_favor_left_parties(self):
        """Strongly left-wing answers should favor progressive parties.

        We selectively answer: agree with progressive, pro-state,
        pro-environment questions; disagree with conservative ones.
        """
        answers = {
            "q1": 5,   # agree: state price controls (left)
            "q2": 1,   # disagree: private > state (left)
            "q3": 5,   # agree: equal marriage (progressive)
            "q4": 5,   # agree: sex ed (progressive)
            "q5": 1,   # disagree: death penalty (libertarian)
            "q6": 1,   # disagree: military power (libertarian)
            "q7": 1,   # disagree: mining > environment (green)
            "q8": 5,   # agree: bar investigated politicians (anti-corruption)
            "q9": 1,   # disagree: foreign investment (left)
            "q10": 5,  # agree: community veto (libertarian)
            "q11": 1,  # disagree: recentralize (libertarian)
            "q12": 5,  # agree: legal abortion (progressive)
            "q13": 5,  # agree: expand social programs (left)
            "q14": 5,  # agree: new constitution (progressive)
            "q15": 1,  # disagree: jobs > labor rights (left)
        }
        result = calculate_affinity(answers)
        top = result[0]
        assert top["party"] in ("jpp", "pm", "pl")

    def test_has_required_fields(self):
        """Each result should have party, name, score, match_percentage."""
        answers = {"q1": 3, "q2": 3}
        result = calculate_affinity(answers)
        for r in result:
            assert "party" in r
            assert "name" in r
            assert "score" in r
            assert "match_percentage" in r


class TestGetQuizQuestions:
    def test_returns_15_questions(self):
        questions = get_quiz_questions()
        assert len(questions) == 15

    def test_question_format(self):
        questions = get_quiz_questions()
        for q in questions:
            assert "id" in q
            assert "text" in q
            assert "category" in q
            # Should NOT expose mapping to the client
            assert "mapping" not in q
