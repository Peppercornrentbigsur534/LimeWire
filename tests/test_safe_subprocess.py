"""Tests for limewire.security.safe_subprocess — allowlist, policy enforcement."""

import pytest

from limewire.security.safe_subprocess import (
    CommandResult,
    SubprocessPolicyError,
    run_safe,
)


class TestCommandResult:
    def test_ok_on_zero(self):
        r = CommandResult("test", ["cmd"], 0, 1.0, "out", "")
        assert r.ok is True

    def test_not_ok_on_nonzero(self):
        r = CommandResult("test", ["cmd"], 1, 1.0, "", "err")
        assert r.ok is False

    def test_slots(self):
        r = CommandResult("f", ["a"], 0, 0.5, "o", "e")
        assert r.family == "f"
        assert r.argv == ["a"]
        assert r.returncode == 0
        assert r.duration == 0.5
        assert r.stdout == "o"
        assert r.stderr == "e"


class TestRunSafe:
    def test_rejects_unlisted_binary(self):
        with pytest.raises(SubprocessPolicyError, match="not in allowlist"):
            run_safe("curl", ["-V"])

    def test_rejects_shell_commands(self):
        with pytest.raises(SubprocessPolicyError, match="not in allowlist"):
            run_safe("bash", ["-c", "echo pwned"])

    def test_rejects_python(self):
        with pytest.raises(SubprocessPolicyError, match="not in allowlist"):
            run_safe("python", ["-c", "print('hi')"])

    def test_rejects_rm(self):
        with pytest.raises(SubprocessPolicyError, match="not in allowlist"):
            run_safe("rm", ["-rf", "/"])

    def test_rejects_powershell(self):
        with pytest.raises(SubprocessPolicyError, match="not in allowlist"):
            run_safe("powershell", ["-c", "Get-Process"])

    def test_rejects_cmd(self):
        with pytest.raises(SubprocessPolicyError, match="not in allowlist"):
            run_safe("cmd", ["/c", "dir"])

    def test_ffprobe_runs_if_installed(self):
        """ffprobe is in the allowlist — should work if installed."""
        import shutil
        if not shutil.which("ffprobe"):
            pytest.skip("ffprobe not installed")
        result = run_safe("ffprobe", ["-version"], timeout=10)
        assert result.ok
        assert "ffprobe" in result.stdout.lower()

    def test_ffmpeg_runs_if_installed(self):
        import shutil
        if not shutil.which("ffmpeg"):
            pytest.skip("ffmpeg not installed")
        result = run_safe("ffmpeg", ["-version"], timeout=10)
        assert result.ok

    def test_not_found_raises(self):
        """An allowed binary that doesn't exist on PATH should raise."""
        # yt-dlp is in the allowlist but might not be installed
        import shutil
        if shutil.which("yt-dlp"):
            pytest.skip("yt-dlp is installed, can't test not-found")
        with pytest.raises(SubprocessPolicyError, match="not found on PATH"):
            run_safe("yt-dlp", ["--version"])

    def test_output_truncation(self):
        import shutil
        if not shutil.which("ffmpeg"):
            pytest.skip("ffmpeg not installed")
        result = run_safe("ffmpeg", ["-version"], max_output=20, timeout=10)
        assert len(result.stdout) <= 20
