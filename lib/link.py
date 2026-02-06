"""Carabiner (Ableton Link) client via TCP sockets.

Replaces nc shell-outs with stdlib socket calls.
Carabiner is GPL so we only talk to it over TCP — no vendoring.
"""

import os
import re
import socket


def _host():
    return os.environ.get("CARABINER_HOST", "localhost")


def _port():
    return int(os.environ.get("CARABINER_PORT", "17000"))


def _send(command: str, timeout: float = 2.0) -> str:
    """Send a command to Carabiner and return the response."""
    try:
        with socket.create_connection((_host(), _port()), timeout=timeout) as sock:
            sock.sendall((command + "\n").encode())
            sock.settimeout(timeout)
            data = sock.recv(4096)
            return data.decode().strip()
    except (ConnectionRefusedError, OSError):
        return ""


def status() -> str:
    """Get Link session status. Returns raw Carabiner status string."""
    result = _send("status")
    if not result:
        return f"Carabiner not running on {_host()}:{_port()}"
    return result


def get_bpm() -> float | None:
    """Extract BPM from Link status."""
    result = _send("status")
    match = re.search(r":bpm\s+([\d.]+)", result)
    if match:
        return float(match.group(1))
    return None


def set_tempo(bpm: float):
    """Set Link tempo."""
    _send(f"bpm {bpm}")


def start():
    """Enable start/stop sync and start playing."""
    _send("enable-start-stop-sync")
    _send("start-playing")


def stop():
    """Stop playing."""
    _send("stop-playing")
