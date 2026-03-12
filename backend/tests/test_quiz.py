"""Tests for quiz affinity calculation — spec-compliant version."""

import pytest

from app.services.quiz import calculate_affinity, get_quiz_questions
from app.data.quiz_questions import QUIZ_QUESTIONS, PARTY_POSITIONS


class TestCalculateAffinity:
    def test_returns_all_parties(self):
        """Should return affinity for every party."""
        answers = {"leyes_procrimen": -2, "pena_muerte": -1}
        result = calculate_affinity(answers)
        assert len(result) == len(PARTY_POSITIONS)

    def test_sorted_by_match(self):
        """Results should be sorted by match_percentage descending."""
        answers = {"leyes_procrimen": -2, "aborto": -2, "constitucion": -2}
        result = calculate_affinity(answers)
        percentages = [r["match_percentage"] for r in result]
        assert percentages == sorted(percentages, reverse=True)

    def test_match_percentage_range(self):
        """Match percentages should be between 0 and 100."""
        answers = {q["id"]: q["options"][0]["value"] for q in QUIZ_QUESTIONS}
        result = calculate_affinity(answers)
        for r in result:
            assert 0 <= r["match_percentage"] <= 100

    def test_perfect_match_is_100(self):
        """Answering exactly like a party should give 100%."""
        # Answer exactly like Renovación Popular
        answers = PARTY_POSITIONS["rp"].copy()
        result = calculate_affinity(answers)
        rp_result = next(r for r in result if r["party"] == "rp")
        assert rp_result["match_percentage"] == 100.0

    def test_opposite_match_is_low(self):
        """Answering opposite to a party should give low score."""
        # Answer opposite of Renovación Popular (negate all values)
        answers = {k: -v for k, v in PARTY_POSITIONS["rp"].items()}
        result = calculate_affinity(answers)
        rp_result = next(r for r in result if r["party"] == "rp")
        assert rp_result["match_percentage"] <= 25.0

    def test_no_se_answers_skipped(self):
        """Answers of 0 ('no sé') should be excluded from calculation."""
        # All "no sé"
        answers = {q["id"]: 0 for q in QUIZ_QUESTIONS}
        result = calculate_affinity(answers)
        for r in result:
            assert r["match_percentage"] == 50.0  # neutral default

    def test_right_wing_answers_favor_right_parties(self):
        """Conservative answers should favor RP, FP."""
        answers = {
            "leyes_procrimen": 1,
            "pena_muerte": 2,
            "mano_dura": 2,
            "petroperu": 2,
            "aborto": 2,
            "matrimonio_igualitario": 2,
            "genero_escuelas": 2,
            "constitucion": 2,
            "caviares": 2,
            "fujimori_indulto": 2,
        }
        result = calculate_affinity(answers)
        top = result[0]
        assert top["party"] in ("rp", "fp", "fep")

    def test_left_wing_answers_favor_left_parties(self):
        """Progressive answers should favor JPP, PM."""
        answers = {
            "leyes_procrimen": -2,
            "pena_muerte": -2,
            "mano_dura": -2,
            "petroperu": -2,
            "impuestos": -2,
            "aborto": -2,
            "matrimonio_igualitario": -2,
            "genero_escuelas": -2,
            "constitucion": -2,
            "fujimori_indulto": -2,
        }
        result = calculate_affinity(answers)
        top = result[0]
        assert top["party"] in ("jpp", "pm")

    def test_has_required_fields(self):
        """Each result should have party, name, match_percentage."""
        answers = {"leyes_procrimen": -1}
        result = calculate_affinity(answers)
        for r in result:
            assert "party" in r
            assert "name" in r
            assert "match_percentage" in r

    def test_partial_answers_work(self):
        """Answering just a few questions should still produce results."""
        answers = {"aborto": -2}
        result = calculate_affinity(answers)
        assert len(result) == len(PARTY_POSITIONS)
        assert all(r["match_percentage"] >= 0 for r in result)


class TestGetQuizQuestions:
    def test_returns_15_questions(self):
        questions = get_quiz_questions()
        assert len(questions) == 15

    def test_question_format(self):
        questions = get_quiz_questions()
        for q in questions:
            assert "id" in q
            assert "question" in q
            assert "category" in q
            assert "options" in q
            assert len(q["options"]) == 4

    def test_each_option_has_text_and_value(self):
        questions = get_quiz_questions()
        for q in questions:
            for opt in q["options"]:
                assert "text" in opt
                assert "value" in opt
                assert -2 <= opt["value"] <= 2

    def test_categories_are_valid(self):
        valid = {"seguridad", "economia", "social", "politica", "corrupcion", "identidad"}
        questions = get_quiz_questions()
        for q in questions:
            assert q["category"] in valid

    def test_does_not_expose_party_positions(self):
        """API should not leak party position data."""
        questions = get_quiz_questions()
        for q in questions:
            assert "mapping" not in q


class TestPartyPositions:
    def test_all_parties_have_all_questions(self):
        """Every party should have a position on every question."""
        question_ids = {q["id"] for q in QUIZ_QUESTIONS}
        for party, positions in PARTY_POSITIONS.items():
            assert set(positions.keys()) == question_ids, f"{party} missing questions"

    def test_position_values_in_range(self):
        """All positions should be between -2 and 2."""
        for party, positions in PARTY_POSITIONS.items():
            for q_id, value in positions.items():
                assert -2 <= value <= 2, f"{party}.{q_id} = {value} out of range"
