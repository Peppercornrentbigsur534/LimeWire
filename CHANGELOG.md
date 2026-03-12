# Changelog

## v3.3.0 — Security & Stability (2026-03-11)

### Security Hardening (All Connectors)
- **OAuth PKCE** (Proof Key for Code Exchange) on Spotify, YouTube, TIDAL
- **CSRF Protection** via cryptographic state parameter on all OAuth flows
- **DPAPI Token Encryption** at rest on Windows (base64 fallback on other OS)
- **Input Validation** — regex ID validation on all service-specific IDs before API interpolation
- **SSRF Protection** — domain-allowlist on pagination URLs (Spotify) and yt-dlp URLs (YouTube, SoundCloud)
- **Error Sanitization** — query params and tokens stripped from exception messages
- **Limit Caps** — pagination bounded to prevent resource exhaustion (10K tracks max)
- **Schema Migration** — `client_secret` column removed from SQLite storage; secrets loaded only from settings at runtime

### Security Indicators (Settings > Accounts)
- Per-service "✓ Secure" badge (green) when linked
- New "Security" GroupBox showing 4 active protections: PKCE, CSRF, Encrypted Storage, Input Validation

### Bug Fixes
- **player.py**: Fixed race condition — frequency profile now written under lock from background thread
- **effects.py / recorder.py / remixer.py**: Fixed temp file deleted while pyglet still playing; temp files now cleaned on next preview
- **stems.py**: `_running` flag now reset in `finally` block — prevents batch separation from becoming permanently locked on exception
- **editor.py**: "End" time label now shows actual selection end instead of total file duration
- **analyze.py**: Image card export now uses correct dictionary keys — results no longer display as "--"
- **batch_processor.py**: "Normalize LUFS" label corrected to "Normalize Loudness (dBFS)" to match actual pydub algorithm
- **search.py**: Subtitle language now reads from user settings instead of hardcoded "en"
- **effects.py**: Undo stack limit now respects configurable `undo_max` setting instead of hardcoded 30

### Playlist Transfer & Sync (GUI)
- Full transfer dialog accessible via "Transfer..." button on Playlist page
- Supports: single playlist, sync playlist, all playlists, liked songs, followed artists, saved albums
- Cross-service: Spotify ↔ YouTube ↔ TIDAL ↔ SoundCloud ↔ Deezer
- Detailed match report with confidence scores and match methods
- CSV export of track lists

---

## v3.0.0 — Modular Architecture (2026-03-11)

### Modular Package Restructuring
- Entire codebase split from single-file monolith into `limewire/` package (~54 modules)
- Clean separation: `core/`, `services/`, `security/`, `ui/`, `pages/`, `i18n/`, `utils/`
- Backward-compatible `LimeWire.py` thin launcher preserved
- `python -m limewire` support via `__main__.py`

### Security Module (`limewire/security/`)
- **safe_paths.py**: Path confinement with allowed-root enforcement, symlink traversal prevention, atomic writes, Windows reserved name blocking
- **safe_subprocess.py**: Binary allowlist (ffmpeg/ffprobe/yt-dlp only), mandatory timeouts, output truncation, audit logging, no `shell=True`
- **safe_json.py**: Size limits (5 MB), depth checks (max 10), key allowlisting, hex color validation for themes
- **plugin_policy.py**: SHA-256 hash-based plugin trust, no auto-execution, auto-revoke on file change

### UI Uniformity
- All 20 pages now use consistent GroupBox card pattern
- Player page: pixel-based album art (160x160 PhotoImage placeholder), split into 4 GroupBoxes
- Remixer/Batch Processor: H2 titles replaced with GroupBox sections
- Converter/Playlist: loose buttons wrapped into GroupBox containers

### Skin Customizer
- Standalone visual theme editor (`skin_customizer.py`)
- Live preview with mock LimeWire UI rendering
- Export to JSON for community theme sharing

---

## v2.0.2 — Settings & Security Hardening (2026-03-09)

### New: Settings Tab (20th Tab)
- Dedicated Settings page with theme selector dropdown (13 built-in + community themes)
- Download folder configuration with browse dialog
- Proxy and rate limit settings
- Clipboard watch toggle
- Discord Rich Presence toggle
- About section with version info

### Security Hardening
- **Theme sandboxing**: `apply_theme()` now uses allowlist — community themes can only set known color keys, preventing globals overwrite
- **Freesound filename sanitization**: Sample downloads now use `sanitize_filename()` instead of ad-hoc `.replace()`
- **Remixer preview temp file**: Replaced predictable `_remix_preview.wav` with `tempfile.mkstemp()` + cleanup
- **Effect preset loading**: Fixed missing default argument in `load_json()` call that would crash preset loading
- **Crash log privacy**: Startup errors now write full traceback to `~/.limewire_crash.log` instead of displaying in message box

