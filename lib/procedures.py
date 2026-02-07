"""Stored procedures — multi-step workflows composing existing primitives.

probe_track: map the sounds available on a track across note ranges
sweep_parameter: test a device parameter at multiple values
mix_check: per-track solo/capture/analyze pass
"""

import time

from . import osc, capture, analyze


def probe_track(track: int, note_ranges=None, bars: int = 1) -> list[dict]:
    """Solo a track and play chromatic notes across octaves, capturing + analyzing each.

    Returns list of {note_range, analysis, spectrograms} per range.
    """
    if note_ranges is None:
        # Default: octaves C1 (24) through C6 (84)
        note_ranges = [(i, i + 11) for i in range(24, 85, 12)]

    slot = 127  # Use high clip slot for temp clips
    results = []

    osc.solo(track)
    time.sleep(0.2)

    try:
        for low, high in note_ranges:
            # Create temp clip long enough for the notes
            length_beats = bars * 4
            osc.create_clip(track, slot, float(length_beats))
            time.sleep(0.1)

            # Fill with chromatic notes across the range
            notes = []
            note_count = high - low + 1
            dur = length_beats / max(note_count, 1)
            for j, pitch in enumerate(range(low, high + 1)):
                notes.append((pitch, j * dur, dur * 0.9, 100, 0))
            osc.add_notes(track, slot, notes)
            time.sleep(0.1)

            # Fire clip, capture, analyze
            osc.fire_clip(track, slot)
            time.sleep(0.3)  # Let clip start
            path = capture.capture_bars(bars)
            osc.stop_clip(track, slot)
            time.sleep(0.1)

            analysis = analyze.full_analysis(str(path), spectrograms=True, extended=True)

            # Clean up temp clip
            osc.delete_clip(track, slot)
            time.sleep(0.1)

            results.append({
                "note_range": f"{low}-{high}",
                "note_range_names": f"MIDI {low}-{high}",
                "analysis": analysis,
                "spectrograms": analysis.get("spectrograms", {}),
            })
    finally:
        osc.unsolo(track)

    return results


def sweep_parameter(
    track: int, device: int, param: int,
    start: float = 0.0, end: float = 1.0, steps: int = 5,
    bars: int = 1,
) -> list[dict]:
    """Sweep a device parameter from start to end, capturing + analyzing at each step.

    Returns list of {param_value, analysis} per step.
    """
    results = []
    values = [start + (end - start) * i / max(steps - 1, 1) for i in range(steps)]

    for value in values:
        osc.set_device_param(track, device, param, value)
        time.sleep(0.3)  # Let parameter settle

        path = capture.capture_bars(bars)
        analysis = analyze.full_analysis(str(path), spectrograms=True)

        results.append({
            "param_value": round(value, 4),
            "analysis": analysis,
        })

    return results


def mix_check(track_count: int | None = None, bars: int = 2) -> list[dict]:
    """Solo each track in turn, capture and analyze with spectrograms.

    If track_count is None, queries the session for the number of tracks.
    Returns list of {track, analysis} per track.
    """
    if track_count is None:
        from . import query_session
        q = query_session.AbletonQuery()
        info = q.get_session_info()
        q.shutdown()
        num = info.get("num_tracks")
        if num and num[0]:
            track_count = int(num[0])
        else:
            raise RuntimeError("Could not determine track count from session")

    results = []
    for i in range(track_count):
        osc.solo(i)
        time.sleep(0.3)

        path = capture.capture_bars(bars)
        analysis = analyze.full_analysis(str(path), spectrograms=True, time_series=True)

        osc.unsolo(i)
        time.sleep(0.1)

        results.append({
            "track": i,
            "analysis": analysis,
        })

    return results
