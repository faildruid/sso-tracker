"""Tests for the repository / storage layer."""

import json
import tempfile
from pathlib import Path

import pytest

from sso_tracker.domain import Progress, Run
from sso_tracker.repository import ProgressRepository


@pytest.fixture
def tmp_repo(tmp_path: Path) -> ProgressRepository:
    return ProgressRepository(path=tmp_path / "progress.json")


class TestRepositoryLoad:
    def test_load_missing_file_returns_empty(self, tmp_repo):
        p = tmp_repo.load()
        assert p.initial_reputation == 0
        assert p.runs == []

    def test_load_after_save(self, tmp_repo):
        original = Progress(
            initial_reputation=5_000,
            runs=[Run(reputation=300, timestamp="2024-01-01T00:00:00")],
        )
        tmp_repo.save(original)
        loaded = tmp_repo.load()
        assert loaded.initial_reputation == 5_000
        assert len(loaded.runs) == 1
        assert loaded.runs[0].reputation == 300
        assert loaded.runs[0].timestamp == "2024-01-01T00:00:00"


class TestRepositorySave:
    def test_creates_parent_dirs(self, tmp_path):
        deep_path = tmp_path / "a" / "b" / "c" / "progress.json"
        repo = ProgressRepository(path=deep_path)
        repo.save(Progress())
        assert deep_path.exists()

    def test_json_structure(self, tmp_repo):
        p = Progress(initial_reputation=1_000, runs=[Run(reputation=250)])
        tmp_repo.save(p)
        raw = json.loads(tmp_repo.path.read_text())
        assert raw["initial_reputation"] == 1_000
        assert len(raw["runs"]) == 1
        assert raw["runs"][0]["reputation"] == 250

    def test_overwrites_previous_save(self, tmp_repo):
        tmp_repo.save(Progress(initial_reputation=100))
        tmp_repo.save(Progress(initial_reputation=999))
        loaded = tmp_repo.load()
        assert loaded.initial_reputation == 999


class TestRepositoryReset:
    def test_reset_deletes_file(self, tmp_repo):
        tmp_repo.save(Progress())
        assert tmp_repo.path.exists()
        tmp_repo.reset()
        assert not tmp_repo.path.exists()

    def test_reset_no_file_is_safe(self, tmp_repo):
        # Should not raise even when file doesn't exist
        tmp_repo.reset()
