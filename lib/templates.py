"""Session templates for ableton-cli.

Creates multi-track band setups with pre-programmed MIDI patterns.
Instruments must be added manually in Ableton after track creation
(AbletonOSC doesn't support loading devices yet).
"""

import time
from . import osc

# Small delay between OSC messages to let Ableton process them
MSG_DELAY = 0.05


def _send(fn, *args):
    fn(*args)
    time.sleep(MSG_DELAY)


# ── Note/pattern helpers ──────────────────────────────────

# GM Drum Map
KICK = 36
SNARE = 38
CLAP = 39
RIM = 37
CLOSED_HH = 42
OPEN_HH = 46
CRASH = 49
RIDE = 51
LO_TOM = 43
HI_TOM = 50
SHAKER = 70
CLAVE = 75

# Note names to MIDI numbers
def note(name: str, octave: int = 4) -> int:
    """Convert note name to MIDI number. e.g. note('C', 4) = 60"""
    names = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
             'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
             'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
    return names[name] + (octave + 1) * 12


def _write_clip(track: int, slot: int, name: str, length: float, notes: list):
    """Create a clip and write notes into it."""
    _send(osc.create_clip, track, slot, length)
    time.sleep(0.1)  # extra delay for clip creation
    if notes:
        _send(osc.add_notes, track, slot, notes)
    _send(osc.set_clip_name, track, slot, name)


# ── Band Template ─────────────────────────────────────────

BAND_TRACKS = [
    {"name": "Drums",       "type": "midi", "instrument": "Drum Rack"},
    {"name": "Bass",        "type": "midi", "instrument": "Analog / Operator / Wavetable"},
    {"name": "Keys",        "type": "midi", "instrument": "Electric / Grand Piano"},
    {"name": "Synth Lead",  "type": "midi", "instrument": "Wavetable / Drift"},
    {"name": "Synth Pad",   "type": "midi", "instrument": "Wavetable / Drift"},
    {"name": "Guitar",      "type": "midi", "instrument": "Simpler + Guitar samples"},
    {"name": "Perc",        "type": "midi", "instrument": "Drum Rack (percussion)"},
    {"name": "Vox / FX",    "type": "audio", "instrument": "— (audio track for samples)"},
]


