# Contributing to LimeWire

Thanks for your interest in contributing! LimeWire is a single-file Python application, so the barrier to entry is low.

## Getting Started

1. Fork the repo and clone it
2. Run `setup.bat` or install dependencies manually with `pip install -r requirements.txt`
3. Make sure FFmpeg is installed (`winget install ffmpeg`)
4. Launch with `python LimeWire.py`

## Project Structure

```
LimeWire.py              — Entire application (single file, ~5200 lines)
requirements.txt         — Python dependencies
screenshots/             — Tab screenshots for README
build_manual.py          — PDF manual generator (optional)
```

The app is intentionally a single file. This makes it easy to distribute, run, and understand without complex project scaffolding.

## How to Contribute

### Bug Reports
- Use the [Bug Report](https://github.com/yourusername/LimeWire/issues/new?template=bug_report.md) template
- Include your Python version, OS, and steps to reproduce

### Feature Requests
- Use the [Feature Request](https://github.com/yourusername/LimeWire/issues/new?template=feature_request.md) template
- Describe the use case, not just the solution

### Pull Requests
1. Create a branch from `main`
2. Keep changes focused — one feature or fix per PR
3. Test at least LiveWire (default), Classic Light, and one community theme
4. Make sure `python -c "import py_compile; py_compile.compile('LimeWire.py', doraise=True)"` passes

### Code Style
- Follow existing patterns in the codebase
- Use compact formatting consistent with the rest of the file
- Thread-safety: use `self.after(0, callback)` for UI updates from background threads
- Lazy imports for heavy libraries (librosa, demucs, whisper, etc.)

## Architecture Quick Reference

- `App(tk.Tk)` — main window, holds `self.pages` dict of 18 page instances
- All pages extend `ScrollFrame` — a custom scrollable frame
- Widget factories: `ModernBtn`, `ClassicBtn`, `LimeBtn`, `OrangeBtn`, `GroupBox`, `ClassicEntry`, `ClassicCombo`, `ClassicListbox`
- Theme system: 12 theme dicts (LiveWire, Light, Dark, Modern, Synthwave, Dracula, Catppuccin, Tokyo Night, Spotify, Classic, Nord, Gruvbox) with `apply_theme()` + `_reconfig_all()`
- Config files: `~/.limewire_*.json` (history, settings, schedule, queue, analysis_cache)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
