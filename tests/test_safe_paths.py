"""Tests for limewire.security.safe_paths — path traversal, sanitization, atomic writes."""

import os
import tempfile

import pytest

from limewire.security.safe_paths import (
    PathPolicyError,
    atomic_write,
    init_allowed_roots,
    is_under_root,
    require_allowed_write,
    require_under_root,
    resolve_path,
    safe_join,
    sanitize_filename,
)


class TestResolvePath:
    def test_expands_user_home(self):
        result = resolve_path("~/test")
        assert os.path.expanduser("~") in result

    def test_absolute_path_unchanged(self, tmp_dir):
        p = str(tmp_dir / "file.txt")
        assert resolve_path(p) == os.path.realpath(p)

    def test_resolves_relative(self):
        result = resolve_path(".")
        assert os.path.isabs(result)


class TestIsUnderRoot:
    def test_file_under_root(self, tmp_dir):
        root = str(tmp_dir)
        child = str(tmp_dir / "sub" / "file.txt")
        assert is_under_root(child, root) is True

    def test_root_equals_path(self, tmp_dir):
        root = str(tmp_dir)
        assert is_under_root(root, root) is True

    def test_path_escapes_root(self, tmp_dir):
        root = str(tmp_dir / "confined")
        escaped = str(tmp_dir / "other" / "file.txt")
        assert is_under_root(escaped, root) is False

    def test_traversal_attempt(self, tmp_dir):
        root = str(tmp_dir / "safe")
        traversal = os.path.join(str(tmp_dir), "safe", "..", "unsafe", "file.txt")
        assert is_under_root(traversal, root) is False


class TestRequireUnderRoot:
    def test_passes_for_valid_path(self, tmp_dir):
        root = str(tmp_dir)
        child = str(tmp_dir / "file.txt")
        require_under_root(child, root)  # Should not raise

    def test_raises_for_escape(self, tmp_dir):
        root = str(tmp_dir / "jail")
        escaped = str(tmp_dir / "outside")
        with pytest.raises(PathPolicyError, match="escapes allowed root"):
            require_under_root(escaped, root)


class TestRequireAllowedWrite:
    def test_permissive_when_uninitialized(self, tmp_dir):
        """When _ALLOWED_ROOTS is empty, writes are permissive."""
        from limewire.security.safe_paths import _ALLOWED_ROOTS
        saved = list(_ALLOWED_ROOTS)
        _ALLOWED_ROOTS.clear()
        try:
            require_allowed_write(str(tmp_dir / "anything.txt"))  # Should not raise
        finally:
            _ALLOWED_ROOTS.extend(saved)

    def test_allowed_in_root(self, tmp_dir):
        init_allowed_roots([str(tmp_dir)])
        require_allowed_write(str(tmp_dir / "ok.txt"))  # Should not raise

    def test_blocked_outside_roots(self, tmp_dir):
        from limewire.security.safe_paths import _ALLOWED_ROOTS
        _ALLOWED_ROOTS.clear()
        _ALLOWED_ROOTS.append(str(tmp_dir / "allowed"))
        try:
            with pytest.raises(PathPolicyError, match="not in allowed roots"):
                require_allowed_write(str(tmp_dir / "forbidden" / "file.txt"))
        finally:
            init_allowed_roots()  # restore defaults

    def test_default_roots_include_home_dirs(self):
        init_allowed_roots()
        from limewire.security.safe_paths import _ALLOWED_ROOTS
        home = os.path.expanduser("~")
        assert os.path.join(home, ".limewire") in _ALLOWED_ROOTS
        assert os.path.join(home, "Downloads") in _ALLOWED_ROOTS
        assert os.path.join(home, "Music") in _ALLOWED_ROOTS


class TestSanitizeFilename:
    def test_strips_path_separators(self):
        assert "/" not in sanitize_filename("path/to/file.mp3")
        assert "\\" not in sanitize_filename("path\\to\\file.mp3")

    def test_strips_dangerous_chars(self):
        result = sanitize_filename('file<>:"|?*.mp3')
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert '"' not in result
        assert "|" not in result
        assert "?" not in result
        assert "*" not in result

    def test_strips_control_chars(self):
        result = sanitize_filename("file\x00\x1f.mp3")
        assert "\x00" not in result
        assert "\x1f" not in result

    def test_blocks_windows_reserved_names(self):
        for name in ["CON", "PRN", "AUX", "NUL", "COM1", "LPT1"]:
            result = sanitize_filename(f"{name}.txt")
            assert result.startswith("_"), f"{name} should be prefixed"

    def test_reserved_names_case_insensitive(self):
        result = sanitize_filename("con.txt")
        assert result.startswith("_")

    def test_enforces_max_length(self):
        long_name = "a" * 300 + ".mp3"
        result = sanitize_filename(long_name)
        assert len(result) <= 200

    def test_custom_max_length(self):
        result = sanitize_filename("a" * 100, max_length=50)
        assert len(result) == 50

    def test_empty_becomes_untitled(self):
        assert sanitize_filename("") == "untitled"
        assert sanitize_filename("...") == "untitled"
        assert sanitize_filename("   ") == "untitled"

    def test_normal_filename_unchanged(self):
        assert sanitize_filename("song.mp3") == "song.mp3"
        assert sanitize_filename("My Track (remix).flac") == "My Track (remix).flac"


class TestAtomicWrite:
    def test_writes_text(self, tmp_dir):
        init_allowed_roots([str(tmp_dir)])
        target = str(tmp_dir / "test.txt")
        atomic_write(target, "hello world", mode="w")
        assert open(target).read() == "hello world"

    def test_writes_bytes(self, tmp_dir):
        init_allowed_roots([str(tmp_dir)])
        target = str(tmp_dir / "test.bin")
        atomic_write(target, b"\x00\x01\x02", mode="wb")
        assert open(target, "rb").read() == b"\x00\x01\x02"

    def test_creates_parent_dirs(self, tmp_dir):
        init_allowed_roots([str(tmp_dir)])
        target = str(tmp_dir / "sub" / "dir" / "file.txt")
        atomic_write(target, "nested", mode="w")
        assert open(target).read() == "nested"

    def test_no_temp_file_left_on_success(self, tmp_dir):
        init_allowed_roots([str(tmp_dir)])
        target = str(tmp_dir / "clean.txt")
        atomic_write(target, "data", mode="w")
        assert not os.path.exists(target + ".tmp")

    def test_blocked_outside_roots(self, tmp_dir):
        from limewire.security.safe_paths import _ALLOWED_ROOTS
        _ALLOWED_ROOTS.clear()
        _ALLOWED_ROOTS.append(str(tmp_dir / "allowed"))
        try:
            with pytest.raises(PathPolicyError):
                atomic_write(str(tmp_dir / "forbidden" / "file.txt"), "nope", mode="w")
        finally:
            init_allowed_roots()  # restore defaults


class TestSafeJoin:
    def test_normal_join(self, tmp_dir):
        root = str(tmp_dir)
        result = safe_join(root, "sub", "file.txt")
        assert result.startswith(os.path.realpath(root))

    def test_blocks_traversal(self, tmp_dir):
        root = str(tmp_dir / "jail")
        os.makedirs(root, exist_ok=True)
        with pytest.raises(PathPolicyError, match="traversal"):
            safe_join(root, "..", "escaped.txt")

    def test_blocks_absolute_escape(self, tmp_dir):
        root = str(tmp_dir / "jail")
        os.makedirs(root, exist_ok=True)
        with pytest.raises(PathPolicyError, match="traversal"):
            safe_join(root, "/tmp/evil.txt")
