#!/usr/bin/env python3
"""Audio analysis for ableton-cli.

Produces JSON output with tempo, key, energy, brightness, and timbre features.
Supports librosa (primary) and essentia (optional) backends.
Extended features: spectrograms, per-beat time-series, onset/chord/HPSS analysis.
"""

import sys
import json
import warnings
from pathlib import Path

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

# 24 chord templates: 12 major + 12 minor triads as normalized 12-bin vectors
_CHORD_TEMPLATES = {}
for i, name in enumerate(KEY_NAMES):
    # Major triad: root, major third (+4), fifth (+7)
    major = np.zeros(12)
    major[i] = 1.0
    major[(i + 4) % 12] = 1.0
    major[(i + 7) % 12] = 1.0
    major /= np.linalg.norm(major)
    _CHORD_TEMPLATES[name] = major

    # Minor triad: root, minor third (+3), fifth (+7)
    minor = np.zeros(12)
    minor[i] = 1.0
    minor[(i + 3) % 12] = 1.0
    minor[(i + 7) % 12] = 1.0
    minor /= np.linalg.norm(minor)
    _CHORD_TEMPLATES[f"{name}m"] = minor


def _prev_power_of_2(n: int) -> int:
    """Largest power of 2 <= n."""
    p = 1
    while p * 2 <= n:
        p *= 2
    return p


def _estimate_chord(chroma_vector: np.ndarray) -> str:
    """Estimate chord from a 12-bin chroma vector using cosine similarity."""
    norm = np.linalg.norm(chroma_vector)
    if norm < 1e-8:
        return "N"  # no chord / silence
    chroma_norm = chroma_vector / norm
    best_chord = "N"
    best_sim = -1.0
    for name, template in _CHORD_TEMPLATES.items():
        sim = float(np.dot(chroma_norm, template))
        if sim > best_sim:
            best_sim = sim
            best_chord = name
    return best_chord


def analyze_with_librosa(filepath: str, y=None, sr=None) -> dict:
    if y is None or sr is None:
        y, sr = librosa.load(filepath)

    # Scale FFT size to signal length so short captures don't zero-pad
    n_fft = min(2048, max(64, _prev_power_of_2(len(y))))
    hop = n_fft // 4

    # Suppress n_fft warnings — we intentionally analyze short captures
    warnings.filterwarnings("ignore", message="n_fft=", category=UserWarning)
    warnings.filterwarnings("ignore", message="Trying to estimate tuning", category=UserWarning)

    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    rms = librosa.feature.rms(y=y, frame_length=n_fft, hop_length=hop)[0]
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr, n_fft=n_fft, hop_length=hop)[0]
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, n_fft=n_fft, hop_length=hop)[0]
    zcr = librosa.feature.zero_crossing_rate(y, frame_length=n_fft, hop_length=hop)[0]
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, n_fft=n_fft, hop_length=hop)

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


