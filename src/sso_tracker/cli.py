"""CLI layer — parses arguments and wires domain + repository + display."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sso_tracker import __version__
from sso_tracker.display import (
    print_init_set,
    print_reset_done,
    print_run_added,
    print_status,
)
from sso_tracker.domain import Run
from sso_tracker.repository import DEFAULT_SAVE_PATH, ProgressRepository
from sso_tracker.reputation import SHORT_CODES, VALID_RANK_INPUT, VALID_RANKS, to_cumulative

# argparse choices: full names + short codes
_RANK_CHOICES = VALID_RANKS + list(SHORT_CODES.keys())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sso",
        description="Track your Shattered Sun Offensive reputation grind.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--save-file",
        type=Path,
        default=DEFAULT_SAVE_PATH,
        metavar="PATH",
        help="Override the save-file location.",
    )

    sub = parser.add_subparsers(dest="command", metavar="<command>")

    # status (default)
    sub.add_parser("status", help="Show current progress (default).")

    # init — takes what WoW shows you
    init_p = sub.add_parser(
        "init",
        help="Set your starting reputation exactly as WoW shows it.",
        description=(
            "Record your current reputation straight from the WoW UI.\n"
            "Example: sso init revered 4500  (WoW shows 'Revered 4500 / 9000')"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    init_p.add_argument(
        "rank",
        choices=_RANK_CHOICES,
        metavar="rank",
        help=f"Current rank as shown in WoW. {VALID_RANK_INPUT}",
    )
    init_p.add_argument(
        "value",
        type=int,
        help="Points within that rank, as shown in WoW (e.g. 1089).",
    )

    # add — record what WoW shows AFTER the run
    add_p = sub.add_parser(
        "add",
        help="Update reputation to what WoW shows after a run.",
        description=(
            "Enter your reputation exactly as WoW shows it after a run.\n"
            "The app calculates the delta automatically.\n"
            "Example: sso add revered 4800  (WoW now shows 'Revered 4800 / 9000')"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    add_p.add_argument(
        "rank",
        choices=_RANK_CHOICES,
        metavar="rank",
        help=f"Current rank after the run. {VALID_RANK_INPUT}",
    )
    add_p.add_argument(
        "value",
        type=int,
        help="Points within that rank after the run.",
    )

    # reset
    sub.add_parser("reset", help="Delete all saved progress.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    repo = ProgressRepository(path=args.save_file)
    command = args.command or "status"

    if command == "status":
        progress = repo.load()
        print_status(progress)

    elif command == "init":
        try:
            cumulative = to_cumulative(args.rank, args.value)
        except ValueError as exc:
            parser.error(str(exc))
            return 1

        progress = repo.load()
        progress.initial_reputation = cumulative
        progress.runs.clear()  # reset runs — new baseline
        repo.save(progress)
        print_init_set(args.rank, args.value, cumulative)
        print_status(progress)

    elif command == "add":
        try:
            new_cumulative = to_cumulative(args.rank, args.value)
        except ValueError as exc:
            parser.error(str(exc))
            return 1

        progress = repo.load()
        previous = progress.total_reputation_gained

        delta = new_cumulative - previous
        if delta <= 0:
            parser.error(
                f"New reputation ({new_cumulative:,}) is not higher than "
                f"current total ({previous:,}). "
                "Did you enter the right rank and value?"
            )
            return 1

        progress.runs.append(Run(reputation=delta))
        repo.save(progress)
        print_run_added(delta, args.rank, args.value, progress)
        print_status(progress)

    elif command == "reset":
        repo.reset()
        print_reset_done()

    else:
        parser.print_help()

    return 0


def entry_point() -> None:
    sys.exit(main())
