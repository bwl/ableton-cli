"""YAML song format — parse, validate, and serialize song definitions.

The YAML format is the canonical representation of a song, renderable by
either Ableton (via OSC push) or the standalone engine (via pedalboard render).

Note format uses the same P:S:D[:V] notation as the CLI:
  pitch:start_beat:duration_beats[:velocity]
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# ── Data model ────────────────────────────────────────────


@dataclass
class Note:
    pitch: int
    start: float  # beats
    duration: float  # beats
    velocity: int = 100


@dataclass
class Clip:
    name: str
    length: float  # beats
    notes: list[Note] = field(default_factory=list)


@dataclass
class Track:
    name: str
    instrument: str = ""  # path to AU/VST, or placeholder
    preset: str | None = None
    volume: float = 0.85
    pan: float = 0.0
    clips: dict[str, Clip] = field(default_factory=dict)


@dataclass
class Scene:
    name: str
    bars: int = 8
    clips: dict[str, str] = field(default_factory=dict)  # track_name → clip_name


@dataclass
class Song:
    name: str = ""
    key: str = "C"
    bpm: float = 120.0
    time_sig: tuple[int, int] = (4, 4)
    tracks: list[Track] = field(default_factory=list)
    scenes: list[Scene] = field(default_factory=list)
    arrangement: list[str] = field(default_factory=list)
    patterns: dict[str, Clip] = field(default_factory=dict)


# ── Note parsing ──────────────────────────────────────────


def parse_note(s: str) -> Note:
    """Parse P:S:D[:V] string into a Note.

    >>> parse_note("60:0:1:100")
    Note(pitch=60, start=0.0, duration=1.0, velocity=100)
    >>> parse_note("48:2.5:0.5")
    Note(pitch=48, start=2.5, duration=0.5, velocity=100)
    """
    parts = s.split(":")
    if len(parts) < 3:
        raise ValueError(f"note format is pitch:start:duration[:velocity] — got '{s}'")
    pitch = int(parts[0])
    start = float(parts[1])
    dur = float(parts[2])
    vel = int(parts[3]) if len(parts) > 3 else 100
    return Note(pitch=pitch, start=start, duration=dur, velocity=vel)


def format_note(n: Note) -> str:
    """Format a Note back to P:S:D:V string."""
    # Use int-like formatting for start/duration when they're whole numbers
    s = f"{n.start:g}"
    d = f"{n.duration:g}"
    return f"{n.pitch}:{s}:{d}:{n.velocity}"


class _QuotedStr(str):
    """String that YAML will always quote (avoids sexagesimal parsing)."""
    pass


# ── YAML loading ──────────────────────────────────────────


def _require_yaml():
    if not HAS_YAML:
        print("Error: pyyaml required. Install: uv pip install pyyaml", file=sys.stderr)
        sys.exit(1)


def _parse_clip(name: str, data) -> Clip:
    """Parse a clip from YAML data (dict with length + notes)."""
    if isinstance(data, dict):
        length = float(data.get("length", 4))
        raw_notes = data.get("notes", [])
    else:
        raise ValueError(f"clip '{name}': expected dict with length and notes")
    notes = [parse_note(str(n)) for n in raw_notes]
    return Clip(name=name, length=length, notes=notes)


def _parse_clip_ref(name: str, data, patterns: dict[str, Clip]) -> tuple[Clip, int]:
    """Parse a clip entry in a track — either a pattern reference or inline definition.

    Returns (clip, slot).
    """
    if isinstance(data, dict):
        slot = int(data.get("slot", 0))
        if "notes" in data or "length" in data:
            # Inline clip definition
            clip = _parse_clip(name, data)
            return clip, slot
        else:
            # Just a slot reference to a pattern
            if name not in patterns:
                raise ValueError(f"clip '{name}': not found in patterns")
            return patterns[name], slot
    else:
        raise ValueError(f"clip '{name}': expected dict")


def load(path: str | Path) -> Song:
    """Load a Song from a YAML file."""
    _require_yaml()
    path = Path(path)
    with open(path) as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError(f"expected YAML mapping, got {type(raw).__name__}")

    # Meta
    meta = raw.get("meta", {})
    time_sig_raw = meta.get("time_sig", [4, 4])
    if isinstance(time_sig_raw, list) and len(time_sig_raw) == 2:
        time_sig = (int(time_sig_raw[0]), int(time_sig_raw[1]))
    else:
        time_sig = (4, 4)

    song = Song(
        name=meta.get("name", path.stem),
        key=meta.get("key", "C"),
        bpm=float(meta.get("bpm", 120)),
        time_sig=time_sig,
    )

    # Patterns (reusable clip definitions)
    for pname, pdata in raw.get("patterns", {}).items():
        song.patterns[pname] = _parse_clip(pname, pdata)

    # Tracks
    for tdata in raw.get("tracks", []):
        track = Track(
            name=tdata["name"],
            instrument=tdata.get("instrument", ""),
            preset=tdata.get("preset"),
            volume=float(tdata.get("volume", 0.85)),
            pan=float(tdata.get("pan", 0.0)),
        )
        for cname, cdata in tdata.get("clips", {}).items():
            clip, slot = _parse_clip_ref(cname, cdata, song.patterns)
            # Store with slot info embedded in the clip name for push
            clip_with_slot = Clip(name=cname, length=clip.length, notes=list(clip.notes))
            clip_with_slot._slot = slot  # type: ignore[attr-defined]
            track.clips[cname] = clip_with_slot
        song.tracks.append(track)

    # Scenes
    for sdata in raw.get("scenes", []):
        scene = Scene(
            name=sdata["name"],
            bars=int(sdata.get("bars", 8)),
            clips={str(k): str(v) for k, v in sdata.get("clips", {}).items()},
        )
        song.scenes.append(scene)

    # Arrangement
    song.arrangement = [str(s) for s in raw.get("arrangement", [])]

    return song


def save(song: Song, path: str | Path):
    """Save a Song to a YAML file."""
    _require_yaml()
    path = Path(path)

    data: dict = {
        "meta": {
            "name": song.name,
            "key": song.key,
            "bpm": song.bpm,
            "time_sig": list(song.time_sig),
        },
    }

    # Patterns
    if song.patterns:
        data["patterns"] = {}
        for pname, clip in song.patterns.items():
            data["patterns"][pname] = {
                "length": clip.length,
                "notes": [_QuotedStr(format_note(n)) for n in clip.notes],
            }

    # Tracks
    data["tracks"] = []
    for track in song.tracks:
        tdata: dict = {"name": track.name}
        if track.instrument:
            tdata["instrument"] = track.instrument
        if track.preset:
            tdata["preset"] = track.preset
        tdata["volume"] = track.volume
        tdata["pan"] = track.pan
        if track.clips:
            tdata["clips"] = {}
            for cname, clip in track.clips.items():
                slot = getattr(clip, "_slot", 0)
                cdata: dict = {"slot": slot}
                if clip.notes:
                    cdata["length"] = clip.length
                    cdata["notes"] = [format_note(n) for n in clip.notes]
                tdata["clips"][cname] = cdata
        data["tracks"].append(tdata)

    # Scenes
    if song.scenes:
        data["scenes"] = []
        for scene in song.scenes:
            sdata = {"name": scene.name, "bars": scene.bars}
            if scene.clips:
                sdata["clips"] = dict(scene.clips)
            data["scenes"].append(sdata)

    # Arrangement
    if song.arrangement:
        data["arrangement"] = song.arrangement

    # Register representer to force-quote note strings (avoids YAML sexagesimal)
    dumper = yaml.Dumper
    dumper.add_representer(
        _QuotedStr,
        lambda d, s: d.represent_scalar("tag:yaml.org,2002:str", str(s), style='"'),
    )

    with open(path, "w") as f:
        yaml.dump(data, f, Dumper=dumper, default_flow_style=False, sort_keys=False, allow_unicode=True)


# ── Validation ────────────────────────────────────────────


def validate(song: Song) -> list[str]:
    """Validate a Song, returning a list of error/warning strings. Empty = valid."""
    errors = []

    if not song.name:
        errors.append("meta: missing name")
    if song.bpm <= 0:
        errors.append(f"meta: invalid bpm {song.bpm}")

    track_names = {t.name for t in song.tracks}

    # Check pattern references
    for track in song.tracks:
        for cname, clip in track.clips.items():
            for i, note in enumerate(clip.notes):
                if note.pitch < 0 or note.pitch > 127:
                    errors.append(f"track '{track.name}' clip '{cname}' note {i}: pitch {note.pitch} out of range 0-127")
                if note.velocity < 0 or note.velocity > 127:
                    errors.append(f"track '{track.name}' clip '{cname}' note {i}: velocity {note.velocity} out of range 0-127")
                if note.start < 0:
                    errors.append(f"track '{track.name}' clip '{cname}' note {i}: negative start {note.start}")
                if note.duration <= 0:
                    errors.append(f"track '{track.name}' clip '{cname}' note {i}: non-positive duration {note.duration}")

    # Check scenes reference valid tracks and clips
    for scene in song.scenes:
        for tname, cname in scene.clips.items():
            if tname not in track_names:
                errors.append(f"scene '{scene.name}': references unknown track '{tname}'")
                continue
            track = next(t for t in song.tracks if t.name == tname)
            if cname not in track.clips and cname not in song.patterns:
                errors.append(f"scene '{scene.name}': track '{tname}' has no clip '{cname}'")

    # Check arrangement references valid scenes
    scene_names = {s.name for s in song.scenes}
    for sname in song.arrangement:
        if sname not in scene_names:
            errors.append(f"arrangement: references unknown scene '{sname}'")

    return errors


def get_clip_slot(clip: Clip) -> int:
    """Get the slot index for a clip (stored as _slot attribute)."""
    return getattr(clip, "_slot", 0)
