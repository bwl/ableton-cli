"""Continuous audio monitor — background capture→analyze loop.

Follows query_session.py daemon thread pattern. Writes latest analysis
to captures/latest_analysis.json for any process to read.
"""

import json
import threading
import time
from pathlib import Path

from . import capture, analyze


class AudioMonitor:
    def __init__(self, interval_bars: int = 4, capture_dir: str | None = None):
        self.interval_bars = interval_bars
        self.capture_dir = Path(capture_dir) if capture_dir else Path("captures")
        self.capture_dir.mkdir(parents=True, exist_ok=True)
        self._stop_event = threading.Event()
        self._thread = None

    def start(self):
        """Spawn daemon thread running the capture→analyze loop."""
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Signal the loop to stop and wait for the thread to finish."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=30)
            self._thread = None

    def _loop(self):
        while not self._stop_event.is_set():
            try:
                path = capture.capture_bars(self.interval_bars)
                result = analyze.full_analysis(
                    str(path), time_series=True, spectrograms=True,
                )
                result["timestamp"] = time.time()
                result["bars"] = self.interval_bars

                out = self.capture_dir / "latest_analysis.json"
                out.write_text(json.dumps(result, indent=2))
            except Exception as e:
                # Write error to the JSON so callers can see what went wrong
                out = self.capture_dir / "latest_analysis.json"
                out.write_text(json.dumps({
                    "error": str(e),
                    "timestamp": time.time(),
                }, indent=2))
                # Brief pause before retrying after error
                time.sleep(2)

    def latest(self) -> dict | None:
        """Read and return the latest analysis JSON."""
        out = self.capture_dir / "latest_analysis.json"
        if out.is_file():
            return json.loads(out.read_text())
        return None


# Module-level singleton API
_monitor: AudioMonitor | None = None


def start(interval_bars: int = 4):
    global _monitor
    if _monitor is not None:
        _monitor.stop()
    _monitor = AudioMonitor(interval_bars=interval_bars)
    _monitor.start()


def stop():
    global _monitor
    if _monitor is not None:
        _monitor.stop()
        _monitor = None


def latest() -> dict | None:
    """Read latest_analysis.json from captures/ (works from any process)."""
    path = Path("captures") / "latest_analysis.json"
    if path.is_file():
        return json.loads(path.read_text())
    return None
