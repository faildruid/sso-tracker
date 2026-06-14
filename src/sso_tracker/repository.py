"""Persistence layer — saves and loads Progress as JSON."""

from __future__ import annotations

import json
from pathlib import Path

from sso_tracker.domain import Progress, Run

DEFAULT_SAVE_PATH = Path.home() / ".sso_tracker" / "progress.json"


class ProgressRepository:
    """Reads and writes Progress to a local JSON file."""

    def __init__(self, path: Path = DEFAULT_SAVE_PATH) -> None:
        self.path = path

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def load(self) -> Progress:
        """Return saved Progress, or a fresh one if none exists."""
        if not self.path.exists():
            return Progress()
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return self._deserialize(data)

    def save(self, progress: Progress) -> None:
        """Persist Progress to disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self._serialize(progress), indent=2),
            encoding="utf-8",
        )

    def reset(self) -> None:
        """Delete saved data."""
        if self.path.exists():
            self.path.unlink()

    # ------------------------------------------------------------------ #
    # (De)serialisation helpers                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _serialize(progress: Progress) -> dict:
        return {
            "initial_reputation": progress.initial_reputation,
            "runs": [
                {"reputation": r.reputation, "timestamp": r.timestamp}
                for r in progress.runs
            ],
        }

    @staticmethod
    def _deserialize(data: dict) -> Progress:
        runs = [
            Run(reputation=r["reputation"], timestamp=r["timestamp"])
            for r in data.get("runs", [])
        ]
        return Progress(
            initial_reputation=data.get("initial_reputation", 0),
            runs=runs,
        )
