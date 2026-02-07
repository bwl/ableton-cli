"""ableton-cli — Unified CLI for Ableton Live control and analysis.

Controls Ableton via:
  - Carabiner (Ableton Link tempo/transport sync) over TCP socket
  - AbletonOSC (full Live Object Model control) via python-osc
  - MIDI via mido + python-rtmidi
  - Audio capture via ffmpeg/sox/jack_capture (subprocess)
  - Audio analysis via librosa

No GPL dependencies are linked — all vendorable libs are MIT/ISC/BSD/Unlicense.
"""

import json
import sys
from pathlib import Path

from . import link, osc, midi_engine, capture


def cmd_status(_args):
    print(link.status())


def cmd_tempo(args):
    bpm = _require_arg(args, 0, "tempo <bpm>")
    link.set_tempo(float(bpm))


def cmd_start(_args):
    link.start()


def cmd_stop(_args):
    link.stop()


# ── OSC commands ──────────────────────────────────────────

def cmd_play(_args):
    osc.play()


def cmd_pause(_args):
    osc.stop()


def cmd_set_tempo(args):
    bpm = _require_arg(args, 0, "set-tempo <bpm>")
    osc.set_tempo(float(bpm))


def cmd_fire(args):
    track = _require_arg(args, 0, "fire <track> <clip>")
    clip = _require_arg(args, 1, "fire <track> <clip>")
    osc.fire_clip(int(track), int(clip))


def cmd_stop_clip(args):
    track = _require_arg(args, 0, "stop-clip <track> <clip>")
    clip = _require_arg(args, 1, "stop-clip <track> <clip>")
    osc.stop_clip(int(track), int(clip))


def cmd_fire_scene(args):
    scene = _require_arg(args, 0, "fire-scene <scene>")
    osc.fire_scene(int(scene))


def cmd_mute(args):
    track = _require_arg(args, 0, "mute <track>")
    osc.mute(int(track))


def cmd_unmute(args):
    track = _require_arg(args, 0, "unmute <track>")
    osc.unmute(int(track))


def cmd_solo(args):
    track = _require_arg(args, 0, "solo <track>")
    osc.solo(int(track))


def cmd_unsolo(args):
    track = _require_arg(args, 0, "unsolo <track>")
    osc.unsolo(int(track))


def cmd_volume(args):
    track = _require_arg(args, 0, "volume <track> <level>")
    level = _require_arg(args, 1, "volume <track> <level 0.0-1.0>")
    osc.set_volume(int(track), float(level))


def cmd_pan(args):
    track = _require_arg(args, 0, "pan <track> <value>")
    value = _require_arg(args, 1, "pan <track> <value -1.0 to 1.0>")
    osc.set_pan(int(track), float(value))


def cmd_arm(args):
    track = _require_arg(args, 0, "arm <track>")
    osc.arm(int(track))


def cmd_disarm(args):
    track = _require_arg(args, 0, "disarm <track>")
    osc.disarm(int(track))


def cmd_device_param(args):
    track = _require_arg(args, 0, "device-param <track> <device> <param> <value>")
    device = _require_arg(args, 1, "device-param <track> <device> <param> <value>")
    param = _require_arg(args, 2, "device-param <track> <device> <param> <value>")
    value = _require_arg(args, 3, "device-param <track> <device> <param> <value>")
    osc.set_device_param(int(track), int(device), int(param), float(value))


# ── Track/Clip creation ────────────────────────────────────

def cmd_create_midi_track(args):
    index = int(args[0]) if args else -1
    osc.create_midi_track(index)


def cmd_create_audio_track(args):
    index = int(args[0]) if args else -1
    osc.create_audio_track(index)


def cmd_delete_track(args):
    track = _require_arg(args, 0, "delete-track <track>")
    osc.delete_track(int(track))


def cmd_set_track_name(args):
    track = _require_arg(args, 0, "set-track-name <track> <name>")
    name = _require_arg(args, 1, "set-track-name <track> <name>")
    osc.set_track_name(int(track), name)


def cmd_create_clip(args):
    track = _require_arg(args, 0, "create-clip <track> <slot> [length_beats]")
    slot = _require_arg(args, 1, "create-clip <track> <slot> [length_beats]")
    length = float(args[2]) if len(args) > 2 else 4.0
    osc.create_clip(int(track), int(slot), length)


