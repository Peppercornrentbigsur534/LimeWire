"""Tests for limewire.services.plugins — PluginManager, PluginBase."""

import hashlib
import os

import pytest

from limewire.services.plugins import PluginBase, PluginManager


def _make_plugin(tmp_path, name, code):
    """Write a plugin file and return (path, sha256)."""
    path = tmp_path / name
    data = code.encode()
    path.write_bytes(data)
    h = hashlib.sha256(data).hexdigest()
    return str(path), h


class TestPluginBase:
    def test_default_name(self):
        p = PluginBase()
        assert p.name == "Unnamed Plugin"

    def test_process_passthrough(self):
        p = PluginBase()
        data = [1.0, 2.0, 3.0]
        assert p.process(data, 44100) is data

    def test_default_category(self):
        p = PluginBase()
        assert p.category == "Custom"


class TestPluginManager:
    def test_discover_no_directory(self, tmp_path):
        """Discover with a non-existent dir creates it."""
        pm = PluginManager()
        new_dir = str(tmp_path / "plugins")
        # Monkey-patch PLUGINS_DIR isn't needed; we call discover indirectly
        from limewire.security.plugin_policy import scan_plugins
        results = scan_plugins(new_dir, set())
        assert results == []
        assert os.path.isdir(new_dir)

    def test_discover_none_means_no_loading(self, tmp_path):
        pm = PluginManager()
        code = '''
from limewire.services.plugins import PluginBase
class TestPlugin(PluginBase):
    name = "Test"
    def process(self, audio_data, sr, **p): return audio_data
'''
        path, h = _make_plugin(tmp_path, "test_plug.py", code)

        # Monkeypatch the plugins dir
        import limewire.services.plugins as mod
        orig = mod.PLUGINS_DIR
        mod.PLUGINS_DIR = str(tmp_path)
        try:
            pm.discover(trusted_hashes=None)
            assert pm.list_plugins() == []  # Not loaded, just discovered
            assert len(pm.get_discovered()) >= 1
        finally:
            mod.PLUGINS_DIR = orig

    def test_discover_with_trusted_hash_loads(self, tmp_path):
        pm = PluginManager()
        code = '''
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from limewire.services.plugins import PluginBase
class MyPlugin(PluginBase):
    name = "MyPlugin"
    def process(self, audio_data, sr, **p): return audio_data
'''
        path, h = _make_plugin(tmp_path, "my_plugin.py", code)

        import limewire.services.plugins as mod
        orig = mod.PLUGINS_DIR
        mod.PLUGINS_DIR = str(tmp_path)
        try:
            pm.discover(trusted_hashes={h})
            loaded = pm.list_plugins()
            assert len(loaded) == 1
            assert loaded[0].name == "MyPlugin"
        finally:
            mod.PLUGINS_DIR = orig

    def test_untrusted_plugin_not_loaded(self, tmp_path):
        pm = PluginManager()
        code = "x = 'should not load'\n"
        _make_plugin(tmp_path, "untrusted.py", code)

        import limewire.services.plugins as mod
        orig = mod.PLUGINS_DIR
        mod.PLUGINS_DIR = str(tmp_path)
        try:
            pm.discover(trusted_hashes={"wrong_hash"})
            assert pm.list_plugins() == []
        finally:
            mod.PLUGINS_DIR = orig

    def test_get_returns_none_for_missing(self):
        pm = PluginManager()
        assert pm.get("nonexistent") is None

    def test_process_raises_for_missing(self):
        pm = PluginManager()
        with pytest.raises(ValueError, match="not found"):
            pm.process("missing", [], 44100)

    def test_errors_tracked(self, tmp_path):
        pm = PluginManager()
        # Create a plugin that will fail to import
        code = "raise ImportError('broken')\n"
        _, h = _make_plugin(tmp_path, "broken.py", code)

        import limewire.services.plugins as mod
        orig = mod.PLUGINS_DIR
        mod.PLUGINS_DIR = str(tmp_path)
        try:
            pm.discover(trusted_hashes={h})
            errors = pm.get_errors()
            assert len(errors) >= 1
            assert "broken" in errors[0][0]  # filename
        finally:
            mod.PLUGINS_DIR = orig
