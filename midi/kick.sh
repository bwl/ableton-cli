#!/usr/bin/env bash
# 4-on-the-floor kick pattern (C1 = 36)
set -euo pipefail
DEV="${MIDI_DEV:-IAC Driver Bus 1}"
sendmidi dev "$DEV" \
    on 36 127 sleep 125 off 36 \
    on 36 127 sleep 125 off 36 \
    on 36 127 sleep 125 off 36 \
    on 36 127 sleep 125 off 36
