"""Offline renderer — YAML song → WAV via pedalboard + AU/VST plugins.

Renders MIDI notes through AU/VST instruments without Ableton.
Requires: pip install pedalboard soundfile

This module is GPLv3-adjacent (pedalboard is GPLv3) and is loaded
only when explicitly requested via `render` command or `.[render]` extras.
"""

from __future__ import annotations

import sys

import numpy as np

try:
    import pedalboard
    from pedalboard.io import AudioFile

    HAS_PEDALBOARD = True
except ImportError:
    HAS_PEDALBOARD = False

try:
    import soundfile as sf

    HAS_SOUNDFILE = True
except ImportError:
    HAS_SOUNDFILE = False


def _require_deps():
    if not HAS_PEDALBOARD:
        print("Error: pedalboard required for rendering. Install: uv pip install -e '.[render]'", file=sys.stderr)
        sys.exit(1)
    if not HAS_SOUNDFILE:
        print("Error: soundfile required for rendering. Install: uv pip install -e '.[render]'", file=sys.stderr)
        sys.exit(1)


def _notes_to_midi_messages(notes, bpm: float):
    """Convert Note objects to a list of (time_seconds, message) tuples for pedalboard.

    Returns a list of mido Message objects sorted by time.
    """
    import mido

    events = []
    spb = 60.0 / bpm  # seconds per beat

    for note in notes:
        on_time = note.start * spb
        off_time = (note.start + note.duration) * spb
        events.append((on_time, mido.Message("note_on", note=note.pitch, velocity=note.velocity, channel=0)))
        events.append((off_time, mido.Message("note_off", note=note.pitch, velocity=0, channel=0)))

    events.sort(key=lambda e: e[0])
    return events


def _load_plugin(instrument_path: str, preset: str | None = None):
    """Load an AU or VST3 plugin via pedalboard."""
    _require_deps()

    if instrument_path.endswith(".component"):
        plugin = pedalboard.load_plugin(instrument_path, plugin_discovery_timeout_seconds=10.0)
    elif instrument_path.endswith(".vst3"):
        plugin = pedalboard.load_plugin(instrument_path, plugin_discovery_timeout_seconds=10.0)
    else:
        raise ValueError(f"Unsupported plugin format: {instrument_path} (expected .component or .vst3)")

    # TODO: preset loading if pedalboard supports it
    return plugin


def render_track(track, clip, duration_beats: float, bpm: float, sr: int = 44100) -> np.ndarray:
    """Render a single track+clip to audio via its AU/VST instrument.

    Returns stereo numpy array of shape (2, num_samples).
    """
    _require_deps()

    spb = 60.0 / bpm
    duration_s = duration_beats * spb
    num_samples = int(duration_s * sr)

    # Check if instrument is an Ableton placeholder
    if track.instrument.startswith("(Ableton)") or not track.instrument:
        # Can't render Ableton-native instruments — return silence
        print(f"  Skipping '{track.name}' (Ableton-only instrument)", file=sys.stderr)
        return np.zeros((2, num_samples), dtype=np.float32)

    plugin = _load_plugin(track.instrument, track.preset)

    # Convert notes to MIDI messages
    events = _notes_to_midi_messages(clip.notes, bpm)

    # Build MIDI message list for pedalboard
    midi_messages = []
    for time_s, msg in events:
        midi_messages.append((time_s, msg))

    # Render through plugin
    # pedalboard's __call__ on instrument plugins accepts MIDI
    audio = plugin(
        np.zeros((2, num_samples), dtype=np.float32),
        sample_rate=sr,
        midi_messages=midi_messages,
    )

    return audio


