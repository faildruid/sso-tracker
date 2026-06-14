"""Tests for the reputation rank conversion utilities."""

import pytest

from sso_tracker.reputation import (
    EXALTED_TOTAL,
    from_cumulative,
    to_cumulative,
)


class TestToCumulative:
    def test_neutral_zero(self):
        assert to_cumulative("neutral", 0) == 0

    def test_neutral_mid(self):
        assert to_cumulative("neutral", 1089) == 1089

    def test_neutral_max(self):
        assert to_cumulative("neutral", 3000) == 3000

    def test_friendly_zero(self):
        assert to_cumulative("friendly", 0) == 3000

    def test_friendly_mid(self):
        assert to_cumulative("friendly", 500) == 3500

    def test_honored_zero(self):
        assert to_cumulative("honored", 0) == 9000

    def test_revered_zero(self):
        assert to_cumulative("revered", 0) == 15000

    def test_revered_mid(self):
        assert to_cumulative("revered", 4500) == 19500

    def test_exalted_zero(self):
        assert to_cumulative("exalted", 0) == 21000

    def test_exalted_max(self):
        assert to_cumulative("exalted", 1000) == 22000

    def test_case_insensitive(self):
        assert to_cumulative("Neutral", 100) == to_cumulative("neutral", 100)
        assert to_cumulative("REVERED", 0) == to_cumulative("revered", 0)

    def test_short_code_n(self):
        assert to_cumulative("n", 1089) == to_cumulative("neutral", 1089)

    def test_short_code_f(self):
        assert to_cumulative("f", 500) == to_cumulative("friendly", 500)

    def test_short_code_h(self):
        assert to_cumulative("h", 0) == to_cumulative("honored", 0)

    def test_short_code_r(self):
        assert to_cumulative("r", 4500) == to_cumulative("revered", 4500)

    def test_short_code_e(self):
        assert to_cumulative("e", 500) == to_cumulative("exalted", 500)

    def test_short_code_uppercase_ignored(self):
        # short codes are lowercased before lookup, so "N" → "n" → "neutral"
        assert to_cumulative("N", 0) == to_cumulative("neutral", 0)

    def test_unknown_rank_raises(self):
        with pytest.raises(ValueError, match="Unknown rank"):
            to_cumulative("legendary", 100)

    def test_value_over_cap_raises(self):
        with pytest.raises(ValueError, match="between 0 and"):
            to_cumulative("neutral", 3001)

    def test_negative_value_raises(self):
        with pytest.raises(ValueError, match="between 0 and"):
            to_cumulative("neutral", -1)


class TestFromCumulative:
    def test_zero(self):
        rank, within, cap = from_cumulative(0)
        assert rank == "Neutral"
        assert within == 0
        assert cap == 3000

    def test_mid_neutral(self):
        rank, within, cap = from_cumulative(1089)
        assert rank == "Neutral"
        assert within == 1089

    def test_start_of_friendly(self):
        rank, within, cap = from_cumulative(3000)
        assert rank == "Friendly"
        assert within == 0

    def test_mid_revered(self):
        rank, within, cap = from_cumulative(19500)
        assert rank == "Revered"
        assert within == 4500
        assert cap == 9000

    def test_exalted(self):
        rank, within, cap = from_cumulative(EXALTED_TOTAL)
        assert rank == "Exalted"

    def test_roundtrip(self):
        """to_cumulative → from_cumulative should recover original values."""
        cases = [
            ("neutral", 1089),
            ("friendly", 2500),
            ("honored", 0),
            ("revered", 4500),
            ("exalted", 500),
        ]
        for rank, value in cases:
            total = to_cumulative(rank, value)
            out_rank, out_value, _ = from_cumulative(total)
            assert out_rank.lower() == rank
            assert out_value == value
