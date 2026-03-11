"""Tests for limewire.utils.helpers — sanitize, URL detection, source detection."""

import pytest

from limewire.utils.helpers import (
    auto_detect_format,
    detect_source,
    fmt_duration,
    is_url,
    sanitize_filename,
)


class TestFmtDuration:
    def test_zero(self):
        assert fmt_duration(0) == "0:00:00"

    def test_one_minute(self):
        assert fmt_duration(60) == "0:01:00"

    def test_one_hour(self):
        assert fmt_duration(3600) == "1:00:00"

    def test_mixed(self):
        assert fmt_duration(3661) == "1:01:01"

    def test_invalid_returns_placeholder(self):
        assert fmt_duration("not a number") == "--:--"
        assert fmt_duration(None) == "--:--"


class TestIsUrl:
    def test_youtube_url(self):
        assert is_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True

    def test_youtu_be(self):
        assert is_url("https://youtu.be/dQw4w9WgXcQ") is True

    def test_soundcloud(self):
        assert is_url("https://soundcloud.com/artist/track") is True

    def test_generic_url(self):
        assert is_url("https://example.com/audio.mp3") is True

    def test_empty_string(self):
        assert is_url("") is False

    def test_plain_text(self):
        assert is_url("hello world") is False

    def test_file_scheme_rejected(self):
        assert is_url("file:///etc/passwd") is False

    def test_ftp_scheme_rejected(self):
        assert is_url("ftp://evil.com/file") is False

    def test_too_long_rejected(self):
        assert is_url("https://example.com/" + "a" * 500) is False


class TestSanitizeFilename:
    def test_normal_filename(self):
        assert sanitize_filename("song.mp3") == "song.mp3"

    def test_strips_slashes(self):
        result = sanitize_filename("path/to\\file.mp3")
        assert "/" not in result
        assert "\\" not in result

    def test_strips_special_chars(self):
        result = sanitize_filename('file<>:"|?*.mp3')
        for c in '<>:"|?*':
            assert c not in result

    def test_blocks_con(self):
        result = sanitize_filename("CON.txt")
        assert result.startswith("_")

    def test_empty_string(self):
        assert sanitize_filename("") == "untitled"

    def test_truncates_long_names(self):
        result = sanitize_filename("a" * 300)
        assert len(result) <= 200


class TestDetectSource:
    def test_youtube(self):
        assert detect_source("https://www.youtube.com/watch?v=abc") == "YouTube"

    def test_youtu_be(self):
        assert detect_source("https://youtu.be/abc") == "YouTube"

    def test_soundcloud(self):
        assert detect_source("https://soundcloud.com/artist/track") == "SoundCloud"

    def test_spotify(self):
        assert detect_source("https://open.spotify.com/track/123") == "Spotify"

    def test_tiktok(self):
        assert detect_source("https://www.tiktok.com/@user/video/123") == "TikTok"

    def test_unknown_returns_web(self):
        assert detect_source("https://random-site.com/audio.mp3") == "Web"


class TestAutoDetectFormat:
    def test_youtube_audio(self):
        fmt_type, fmt = auto_detect_format("https://youtube.com/watch?v=abc")
        assert fmt_type == "audio"
        assert fmt == "mp3"

    def test_soundcloud_audio(self):
        fmt_type, fmt = auto_detect_format("https://soundcloud.com/a/b")
        assert fmt_type == "audio"
        assert fmt == "mp3"

    def test_twitter_video(self):
        fmt_type, fmt = auto_detect_format("https://twitter.com/user/status/123")
        assert fmt_type == "video"
        assert fmt == "mp4"

    def test_unknown_returns_none(self):
        fmt_type, fmt = auto_detect_format("https://unknown-site.com/media")
        assert fmt_type is None
        assert fmt is None
