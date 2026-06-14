"""Reputation rank table and conversion utilities.

WoW reports reputation as `<rank> <current> / <rank_cap>`.
We store everything as a single cumulative value (0–22,000).

Bracket table (as shown in-game):
  Neutral   0 – 3,000    cumulative base:  0
  Friendly  0 – 6,000    cumulative base:  3,000
  Honored   0 – 6,000    cumulative base:  9,000
  Revered   0 – 9,000    cumulative base: 15,000
  Exalted   0 – 1,000    cumulative base: 24,000  (complete)
"""

from __future__ import annotations

from dataclasses import dataclass


EXALTED_TOTAL = 22_000  # cumulative rep at the start of Exalted


@dataclass(frozen=True)
class Bracket:
    name: str
    size: int           # points within the bracket
    cumulative_base: int  # cumulative rep at the START of this bracket


# Ordered lowest → highest
BRACKETS: list[Bracket] = [
    Bracket("neutral",  3_000, 0),
    Bracket("friendly", 6_000, 3_000),
    Bracket("honored",  6_000, 9_000),
    Bracket("revered",  9_000, 15_000),
    Bracket("exalted",  1_000, 21_000),
]

BRACKET_BY_NAME: dict[str, Bracket] = {b.name: b for b in BRACKETS}

# Single-letter short codes
SHORT_CODES: dict[str, str] = {
    "n": "neutral",
    "f": "friendly",
    "h": "honored",
    "r": "revered",
    "e": "exalted",
}

VALID_RANKS = list(BRACKET_BY_NAME.keys())
VALID_RANK_INPUT = f"{', '.join(VALID_RANKS)} (or short codes: {', '.join(SHORT_CODES)})"


def _resolve_rank(rank: str) -> str:
    """Expand a short code or full name to a canonical lowercase rank name."""
    rank = rank.strip().lower()
    return SHORT_CODES.get(rank, rank)


def to_cumulative(rank: str, value: int) -> int:
    """Convert a WoW rep display (rank + within-bracket value) to cumulative.

    Accepts full rank names or single-letter short codes (n/f/h/r/e).

    Example: ("n", 1089)      → 1089
             ("friendly", 500) → 3500
             ("r", 0)          → 15000
    """
    rank = _resolve_rank(rank)
    bracket = BRACKET_BY_NAME.get(rank)
    if bracket is None:
        raise ValueError(
            f"Unknown rank {rank!r}. Valid: {VALID_RANK_INPUT}"
        )
    if not (0 <= value <= bracket.size):
        raise ValueError(
            f"{rank.title()} value must be between 0 and {bracket.size:,}, got {value}."
        )
    return bracket.cumulative_base + value


def from_cumulative(total: int) -> tuple[str, int, int]:
    """Return (rank_name, within_bracket_value, bracket_size) for a cumulative total."""
    total = max(0, min(total, EXALTED_TOTAL))
    for bracket in reversed(BRACKETS):
        if total >= bracket.cumulative_base:
            within = total - bracket.cumulative_base
            return bracket.name.title(), within, bracket.size
    # Fallback — shouldn't happen
    b = BRACKETS[0]
    return b.name.title(), total, b.size
