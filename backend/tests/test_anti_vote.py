"""Tests for the anti-vote strategy service layer."""

import pytest

from app.services.anti_vote import (
    compute_anti_vote_strategy,
    get_region_by_slug,
    percentages_to_votes,
)


class TestHelpers:
    def test_get_region_by_slug_found(self):
        region = get_region_by_slug("lima")
        assert region is not None
        assert region["name"] == "Lima Metropolitana"
        assert region["seats_diputados"] == 36

    def test_get_region_by_slug_not_found(self):
        assert get_region_by_slug("atlantis") is None

    def test_percentages_to_votes(self):
        pcts = {"A": 50.0, "B": 30.0, "C": 20.0}
        votes = percentages_to_votes(pcts, electorate=10_000)
        assert votes == {"A": 5000, "B": 3000, "C": 2000}


class TestComputeAntiVoteStrategy:
    def test_lima_basic(self):
        """Test anti-vote computation for Lima."""
        result = compute_anti_vote_strategy(
            region_slug="lima",
            rejected_parties=["fp", "rp"],
        )
        assert result["recommended_party"] != ""
        assert result["recommended_party"] not in ("fp", "rp")
        assert result["seats_saved"] >= 0
        assert len(result["seat_allocation_without_strategy"]) > 0

    def test_small_region(self):
        """Test with a small region (few seats)."""
        result = compute_anti_vote_strategy(
            region_slug="madre-de-dios",
            rejected_parties=["fp"],
        )
        assert result["recommended_party"] != ""
        assert result["recommended_party"] != "fp"

    def test_invalid_region(self):
        """Test with invalid region slug raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            compute_anti_vote_strategy(
                region_slug="narnia",
                rejected_parties=["fp"],
            )

    def test_custom_votes(self):
        """Test with custom vote distribution."""
        custom = {"fp": 50_000, "rp": 30_000, "pm": 20_000}
        result = compute_anti_vote_strategy(
            region_slug="arequipa",
            rejected_parties=["fp"],
            custom_votes=custom,
        )
        assert result["recommended_party"] in ("rp", "pm")
        assert result["seats_saved"] >= 0

    def test_explanation_contains_region(self):
        """Explanation should mention the region name."""
        result = compute_anti_vote_strategy(
            region_slug="cusco",
            rejected_parties=["pl"],
        )
        assert "Cusco" in result["explanation"]
