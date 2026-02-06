#!/usr/bin/env bash
# Play through scenes in sequence with configurable wait time
set -euo pipefail

SCENES="${1:-4}"       # number of scenes to fire
WAIT="${2:-8}"         # seconds between scenes
OSC_HOST="${OSC_HOST:-localhost}"
OSC_PORT="${OSC_PORT:-11000}"

for scene in $(seq 0 $((SCENES - 1))); do
    echo "→ Firing scene $scene"
    oscsend "$OSC_HOST" "$OSC_PORT" /live/song/fire_scene i "$scene"
    if [[ $scene -lt $((SCENES - 1)) ]]; then
        sleep "$WAIT"
    fi
done

echo "Done."
