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
import signal
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


def cmd_set_scene_name(args):
    scene = _require_arg(args, 0, "set-scene-name <scene> <name>")
    name = _require_arg(args, 1, "set-scene-name <scene> <name>")
    osc.set_scene_name(int(scene), name)


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
    from .song import parse_note
    track = _require_arg(args, 0, "add-notes <track> <slot> <pitch:start:dur:vel> ...")
    slot = _require_arg(args, 1, "add-notes <track> <slot> <pitch:start:dur:vel> ...")
    if len(args) < 3:
        _die("add-notes <track> <slot> <pitch:start:dur:vel> ...")
    notes = []
    for note_str in args[2:]:
        try:
            n = parse_note(note_str)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        notes.append((n.pitch, n.start, n.duration, n.velocity, 0))
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

def _parse_analysis_flags(args):
    """Parse -s/-t/-e flags from args, return (flags_dict, remaining_args)."""
    flags = {"spectrograms": False, "time_series": False, "extended": False}
    remaining = []
    for a in args:
        if a in ("-s", "--spectrogram", "--spectrograms"):
            flags["spectrograms"] = True
        elif a in ("-t", "--time-series"):
            flags["time_series"] = True
        elif a in ("-e", "--extended"):
            flags["extended"] = True
        else:
            remaining.append(a)
    return flags, remaining


def cmd_analyze(args):
    flags, rest = _parse_analysis_flags(args)
    filepath = _require_arg(rest, 0, "analyze [-s] [-t] [-e] <file.wav>")
    if not Path(filepath).is_file():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    from . import analyze

    if any(flags.values()):
        result = analyze.full_analysis(filepath, **flags)
    else:
        result = {"file": filepath}
        if analyze.HAS_LIBROSA:
            result["librosa"] = analyze.analyze_with_librosa(filepath)
        if analyze.HAS_ESSENTIA:
            result["essentia"] = analyze.analyze_with_essentia(filepath)
        if not analyze.HAS_LIBROSA and not analyze.HAS_ESSENTIA:
            result["error"] = "No analysis library available. Install: pip install librosa"
    print(json.dumps(result, indent=2))


def cmd_spectrogram(args):
    """Generate spectrograms from an existing audio file."""
    filepath = _require_arg(args, 0, "spectrogram <file.wav>")
    if not Path(filepath).is_file():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    from . import analyze
    paths = analyze.generate_spectrograms(filepath)
    print(json.dumps(paths, indent=2))


# ── Listen (capture + analyze) ────────────────────────────

def cmd_listen(args):
    flags, rest = _parse_analysis_flags(args)
    bars = float(rest[0]) if rest else 4
    path = capture.capture_bars(bars)
    if not path.is_file():
        return

    from . import analyze

    if any(flags.values()):
        result = analyze.full_analysis(str(path), **flags)
    else:
        result = {"file": str(path)}
        if analyze.HAS_LIBROSA:
            result["librosa"] = analyze.analyze_with_librosa(str(path))
        if analyze.HAS_ESSENTIA:
            result["essentia"] = analyze.analyze_with_essentia(str(path))
        if not analyze.HAS_LIBROSA and not analyze.HAS_ESSENTIA:
            result["error"] = "No analysis library available."
    print(json.dumps(result, indent=2))


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


# ── Procedures ────────────────────────────────────────────

def cmd_probe(args):
    from . import procedures
    track = int(_require_arg(args, 0, "probe <track> [bars]"))
    bars = int(args[1]) if len(args) > 1 else 1
    results = procedures.probe_track(track, bars=bars)
    print(json.dumps(results, indent=2))


def cmd_sweep(args):
    from . import procedures
    track = int(_require_arg(args, 0, "sweep <track> <device> <param> [start end steps] [bars]"))
    device = int(_require_arg(args, 1, "sweep <track> <device> <param> [start end steps] [bars]"))
    param = int(_require_arg(args, 2, "sweep <track> <device> <param> [start end steps] [bars]"))
    start = float(args[3]) if len(args) > 3 else 0.0
    end = float(args[4]) if len(args) > 4 else 1.0
    steps = int(args[5]) if len(args) > 5 else 5
    bars = int(args[6]) if len(args) > 6 else 1
    results = procedures.sweep_parameter(track, device, param, start, end, steps, bars=bars)
    print(json.dumps(results, indent=2))


def cmd_mix_check(args):
    from . import procedures
    track_count = int(args[0]) if args else None
    bars = int(args[1]) if len(args) > 1 else 2
    results = procedures.mix_check(track_count=track_count, bars=bars)
    print(json.dumps(results, indent=2))


# ── Monitor ───────────────────────────────────────────────

