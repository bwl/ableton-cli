#!/usr/bin/env bash
# 8th note hi-hats (F#1 = 42)
set -euo pipefail
DEV="${MIDI_DEV:-IAC Driver Bus 1}"
for i in {1..8}; do
    sendmidi dev "$DEV" on 42 80 sleep 62 off 42
done
