"""Tests for the CLI layer."""

from pathlib import Path

import pytest

from sso_tracker.cli import main
from sso_tracker.repository import ProgressRepository


@pytest.fixture
def save_file(tmp_path: Path) -> Path:
    return tmp_path / "progress.json"


def run(*args, save_file: Path) -> int:
    return main(["--save-file", str(save_file), *args])


class TestStatusCommand:
    def test_status_empty(self, save_file, capsys):
        rc = run("status", save_file=save_file)
        assert rc == 0
        out = capsys.readouterr().out
        assert "22,000" in out

    def test_default_command_is_status(self, save_file, capsys):
        rc = run(save_file=save_file)
        assert rc == 0


class TestInitCommand:
    def test_init_neutral(self, save_file):
        run("init", "neutral", "1089", save_file=save_file)
        p = ProgressRepository(save_file).load()
        assert p.initial_reputation == 1089  # cumulative

    def test_init_revered(self, save_file):
        # Revered 4500 → cumulative 19500
        run("init", "revered", "4500", save_file=save_file)
        p = ProgressRepository(save_file).load()
        assert p.initial_reputation == 19_500

    def test_init_shows_rank_in_output(self, save_file, capsys):
        run("init", "neutral", "1089", save_file=save_file)
        out = capsys.readouterr().out
        assert "Neutral" in out
        assert "1,089" in out

    def test_init_clears_prior_runs(self, save_file):
        run("init", "neutral", "500", save_file=save_file)
        run("add", "neutral", "800", save_file=save_file)
        # Re-init should clear runs
        run("init", "neutral", "500", save_file=save_file)
        p = ProgressRepository(save_file).load()
        assert p.run_count == 0

    def test_init_invalid_rank_exits(self, save_file):
        with pytest.raises(SystemExit):
            run("init", "legendary", "100", save_file=save_file)

    def test_init_value_over_cap_exits(self, save_file):
        with pytest.raises(SystemExit):
            run("init", "neutral", "9999", save_file=save_file)


class TestAddCommand:
    def test_add_records_delta(self, save_file):
        run("init", "neutral", "1000", save_file=save_file)
        run("add", "neutral", "1300", save_file=save_file)
        p = ProgressRepository(save_file).load()
        assert p.run_count == 1
        assert p.runs[0].reputation == 300

    def test_add_across_bracket_boundary(self, save_file):
        # Start at Neutral 2900 (cumulative 2900)
        run("init", "neutral", "2900", save_file=save_file)
        # After run: Friendly 100 (cumulative 3100) → delta = 200
        run("add", "friendly", "100", save_file=save_file)
        p = ProgressRepository(save_file).load()
        assert p.runs[0].reputation == 200

    def test_add_multiple_runs_accumulate(self, save_file):
        run("init", "neutral", "0", save_file=save_file)
        run("add", "neutral", "300", save_file=save_file)
        run("add", "neutral", "550", save_file=save_file)
        p = ProgressRepository(save_file).load()
        assert p.run_count == 2
        assert p.reputation_from_runs == 550

    def test_add_same_or_lower_value_exits(self, save_file):
        run("init", "neutral", "1000", save_file=save_file)
        with pytest.raises(SystemExit):
            run("add", "neutral", "1000", save_file=save_file)

    def test_add_shows_run_number(self, save_file, capsys):
        run("init", "neutral", "0", save_file=save_file)
        run("add", "neutral", "300", save_file=save_file)
        out = capsys.readouterr().out
        assert "Run #1" in out

    def test_add_shows_delta(self, save_file, capsys):
        run("init", "neutral", "1000", save_file=save_file)
        run("add", "neutral", "1250", save_file=save_file)
        out = capsys.readouterr().out
        assert "+250" in out

    def test_short_codes_accepted(self, save_file):
        run("init", "n", "0", save_file=save_file)
        run("add", "n", "300", save_file=save_file)
        run("add", "f", "100", save_file=save_file)   # cross bracket
        p = ProgressRepository(save_file).load()
        assert p.run_count == 2
        assert p.total_reputation_gained == 3100  # friendly 100 = cumulative 3100


class TestResetCommand:
    def test_reset_clears_all(self, save_file):
        run("init", "revered", "4500", save_file=save_file)
        run("add", "revered", "4800", save_file=save_file)
        run("reset", save_file=save_file)
        p = ProgressRepository(save_file).load()
        assert p.initial_reputation == 0
        assert p.run_count == 0
