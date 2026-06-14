"""Domain model for the Shattered Sun Offensive reputation tracker."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from sso_tracker.reputation import EXALTED_TOTAL


@dataclass
class Run:
    """A single Magisters' Terrace run with the reputation gained."""

    reputation: int  # delta gained this run (always positive)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Progress:
    """All tracked data for the grind.

    ``initial_reputation`` is a cumulative value (0–22,000) derived from
    whatever WoW was showing when the user first ran ``sso init``.
    """

    initial_reputation: int = 0  # cumulative
    runs: list[Run] = field(default_factory=list)

    # ------------------------------------------------------------------ #
    # Derived properties                                                   #
    # ------------------------------------------------------------------ #

    @property
    def run_count(self) -> int:
        return len(self.runs)

    @property
    def reputation_from_runs(self) -> int:
        return sum(r.reputation for r in self.runs)

    @property
    def total_reputation_gained(self) -> int:
        return self.initial_reputation + self.reputation_from_runs

    @property
    def remaining_reputation(self) -> int:
        return max(0, EXALTED_TOTAL - self.total_reputation_gained)

    @property
    def percentage_complete(self) -> float:
        return min(100.0, self.total_reputation_gained / EXALTED_TOTAL * 100)

    @property
    def average_reputation_per_run(self) -> float:
        if not self.runs:
            return 0.0
        return self.reputation_from_runs / self.run_count

    @property
    def estimated_runs_remaining(self) -> float:
        if self.remaining_reputation == 0:
            return 0.0
        avg = self.average_reputation_per_run
        if avg <= 0:
            return float("inf")
        return self.remaining_reputation / avg

    @property
    def is_complete(self) -> bool:
        return self.total_reputation_gained >= EXALTED_TOTAL
