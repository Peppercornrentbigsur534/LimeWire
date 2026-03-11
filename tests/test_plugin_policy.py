"""Tests for limewire.security.plugin_policy — hash trust, scan without execute."""

import hashlib
import os

import pytest

from limewire.security.plugin_policy import (
    PluginScan,
    PluginTrustError,
    load_trusted_plugin,
    scan_plugins,
    sha256_file,
)


def _write_plugin(path, code="x = 1\n"):
    # Write in binary to avoid Windows \r\n line ending mismatch
    data = code.encode()
    with open(path, "wb") as f:
        f.write(data)
    return hashlib.sha256(data).hexdigest()


class TestSha256File:
    def test_consistent_hash(self, tmp_path):
        p = str(tmp_path / "file.txt")
        with open(p, "w") as f:
            f.write("hello world")
        h1 = sha256_file(p)
        h2 = sha256_file(p)
        assert h1 == h2
        assert len(h1) == 64  # hex digest length

    def test_different_content_different_hash(self, tmp_path):
        p1 = str(tmp_path / "a.txt")
        p2 = str(tmp_path / "b.txt")
        with open(p1, "w") as f:
            f.write("content A")
        with open(p2, "w") as f:
            f.write("content B")
        assert sha256_file(p1) != sha256_file(p2)

    def test_matches_known_hash(self, tmp_path):
        p = str(tmp_path / "known.txt")
        content = b"test data"
        with open(p, "wb") as f:
            f.write(content)
        expected = hashlib.sha256(content).hexdigest()
        assert sha256_file(p) == expected


class TestScanPlugins:
    def test_discovers_py_files(self, tmp_path):
        _write_plugin(str(tmp_path / "plugin_a.py"), "a = 1\n")
        _write_plugin(str(tmp_path / "plugin_b.py"), "b = 2\n")
        results = scan_plugins(str(tmp_path), set())
        assert len(results) == 2
        names = {r.filename for r in results}
        assert "plugin_a.py" in names
        assert "plugin_b.py" in names

    def test_ignores_underscore_prefix(self, tmp_path):
        _write_plugin(str(tmp_path / "_private.py"))
        _write_plugin(str(tmp_path / "__init__.py"))
        _write_plugin(str(tmp_path / "visible.py"))
        results = scan_plugins(str(tmp_path), set())
        assert len(results) == 1
        assert results[0].filename == "visible.py"

    def test_ignores_non_py_files(self, tmp_path):
        with open(str(tmp_path / "readme.txt"), "w") as f:
            f.write("not a plugin")
        _write_plugin(str(tmp_path / "plugin.py"))
        results = scan_plugins(str(tmp_path), set())
        assert len(results) == 1

    def test_trusted_flag_set_correctly(self, tmp_path):
        h = _write_plugin(str(tmp_path / "trusted.py"), "code = True\n")
        _write_plugin(str(tmp_path / "untrusted.py"), "code = False\n")
        results = scan_plugins(str(tmp_path), {h})
        trusted = [r for r in results if r.trusted]
        untrusted = [r for r in results if not r.trusted]
        assert len(trusted) == 1
        assert trusted[0].filename == "trusted.py"
        assert len(untrusted) == 1

    def test_creates_missing_directory(self, tmp_path):
        new_dir = str(tmp_path / "plugins")
        assert not os.path.exists(new_dir)
        results = scan_plugins(new_dir, set())
        assert os.path.isdir(new_dir)
        assert results == []

    def test_scan_contains_size(self, tmp_path):
        code = "x = 42\n"
        _write_plugin(str(tmp_path / "sized.py"), code)
        results = scan_plugins(str(tmp_path), set())
        assert results[0].size_bytes == len(code.encode())

    def test_sorted_results(self, tmp_path):
        _write_plugin(str(tmp_path / "z_last.py"), "z = 1\n")
        _write_plugin(str(tmp_path / "a_first.py"), "a = 1\n")
        results = scan_plugins(str(tmp_path), set())
        assert results[0].filename == "a_first.py"
        assert results[1].filename == "z_last.py"


class TestLoadTrustedPlugin:
    def test_loads_matching_hash(self, tmp_path):
        code = "plugin_value = 42\n"
        p = str(tmp_path / "good.py")
        h = _write_plugin(p, code)
        mod = load_trusted_plugin(p, h)
        assert mod.plugin_value == 42

    def test_rejects_hash_mismatch(self, tmp_path):
        p = str(tmp_path / "bad.py")
        _write_plugin(p, "x = 1\n")
        with pytest.raises(PluginTrustError, match="hash mismatch"):
            load_trusted_plugin(p, "0" * 64)

    def test_rejects_modified_file(self, tmp_path):
        code = "original = True\n"
        p = str(tmp_path / "modified.py")
        h = _write_plugin(p, code)
        # Modify file after hashing
        with open(p, "w") as f:
            f.write("modified = True\nhacked = True\n")
        with pytest.raises(PluginTrustError, match="hash mismatch"):
            load_trusted_plugin(p, h)

    def test_module_name_prefix(self, tmp_path):
        p = str(tmp_path / "my_plugin.py")
        h = _write_plugin(p, "name = 'test'\n")
        mod = load_trusted_plugin(p, h)
        assert mod.__name__ == "limewire_plugin_my_plugin"