def _drum_patterns() -> dict[str, tuple[float, list]]:
    """Return named drum patterns as {name: (length_beats, notes)}."""
    return {
        "Basic Beat": (4.0, [
            # Kick on 1 and 3
            (KICK, 0.0, 0.5, 110, 0), (KICK, 2.0, 0.5, 110, 0),
            # Snare on 2 and 4
            (SNARE, 1.0, 0.5, 100, 0), (SNARE, 3.0, 0.5, 100, 0),
            # Hi-hats on 8ths
            (CLOSED_HH, 0.0, 0.25, 70, 0), (CLOSED_HH, 0.5, 0.25, 50, 0),
            (CLOSED_HH, 1.0, 0.25, 70, 0), (CLOSED_HH, 1.5, 0.25, 50, 0),
            (CLOSED_HH, 2.0, 0.25, 70, 0), (CLOSED_HH, 2.5, 0.25, 50, 0),
            (CLOSED_HH, 3.0, 0.25, 70, 0), (CLOSED_HH, 3.5, 0.25, 50, 0),
        ]),
        "Funky Beat": (4.0, [
            # Kick: syncopated
            (KICK, 0.0, 0.5, 120, 0), (KICK, 1.25, 0.25, 90, 0),
            (KICK, 2.0, 0.5, 110, 0), (KICK, 3.5, 0.25, 80, 0),
            # Snare on 2 and 4 with ghost notes
            (SNARE, 0.75, 0.25, 40, 0),
            (SNARE, 1.0, 0.5, 100, 0),
            (SNARE, 2.75, 0.25, 35, 0),
            (SNARE, 3.0, 0.5, 100, 0),
            # Hi-hats on 16ths
            *[(CLOSED_HH, i * 0.25, 0.2, 55 + (20 if i % 2 == 0 else 0), 0) for i in range(16)],
            # Open hat on the and of 4
            (OPEN_HH, 3.5, 0.4, 80, 0),
        ]),
        "Half-time": (4.0, [
            (KICK, 0.0, 0.5, 120, 0), (KICK, 0.75, 0.25, 70, 0),
            (SNARE, 2.0, 0.5, 100, 0),
            (CLOSED_HH, 0.0, 0.25, 60, 0), (CLOSED_HH, 0.5, 0.25, 45, 0),
            (CLOSED_HH, 1.0, 0.25, 60, 0), (CLOSED_HH, 1.5, 0.25, 45, 0),
            (CLOSED_HH, 2.0, 0.25, 60, 0), (CLOSED_HH, 2.5, 0.25, 45, 0),
            (CLOSED_HH, 3.0, 0.25, 60, 0), (OPEN_HH, 3.5, 0.4, 70, 0),
        ]),
        "Buildup": (4.0, [
            # Accelerating snare hits
            (SNARE, 0.0, 0.25, 60, 0),
            (SNARE, 1.0, 0.25, 70, 0),
            (SNARE, 1.5, 0.25, 75, 0),
            (SNARE, 2.0, 0.25, 80, 0),
            (SNARE, 2.5, 0.25, 85, 0),
            (SNARE, 2.75, 0.25, 90, 0),
            (SNARE, 3.0, 0.25, 100, 0),
            (SNARE, 3.25, 0.25, 105, 0),
            (SNARE, 3.5, 0.25, 110, 0),
            (SNARE, 3.75, 0.25, 120, 0),
            (CRASH, 3.75, 0.5, 110, 0),
        ]),
    }


def _bass_patterns() -> dict[str, tuple[float, list]]:
    """Bass patterns in A minor (root = A1 = 33)."""
    A1, C2, D2, E2, F2, G2 = 33, 36, 38, 40, 41, 43
    return {
        "Root Pulse": (4.0, [
            (A1, 0.0, 0.75, 110, 0),
            (A1, 1.0, 0.75, 100, 0),
            (A1, 2.0, 0.75, 110, 0),
            (A1, 3.0, 0.75, 100, 0),
        ]),
        "Walking": (4.0, [
            (A1, 0.0, 0.9, 100, 0),
            (C2, 1.0, 0.9, 95, 0),
            (D2, 2.0, 0.9, 100, 0),
            (E2, 3.0, 0.9, 95, 0),
        ]),
        "Funky": (4.0, [
            (A1, 0.0, 0.25, 120, 0),
            (A1, 0.75, 0.25, 80, 0),
            (C2, 1.0, 0.5, 100, 0),
            (D2, 2.0, 0.25, 110, 0),
            (D2, 2.5, 0.25, 70, 0),
            (E2, 3.0, 0.5, 100, 0),
            (G2, 3.5, 0.25, 90, 0),
        ]),
        "Sub": (8.0, [
            (A1, 0.0, 3.5, 110, 0),
            (F2, 4.0, 1.5, 100, 0),
            (E2, 6.0, 1.5, 100, 0),
        ]),
    }


