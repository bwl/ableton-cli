"""MIDI engine using mido + python-rtmidi.

Replaces sendmidi/receivemidi shell-outs with direct Python calls.
Both mido (MIT) and python-rtmidi (MIT) can be fully vendored.
"""

import os
import time
import mido


def _port_name():
    return os.environ.get("MIDI_DEV", "IAC Driver Bus 1")


def list_ports():
    """List available MIDI input and output ports."""
    return {
        "inputs": mido.get_input_names(),
        "outputs": mido.get_output_names(),
    }


# ── Single Messages ───────────────────────────────────────

def send_note(note: int, velocity: int = 100, duration_ms: int = 500, channel: int = 0):
    """Send a note on/off pair."""
    with mido.open_output(_port_name()) as port:
        port.send(mido.Message("note_on", note=note, velocity=velocity, channel=channel))
        time.sleep(duration_ms / 1000)
        port.send(mido.Message("note_off", note=note, velocity=0, channel=channel))


def send_cc(cc: int, value: int, channel: int = 0):
    """Send a CC message."""
    with mido.open_output(_port_name()) as port:
        port.send(mido.Message("control_change", control=cc, value=value, channel=channel))


def send_program_change(program: int, channel: int = 0):
    """Send a program change."""
    with mido.open_output(_port_name()) as port:
        port.send(mido.Message("program_change", program=program, channel=channel))


# ── Chords ─────────────────────────────────────────────────

CHORD_INTERVALS = {
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "7th": [0, 4, 7, 10],
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
}


def send_chord(root: int, chord_type: str = "major", velocity: int = 100,
               duration_ms: int = 1000, channel: int = 0):
    """Send a chord (all notes on, wait, all notes off)."""
    intervals = CHORD_INTERVALS.get(chord_type)
    if intervals is None:
        raise ValueError(f"Unknown chord type: {chord_type}. "
                         f"Available: {', '.join(CHORD_INTERVALS)}")

    notes = [root + i for i in intervals if root + i <= 127]

    with mido.open_output(_port_name()) as port:
        for n in notes:
            port.send(mido.Message("note_on", note=n, velocity=velocity, channel=channel))
        time.sleep(duration_ms / 1000)
        for n in notes:
            port.send(mido.Message("note_off", note=n, velocity=0, channel=channel))


# ── Patterns ───────────────────────────────────────────────

# GM drum map
KICK = 36
SNARE = 38
CLAP = 39
CLOSED_HH = 42
OPEN_HH = 46
CRASH = 49
RIDE = 51

# Pattern format: list of (note | None, velocity, duration_in_beats)
PATTERNS = {
    "four-on-floor": [
        (KICK, 127, 1), (KICK, 127, 1), (KICK, 127, 1), (KICK, 127, 1),
    ],
    "backbeat": [
        (KICK, 127, 1), (SNARE, 100, 1), (KICK, 127, 1), (SNARE, 100, 1),
    ],
    "8th-hats": [(CLOSED_HH, 80, 0.5)] * 8,
    "16th-hats": [(CLOSED_HH, 60, 0.25)] * 16,
    "boom-bap": [
        (KICK, 127, 0.75), (None, 0, 0.25),
        (SNARE, 100, 0.5), (None, 0, 0.5),
        (None, 0, 0.25), (KICK, 110, 0.25),
        (KICK, 100, 0.5), (SNARE, 100, 1),
    ],
    "house": [
        (KICK, 127, 0.5), (CLOSED_HH, 60, 0.5),
        (KICK, 127, 0.25), (CLOSED_HH, 80, 0.25),
        (SNARE, 90, 0.5), (KICK, 127, 0.5),
        (CLOSED_HH, 60, 0.5), (KICK, 127, 0.5),
        (CLOSED_HH, 80, 0.25), (CLAP, 100, 0.25),
    ],
}


def play_pattern(pattern_name: str, bpm: int = 120, repeats: int = 1, channel: int = 9):
    """Play a named drum pattern."""
    if pattern_name not in PATTERNS:
        raise ValueError(f"Unknown pattern: {pattern_name}. "
                         f"Available: {', '.join(sorted(PATTERNS))}")

    pattern = PATTERNS[pattern_name]
    beat_duration = 60 / bpm

    with mido.open_output(_port_name()) as port:
        for _ in range(repeats):
            for note, vel, dur in pattern:
                if note is not None:
                    port.send(mido.Message("note_on", note=note, velocity=vel, channel=channel))
                    time.sleep(beat_duration * dur * 0.9)
                    port.send(mido.Message("note_off", note=note, velocity=0, channel=channel))
                    time.sleep(beat_duration * dur * 0.1)
                else:
                    time.sleep(beat_duration * dur)


def list_patterns() -> dict[str, float]:
    """Return pattern names and their length in beats."""
    return {name: sum(d for _, _, d in pat) for name, pat in sorted(PATTERNS.items())}