def cmd_monitor(args):
    from . import monitor
    subcmd = args[0] if args else ""

    if subcmd == "start":
        bars = int(args[1]) if len(args) > 1 else 4
        print(f"Starting monitor: capturing {bars} bars per cycle", flush=True)
        print("Press Ctrl-C to stop.", flush=True)
        monitor.start(interval_bars=bars)
        try:
            signal.pause()
        except KeyboardInterrupt:
            pass
        finally:
            monitor.stop()
            print("\nMonitor stopped.", flush=True)

    elif subcmd == "latest":
        result = monitor.latest()
        if result is None:
            print("No analysis available yet. Run 'monitor start' first.", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(result, indent=2))

    else:
        print("Usage: ableton-cli monitor <start [bars]|latest>", file=sys.stderr)
        print("  start [bars]   Start continuous capture+analyze loop (default: 4 bars)", file=sys.stderr)
        print("  latest         Read latest analysis from captures/latest_analysis.json", file=sys.stderr)
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


# ── Song (YAML) ──────────────────────────────────────────

def cmd_validate(args):
    """Validate a YAML song file."""
    from . import song
    filepath = _require_arg(args, 0, "validate <song.yaml>")
    if not Path(filepath).is_file():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    try:
        s = song.load(filepath)
    except Exception as e:
        print(f"Error parsing YAML: {e}", file=sys.stderr)
        sys.exit(1)
    errors = song.validate(s)
    if errors:
        print(f"Validation failed ({len(errors)} errors):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print(f"OK: '{s.name}' — {s.key} @ {s.bpm} BPM")
        print(f"  {len(s.tracks)} tracks, {len(s.scenes)} scenes, {sum(len(t.clips) for t in s.tracks)} clips")


def cmd_push(args):
    """Push a YAML song to Ableton via OSC — creates tracks, clips, notes."""
    import time
    from . import song

    filepath = _require_arg(args, 0, "push <song.yaml> [--clear]")
    clear = "--clear" in args

    if not Path(filepath).is_file():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    s = song.load(filepath)
    errors = song.validate(s)
    if errors:
        print(f"Validation failed:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    MSG_DELAY = 0.05

    print(f"Pushing '{s.name}' ({s.key} @ {s.bpm} BPM) to Ableton...")

    # Set tempo
    osc.set_tempo(s.bpm)
    time.sleep(MSG_DELAY)

    if clear:
        print("  Clearing existing tracks...")
        for i in range(15, -1, -1):
            try:
                osc.delete_track(i)
                time.sleep(MSG_DELAY)
            except Exception:
                pass
        time.sleep(0.5)

    # Create tracks
    print(f"  Creating {len(s.tracks)} tracks...")
    for track in s.tracks:
        osc.create_midi_track(-1)
        time.sleep(0.1)
    time.sleep(0.5)

    # Name tracks and set mixer
    for i, track in enumerate(s.tracks):
        osc.set_track_name(i, track.name)
        time.sleep(MSG_DELAY)
        osc.set_volume(i, track.volume)
        time.sleep(MSG_DELAY)
        if track.pan != 0.0:
            osc.set_pan(i, track.pan)
            time.sleep(MSG_DELAY)

    # Write clips
    total_clips = 0
    for i, track in enumerate(s.tracks):
        if not track.clips:
            continue
        for cname, clip in track.clips.items():
            slot = song.get_clip_slot(clip)
            # Create clip
            osc.create_clip(i, slot, clip.length)
            time.sleep(0.1)
            # Add notes
            if clip.notes:
                note_tuples = [(n.pitch, n.start, n.duration, n.velocity, 0) for n in clip.notes]
                osc.add_notes(i, slot, note_tuples)
                time.sleep(MSG_DELAY)
            # Name clip
            osc.set_clip_name(i, slot, cname)
            time.sleep(MSG_DELAY)
            total_clips += 1
    print(f"  Wrote {total_clips} clips across {len(s.tracks)} tracks")

    # Name scenes
    for i, scene in enumerate(s.scenes):
        osc.set_scene_name(i, scene.name)
        time.sleep(MSG_DELAY)

    print(f"  Named {len(s.scenes)} scenes")
    print(f"\nDone! Add instruments in Ableton, then 'fire-scene 0' to begin.")
    for i, track in enumerate(s.tracks):
        print(f"  Track {i}: {track.name:14s} → {track.instrument}")


def cmd_render(args):
    """Render a YAML song to WAV (offline, requires pedalboard)."""
    from . import render
    if not render.HAS_PEDALBOARD:
        print("Error: render requires pedalboard. Install: uv pip install -e '.[render]'", file=sys.stderr)
        sys.exit(1)

    from . import song

    # Parse flags
    filepath = None
    scene_idx = None
    output = None
    do_analyze = False
    full = False
    remaining = []

    i = 0
    while i < len(args):
        if args[i] == "--scene" and i + 1 < len(args):
            scene_idx = int(args[i + 1])
            i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            output = args[i + 1]
            i += 2
        elif args[i] == "--analyze":
            do_analyze = True
            i += 1
        elif args[i] == "--full":
            full = True
            i += 1
        else:
            remaining.append(args[i])
            i += 1

    if not remaining:
        _die("render <song.yaml> [--scene N] [--full] [--output path] [--analyze]")
    filepath = remaining[0]

    if not Path(filepath).is_file():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    s = song.load(filepath)
    errors = song.validate(s)
    if errors:
        print(f"Validation failed:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    sr = 44100

    if scene_idx is not None:
        if scene_idx >= len(s.scenes):
            print(f"Error: scene {scene_idx} out of range (0-{len(s.scenes)-1})", file=sys.stderr)
            sys.exit(1)
        print(f"Rendering scene {scene_idx} ({s.scenes[scene_idx].name})...")
        audio = render.render_scene(s, scene_idx, sr=sr)
        default_name = f"{Path(filepath).stem}_scene{scene_idx}.wav"
    elif full:
        print(f"Rendering full arrangement ({len(s.arrangement)} scenes)...")
        audio = render.render_arrangement(s, sr=sr)
        default_name = f"{Path(filepath).stem}_full.wav"
    else:
        # Default: render first scene
        print(f"Rendering scene 0 ({s.scenes[0].name})...")
        audio = render.render_scene(s, 0, sr=sr)
        default_name = f"{Path(filepath).stem}_scene0.wav"

    out_path = output or str(Path("captures") / default_name)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    render.render_to_file(audio, out_path, sr=sr)
    print(f"Rendered to {out_path}")

    if do_analyze:
        from . import analyze
        result = analyze.full_analysis(out_path, spectrograms=True, extended=True)
        print(json.dumps(result, indent=2))


def cmd_export(args):
    """Export current Ableton session to YAML."""
    from . import export_session
    output = args[0] if args else "exported_session.yaml"
    include_notes = "--no-notes" not in args
    s = export_session.export_session(include_notes=include_notes)
    from . import song
    song.save(s, output)
    print(f"Exported to {output}")


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
    "set-scene-name": cmd_set_scene_name,
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
    "spectrogram": cmd_spectrogram,
    # Combined
    "listen": cmd_listen,
    # Templates
    "template": cmd_template,
    # Procedures
    "probe": cmd_probe,
    "sweep": cmd_sweep,
    "mix-check": cmd_mix_check,
    # Monitor
    "monitor": cmd_monitor,
    # MIDI
    "midi": cmd_midi,
    # Song (YAML)
    "validate": cmd_validate,
    "push": cmd_push,
    "render": cmd_render,
    "export": cmd_export,
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
  analyze [-s] [-t] [-e] <file.wav>   Analyze audio file → JSON
  spectrogram <file.wav>    Generate mel + chroma PNGs from audio file
    -s  --spectrogram       Generate mel + chroma spectrogram PNGs
    -t  --time-series       Include per-beat energy/brightness/chroma arrays
    -e  --extended          Include onsets, HPSS, spectral contrast, tonnetz, chords

COMBINED:
  listen [-s] [-t] [-e] [bars]   Capture + analyze (default: 4 bars)

PROCEDURES:
  probe <track> [bars]      Map sounds on a track (solo, play octaves, analyze)
  sweep <t> <d> <p> [start end steps] [bars]
                            Sweep device parameter and capture at each step
  mix-check [tracks] [bars] Per-track solo/capture/analyze pass

MONITOR:
  monitor start [bars]      Start continuous capture+analyze loop (Ctrl-C to stop)
  monitor latest            Read latest analysis from captures/latest_analysis.json

TEMPLATES:
  template band [bpm]       Create 8-track band setup with starter patterns
  template list             List available templates

MIDI:
  midi list                 List MIDI devices
  midi note <n> [vel] [ms]  Send note (MIDI number, velocity, duration)
  midi chord <root> [type]  Send chord (major, minor, 7th, maj7, min7, dim, aug, sus2, sus4)
  midi cc <num> <val>       Send CC message
  midi pattern <name|list>  Play/list MIDI patterns

SONG (YAML):
  validate <song.yaml>      Validate a YAML song file
  push <song.yaml> [--clear] Push song to Ableton (create tracks, clips, notes)
  render <song.yaml> [opts] Render song to WAV (offline, needs pedalboard)
    --scene N               Render specific scene
    --full                  Render full arrangement
    --output <path>         Output file path
    --analyze               Auto-analyze rendered audio
  export [output.yaml]      Export current Ableton session to YAML

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