def render_scene(song, scene_idx: int, sr: int = 44100) -> np.ndarray:
    """Render all active tracks for a scene, mix with volume/pan."""
    scene = song.scenes[scene_idx]
    beats_per_bar = song.time_sig[0]
    duration_beats = scene.bars * beats_per_bar
    spb = 60.0 / song.bpm
    duration_s = duration_beats * spb
    num_samples = int(duration_s * sr)

    track_audios = []
    track_metas = []

    for tname, cname in scene.clips.items():
        # Find the track
        track = next((t for t in song.tracks if t.name == tname), None)
        if track is None:
            print(f"  Warning: track '{tname}' not found, skipping", file=sys.stderr)
            continue

        # Find the clip (check track clips, then patterns)
        clip = track.clips.get(cname) or song.patterns.get(cname)
        if clip is None:
            print(f"  Warning: clip '{cname}' not found on track '{tname}', skipping", file=sys.stderr)
            continue

        print(f"  Rendering {tname}: {cname}...")
        audio = render_track(track, clip, duration_beats, song.bpm, sr=sr)

        # Ensure correct length (pad or trim)
        if audio.shape[1] < num_samples:
            pad = np.zeros((2, num_samples - audio.shape[1]), dtype=np.float32)
            audio = np.concatenate([audio, pad], axis=1)
        elif audio.shape[1] > num_samples:
            audio = audio[:, :num_samples]

        track_audios.append(audio)
        track_metas.append({"volume": track.volume, "pan": track.pan})

    if not track_audios:
        return np.zeros((2, num_samples), dtype=np.float32)

    return mix_tracks(track_audios, track_metas, sr=sr)


def render_arrangement(song, sr: int = 44100) -> np.ndarray:
    """Render full arrangement (scene sequence) to audio."""
    segments = []
    for i, scene_name in enumerate(song.arrangement):
        scene_idx = next(
            (j for j, s in enumerate(song.scenes) if s.name == scene_name), None
        )
        if scene_idx is None:
            print(f"  Warning: scene '{scene_name}' not found, skipping", file=sys.stderr)
            continue
        print(f"Scene {i}: {scene_name}")
        segment = render_scene(song, scene_idx, sr=sr)
        segments.append(segment)

    if not segments:
        return np.zeros((2, 0), dtype=np.float32)

    return np.concatenate(segments, axis=1)


def mix_tracks(track_audios: list[np.ndarray], track_metas: list[dict], sr: int = 44100) -> np.ndarray:
    """Sum tracks with volume scaling + constant-power panning.

    Each track_meta has 'volume' (0-1) and 'pan' (-1 to 1, negative = left).
    """
    import math

    if not track_audios:
        return np.zeros((2, 0), dtype=np.float32)

    max_len = max(a.shape[1] for a in track_audios)
    mix = np.zeros((2, max_len), dtype=np.float64)

    for audio, meta in zip(track_audios, track_metas):
        vol = meta.get("volume", 0.85)
        pan = meta.get("pan", 0.0)

        # Constant-power pan: pan in [-1, 1] → angle in [0, pi/2]
        angle = (pan + 1.0) / 2.0 * (math.pi / 2.0)
        gain_l = vol * math.cos(angle)
        gain_r = vol * math.sin(angle)

        # Ensure audio is padded to max_len
        if audio.shape[1] < max_len:
            pad = np.zeros((2, max_len - audio.shape[1]), dtype=np.float32)
            audio = np.concatenate([audio, pad], axis=1)

        mix[0] += audio[0] * gain_l
        mix[1] += audio[1] * gain_r

    # Soft-clip to prevent digital clipping
    peak = np.max(np.abs(mix))
    if peak > 1.0:
        mix /= peak
        print(f"  Mix normalized (peak was {peak:.2f})", file=sys.stderr)

    return mix.astype(np.float32)


def render_to_file(audio: np.ndarray, path: str, sr: int = 44100):
    """Write stereo audio to WAV file."""
    _require_deps()

    # Ensure 2D stereo
    if audio.ndim == 1:
        audio = np.stack([audio, audio])
    elif audio.shape[0] != 2:
        audio = audio[:2]

    with AudioFile(path, "w", samplerate=sr, num_channels=2) as f:
        f.write(audio)

    print(f"  Wrote {path} ({audio.shape[1] / sr:.1f}s, {sr}Hz stereo)")
