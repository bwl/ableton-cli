"""Audio capture via external tools (ffmpeg, sox, jack_capture).

These remain subprocess calls since the tools are GPL/LGPL —
we invoke them as separate processes, which is license-compatible.
"""

import os
import shutil
import subprocess
import time
from pathlib import Path


def _capture_dir() -> Path:
    d = Path(os.environ.get("CAPTURE_DIR", Path(__file__).parent.parent / "captures"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def _outfile() -> Path:
    return _capture_dir() / f"capture_{int(time.time())}.wav"


def capture_seconds(duration: float) -> Path:
    """Capture audio for a given number of seconds. Returns path to WAV file."""
    outfile = _outfile()

    if shutil.which("ffmpeg"):
        # macOS: capture from BlackHole virtual audio device
        subprocess.run(
            [
                "ffmpeg", "-f", "avfoundation",
                "-i", ":BlackHole 2ch",
                "-t", str(duration),
                "-y", "-loglevel", "warning",
                str(outfile),
            ],
            check=True,
        )
    elif shutil.which("sox"):
        subprocess.run(
            ["sox", "-d", "-c", "2", str(outfile), "trim", "0", str(duration)],
            check=True,
        )
    elif shutil.which("jack_capture"):
        subprocess.run(
            ["jack_capture", "--duration", str(duration), str(outfile)],
            check=True,
        )
    else:
        raise RuntimeError("No capture tool found. Install ffmpeg, sox, or jack_capture.")

    return outfile


def capture_bars(bars: float, bpm: float | None = None) -> Path:
    """Capture N bars of audio. If bpm is None, queries Carabiner."""
    if bpm is None:
        from . import link
        bpm = link.get_bpm()

    if bpm is None:
        bpm = 120.0
        print(f"Warning: Could not get BPM from Link, using default {bpm}", flush=True)

    duration = round(bars * 4 * 60 / bpm, 2)
    print(f"Capturing {bars} bars at {bpm} BPM ({duration}s)...", flush=True)
    return capture_seconds(duration)