### UI Changes
- Toolbar icons reverted to emoji style (from monochrome Unicode symbols)
- Menu backgrounds properly themed in dark modes (explicit fg/activebackground)
- Theme dropdown moved from toolbar to Settings tab for cleaner toolbar layout
- Window width widened from 820px to 960px to accommodate 20 toolbar buttons

### Screenshots
- All 20 screenshots automated via `--screenshots` CLI flag
- Screenshots anonymized (personal paths replaced, LiveWire theme forced)

### Tab Count
- 20 tabs (added Settings)

---

## v2.0.1 — Visual Facelift (2026-03-09)

### Typography
- Body text bumped to 11pt, buttons to 10pt for better readability
- Logo uses Segoe UI Black 22pt for stronger branding
- New F_CAPTION (8pt) and F_LABEL (9pt) font tiers
- Monospace font bumped to 10pt to match body text

### Theme Refinements
- 4 new color tokens: BTN_PRESSED, CARD_SHADOW, DIVIDER, FOCUS_RING
- Fixed WCAG contrast issues in Light theme (TEXT_DIM)
- Fixed CARD_BG matching PANEL in Dark and LiveWire themes
- High Contrast theme: improved TEXT_DIM and panel layering
- Classic theme: improved TEXT_DIM contrast
- Backward-compatible defaults for community themes missing new keys

### Button Polish
- ModernBtn: increased padding (20x8), radius 10, subtle outline ring
- Smooth 3-step hover transitions via color lerp animation
- ClassicBtn now has visible SURFACE_2 background instead of blending into page
- Improved disabled state visual (SURFACE_2 + faded text)

### Card & Input Styling
- GroupBox uses CARD_BG background (distinct from page), thinner 1px border
- Accent stripe: 4px wide, 85% height with offset for polished look
- Entry cursor color matches accent (LIME)
- Checkboxes: active foreground lights up in LIME, hand cursor
- Listbox scrollbar: thinner 10px ttk.Scrollbar

### Logo Bar
- Height 56→52px, smoothstep gradient interpolation
- Lightning bolt icon, drop shadow on title text
- Version badge: 8pt with outline, accent-derived colors
- Status: smaller dot, "Ready" label, F_CAPTION font

### Toolbar Icons
- All emoji replaced with monochrome Unicode symbols (Segoe UI Symbol 13pt)
- Toolbar height 48→44px, DIVIDER separators
- Consistent rendering across all Windows versions

### Status Bar
- SURFACE_3 background (distinct from content area), 26px height
- Compact download count (↓ N), DIVIDER separators
- Module indicator uses semantic SUCCESS/WARNING/ERROR colors

### Toast Notifications
- Border tint derived from toast bg color (more cohesive)
- Larger icon (16pt), more padding, close button (✕)
- New "success" toast level

### Progress Bars & Scrollbars
- Thinner progress bars (8px), softer SURFACE_2 trough
- New Thin variant (4px) for inline indicators
- All scrollbars themed via ttk (10px width, dark-matching colors)
- Treeview row height 24→28px with better heading style

---

## v2.0.0 — Cross-Platform & Plugins (2026-03-09)

### v1.2: Keyboard & Navigation
- **Tab/Shift+Tab focus cycling**: Cycle through interactive widgets on the active page
- **Enter for primary action**: Press Enter to trigger the main action on any page
- **Keyboard shortcut customization**: Tools → Customize Shortcuts dialog to rebind any shortcut
- **Arrow key seeking**: Left/Right arrow keys seek ±5s in Player (Shift+Arrow ±15s)

### v1.3: Streaming & Social
- **SoundCloud/Bandcamp search**: Type `sc:query` or `bc:query` in Search to find music (also `yt:query`)
- **Bare text search**: Typing plain text searches YouTube automatically
- **Analysis image cards**: Export BPM/key/loudness results as shareable PNG cards with album art
- **Collaborative playlists**: Share JSON and Import JSON buttons in Player for playlist sharing
- **Discord Rich Presence**: Shows currently playing track in Discord (requires `pypresence`)

### v2.0: Cross-Platform & Plugins
- **Platform detection**: IS_WINDOWS, IS_MACOS, IS_LINUX constants for platform-specific code
- **Plugin system**: `PluginBase` class + `PluginManager` loads custom `.py` plugins from `~/.limewire/plugins/`
- **VST3/AU hosting**: Load VST3 plugins directly into Effects chain via pedalboard
- **MIDI controller mapping**: MIDI Learn mode in Remixer for mapping CC controls to stem faders
- **Cloud sync**: Export/import settings, history, and analysis cache to cloud folders (Dropbox/OneDrive/Google Drive)
- **Auto-update**: Check for new releases via GitHub API (Tools → Check App Update)
- **Community themes**: Load custom theme JSON files (Tools → Load Community Theme)

