"""Shared fixtures for LimeWire test suite."""

import os
import sys
import tempfile

import pytest

# Ensure the package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def tmp_dir(tmp_path):
    """Provide a temporary directory for file operations."""
    return tmp_path


@pytest.fixture
def sample_json_file(tmp_path):
    """Create a sample JSON file for testing."""
    import json
    path = tmp_path / "test.json"
    data = {"key": "value", "count": 42}
    path.write_text(json.dumps(data))
    return path


@pytest.fixture
def sample_plugin_file(tmp_path):
    """Create a minimal plugin .py file for testing."""
    code = '''
name = "Test Plugin"
description = "A test plugin"

def process(audio_data, sr, **params):
    return audio_data
'''
    path = tmp_path / "test_plugin.py"
    path.write_text(code)
    return path
