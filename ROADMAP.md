# Roadmap

## v1.0.1 — Shipped!
- [x] Drag-and-drop file loading across all tabs
- [x] Global search across downloads, history, and library
- [x] Playlist auto-queue from Discovery matches
- [x] Waveform zoom and scroll in Editor
- [x] Batch stem separation
- [x] Export presets (save/load effect chains)
- [x] Dark title bar (Windows DWM API)
- [x] Recent files menu
- [x] Auto-save/restore session state
- [x] Media key shortcuts
- [x] Editor minimap with viewport indicator
- [x] Snap to zero-crossing for clean cuts
- [x] Now Playing toast notifications
- [x] Export library analysis to CSV

## v1.1 — Quality of Life — Shipped!
- [x] Cover Art Manager (19th tab) — view, add, fetch, batch-apply album artwork
- [x] Fetch cover art from iTunes Search API and MusicBrainz Cover Art Archive
- [x] Universal cover art embedding (MP3/FLAC/OGG/M4A/WAV)
- [x] Undo/redo in Effects chain (30-level stack)
- [x] Waveform color coding by frequency in Editor (spectral centroid)
- [x] Batch rename downloaded files with pattern tokens
- [x] Auto-tag metadata from analysis results (multi-format)
- [x] Enhanced Player album art (200x200, click-to-enlarge, all formats)

## v1.2 — Keyboard & Navigation — Shipped!
- [x] Tab/Shift+Tab focus cycling across all tabs
- [x] Enter to trigger primary action on each page
- [x] Keyboard shortcut customization dialog (rebind any shortcut)
- [x] Arrow key waveform seeking in Player (±5s, Shift ±15s)

## v1.3 — Streaming & Social — Shipped!
- [x] SoundCloud search (`sc:query`) and Bandcamp search (`bc:query`)
- [x] Bare text YouTube search (just type and press Enter)
- [x] Share analysis results as PNG image cards with album art
- [x] Collaborative playlist building via shared JSON export/import
- [x] Discord Rich Presence (show currently playing track)

## v2.0 — Cross-Platform & Plugins — Shipped!
- [x] Platform detection (IS_WINDOWS, IS_MACOS, IS_LINUX)
- [x] Plugin system for custom audio processors (`~/.limewire/plugins/`)
- [x] VST3/AU plugin hosting in Effects chain via pedalboard
- [x] MIDI controller mapping for Remixer (MIDI Learn mode)
- [x] Cloud sync for settings and history (export/import to cloud folders)
- [x] Auto-update mechanism (GitHub release check)
- [x] Community theme support (load theme JSON files)

## Ongoing — Shipped!
- [x] Performance optimization: recursive scan, parallel analysis (ThreadPoolExecutor)
- [x] Accessibility: High Contrast theme (13 total)
- [x] Localization: 6 languages (EN, ES, FR, DE, JA, PT)
- [x] Community theme submissions via JSON

## Future Ideas
- [ ] Real-time collaborative mixing via WebSocket
- [ ] AI-powered auto-mixing suggestions
- [ ] Built-in sample marketplace
- [ ] Stem-based karaoke mode with lyrics overlay
- [ ] Spotify playlist import (resolve to YouTube)
- [ ] Ableton Live / Logic Pro project export

---

Have an idea? [Open a feature request](https://github.com/Ccwilliams314/LimeWire/issues/new?template=feature_request.md)
