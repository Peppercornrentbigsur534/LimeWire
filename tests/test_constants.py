"""Tests for limewire.core.constants — validate constant values and types."""

import re

import pytest

from limewire.core.constants import (
    ALL_KEYS,
    AUDIO_FMTS,
    CLIPBOARD_POLL_MS,
    CONV_AUDIO,
    CONV_VIDEO,
    EQ_BAR_COUNT,
    FILENAME_MAX_LENGTH,
    HISTORY_MAX,
    KEY_NAMES_FULL,
    MAX_URL_LENGTH,
    NETWORK_TIMEOUT,
    PLAYER_UPDATE_MS,
    QUALITIES,
    RECORDER_CHANNELS,
    RECORDER_SAMPLE_RATE,
    SCHEDULER_POLL_SEC,
    SP_LG,
    SP_MD,
    SP_SM,
    SP_XL,
    SP_XS,
    STATUS_PULSE_MS,
    SUPPRESS,
    TEMPO_RANGE,
    URL_PATTERNS,
    VIDEO_FMTS,
    ydl_opts,
)


class TestTimingConstants:
    def test_clipboard_poll_positive(self):
        assert CLIPBOARD_POLL_MS > 0

    def test_status_pulse_positive(self):
        assert STATUS_PULSE_MS > 0

    def test_player_update_positive(self):
        assert PLAYER_UPDATE_MS > 0

    def test_scheduler_poll_positive(self):
        assert SCHEDULER_POLL_SEC > 0


class TestLimits:
    def test_history_max_reasonable(self):
        assert 100 <= HISTORY_MAX <= 10000

    def test_max_url_length_reasonable(self):
        assert 100 <= MAX_URL_LENGTH <= 2048

    def test_filename_max_length(self):
        assert 50 <= FILENAME_MAX_LENGTH <= 255

    def test_network_timeout_reasonable(self):
        assert 5 <= NETWORK_TIMEOUT <= 120


class TestFormats:
    def test_audio_formats_non_empty(self):
        assert len(AUDIO_FMTS) > 0

    def test_video_formats_non_empty(self):
        assert len(VIDEO_FMTS) > 0

    def test_mp3_in_audio(self):
        assert "mp3" in AUDIO_FMTS

    def test_mp4_in_video(self):
        assert "mp4" in VIDEO_FMTS

    def test_conv_audio_subset(self):
        for fmt in CONV_AUDIO:
            assert isinstance(fmt, str)

    def test_qualities_include_best_worst(self):
        assert "best" in QUALITIES
        assert "worst" in QUALITIES


class TestKeys:
    def test_12_key_names(self):
        assert len(KEY_NAMES_FULL) == 12

    def test_24_all_keys(self):
        assert len(ALL_KEYS) == 24  # 12 major + 12 minor

    def test_all_keys_have_major_minor(self):
        majors = [k for k in ALL_KEYS if "Major" in k]
        minors = [k for k in ALL_KEYS if "Minor" in k]
        assert len(majors) == 12
        assert len(minors) == 12


class TestRecorder:
    def test_sample_rate(self):
        assert RECORDER_SAMPLE_RATE in (22050, 44100, 48000, 96000)

    def test_channels(self):
        assert RECORDER_CHANNELS in (1, 2)


class TestSpacing:
    def test_spacing_ascending(self):
        assert SP_XS < SP_SM < SP_MD < SP_LG < SP_XL


class TestUrlPatterns:
    def test_patterns_are_compiled_regex(self):
        for p in URL_PATTERNS:
            assert hasattr(p, "match")

    def test_matches_youtube(self):
        assert any(p.match("https://www.youtube.com/watch?v=abc123") for p in URL_PATTERNS)

    def test_matches_youtu_be(self):
        assert any(p.match("https://youtu.be/abc123") for p in URL_PATTERNS)


class TestYdlOpts:
    def test_returns_dict(self):
        assert isinstance(ydl_opts(), dict)

    def test_includes_timeout(self):
        opts = ydl_opts()
        assert "socket_timeout" in opts

    def test_custom_overrides(self):
        opts = ydl_opts(format="bestaudio")
        assert opts["format"] == "bestaudio"

    def test_base_preserved(self):
        opts = ydl_opts(extra="value")
        assert "socket_timeout" in opts
        assert opts["extra"] == "value"


class TestTempoRange:
    def test_tuple_of_two(self):
        assert len(TEMPO_RANGE) == 2

    def test_min_less_than_max(self):
        assert TEMPO_RANGE[0] < TEMPO_RANGE[1]

    def test_reasonable_range(self):
        assert TEMPO_RANGE[0] > 0
        assert TEMPO_RANGE[1] <= 10