def cmd_delete_clip(args):
    track = _require_arg(args, 0, "delete-clip <track> <slot>")
    slot = _require_arg(args, 1, "delete-clip <track> <slot>")
    osc.delete_clip(int(track), int(slot))


def cmd_set_clip_name(args):
    track = _require_arg(args, 0, "set-clip-name <track> <slot> <name>")
    slot = _require_arg(args, 1, "set-clip-name <track> <slot> <name>")
    name = _require_arg(args, 2, "set-clip-name <track> <slot> <name>")
    osc.set_clip_name(int(track), int(slot), name)


def cmd_add_notes(args):
    """Add MIDI notes: add-notes <track> <slot> <pitch:start:dur:vel> ..."""
    track = _require_arg(args, 0, "add-notes <track> <slot> <pitch:start:dur:vel> ...")
    slot = _require_arg(args, 1, "add-notes <track> <slot> <pitch:start:dur:vel> ...")
    if len(args) < 3:
        _die("add-notes <track> <slot> <pitch:start:dur:vel> ...")
    notes = []
    for note_str in args[2:]:
        parts = note_str.split(":")
        if len(parts) < 3:
            print(f"Error: note format is pitch:start:duration[:velocity] — got '{note_str}'", file=sys.stderr)
            sys.exit(1)
        pitch = int(parts[0])
        start = float(parts[1])
        dur = float(parts[2])
        vel = int(parts[3]) if len(parts) > 3 else 100
        notes.append((pitch, start, dur, vel, 0))
    osc.add_notes(int(track), int(slot), notes)


def cmd_clear_notes(args):
    track = _require_arg(args, 0, "clear-notes <track> <slot>")
    slot = _require_arg(args, 1, "clear-notes <track> <slot>")
    osc.remove_notes(int(track), int(slot))


def cmd_osc_send(args):
    if len(args) < 1:
        _die("osc <address> [args...]")
    address = args[0]
    osc_args = []
    for a in args[1:]:
        try:
            osc_args.append(float(a) if "." in a else int(a))
        except ValueError:
            osc_args.append(a)
    osc.send(address, *osc_args)


# ── Query ─────────────────────────────────────────────────

def cmd_query(args):
    from . import query_session
    q = query_session.AbletonQuery()
    subcmd = args[0] if args else "session"

    if subcmd == "session":
        result = q.get_session_info()
    elif subcmd == "tracks":
        result = q.get_all_tracks()
    elif subcmd == "track":
        idx = int(args[1]) if len(args) > 1 else 0
        result = q.get_track_info(idx)
    elif subcmd == "clips":
        idx = int(args[1]) if len(args) > 1 else 0
        result = q.get_clip_slots(idx)
    elif subcmd == "devices":
        idx = int(args[1]) if len(args) > 1 else 0
        result = q.get_devices(idx)
    elif subcmd == "params":
        track_idx = int(args[1]) if len(args) > 1 else 0
        device_idx = int(args[2]) if len(args) > 2 else 0
        result = q.get_device_params(track_idx, device_idx)
    else:
        _die("query [session|tracks|track <n>|clips <n>|devices <n>|params <t> [d]]")

    print(json.dumps(result, indent=2, default=str))
    q.shutdown()


# ── Capture ───────────────────────────────────────────────

def cmd_capture(args):
    seconds = _require_arg(args, 0, "capture <seconds>")
    path = capture.capture_seconds(float(seconds))
    print(path)


def cmd_capture_bars(args):
    bars = int(args[0]) if args else 4
    path = capture.capture_bars(bars)
    print(path)


# ── Analysis ──────────────────────────────────────────────

def cmd_analyze(args):
    filepath = _require_arg(args, 0, "analyze <file.wav>")
    if not Path(filepath).is_file():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    from . import analyze
    result = {"file": filepath}
    if analyze.HAS_LIBROSA:
        result["librosa"] = analyze.analyze_with_librosa(filepath)
    if analyze.HAS_ESSENTIA:
        result["essentia"] = analyze.analyze_with_essentia(filepath)
    if not analyze.HAS_LIBROSA and not analyze.HAS_ESSENTIA:
        result["error"] = "No analysis library available. Install: pip install librosa"
    print(json.dumps(result, indent=2))


