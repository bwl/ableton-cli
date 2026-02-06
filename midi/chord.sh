#!/usr/bin/env bash
# Play a chord: root + type (major/minor/7th)
set -euo pipefail
DEV="${MIDI_DEV:-IAC Driver Bus 1}"
ROOT=${1:-60}
TYPE=${2:-major}
VEL=${3:-100}

case "$TYPE" in
    major) sendmidi dev "$DEV" on $ROOT $VEL on $((ROOT+4)) $VEL on $((ROOT+7)) $VEL ;;
    minor) sendmidi dev "$DEV" on $ROOT $VEL on $((ROOT+3)) $VEL on $((ROOT+7)) $VEL ;;
    7th)   sendmidi dev "$DEV" on $ROOT $VEL on $((ROOT+4)) $VEL on $((ROOT+7)) $VEL on $((ROOT+10)) $VEL ;;
    *)     echo "Unknown chord type: $TYPE (use major, minor, 7th)" >&2; exit 1 ;;
esac

sleep 1
sendmidi dev "$DEV" off $ROOT off $((ROOT+3)) off $((ROOT+4)) off $((ROOT+7)) off $((ROOT+10)) 2>/dev/null || true
