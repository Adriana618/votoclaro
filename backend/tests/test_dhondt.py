"""Comprehensive tests for D'Hondt method with known results."""

import pytest

from app.services.dhondt import dhondt_method, calculate_anti_vote


class TestDHondtMethod:
    """Tests for the standard D'Hondt seat allocation."""

    def test_basic_allocation(self):
        """Classic D'Hondt example: 3 parties, 7 seats."""
        votes = {"A": 100_000, "B": 80_000, "C": 30_000}
        result = dhondt_method(votes, 7)
        assert result == {"A": 3, "B": 3, "C": 1}

    def test_single_party(self):
        """Single party gets all seats."""
        votes = {"A": 50_000}
        result = dhondt_method(votes, 5)
        assert result == {"A": 5}

    def test_two_parties_equal(self):
        """Two parties with equal votes: tie-break alphabetically."""
        votes = {"A": 10_000, "B": 10_000}
        result = dhondt_method(votes, 4)
        # Each gets 2 seats
        assert result == {"A": 2, "B": 2}

    def test_small_party_gets_no_seats(self):
        """Very small party might not get any seats."""
        votes = {"A": 100_000, "B": 50_000, "C": 1_000}
        result = dhondt_method(votes, 3)
        # C's highest quotient (1000/1=1000) is less than A's 3rd (100000/3=33333)
        assert result["C"] == 0
        assert sum(result.values()) == 3

    def test_zero_seats(self):
        """Zero seats returns all zeros."""
        votes = {"A": 10_000, "B": 5_000}
        result = dhondt_method(votes, 0)
        assert result == {"A": 0, "B": 0}

    def test_zero_votes_party_excluded(self):
        """Party with zero votes gets no seats."""
        votes = {"A": 10_000, "B": 0, "C": 5_000}
        result = dhondt_method(votes, 3)
        assert result["B"] == 0
        assert result["A"] + result["C"] == 3

    def test_known_peru_example(self):
        """Realistic Peru scenario: Lima with 36 seats."""
        votes = {
            "rp": 12_000,
            "fp": 15_000,
            "pm": 5_000,
            "ap": 8_000,
            "app": 10_000,
            "pl": 6_000,
            "avp": 5_000,
        }
        result = dhondt_method(votes, 36)
        # Total seats allocated must equal 36
        assert sum(result.values()) == 36
        # Largest party should get most seats
        assert result["fp"] >= result["rp"] >= result["app"]

    def test_one_seat(self):
        """Single seat goes to the largest party."""
        votes = {"A": 500, "B": 300, "C": 200}
        result = dhondt_method(votes, 1)
        assert result == {"A": 1, "B": 0, "C": 0}

    def test_many_parties_few_seats(self):
        """More parties than seats: only top parties get seats."""
        votes = {chr(65 + i): (10 - i) * 1000 for i in range(10)}
        result = dhondt_method(votes, 3)
        assert sum(result.values()) == 3
        # Only the top few should have seats
        parties_with_seats = [p for p, s in result.items() if s > 0]
        assert len(parties_with_seats) <= 3

    def test_proportionality(self):
        """With many seats, allocation approaches proportional."""
        votes = {"A": 60_000, "B": 30_000, "C": 10_000}
        result = dhondt_method(votes, 100)
        # A should get ~60, B ~30, C ~10 (D'Hondt favors larger)
        assert 58 <= result["A"] <= 62
        assert 28 <= result["B"] <= 32
        assert 8 <= result["C"] <= 12

    def test_empty_votes(self):
        """No votes returns empty allocation."""
        result = dhondt_method({}, 5)
        assert result == {}

    def test_all_zero_votes(self):
        """All parties with zero votes."""
        votes = {"A": 0, "B": 0}
        result = dhondt_method(votes, 3)
        assert result == {"A": 0, "B": 0}


class TestCalculateAntiVote:
    """Tests for the anti-vote strategic calculator."""

    def test_basic_anti_vote(self):
        """Rejecting largest party should shift seats away from it."""
        votes = {"A": 10_000, "B": 8_000, "C": 5_000}
        recommended, original, strategy = calculate_anti_vote(
            votes, rejected_parties=["A"], seats=5
        )
        # Should recommend a non-A party
        assert recommended != "A"
        assert recommended in ("B", "C")

    def test_anti_vote_all_rejected(self):
        """If all parties are rejected, returns empty recommendation."""
        votes = {"A": 10_000, "B": 8_000}
        recommended, _, _ = calculate_anti_vote(
            votes, rejected_parties=["A", "B"], seats=5
        )
        assert recommended == ""

    def test_anti_vote_single_non_rejected(self):
        """If only one party is not rejected, it must be recommended."""
        votes = {"A": 10_000, "B": 8_000, "C": 5_000}
        recommended, _, _ = calculate_anti_vote(
            votes, rejected_parties=["A", "B"], seats=5
        )
        assert recommended == "C"

    def test_anti_vote_preserves_total_seats(self):
        """Strategy allocation should still fill all seats."""
        votes = {"A": 10_000, "B": 8_000, "C": 5_000, "D": 3_000}
        _, original, strategy = calculate_anti_vote(
            votes, rejected_parties=["A"], seats=5
        )
        assert sum(original.values()) == 5
        assert sum(strategy.values()) == 5

    def test_anti_vote_reduces_or_maintains_rejected_seats(self):
        """Strategy should not increase seats for rejected parties."""
        votes = {"A": 15_000, "B": 10_000, "C": 5_000, "D": 3_000}
        _, original, strategy = calculate_anti_vote(
            votes, rejected_parties=["A"], seats=7
        )
        rejected_before = original.get("A", 0)
        rejected_after = strategy.get("A", 0)
        assert rejected_after <= rejected_before

    def test_anti_vote_multiple_rejected(self):
        """Rejecting multiple parties."""
        votes = {"A": 15_000, "B": 10_000, "C": 5_000, "D": 3_000}
        recommended, original, strategy = calculate_anti_vote(
            votes, rejected_parties=["A", "B"], seats=7
        )
        assert recommended in ("C", "D")
        rejected_before = original.get("A", 0) + original.get("B", 0)
        rejected_after = strategy.get("A", 0) + strategy.get("B", 0)
        assert rejected_after <= rejected_before

    def test_anti_vote_edge_one_seat(self):
        """With 1 seat, only the largest party gets it."""
        votes = {"A": 10_000, "B": 8_000, "C": 5_000}
        recommended, original, strategy = calculate_anti_vote(
            votes, rejected_parties=["A"], seats=1
        )
        assert original["A"] == 1
        # Strategy should recommend B or C
        assert recommended in ("B", "C")
