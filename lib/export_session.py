"""Export Ableton Live session state to YAML Song format.

Queries Ableton via OSC and builds a Song dataclass that can be saved as YAML.
Note: instrument paths are placeholders since Ableton doesn't expose AU/VST paths.
"""

from __future__ import annotations

from .song import Song, Track, Clip, Scene, Note, parse_note
from . import query_session


def export_session(include_notes: bool = True) -> Song:
    """Query Ableton via OSC, build Song object.

    Instrument fields get placeholder names (Ableton device names)
    since AU/VST file paths can't be determined via OSC.
    """
    q = query_session.AbletonQuery()

    try:
        # Get session info
        session = q.get_session_info()
        tempo_raw = session.get("tempo")
        bpm = float(tempo_raw[0]) if tempo_raw else 120.0
        num_raw = session.get("signature_numerator")
        den_raw = session.get("signature_denominator")
        numerator = int(num_raw[0]) if num_raw else 4
        denominator = int(den_raw[0]) if den_raw else 4

        song = Song(
            name="Exported Session",
            bpm=bpm,
            time_sig=(numerator, denominator),
        )

        # Get tracks
        num_tracks_raw = session.get("num_tracks")
        num_tracks = int(num_tracks_raw[0]) if num_tracks_raw else 0

        for i in range(num_tracks):
            info = q.get_track_info(i)
            name_raw = info.get("name")
            name = str(name_raw[1]) if name_raw and len(name_raw) > 1 else f"Track {i}"
            vol_raw = info.get("volume")
            volume = float(vol_raw[1]) if vol_raw and len(vol_raw) > 1 else 0.85
            pan_raw = info.get("panning")
            pan = float(pan_raw[1]) if pan_raw and len(pan_raw) > 1 else 0.0

            # Get device name as instrument placeholder
            devices = q.get_devices(i)
            instrument = ""
            if devices and len(devices) > 1:
                instrument = f"(Ableton) {devices[1]}"

            track = Track(
                name=name,
                instrument=instrument,
                volume=round(volume, 2),
                pan=round(pan, 2),
            )

            # Get clips
            clip_names = q.get_clip_slots(i)
            if clip_names and len(clip_names) > 1:
                for slot_idx, cname in enumerate(clip_names[1:]):
                    if cname and str(cname).strip():
                        clip = Clip(
                            name=str(cname),
                            length=4.0,  # Default — can't easily query clip length
                        )
                        clip._slot = slot_idx  # type: ignore[attr-defined]
                        track.clips[str(cname)] = clip

            song.tracks.append(track)

        return song

    finally:
        q.shutdown()
