#!/usr/bin/env bash
# Fire random clips for generative composition
set -euo pipefail

OSC_HOST="${OSC_HOST:-localhost}"
OSC_PORT="${OSC_PORT:-11000}"
TRACKS="${1:-4}"       # number of tracks
CLIPS="${2:-8}"        # number of clip slots
MIN_WAIT="${3:-2}"     # minimum seconds between fires
MAX_WAIT="${4:-6}"     # maximum seconds between fires

echo "Random clip mode: ${TRACKS} tracks, ${CLIPS} clips, ${MIN_WAIT}-${MAX_WAIT}s intervals"
echo "Press Ctrl+C to stop"

while true; do
    track=$((RANDOM % TRACKS))
    clip=$((RANDOM % CLIPS))
    echo "→ Fire track $track, clip $clip"
    oscsend "$OSC_HOST" "$OSC_PORT" /live/clip/fire ii "$track" "$clip"
    wait_time=$((RANDOM % (MAX_WAIT - MIN_WAIT + 1) + MIN_WAIT))
    sleep "$wait_time"
done
