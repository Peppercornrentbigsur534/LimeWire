"""Tests for limewire.security.safe_json — size limits, key allowlists, depth checks."""

import json
import os

import pytest

from limewire.security.safe_paths import init_allowed_roots
from limewire.security.safe_json import (
    JsonPolicyError,
    _check_depth,
    load_validated,
    save_validated,
    validate_theme,
)


@pytest.fixture(autouse=True)
def allow_tmp_writes(tmp_path):
    """Allow writes to tmp_path for all tests in this module."""
    init_allowed_roots([str(tmp_path)])


class TestLoadValidated:
    def test_loads_valid_json(self, tmp_path):
        p = str(tmp_path / "data.json")
        with open(p, "w") as f:
            json.dump({"a": 1, "b": 2}, f)
        result = load_validated(p, {})
        assert result == {"a": 1, "b": 2}

    def test_returns_default_on_missing_file(self, tmp_path):
        p = str(tmp_path / "missing.json")
        result = load_validated(p, {"default": True})
        assert result == {"default": True}

    def test_returns_default_on_invalid_json(self, tmp_path):
        p = str(tmp_path / "bad.json")
        with open(p, "w") as f:
            f.write("{invalid json")
        result = load_validated(p, [])
        assert result == []

    def test_rejects_oversized_file(self, tmp_path):
        p = str(tmp_path / "big.json")
        data = {"data": "x" * 1000}
        with open(p, "w") as f:
            json.dump(data, f)
        result = load_validated(p, {}, max_bytes=100)
        assert result == {}

    def test_strips_unknown_keys(self, tmp_path):
        p = str(tmp_path / "extra.json")
        with open(p, "w") as f:
            json.dump({"allowed": 1, "forbidden": 2}, f)
        allowed = frozenset({"allowed"})
        result = load_validated(p, {}, allowed_keys=allowed)
        assert result == {"allowed": 1}
        assert "forbidden" not in result

    def test_rejects_deep_nesting(self, tmp_path):
        p = str(tmp_path / "deep.json")
        # Create nested structure 15 levels deep
        data = {"a": {"b": {"c": {"d": {"e": {"f": {"g": {"h": {"i": {"j": {"k": {"l": 1}}}}}}}}}}}}
        with open(p, "w") as f:
            json.dump(data, f)
        result = load_validated(p, "fallback", max_depth=5)
        assert result == "fallback"

    def test_allows_shallow_nesting(self, tmp_path):
        p = str(tmp_path / "shallow.json")
        data = {"a": {"b": 1}}
        with open(p, "w") as f:
            json.dump(data, f)
        result = load_validated(p, {}, max_depth=5)
        assert result == {"a": {"b": 1}}

    def test_loads_list(self, tmp_path):
        p = str(tmp_path / "list.json")
        with open(p, "w") as f:
            json.dump([1, 2, 3], f)
        result = load_validated(p, [])
        assert result == [1, 2, 3]


class TestSaveValidated:
    def test_saves_and_reads_back(self, tmp_path):
        p = str(tmp_path / "out.json")
        save_validated(p, {"key": "value"})
        with open(p) as f:
            data = json.load(f)
        assert data == {"key": "value"}

    def test_rejects_oversized_output(self, tmp_path):
        p = str(tmp_path / "toobig.json")
        with pytest.raises(JsonPolicyError, match="too large"):
            save_validated(p, {"data": "x" * 10000}, max_bytes=100)

    def test_creates_parent_dirs(self, tmp_path):
        p = str(tmp_path / "sub" / "dir" / "out.json")
        save_validated(p, [1, 2])
        assert os.path.exists(p)


class TestValidateTheme:
    KEYS = frozenset({"BG", "TEXT", "LIME", "BORDER_L"})

    def test_valid_theme(self):
        data = {"BG": "#080C12", "TEXT": "#E0F4FF"}
        result = validate_theme(data, self.KEYS)
        assert result == {"BG": "#080C12", "TEXT": "#E0F4FF"}

    def test_strips_unknown_keys(self):
        data = {"BG": "#000", "TEXT": "#FFF", "EVIL_KEY": "injected"}
        result = validate_theme(data, self.KEYS)
        assert "EVIL_KEY" not in result
        assert "BG" in result

    def test_rejects_non_dict(self):
        with pytest.raises(JsonPolicyError, match="JSON object"):
            validate_theme([], self.KEYS)

    def test_requires_bg_and_text(self):
        with pytest.raises(JsonPolicyError, match="BG and TEXT"):
            validate_theme({"LIME": "#00E5FF"}, self.KEYS)

    def test_validates_hex_color_length(self):
        data = {"BG": "#12345", "TEXT": "#FFF"}  # 5-char hex invalid
        result = validate_theme(data, self.KEYS)
        assert "BG" not in result  # stripped as invalid
        assert result["TEXT"] == "#FFF"

    def test_validates_hex_chars(self):
        data = {"BG": "#GGGGGG", "TEXT": "#FFF"}
        result = validate_theme(data, self.KEYS)
        assert "BG" not in result  # invalid hex chars

    def test_allows_3_6_8_char_hex(self):
        data = {"BG": "#FFF", "TEXT": "#AABBCC"}
        result = validate_theme(data, self.KEYS)
        assert result["BG"] == "#FFF"
        assert result["TEXT"] == "#AABBCC"

    def test_allows_8_char_hex_with_alpha(self):
        data = {"BG": "#AABBCCDD", "TEXT": "#FFF"}
        result = validate_theme(data, self.KEYS)
        assert result["BG"] == "#AABBCCDD"

    def test_non_color_values_pass_through(self):
        data = {"BG": "#000", "TEXT": "#FFF", "LIME": 42}
        result = validate_theme(data, self.KEYS)
        assert result["LIME"] == 42  # non-string passes through


class TestCheckDepth:
    def test_flat_dict(self):
        assert _check_depth({"a": 1}, 3) is True

    def test_flat_list(self):
        assert _check_depth([1, 2, 3], 3) is True

    def test_nested_within_limit(self):
        assert _check_depth({"a": {"b": 1}}, 3) is True

    def test_nested_exceeds_limit(self):
        data = {"a": {"b": {"c": {"d": 1}}}}
        assert _check_depth(data, 2) is False

    def test_scalar(self):
        assert _check_depth(42, 0) is True
        assert _check_depth("hello", 0) is True

    def test_empty_containers(self):
        assert _check_depth({}, 0) is True
        assert _check_depth([], 0) is True
