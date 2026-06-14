"""Rendering helpers — keep all terminal output here."""

from __future__ import annotations

from sso_tracker.domain import Progress
from sso_tracker.reputation import EXALTED_TOTAL, from_cumulative

# ANSI colour codes
_RESET = "\033[0m"
_BOLD = "\033[1m"
_GREEN = "\033[32m"
_CYAN = "\033[36m"
_YELLOW = "\033[33m"


def _bar(percentage: float, width: int = 30) -> str:
    filled = int(width * percentage / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {percentage:.1f}%"


def print_status(progress: Progress) -> None:
    """Print a full status report to stdout."""
    p = progress
    est = p.estimated_runs_remaining

    rank, within, cap = from_cumulative(p.total_reputation_gained)

    print()
    print(f"{_BOLD}{_CYAN}⚔  Shattered Sun Offensive — Rep Tracker{_RESET}")
    print("─" * 48)
    print(f"  Current standing     {rank} ({within:,} / {cap:,})")
    print(f"  Cumulative total     {p.total_reputation_gained:>10,} / {EXALTED_TOTAL:,}")
    print(f"  Remaining            {p.remaining_reputation:>10,}")
    print()
    print(f"  Run count            {p.run_count:>10}")

    if p.run_count:
        print(f"  Avg rep / run        {p.average_reputation_per_run:>10.1f}")
        if p.remaining_reputation > 0:
            print(f"  Est. runs left       {est:>10.1f}")
        else:
            print(f"  Est. runs left       {'—':>10}")

    print()
    colour = _GREEN if p.is_complete else _YELLOW
    print(f"  {colour}{_bar(p.percentage_complete)}{_RESET}")

    if p.is_complete:
        print(f"\n  {_GREEN}{_BOLD}🎉  Exalted! Grind complete.{_RESET}")

    print()


def print_run_added(delta: int, rank: str, value: int, progress: Progress) -> None:
    print(
        f"{_GREEN}+{delta:,} rep gained.{_RESET}  "
        f"Now {rank.title()} {value:,}.  "
        f"Run #{progress.run_count} recorded."
    )


def print_reset_done() -> None:
    print(f"{_YELLOW}Progress reset.{_RESET}")


def print_init_set(rank: str, value: int, cumulative: int) -> None:
    print(
        f"{_CYAN}Starting point set: {rank.title()} {value:,}  "
        f"(cumulative: {cumulative:,}).{_RESET}"
    )
