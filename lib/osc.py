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


# ── Clips & Scenes ────────────────────────────────────────

def fire_clip(track: int, clip: int):
    _client().send_message("/live/clip/fire", [int(track), int(clip)])


def stop_clip(track: int, clip: int):
    _client().send_message("/live/clip/stop", [int(track), int(clip)])


def fire_scene(scene: int):
    _client().send_message("/live/song/fire_scene", [int(scene)])


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
