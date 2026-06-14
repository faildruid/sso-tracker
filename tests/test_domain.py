"""Tests for the domain model."""

import pytest

from sso_tracker.domain import Progress, Run
from sso_tracker.reputation import EXALTED_TOTAL


def make_progress(initial: int = 0, reps: list[int] | None = None) -> Progress:
    runs = [Run(reputation=r) for r in (reps or [])]
    return Progress(initial_reputation=initial, runs=runs)


class TestProgressDefaults:
    def test_empty_progress(self):
        p = Progress()
        assert p.initial_reputation == 0
        assert p.run_count == 0
        assert p.reputation_from_runs == 0
        assert p.total_reputation_gained == 0
        assert p.remaining_reputation == EXALTED_TOTAL
        assert p.percentage_complete == 0.0
        assert p.average_reputation_per_run == 0.0
        assert p.estimated_runs_remaining == float("inf")
        assert not p.is_complete


class TestProgressWithInitial:
    def test_neutral_start(self):
        # Neutral 1089 → cumulative 1089
        p = make_progress(initial=1089)
        assert p.total_reputation_gained == 1089
        assert p.remaining_reputation == EXALTED_TOTAL - 1089
        assert round(p.percentage_complete, 4) == round(1089 / EXALTED_TOTAL * 100, 4)

    def test_revered_start(self):
        # Revered 4500 → cumulative 19500
        p = make_progress(initial=19_500)
        assert p.total_reputation_gained == 19_500
        assert p.remaining_reputation == EXALTED_TOTAL - 19_500


class TestProgressWithRuns:
    def test_single_run(self):
        p = make_progress(initial=1089, reps=[300])
        assert p.run_count == 1
        assert p.reputation_from_runs == 300
        assert p.total_reputation_gained == 1389
        assert p.average_reputation_per_run == 300.0

    def test_multiple_runs(self):
        p = make_progress(initial=1000, reps=[200, 400, 300])
        assert p.run_count == 3
        assert p.reputation_from_runs == 900
        assert p.average_reputation_per_run == 300.0

    def test_estimated_runs_remaining(self):
        p = make_progress(initial=0, reps=[500, 500])
        expected = (EXALTED_TOTAL - 1000) / 500
        assert p.estimated_runs_remaining == pytest.approx(expected)


class TestCompletion:
    def test_exactly_complete(self):
        p = make_progress(initial=EXALTED_TOTAL)
        assert p.is_complete
        assert p.remaining_reputation == 0
        assert p.percentage_complete == 100.0
        assert p.estimated_runs_remaining == 0.0

    def test_over_threshold_clamps(self):
        p = make_progress(initial=EXALTED_TOTAL + 500)
        assert p.remaining_reputation == 0
        assert p.percentage_complete == 100.0

    def test_runs_push_to_complete(self):
        p = make_progress(initial=EXALTED_TOTAL - 300, reps=[300])
        assert p.is_complete
