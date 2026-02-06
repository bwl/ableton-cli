#!/usr/bin/env bash
# Simple arpeggiator: plays root, 3rd, 5th, octave
set -euo pipefail
DEV="${MIDI_DEV:-IAC Driver Bus 1}"
ROOT=${1:-60}
SPEED=${2:-100}  # ms between notes
VEL=100

for offset in 0 4 7 12; do
    note=$((ROOT + offset))
    sendmidi dev "$DEV" on $note $VEL sleep "$SPEED" off $note
done
