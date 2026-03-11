"""Tests for limewire.core.config — load_json, save_json, file paths."""

import json
import os

import pytest

from limewire.core.config import (
    ANALYSIS_CACHE_FILE,
    HISTORY_FILE,
    QUEUE_FILE,
    SCHEDULE_FILE,
    SESSION_FILE,
    SETTINGS_FILE,
    load_json,
    save_json,
)


class TestConfigPaths:
    def test_all_paths_are_absolute(self):
        for path in [HISTORY_FILE, SCHEDULE_FILE, SETTINGS_FILE,
                     QUEUE_FILE, ANALYSIS_CACHE_FILE, SESSION_FILE]:
            assert os.path.isabs(path), f"{path} is not absolute"

    def test_all_paths_use_limewire_prefix(self):
        for path in [HISTORY_FILE, SCHEDULE_FILE, SETTINGS_FILE,
                     QUEUE_FILE, ANALYSIS_CACHE_FILE, SESSION_FILE]:
            basename = os.path.basename(path)
            assert basename.startswith(".limewire_"), f"{basename} missing .limewire_ prefix"

    def test_all_paths_are_json(self):
        for path in [HISTORY_FILE, SCHEDULE_FILE, SETTINGS_FILE,
                     QUEUE_FILE, ANALYSIS_CACHE_FILE, SESSION_FILE]:
            assert path.endswith(".json"), f"{path} should be .json"


class TestLoadJson:
    def test_loads_valid_json(self, tmp_path):
        p = str(tmp_path / "test.json")
        with open(p, "w") as f:
            json.dump({"key": "value"}, f)
        assert load_json(p, {}) == {"key": "value"}

    def test_returns_default_on_missing_file(self, tmp_path):
        p = str(tmp_path / "nonexistent.json")
        assert load_json(p, [1, 2, 3]) == [1, 2, 3]

    def test_returns_default_on_corrupt_json(self, tmp_path):
        p = str(tmp_path / "corrupt.json")
        with open(p, "w") as f:
            f.write("not json {{{")
        assert load_json(p, "fallback") == "fallback"

    def test_loads_list(self, tmp_path):
        p = str(tmp_path / "list.json")
        with open(p, "w") as f:
            json.dump([1, 2, 3], f)
        assert load_json(p, []) == [1, 2, 3]

    def test_loads_empty_dict(self, tmp_path):
        p = str(tmp_path / "empty.json")
        with open(p, "w") as f:
            json.dump({}, f)
        assert load_json(p, {"default": True}) == {}


class TestSaveJson:
    def test_saves_and_reads_back(self, tmp_path):
        p = str(tmp_path / "out.json")
        save_json(p, {"saved": True})
        with open(p) as f:
            assert json.load(f) == {"saved": True}

    def test_atomic_no_tmp_left(self, tmp_path):
        p = str(tmp_path / "clean.json")
        save_json(p, [1, 2])
        assert not os.path.exists(p + ".tmp")

    def test_overwrites_existing(self, tmp_path):
        p = str(tmp_path / "overwrite.json")
        save_json(p, {"v": 1})
        save_json(p, {"v": 2})
        with open(p) as f:
            assert json.load(f) == {"v": 2}

    def test_saves_with_indent(self, tmp_path):
        p = str(tmp_path / "pretty.json")
        save_json(p, {"a": 1})
        content = open(p).read()
        assert "\n" in content  # indented output