# ── Listen (capture + analyze) ────────────────────────────

def cmd_listen(args):
    bars = int(args[0]) if args else 4
    path = capture.capture_bars(bars)
    if path.is_file():
        cmd_analyze([str(path)])


# ── Templates ─────────────────────────────────────────────

def cmd_template(args):
    from . import templates
    name = args[0] if args else ""

    if name == "band":
        bpm = float(args[1]) if len(args) > 1 else 120.0
        templates.setup_band(bpm=bpm, delete_existing=True)
    elif name == "list":
        print("Available templates:")
        print("  band [bpm]    8-track band (Drums, Bass, Keys, Lead, Pad, Guitar, Perc, Vox)")
    else:
        print("Usage: ableton-cli template <band|list> [options]", file=sys.stderr)
        print("  band [bpm]    Create 8-track band template (default: 120 BPM)", file=sys.stderr)
        print("  list          List available templates", file=sys.stderr)
        sys.exit(1)


# ── MIDI ──────────────────────────────────────────────────

def cmd_midi(args):
    subcmd = args[0] if args else ""

    if subcmd == "list":
        ports = midi_engine.list_ports()
        print("Inputs:")
        for p in ports["inputs"]:
            print(f"  {p}")
        print("Outputs:")
        for p in ports["outputs"]:
            print(f"  {p}")

    elif subcmd == "note":
        note = int(_require_arg(args, 1, "midi note <note> [velocity] [duration_ms]"))
        vel = int(args[2]) if len(args) > 2 else 100
        dur = int(args[3]) if len(args) > 3 else 500
        midi_engine.send_note(note, vel, dur)

    elif subcmd == "chord":
        root = int(_require_arg(args, 1, "midi chord <root> [type]"))
        chord_type = args[2] if len(args) > 2 else "major"
        midi_engine.send_chord(root, chord_type)

    elif subcmd == "cc":
        cc_num = int(_require_arg(args, 1, "midi cc <num> <val>"))
        cc_val = int(_require_arg(args, 2, "midi cc <num> <val>"))
        midi_engine.send_cc(cc_num, cc_val)

    elif subcmd == "pattern":
        name = _require_arg(args, 1, "midi pattern <name> [bpm] [repeats]")
        if name == "list":
            for pname, beats in midi_engine.list_patterns().items():
                print(f"  {pname:20s} ({beats} beats)")
            return
        bpm = int(args[2]) if len(args) > 2 else 120
        repeats = int(args[3]) if len(args) > 3 else 1
        print(f"Playing '{name}' at {bpm} BPM x{repeats}")
        midi_engine.play_pattern(name, bpm, repeats)

    else:
        print("Usage: ableton-cli midi <list|note|chord|cc|pattern>", file=sys.stderr)
        print("  list                    List MIDI devices", file=sys.stderr)
        print("  note <n> [vel] [ms]     Send note", file=sys.stderr)
        print("  chord <root> [type]     Send chord (major, minor, 7th, ...)", file=sys.stderr)
        print("  cc <num> <val>          Send CC message", file=sys.stderr)
        print("  pattern <name|list>     Play/list MIDI patterns", file=sys.stderr)
        sys.exit(1)


# ── Helpers ───────────────────────────────────────────────

def _require_arg(args, index, usage_hint):
    if index >= len(args):
        _die(usage_hint)
    return args[index]


def _die(usage_hint):
    print(f"Usage: ableton-cli {usage_hint}", file=sys.stderr)
    sys.exit(1)


# ── Dispatch ──────────────────────────────────────────────

