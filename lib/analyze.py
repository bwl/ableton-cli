#!/usr/bin/env python3
"""Audio analysis for ableton-cli.

Produces JSON output with tempo, key, energy, brightness, and timbre features.
Supports librosa (primary) and essentia (optional) backends.
"""

import sys
import json
import numpy as np

try:
    import librosa

    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False

try:
    import essentia.standard as es

    HAS_ESSENTIA = True
except ImportError:
    HAS_ESSENTIA = False

KEY_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def analyze_with_librosa(filepath: str) -> dict:
    y, sr = librosa.load(filepath)

    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    rms = librosa.feature.rms(y=y)[0]
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

    key_profile = chroma.mean(axis=1)
    estimated_key = KEY_NAMES[int(np.argmax(key_profile))]

    return {
        "tempo": float(tempo),
        "estimated_key": estimated_key,
        "energy": {
            "mean": round(float(np.mean(rms)), 4),
            "max": round(float(np.max(rms)), 4),
            "std": round(float(np.std(rms)), 4),
        },
        "brightness": {
            "centroid_mean": round(float(np.mean(centroid)), 1),
            "rolloff_mean": round(float(np.mean(rolloff)), 1),
        },
        "dynamics": {
            "zcr_mean": round(float(np.mean(zcr)), 4),
        },
        "key_profile": [round(v, 4) for v in key_profile.tolist()],
        "mfcc_summary": {
            "mean": [round(v, 4) for v in mfccs.mean(axis=1).tolist()],
            "std": [round(v, 4) for v in mfccs.std(axis=1).tolist()],
        },
    }


def analyze_with_essentia(filepath: str) -> dict:
    audio = es.MonoLoader(filename=filepath)()

    rhythm_extractor = es.RhythmExtractor2013(method="multifeature")
    bpm, beats, beats_confidence, _, _ = rhythm_extractor(audio)

    key_extractor = es.KeyExtractor()
    key, scale, strength = key_extractor(audio)

    energy = es.Energy()(audio)
    loudness = es.Loudness()(audio)
    danceability, _ = es.Danceability()(audio)

    return {
        "tempo": round(float(bpm), 1),
        "tempo_confidence": round(float(np.mean(beats_confidence)), 3),
        "key": key,
        "scale": scale,
        "key_strength": round(float(strength), 3),
        "energy": round(float(energy), 4),
        "loudness": round(float(loudness), 4),
        "danceability": round(float(danceability), 3),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: analyze.py <audio_file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    result = {"file": filepath}

    if HAS_LIBROSA:
        result["librosa"] = analyze_with_librosa(filepath)
    if HAS_ESSENTIA:
        result["essentia"] = analyze_with_essentia(filepath)
    if not HAS_LIBROSA and not HAS_ESSENTIA:
        result["error"] = "No analysis library available. Install: pip install librosa"

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
