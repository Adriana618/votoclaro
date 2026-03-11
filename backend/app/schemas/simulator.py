"""Simulator schemas for anti-vote and D'Hondt calculations."""

from pydantic import BaseModel


class AntiVoteRequest(BaseModel):
    region_slug: str
    rejected_parties: list[str]  # list of party abbreviations to reject
    custom_votes: dict[str, int] | None = None  # optional override for poll data


class SeatAllocation(BaseModel):
    party: str
    seats: int


class AntiVoteResult(BaseModel):
    recommended_party: str
    recommended_party_name: str
    explanation: str
    seat_allocation_without_strategy: list[SeatAllocation]
    seat_allocation_with_strategy: list[SeatAllocation]
    rejected_seats_before: int
    rejected_seats_after: int
    seats_saved: int


class DHondtRequest(BaseModel):
    votes: dict[str, int]
    seats: int


class DHondtResult(BaseModel):
    allocation: dict[str, int]
