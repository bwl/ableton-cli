"""OSC client for AbletonOSC control.

Replaces oscsend shell-outs with direct python-osc calls.
All Ableton Live Object Model operations go through here.
"""

import os
from pythonosc.udp_client import SimpleUDPClient


def _client():
    host = os.environ.get("OSC_HOST", "127.0.0.1")
    port = int(os.environ.get("OSC_PORT", "11000"))
    return SimpleUDPClient(host, port)


# ── Transport ──────────────────────────────────────────────

def play():
    _client().send_message("/live/song/start_playing", [])


def stop():
    _client().send_message("/live/song/stop_playing", [])


def set_tempo(bpm: float):
    _client().send_message("/live/song/set/tempo", [float(bpm)])


# ── Track Management ──────────────────────────────────────

def create_midi_track(index: int = -1):
    """Create a MIDI track at index (-1 = append at end)."""
    _client().send_message("/live/song/create_midi_track", [int(index)])


def create_audio_track(index: int = -1):
    """Create an audio track at index (-1 = append at end)."""
    _client().send_message("/live/song/create_audio_track", [int(index)])


def delete_track(track: int):
    _client().send_message("/live/song/delete_track", [int(track)])


def duplicate_track(track: int):
    _client().send_message("/live/song/duplicate_track", [int(track)])


def set_track_name(track: int, name: str):
    _client().send_message("/live/track/set/name", [int(track), name])


# ── Clips & Scenes ────────────────────────────────────────

def create_clip(track: int, slot: int, length_beats: float = 4.0):
    """Create an empty MIDI clip in a clip slot."""
    _client().send_message("/live/clip_slot/create_clip", [int(track), int(slot), float(length_beats)])


def delete_clip(track: int, slot: int):
    _client().send_message("/live/clip_slot/delete_clip", [int(track), int(slot)])


def set_clip_name(track: int, slot: int, name: str):
    _client().send_message("/live/clip/set/name", [int(track), int(slot), name])


def add_notes(track: int, slot: int, notes: list[tuple[int, float, float, int, int]]):
    """Add MIDI notes to a clip.

    Each note is (pitch, start_beat, duration_beats, velocity, mute).
    mute: 0 = normal, 1 = muted.
    """
    flat = [int(track), int(slot)]
    for pitch, start, dur, vel, muted in notes:
        flat.extend([int(pitch), float(start), float(dur), int(vel), int(muted)])
    _client().send_message("/live/clip/add/notes", flat)


def remove_notes(track: int, slot: int):
    """Remove all notes from a clip."""
    _client().send_message("/live/clip/remove/notes", [int(track), int(slot)])


def get_notes(track: int, slot: int):
    """Request notes from a clip (response comes on /live/clip/get/notes)."""
    _client().send_message("/live/clip/get/notes", [int(track), int(slot)])


def fire_clip(track: int, clip: int):
    _client().send_message("/live/clip/fire", [int(track), int(clip)])


def stop_clip(track: int, clip: int):
    _client().send_message("/live/clip/stop", [int(track), int(clip)])


def fire_scene(scene: int):
    _client().send_message("/live/scene/fire", [int(scene)])


def set_scene_name(scene: int, name: str):
    _client().send_message("/live/scene/set/name", [int(scene), name])


# ── Track Mixer ────────────────────────────────────────────

def mute(track: int):
    _client().send_message("/live/track/set/mute", [int(track), 1])


def unmute(track: int):
    _client().send_message("/live/track/set/mute", [int(track), 0])


def solo(track: int):
    _client().send_message("/live/track/set/solo", [int(track), 1])


def unsolo(track: int):
    _client().send_message("/live/track/set/solo", [int(track), 0])


def set_volume(track: int, level: float):
    _client().send_message("/live/track/set/volume", [int(track), float(level)])


def set_pan(track: int, value: float):
    _client().send_message("/live/track/set/panning", [int(track), float(value)])


def arm(track: int):
    _client().send_message("/live/track/set/arm", [int(track), 1])


def disarm(track: int):
    _client().send_message("/live/track/set/arm", [int(track), 0])


# ── Devices ────────────────────────────────────────────────

def set_device_param(track: int, device: int, param: int, value: float):
    _client().send_message(
        "/live/device/set/parameter/value",
        [int(track), int(device), int(param), float(value)],
    )


# ── Raw send (for advanced use) ────────────────────────────

def send(address: str, *args):
    _client().send_message(address, list(args))