### Ongoing Improvements
- **Performance**: Recursive library scan with ThreadPoolExecutor (parallel BPM/key analysis, 4 workers)
- **Accessibility**: High Contrast theme (13 themes total) with maximum contrast ratios
- **Localization**: 6 languages (English, Spanish, French, German, Japanese, Portuguese) via `_t()` i18n system
- **50,000 file cap** on library scan to prevent OOM

### Theme Count
- 13 themes (added High Contrast)

---

## v1.1.0 — Quality of Life (2026-03-09)

### New: Cover Art Manager (19th Tab)
- Dedicated Cover Art page for viewing, adding, and managing album artwork
- Browse and embed cover art from local images (JPG/PNG)
- Auto-fetch cover art from iTunes Search API (no auth required)
- Auto-fetch cover art from MusicBrainz Cover Art Archive (no auth required)
- Batch apply cover art to entire album folders
- Remove embedded art from files
- Universal format support: MP3, FLAC, OGG, M4A, WAV
- Auto-populate artist/album fields from file tags
- Smart image processing: center-crop to square, resize to 500x500, JPEG optimization

### Enhanced Features
- **Effects chain undo/redo**: Full undo/redo stack (30 levels) for add, remove, edit, clear, and preset load operations
- **Waveform frequency coloring**: Editor waveform bars colored by spectral centroid (cyan=low, green=mid, orange=high) with toggle checkbox
- **Batch rename**: Pattern-based file renaming in History tab with tokens ({title}, {artist}, {bpm}, {key}, {date}, {n}, {ext}) and live preview
- **Multi-format auto-tagging**: AnalyzePage now writes tags to MP3, FLAC, OGG, M4A (not just MP3); optional auto-tag after analysis
- **Enhanced Player album art**: 200x200 display (up from 80x80), click to view full-size, universal format extraction (MP3/FLAC/OGG/M4A/WAV)

### Tab Count
- 19 tabs (added Cover Art)

---

## v1.0.0 — Studio Edition (2026-03-09)

First public release as **LimeWire 1.0 Studio Edition** — a complete all-in-one audio production studio.

### 18 Tabs (v1.0)

| Tab | Description |
|-----|-------------|
| Search & Grab | Download from 1000+ sites via yt-dlp |
| Batch Download | Queue multiple URLs with format selection |
| Playlist | Fetch and download entire playlists |
| Converter | Convert between mp3, wav, flac, ogg, m4a, aac, opus |
| Player | Playback with waveform, seek, A-B loop, EQ visualizer |
| Analyze | BPM, key, Camelot, loudness (LUFS), true peak |
| Stems | AI stem separation via Demucs (vocals, drums, bass, other, piano, guitar) |
| Effects | Effects chain with pedalboard (reverb, chorus, delay, compressor, etc.) |
| Discovery | Music library scanner with BPM/key indexing |
| Samples | Sample browser with preview and metadata |
| Editor | Non-destructive audio editor with trim, cut, fade, merge, undo/redo |
| Recorder | Microphone recording with VU meter, live waveform, Whisper transcription |
| Spectrogram | Linear/Mel/CQT spectrograms with custom colormaps |
| Pitch & Time | Pitch shift, time stretch, BPM-synced rate calc |
| Remixer | Per-stem volume, pan, mute/solo mixing console |
| Batch Process | Normalize, convert, fade, trim silence across many files |
| Scheduler | Schedule downloads for later |
| History | Full download history with search and re-download |

### Features

- Track identification via Shazam, MusicBrainz, Chromaprint/AcoustID, Apple Music
- Harmonic mixing with Camelot wheel compatibility
- Smart playlists with energy filtering and harmonic key flow
- Noise reduction, lyrics lookup, Serato crate export, FL Studio integration
- 12 themes: LiveWire (default), Classic Light, Classic Dark, Modern Dark, Synthwave, Dracula, Catppuccin, Tokyo Night, Spotify, LimeWire Classic, Nord, Gruvbox
- Gradient logo bar, icon toolbar, command palette (Ctrl+K), toast notifications
- Drag-and-drop file loading across all tabs (tkinterdnd2)
- Global search in command palette (history + discovery library)
- Editor waveform zoom/scroll (up to 32x) with minimap overview
- Effect chain presets (save/load as JSON)
- Dark title bar via Windows DWM API
- Recent files menu (File > Recent Files)
- Auto-save/restore session state between launches
- Batch stem separation (queue multiple files)
- Export library analysis to CSV
- Send to Player (auto-queue from Discovery)
- Media key shortcuts (Ctrl+Arrow for next/prev/volume)
- Now Playing toast notification on track change
- Snap to zero-crossing for clean Editor cuts
- Anonymized default paths, atomic JSON config writes, thread-safe operations