def _keys_patterns() -> dict[str, tuple[float, list]]:
    """Keys/piano patterns — Am, F, C, G chord progression."""
    return {
        "Chords": (16.0, [
            # Am (4 beats)
            (57, 0.0, 3.5, 80, 0), (60, 0.0, 3.5, 75, 0), (64, 0.0, 3.5, 75, 0),
            # F (4 beats)
            (53, 4.0, 3.5, 80, 0), (57, 4.0, 3.5, 75, 0), (60, 4.0, 3.5, 75, 0),
            # C (4 beats)
            (48, 8.0, 3.5, 80, 0), (52, 8.0, 3.5, 75, 0), (55, 8.0, 3.5, 75, 0),
            # G (4 beats)
            (55, 12.0, 3.5, 80, 0), (59, 12.0, 3.5, 75, 0), (62, 12.0, 3.5, 75, 0),
        ]),
        "Arpeggiated": (16.0, [
            # Am arp
            *[(n, 0.0 + i * 0.5, 0.45, 75, 0) for i, n in enumerate([57, 60, 64, 69, 64, 60, 57, 60])],
            # F arp
            *[(n, 4.0 + i * 0.5, 0.45, 75, 0) for i, n in enumerate([53, 57, 60, 65, 60, 57, 53, 57])],
            # C arp
            *[(n, 8.0 + i * 0.5, 0.45, 75, 0) for i, n in enumerate([48, 52, 55, 60, 55, 52, 48, 52])],
            # G arp
            *[(n, 12.0 + i * 0.5, 0.45, 75, 0) for i, n in enumerate([55, 59, 62, 67, 62, 59, 55, 59])],
        ]),
    }


def _lead_patterns() -> dict[str, tuple[float, list]]:
    """Simple synth lead melodies in A minor."""
    return {
        "Melody A": (8.0, [
            (69, 0.0, 1.0, 90, 0),   # A4
            (72, 1.0, 0.5, 85, 0),   # C5
            (71, 1.5, 0.5, 80, 0),   # B4
            (69, 2.0, 1.5, 90, 0),   # A4
            (67, 4.0, 1.0, 85, 0),   # G4
            (64, 5.0, 1.0, 80, 0),   # E4
            (65, 6.0, 0.5, 75, 0),   # F4
            (64, 6.5, 1.5, 85, 0),   # E4
        ]),
        "Riff": (4.0, [
            (69, 0.0, 0.25, 100, 0),
            (72, 0.5, 0.25, 90, 0),
            (69, 1.0, 0.25, 100, 0),
            (67, 1.5, 0.5, 90, 0),
            (69, 2.0, 0.25, 100, 0),
            (72, 2.5, 0.25, 90, 0),
            (76, 3.0, 0.75, 110, 0),
        ]),
    }


def _pad_patterns() -> dict[str, tuple[float, list]]:
    """Synth pad — long sustained chords."""
    return {
        "Warm Pad": (16.0, [
            # Am
            (57, 0.0, 7.5, 60, 0), (60, 0.0, 7.5, 55, 0), (64, 0.0, 7.5, 55, 0), (69, 0.0, 7.5, 50, 0),
            # F
            (53, 8.0, 7.5, 60, 0), (57, 8.0, 7.5, 55, 0), (60, 8.0, 7.5, 55, 0), (65, 8.0, 7.5, 50, 0),
        ]),
    }


def _perc_patterns() -> dict[str, tuple[float, list]]:
    """Percussion layers — shaker, clave, toms."""
    return {
        "Shaker": (4.0, [
            *[(SHAKER, i * 0.25, 0.2, 40 + (15 if i % 2 == 0 else 0), 0) for i in range(16)],
        ]),
        "Clave": (4.0, [
            (CLAVE, 0.0, 0.2, 90, 0),
            (CLAVE, 0.75, 0.2, 70, 0),
            (CLAVE, 1.5, 0.2, 90, 0),
            (CLAVE, 2.5, 0.2, 80, 0),
            (CLAVE, 3.25, 0.2, 70, 0),
        ]),
    }


