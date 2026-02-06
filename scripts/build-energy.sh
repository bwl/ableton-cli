#!/usr/bin/env bash
# Gradually unmute tracks to build energy over time
set -euo pipefail

OSC_HOST="${OSC_HOST:-localhost}"
OSC_PORT="${OSC_PORT:-11000}"
DELAY="${DELAY:-8}"    # seconds between each track coming in

# Tracks to unmute in order (override via args or default 1-5)
if [[ $# -gt 0 ]]; then
    TRACKS=("$@")
else
    TRACKS=(1 2 3 4 5)
fi

echo "Building energy: tracks ${TRACKS[*]}, ${DELAY}s between each"

for track in "${TRACKS[@]}"; do
    echo "→ Bringing in track $track"
    oscsend "$OSC_HOST" "$OSC_PORT" /live/track/set/mute iii "$track" 0
    sleep "$DELAY"
done

echo "All tracks in."