def generate_spectrograms(filepath: str, y=None, sr=None) -> dict:
    """Generate mel spectrogram and chromagram PNGs. Returns dict of paths."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import librosa.display

    if y is None or sr is None:
        y, sr = librosa.load(filepath)

    stem = Path(filepath).stem
    out_dir = Path(filepath).parent
    paths = {}

    # Mel spectrogram
    n_fft = min(2048, max(64, _prev_power_of_2(len(y))))
    hop = n_fft // 4
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=n_fft, hop_length=hop)
    S_db = librosa.power_to_db(S, ref=np.max)

    fig, ax = plt.subplots(figsize=(10, 4))
    librosa.display.specshow(S_db, sr=sr, hop_length=hop, x_axis="time", y_axis="mel", ax=ax)
    ax.set_title("Mel Spectrogram")
    fig.colorbar(ax.collections[0], ax=ax, format="%+2.0f dB")
    fig.tight_layout()
    mel_path = out_dir / f"{stem}_mel.png"
    fig.savefig(mel_path, dpi=100)
    plt.close(fig)
    paths["mel"] = str(mel_path)

    # Chromagram
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop)
    fig, ax = plt.subplots(figsize=(10, 4))
    librosa.display.specshow(chroma, sr=sr, hop_length=hop, x_axis="time", y_axis="chroma", ax=ax)
    ax.set_title("Chromagram")
    fig.colorbar(ax.collections[0], ax=ax)
    fig.tight_layout()
    chroma_path = out_dir / f"{stem}_chroma.png"
    fig.savefig(chroma_path, dpi=100)
    plt.close(fig)
    paths["chroma"] = str(chroma_path)

    return paths


def analyze_time_series(filepath: str, y=None, sr=None) -> dict:
    """Per-beat time-series analysis: energy, brightness, chroma at each beat."""
    if y is None or sr is None:
        y, sr = librosa.load(filepath)

    n_fft = min(2048, max(64, _prev_power_of_2(len(y))))
    hop = n_fft // 4

    warnings.filterwarnings("ignore", message="n_fft=", category=UserWarning)
    warnings.filterwarnings("ignore", message="Trying to estimate tuning", category=UserWarning)

    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop)
    if len(beat_frames) < 2:
        return {"error": "Signal too short for beat detection"}

    beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop)

    rms = librosa.feature.rms(y=y, frame_length=n_fft, hop_length=hop)[0]
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr, n_fft=n_fft, hop_length=hop)[0]
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop)

    # Sync features to beat boundaries
    rms_sync = librosa.util.sync(rms.reshape(1, -1), beat_frames, aggregate=np.mean)[0]
    centroid_sync = librosa.util.sync(centroid.reshape(1, -1), beat_frames, aggregate=np.mean)[0]
    chroma_sync = librosa.util.sync(chroma, beat_frames, aggregate=np.mean)

    return {
        "beat_times": [round(float(t), 3) for t in beat_times],
        "energy_per_beat": [round(float(v), 4) for v in rms_sync],
        "brightness_per_beat": [round(float(v), 1) for v in centroid_sync],
        "chroma_per_beat": [[round(float(c), 4) for c in col] for col in chroma_sync.T],
    }


def analyze_mir_extended(filepath: str, y=None, sr=None) -> dict:
    """Extended MIR: onsets, HPSS, spectral contrast, tonnetz, chord estimation."""
    if y is None or sr is None:
        y, sr = librosa.load(filepath)

    n_fft = min(2048, max(64, _prev_power_of_2(len(y))))
    hop = n_fft // 4

    warnings.filterwarnings("ignore", message="n_fft=", category=UserWarning)
    warnings.filterwarnings("ignore", message="Trying to estimate tuning", category=UserWarning)

    result = {}

    # Onset detection
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, hop_length=hop)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=hop)
    duration = len(y) / sr
    result["onsets"] = {
        "count": len(onset_frames),
        "times": [round(float(t), 3) for t in onset_times],
        "density_per_sec": round(len(onset_frames) / max(duration, 0.01), 2),
    }

    # Harmonic/Percussive separation
    y_harm, y_perc = librosa.effects.hpss(y)
    harm_energy = float(np.sum(y_harm ** 2))
    perc_energy = float(np.sum(y_perc ** 2))
    total = harm_energy + perc_energy
    if total > 0:
        result["hpss"] = {
            "harmonic_ratio": round(harm_energy / total, 4),
            "percussive_ratio": round(perc_energy / total, 4),
        }
    else:
        result["hpss"] = {"harmonic_ratio": 0.0, "percussive_ratio": 0.0}

    # Spectral contrast
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr, n_fft=n_fft, hop_length=hop)
    result["spectral_contrast"] = [round(float(v), 2) for v in contrast.mean(axis=1)]

    # Tonnetz (tonal centroid)
    tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
    result["tonnetz"] = [round(float(v), 4) for v in tonnetz.mean(axis=1)]

    # Chord estimation via beat-synced chroma
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop)
    if len(beat_frames) >= 2:
        chroma_sync = librosa.util.sync(chroma, beat_frames, aggregate=np.mean)
        result["chords_per_beat"] = [_estimate_chord(col) for col in chroma_sync.T]
    else:
        # Fallback: single chord for the whole signal
        result["chords_per_beat"] = [_estimate_chord(chroma.mean(axis=1))]

    return result


def full_analysis(filepath: str, time_series=False, spectrograms=False, extended=False) -> dict:
    """Coordinator: loads audio once, runs requested analyses."""
    if not HAS_LIBROSA:
        return {"error": "librosa not available"}

    y, sr = librosa.load(filepath)

    result = {"file": filepath}
    result["librosa"] = analyze_with_librosa(filepath, y=y, sr=sr)

    if spectrograms:
        result["spectrograms"] = generate_spectrograms(filepath, y=y, sr=sr)

    if time_series:
        result["time_series"] = analyze_time_series(filepath, y=y, sr=sr)

    if extended:
        result["extended"] = analyze_mir_extended(filepath, y=y, sr=sr)

    if HAS_ESSENTIA:
        result["essentia"] = analyze_with_essentia(filepath)

    return result


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