COMMANDS = {
    # Link
    "status": cmd_status,
    "tempo": cmd_tempo,
    "start": cmd_start,
    "stop": cmd_stop,
    # OSC — transport
    "play": cmd_play,
    "pause": cmd_pause,
    "set-tempo": cmd_set_tempo,
    # OSC — tracks
    "create-midi-track": cmd_create_midi_track,
    "create-audio-track": cmd_create_audio_track,
    "delete-track": cmd_delete_track,
    "set-track-name": cmd_set_track_name,
    # OSC — clips
    "fire": cmd_fire,
    "stop-clip": cmd_stop_clip,
    "fire-scene": cmd_fire_scene,
    "create-clip": cmd_create_clip,
    "delete-clip": cmd_delete_clip,
    "set-clip-name": cmd_set_clip_name,
    "add-notes": cmd_add_notes,
    "clear-notes": cmd_clear_notes,
    # OSC — mixer
    "mute": cmd_mute,
    "unmute": cmd_unmute,
    "solo": cmd_solo,
    "unsolo": cmd_unsolo,
    "volume": cmd_volume,
    "pan": cmd_pan,
    "arm": cmd_arm,
    "disarm": cmd_disarm,
    "device-param": cmd_device_param,
    "osc": cmd_osc_send,
    # Query
    "query": cmd_query,
    # Capture
    "capture": cmd_capture,
    "capture-bars": cmd_capture_bars,
    # Analysis
    "analyze": cmd_analyze,
    # Combined
    "listen": cmd_listen,
    # Templates
    "template": cmd_template,
    # MIDI
    "midi": cmd_midi,
}

USAGE = """\
Usage: ableton-cli <command> [args]

LINK (Carabiner):
  status                    Show Link session status
  tempo <bpm>               Set Link tempo
  start                     Start transport (Link sync)
  stop                      Stop transport

TRANSPORT:
  play                      Start Ableton playback
  pause                     Stop Ableton playback
  set-tempo <bpm>           Set Ableton tempo via OSC

TRACKS:
  create-midi-track [index] Create MIDI track (-1 or omit = append)
  create-audio-track [idx]  Create audio track
  delete-track <track>      Delete a track
  set-track-name <t> <name> Rename a track

CLIPS:
  fire <track> <clip>       Fire clip at track/clip index
  stop-clip <track> <clip>  Stop clip
  fire-scene <scene>        Fire entire scene
  create-clip <t> <s> [len] Create empty MIDI clip (len in beats, default 4)
  delete-clip <t> <s>       Delete clip
  set-clip-name <t> <s> <n> Rename clip
  add-notes <t> <s> P:S:D[:V] ...  Add MIDI notes (pitch:start:dur[:vel])
  clear-notes <t> <s>       Remove all notes from clip

MIXER:
  mute <track>              Mute track
  unmute <track>            Unmute track
  solo <track>              Solo track
  unsolo <track>            Unsolo track
  volume <track> <0.0-1.0>  Set track volume
  pan <track> <-1.0-1.0>    Set track panning
  arm <track>               Arm track for recording
  disarm <track>            Disarm track
  device-param <t> <d> <p> <v>  Set device parameter value
  osc <addr> [args...]      Send raw OSC message

QUERY:
  query [session|tracks|track <n>|clips <n>|devices <n>]

CAPTURE:
  capture <seconds>         Capture N seconds of audio
  capture-bars [n]          Capture N bars (auto-calculates from BPM)

ANALYSIS:
  analyze <file.wav>        Analyze audio file → JSON

COMBINED:
  listen [bars]             Capture + analyze (default: 4 bars)

TEMPLATES:
  template band [bpm]       Create 8-track band setup with starter patterns
  template list             List available templates

MIDI:
  midi list                 List MIDI devices
  midi note <n> [vel] [ms]  Send note (MIDI number, velocity, duration)
  midi chord <root> [type]  Send chord (major, minor, 7th, maj7, min7, dim, aug, sus2, sus4)
  midi cc <num> <val>       Send CC message
  midi pattern <name|list>  Play/list MIDI patterns

ENVIRONMENT:
  CARABINER_HOST  Carabiner host    (default: localhost)
  CARABINER_PORT  Carabiner port    (default: 17000)
  OSC_HOST        AbletonOSC host   (default: 127.0.0.1)
  OSC_PORT        AbletonOSC port   (default: 11000)
  CAPTURE_DIR     Capture directory (default: ./captures)
  MIDI_DEV        MIDI device       (default: IAC Driver Bus 1)"""


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        print(USAGE)
        sys.exit(0)

    command = args[0]
    rest = args[1:]

    handler = COMMANDS.get(command)
    if handler is None:
        print(f"Unknown command: {command}", file=sys.stderr)
        print("Run 'ableton-cli --help' for usage.", file=sys.stderr)
        sys.exit(1)

    handler(rest)