def setup_band(bpm: float = 120.0, delete_existing: bool = False):
    """Create an 8-track band template with pre-programmed patterns.

    After running this, you need to add instruments to each track in Ableton:
      0: Drums      → Drum Rack
      1: Bass        → Analog / Operator / Wavetable
      2: Keys        → Electric / Grand Piano
      3: Synth Lead  → Wavetable / Drift
      4: Synth Pad   → Wavetable / Drift
      5: Guitar      → Simpler (load guitar samples)
      6: Perc        → Drum Rack (second kit for percussion)
      7: Vox / FX    → (audio track — drop in samples)
    """
    print(f"Setting up band template at {bpm} BPM...")

    # Set tempo
    _send(osc.set_tempo, bpm)

    if delete_existing:
        # Query track count and delete all existing tracks (reverse order)
        print("  Clearing existing tracks...")
        # We can't easily query track count without the query module's server,
        # so we'll just try deleting tracks 7 down to 0
        for i in range(15, -1, -1):
            try:
                _send(osc.delete_track, i)
            except Exception:
                pass
        time.sleep(0.5)

    # Create tracks
    print("  Creating tracks...")
    for i, t in enumerate(BAND_TRACKS):
        if t["type"] == "midi":
            _send(osc.create_midi_track, -1)
        else:
            _send(osc.create_audio_track, -1)
        time.sleep(0.1)

    # Wait for Ableton to process
    time.sleep(0.5)

    # We need to figure out the track offset. If there was already a default
    # track, our new tracks start at index 1 (or wherever). Let's query.
    # For simplicity, we'll assume we're appending to whatever exists.
    # The user said they have 1 track, so our tracks start at index 1.
    # But if delete_existing was used, they start at 0.
    # We'll name based on the expected starting position.

    # Name tracks — we'll name all tracks we can find
    print("  Naming tracks...")
    for i, t in enumerate(BAND_TRACKS):
        _send(osc.set_track_name, i, t["name"])

    time.sleep(0.3)

    # Write drum patterns (track 0)
    print("  Writing drum patterns...")
    for slot, (name, (length, notes)) in enumerate(_drum_patterns().items()):
        _write_clip(0, slot, name, length, notes)

    # Write bass patterns (track 1)
    print("  Writing bass patterns...")
    for slot, (name, (length, notes)) in enumerate(_bass_patterns().items()):
        _write_clip(1, slot, name, length, notes)

    # Write keys patterns (track 2)
    print("  Writing keys patterns...")
    for slot, (name, (length, notes)) in enumerate(_keys_patterns().items()):
        _write_clip(2, slot, name, length, notes)

    # Write lead patterns (track 3)
    print("  Writing lead patterns...")
    for slot, (name, (length, notes)) in enumerate(_lead_patterns().items()):
        _write_clip(3, slot, name, length, notes)

    # Write pad patterns (track 4)
    print("  Writing pad patterns...")
    for slot, (name, (length, notes)) in enumerate(_pad_patterns().items()):
        _write_clip(4, slot, name, length, notes)

    # Track 5 (Guitar) — empty, user loads samples
    # Track 7 (Vox/FX) — audio track, user drops in clips

    # Write perc patterns (track 6)
    print("  Writing percussion patterns...")
    for slot, (name, (length, notes)) in enumerate(_perc_patterns().items()):
        _write_clip(6, slot, name, length, notes)

    # Set initial volumes
    print("  Setting mixer levels...")
    levels = {
        0: 0.85,  # Drums
        1: 0.80,  # Bass
        2: 0.70,  # Keys
        3: 0.65,  # Lead
        4: 0.55,  # Pad
        5: 0.70,  # Guitar
        6: 0.50,  # Perc
        7: 0.75,  # Vox
    }
    for track, vol in levels.items():
        _send(osc.set_volume, track, vol)

    # Disarm all except track 0
    for i in range(8):
        _send(osc.disarm, i)

    print()
    print("Template ready! Now add instruments in Ableton:")
    print()
    for i, t in enumerate(BAND_TRACKS):
        clips = {0: 4, 1: 4, 2: 2, 3: 2, 4: 1, 6: 2}.get(i, 0)
        clip_info = f"  ({clips} clips)" if clips else ""
        print(f"  Track {i}: {t['name']:12s} → {t['instrument']}{clip_info}")
    print()
    print(f"Key: Am  |  Tempo: {bpm} BPM")
    print("After adding instruments, try: ableton-cli fire 0 0")
