# ableton-cli

CLI-based music composition with Ableton Live - tempo sync, remote control, audio capture, AI analysis

Status: active

## Overview

A complete system for creative music-making via command line, with tempo sync, remote control, audio capture, and AI-powered analysis.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      ABLETON LIVE                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Link (sync) │  │ AbletonOSC  │  │ Audio Out → JACK/etc    │ │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘ │
└─────────┼────────────────┼─────────────────────┼───────────────┘
          │                │                     │
          ▼                ▼                     ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────────┐
│   Carabiner     │ │   OSC Client    │ │   jack_capture / sox    │
│   TCP :17000    │ │   UDP :11000    │ │   (record audio)        │
└────────┬────────┘ └────────┬────────┘ └───────────┬─────────────┘
         │                   │                      │
         └───────────────────┴──────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Analysis Layer │
                    │  Essentia/librosa│
                    │  → JSON output  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Claude Code   │
                    │  Interprets mood│
                    │  Suggests changes│
                    │  Executes OSC   │
                    └─────────────────┘
```

## Components

### 1. Ableton Link + Carabiner (Tempo/Transport Sync)

**What it does:** Syncs tempo, beat phase, and start/stop across all Link-enabled apps.

**Install Carabiner:**

```bash
# Download from https://github.com/Deep-Symmetry/carabiner/releases
# Available for macOS, Windows, Linux, Raspberry Pi

# Linux example:
wget https://github.com/Deep-Symmetry/carabiner/releases/download/v1.1.6/Carabiner_Linux_x64.gz
gunzip Carabiner_Linux_x64.gz
chmod +x Carabiner_Linux_x64
mv Carabiner_Linux_x64 /usr/local/bin/carabiner
```

**Run as daemon:**

```bash
carabiner --port 17000 --daemon &
```

**CLI usage:**

```bash
# Query status
echo "status" | nc -q1 localhost 17000
# Response: status {:peers 1 :bpm 120.0 :start 73746356220 :beat 597.231}

# Set tempo
echo "bpm 128" | nc -q1 localhost 17000

# Enable transport sync
echo "enable-start-stop-sync" | nc -q1 localhost 17000
echo "start-playing" | nc -q1 localhost 17000
echo "stop-playing" | nc -q1 localhost 17000
```

-----

### 2. AbletonOSC (Full Control via OSC)

**What it does:** Exposes the entire Live Object Model via OSC. Control tracks, clips, devices, tempo, transport, and more.

**Install:**

```bash
# Download from https://github.com/ideoforms/AbletonOSC
git clone https://github.com/ideoforms/AbletonOSC.git

# Copy to Ableton's Remote Scripts folder:
# macOS: ~/Music/Ableton/User Library/Remote Scripts/
# Windows: ~\Documents\Ableton\User Library\Remote Scripts\

# In Ableton: Preferences → Link/Tempo/MIDI → Control Surface → AbletonOSC
```

**Ports:**

- Listens: UDP 11000
- Replies: UDP 11001

**CLI usage with oscsend (liblo-tools):**

```bash
# Install oscsend
# Ubuntu: sudo apt install liblo-tools
# macOS: brew install liblo

# Set tempo
oscsend localhost 11000 /live/song/set/tempo f 128.0

# Start/stop
oscsend localhost 11000 /live/song/start_playing
oscsend localhost 11000 /live/song/stop_playing

# Fire clip (track 0, slot 0)
oscsend localhost 11000 /live/clip/fire ii 0 0

# Get track names (need listener)
oscsend localhost 11000 /live/song/get/track_names
```

**Python usage:**

```python
from pythonosc.udp_client import SimpleUDPClient

client = SimpleUDPClient("127.0.0.1", 11000)
client.send_message("/live/song/set/tempo", [140.0])
client.send_message("/live/clip/fire", [0, 0])
```

**Interactive console:**

```bash
cd AbletonOSC
python run-console.py
>>> /live/song/get/tempo
(120.0,)
>>> /live/song/set/tempo 140
>>> /live/clip/fire 0 0
```

-----

### 3. Audio Capture

#### Option A: JACK (Linux, cross-platform)

```bash
# Install
sudo apt install jackd2 jack-capture  # Ubuntu/Debian
brew install jack jack-capture         # macOS

# Start JACK
jackd -d alsa -r 44100 &

# Capture from Ableton's output (4 bars at 120 BPM = 8 seconds)
jack_capture \
  --port "Ableton*:out*" \
  --duration 8 \
  --format wav \
  /tmp/capture.wav

# Timemachine mode (always-rolling buffer)
jack_capture --timemachine --timemachine-prebuffer 30 /tmp/buffer.wav
```

#### Option B: PipeWire (Modern Linux)

```bash
# PipeWire usually works as JACK drop-in
pw-jack jack_capture --duration 8 /tmp/capture.wav
```

#### Option C: BlackHole + sox/ffmpeg (macOS)

```bash
# Install BlackHole from https://existential.audio/blackhole/
# Route Ableton output to BlackHole

# Capture with sox
sox -d -c 2 /tmp/capture.wav trim 0 8

# Or ffmpeg
ffmpeg -f avfoundation -i ":BlackHole 2ch" -t 8 -y /tmp/capture.wav
```

#### Option D: Virtual Audio Cable (Windows)

```bash
# Use VB-Cable or similar
# Capture with ffmpeg
ffmpeg -f dshow -i audio="CABLE Output" -t 8 -y capture.wav
```

-----

### 4. Audio Analysis

#### Essentia CLI (Fast, comprehensive)

```bash
# Install
pip install essentia

# Or download pre-built binaries from https://essentia.upf.edu/downloads/

# Run music extractor
essentia_streaming_extractor_music input.wav output.json

# With custom profile for mood analysis
essentia_streaming_extractor_music input.wav output.json profile.yaml
```

**profile.yaml for mood/energy analysis:**

```yaml
outputFormat: json
indent: 4
startTime: 0
endTime: 30
highlevel:
  compute: 1
  svm_models:
    - 'svm_models/mood_sad.history'
    - 'svm_models/mood_aggressive.history'
    - 'svm_models/mood_relaxed.history'
    - 'svm_models/mood_happy.history'
    - 'svm_models/danceability.history'
lowlevel:
  frameSize: 2048
  hopSize: 1024
rhythm:
  method: degara
tonal:
  frameSize: 4096
  hopSize: 2048
```

#### librosa (Python, flexible)

```bash
pip install librosa numpy
```

```python
import librosa
import json
import numpy as np

def analyze(filepath):
    y, sr = librosa.load(filepath)

    # Tempo
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

    # Energy
    rms = librosa.feature.rms(y=y)[0]

    # Brightness (spectral centroid)
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]

    # Chroma (key detection)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    key_profile = chroma.mean(axis=1)

    # MFCCs (timbre)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

    return {
        "tempo": float(tempo),
        "energy_mean": float(np.mean(rms)),
        "energy_max": float(np.max(rms)),
        "brightness_mean": float(np.mean(centroid)),
        "key_profile": key_profile.tolist(),
        "mfcc_mean": mfccs.mean(axis=1).tolist()
    }

if __name__ == "__main__":
    import sys
    result = analyze(sys.argv[1])
    print(json.dumps(result, indent=2))
```

#### Essentia with Deep Learning Models (Mood detection)

```python
from essentia.standard import MonoLoader, TensorflowPredictMusiCNN, TensorflowPredict2D
import numpy as np

# Download models from https://essentia.upf.edu/models.html

def analyze_mood(filepath):
    audio = MonoLoader(filename=filepath, sampleRate=16000, resampleQuality=4)()

    # Get embeddings
    embedding_model = TensorflowPredictMusiCNN(
        graphFilename="msd-musicnn-1.pb",
        output="model/dense/BiasAdd"
    )
    embeddings = embedding_model(audio)

    # Mood classifiers
    results = {}
    for mood in ['sad', 'aggressive', 'relaxed', 'happy']:
        model = TensorflowPredict2D(
            graphFilename=f"mood_{mood}-msd-musicnn-1.pb",
            output="model/Softmax"
        )
        pred = model(embeddings)
        results[f"mood_{mood}"] = float(np.mean(pred[:, 1]))

    return results
```

-----

### 5. Unified CLI Script

Save as `ableton-cli`:

```bash
#!/bin/bash
# ableton-cli - Unified CLI for Ableton Live control and analysis

set -e

CARABINER_PORT=${CARABINER_PORT:-17000}
OSC_PORT=${OSC_PORT:-11000}
CAPTURE_DIR="${CAPTURE_DIR:-/tmp/ableton_captures}"
ANALYSIS_SCRIPT="${ANALYSIS_SCRIPT:-$(dirname $0)/analyze.py}"

mkdir -p "$CAPTURE_DIR"

# ═══════════════════════════════════════════════════════════════
# LINK COMMANDS (via Carabiner)
# ═══════════════════════════════════════════════════════════════

link_status() {
    echo "status" | nc -q1 localhost "$CARABINER_PORT" 2>/dev/null || echo "Carabiner not running"
}

link_tempo() {
    echo "bpm $1" | nc -q1 localhost "$CARABINER_PORT"
}

link_start() {
    echo "enable-start-stop-sync" | nc -q1 localhost "$CARABINER_PORT"
    echo "start-playing" | nc -q1 localhost "$CARABINER_PORT"
}

link_stop() {
    echo "stop-playing" | nc -q1 localhost "$CARABINER_PORT"
}

get_bpm() {
    link_status | grep -oP ':bpm \K[0-9.]+'
}

# ═══════════════════════════════════════════════════════════════
# OSC COMMANDS (via AbletonOSC)
# ═══════════════════════════════════════════════════════════════

osc() {
    oscsend localhost "$OSC_PORT" "$@"
}

play() {
    osc /live/song/start_playing
}

stop() {
    osc /live/song/stop_playing
}

set_tempo() {
    osc /live/song/set/tempo f "$1"
}

fire_clip() {
    osc /live/clip/fire ii "$1" "$2"
}

stop_clip() {
    osc /live/clip/stop ii "$1" "$2"
}

mute_track() {
    osc /live/track/set/mute iii "$1" 1
}

unmute_track() {
    osc /live/track/set/mute iii "$1" 0
}

set_volume() {
    osc /live/track/set/volume if "$1" "$2"
}

# ═══════════════════════════════════════════════════════════════
# AUDIO CAPTURE
# ═══════════════════════════════════════════════════════════════

capture_duration() {
    local duration="$1"
    local outfile="$CAPTURE_DIR/capture_$(date +%s).wav"

    # Try JACK first, fall back to alternatives
    if command -v jack_capture &> /dev/null; then
        jack_capture --duration "$duration" "$outfile" 2>/dev/null
    elif command -v pw-record &> /dev/null; then
        pw-record --target 0 "$outfile" &
        sleep "$duration"
        kill $!
    else
        echo "Error: No capture tool found (jack_capture, pw-record)" >&2
        return 1
    fi

    echo "$outfile"
}

capture_bars() {
    local bars="${1:-4}"
    local bpm
    bpm=$(get_bpm)

    if [ -z "$bpm" ]; then
        bpm=120
        echo "Warning: Could not get BPM from Link, using default $bpm" >&2
    fi

    local duration
    duration=$(echo "scale=2; $bars * 4 * 60 / $bpm" | bc)

    echo "Capturing $bars bars at $bpm BPM ($duration seconds)..." >&2
    capture_duration "$duration"
}

# ═══════════════════════════════════════════════════════════════
# ANALYSIS
# ═══════════════════════════════════════════════════════════════

analyze() {
    local wavfile="$1"

    if [ ! -f "$wavfile" ]; then
        echo "Error: File not found: $wavfile" >&2
        return 1
    fi

    if [ -f "$ANALYSIS_SCRIPT" ]; then
        python3 "$ANALYSIS_SCRIPT" "$wavfile"
    else
        # Fallback to essentia CLI if available
        if command -v essentia_streaming_extractor_music &> /dev/null; then
            local jsonfile="${wavfile%.wav}.json"
            essentia_streaming_extractor_music "$wavfile" "$jsonfile" 2>/dev/null
            cat "$jsonfile"
        else
            echo "Error: No analysis tool found" >&2
            return 1
        fi
    fi
}

# ═══════════════════════════════════════════════════════════════
# COMBINED: LISTEN = CAPTURE + ANALYZE
# ═══════════════════════════════════════════════════════════════

listen() {
    local bars="${1:-4}"
    local wavfile
    wavfile=$(capture_bars "$bars")

    if [ -f "$wavfile" ]; then
        analyze "$wavfile"
    fi
}

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

usage() {
    cat <<EOF
Usage: ableton-cli <command> [args]

LINK COMMANDS (Carabiner):
  status              Show Link session status (tempo, peers, beat)
  tempo <bpm>         Set Link tempo
  start               Start transport (Link sync)
  stop                Stop transport (Link sync)

OSC COMMANDS (AbletonOSC):
  play                Start Ableton playback
  pause               Stop Ableton playback
  set-tempo <bpm>     Set Ableton tempo directly
  fire <track> <clip> Fire clip at track/clip index
  stop-clip <t> <c>   Stop clip
  mute <track>        Mute track
  unmute <track>      Unmute track
  volume <track> <v>  Set track volume (0.0-1.0)

CAPTURE:
  capture <seconds>   Capture N seconds of audio
  capture-bars <n>    Capture N bars (calculates from BPM)

ANALYSIS:
  analyze <file.wav>  Analyze audio file → JSON

COMBINED:
  listen [bars]       Capture N bars and analyze (default: 4)

ENVIRONMENT:
  CARABINER_PORT      Carabiner TCP port (default: 17000)
  OSC_PORT            AbletonOSC UDP port (default: 11000)
  CAPTURE_DIR         Directory for captures (default: /tmp/ableton_captures)
  ANALYSIS_SCRIPT     Path to analysis Python script

EOF
}

case "${1:-}" in
    # Link
    status)       link_status ;;
    tempo)        link_tempo "$2" ;;
    start)        link_start ;;
    stop)         link_stop ;;

    # OSC
    play)         play ;;
    pause)        stop ;;
    set-tempo)    set_tempo "$2" ;;
    fire)         fire_clip "$2" "$3" ;;
    stop-clip)    stop_clip "$2" "$3" ;;
    mute)         mute_track "$2" ;;
    unmute)       unmute_track "$2" ;;
    volume)       set_volume "$2" "$3" ;;

    # Capture
    capture)      capture_duration "$2" ;;
    capture-bars) capture_bars "$2" ;;

    # Analysis
    analyze)      analyze "$2" ;;

    # Combined
    listen)       listen "$2" ;;

    # Help
    -h|--help|help|"")
        usage ;;

    *)
        echo "Unknown command: $1" >&2
        usage >&2
        exit 1 ;;
esac
```

Save as `analyze.py`:

```python
#!/usr/bin/env python3
"""Audio analysis script for ableton-cli"""

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


def analyze_with_librosa(filepath):
    y, sr = librosa.load(filepath)

    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    rms = librosa.feature.rms(y=y)[0]
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

    # Estimate key from chroma
    key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    key_profile = chroma.mean(axis=1)
    estimated_key = key_names[int(np.argmax(key_profile))]

    return {
        "tempo": float(tempo),
        "estimated_key": estimated_key,
        "energy": {
            "mean": float(np.mean(rms)),
            "max": float(np.max(rms)),
            "std": float(np.std(rms))
        },
        "brightness": {
            "centroid_mean": float(np.mean(centroid)),
            "rolloff_mean": float(np.mean(rolloff))
        },
        "dynamics": {
            "zcr_mean": float(np.mean(zcr)),
        },
        "key_profile": key_profile.tolist(),
        "mfcc_summary": {
            "mean": mfccs.mean(axis=1).tolist(),
            "std": mfccs.std(axis=1).tolist()
        }
    }


def analyze_with_essentia(filepath):
    loader = es.MonoLoader(filename=filepath)
    audio = loader()

    # Rhythm
    rhythm_extractor = es.RhythmExtractor2013(method="multifeature")
    bpm, beats, beats_confidence, _, _ = rhythm_extractor(audio)

    # Key
    key_extractor = es.KeyExtractor()
    key, scale, strength = key_extractor(audio)

    # Energy
    energy = es.Energy()(audio)
    loudness = es.Loudness()(audio)

    # Danceability
    danceability, _ = es.Danceability()(audio)

    return {
        "tempo": float(bpm),
        "tempo_confidence": float(np.mean(beats_confidence)),
        "key": key,
        "scale": scale,
        "key_strength": float(strength),
        "energy": float(energy),
        "loudness": float(loudness),
        "danceability": float(danceability)
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
        result["error"] = "No analysis library available. Install librosa or essentia."

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
```

-----

## Quick Start (macOS)

### 1. Install Everything via Homebrew

```bash
# Core tools
brew install liblo              # OSC send/receive (oscsend, oscdump)
brew install netcat             # TCP for Carabiner
brew install sox                # Audio Swiss Army knife
brew install ffmpeg             # Audio/video processing
brew install jq                 # JSON parsing for scripts
brew install bc                 # Calculator for bar→seconds

# MIDI tools
brew install --cask sendmidi    # CLI MIDI sender
brew install --cask receivemidi # CLI MIDI receiver

# Audio capture (pick one)
brew install blackhole-2ch      # Virtual audio device
brew install jack               # Pro audio routing

# Carabiner (Ableton Link bridge)
brew install --cask carabiner   # Or download from GitHub releases

# Python libraries
pip install librosa numpy python-osc mido
pip install essentia            # May need: brew install tensorflow first
```

### 2. One-liner Setup

```bash
# Full macOS setup
brew install liblo netcat sox ffmpeg jq bc && \
brew install --cask sendmidi receivemidi blackhole-2ch carabiner && \
pip install librosa numpy python-osc mido essentia
```

### 3. AbletonOSC Setup

```bash
# Clone and install
git clone https://github.com/ideoforms/AbletonOSC.git
cp -r AbletonOSC ~/Music/Ableton/User\ Library/Remote\ Scripts/

# In Ableton: Preferences → Link/Tempo/MIDI → Control Surface → AbletonOSC
```

### 4. Configure Ableton

1. **Enable Link:** Preferences → Link/Tempo/MIDI → Enable Link
2. **Enable AbletonOSC:** Control Surface dropdown → Select "AbletonOSC"
3. **Audio routing:** Set output to BlackHole 2ch (for capture)

### 5. Start Services

```bash
# Start Carabiner daemon
carabiner &

# Verify OSC is responding
oscsend localhost 11000 /live/song/get/tempo
```

### 6. Test

```bash
./ableton-cli status
./ableton-cli set-tempo 128
./ableton-cli fire 0 0
./ableton-cli listen 4
```

-----

## Querying Ableton (What's Available?)

AbletonOSC exposes the entire Live Object Model. Here's how to discover what you have:

### Session Overview

```bash
# Get all track names
oscsend localhost 11000 /live/song/get/track_data

# Get scene names
oscsend localhost 11000 /live/song/get/scene_names

# Get tempo, time signature, etc.
oscsend localhost 11000 /live/song/get/tempo
oscsend localhost 11000 /live/song/get/signature_numerator
oscsend localhost 11000 /live/song/get/signature_denominator
```

### Track Information

```bash
# Track count
oscsend localhost 11000 /live/song/get/num_tracks

# Individual track info (track index 0)
oscsend localhost 11000 /live/track/get/name i 0
oscsend localhost 11000 /live/track/get/color i 0
oscsend localhost 11000 /live/track/get/volume i 0
oscsend localhost 11000 /live/track/get/panning i 0
oscsend localhost 11000 /live/track/get/mute i 0
oscsend localhost 11000 /live/track/get/solo i 0
oscsend localhost 11000 /live/track/get/arm i 0

# Get all clips on a track
oscsend localhost 11000 /live/track/get/clips/name i 0
```

### Clip Information

```bash
# Clip details (track 0, clip slot 0)
oscsend localhost 11000 /live/clip/get/name ii 0 0
oscsend localhost 11000 /live/clip/get/length ii 0 0
oscsend localhost 11000 /live/clip/get/is_playing ii 0 0
oscsend localhost 11000 /live/clip/get/is_recording ii 0 0
oscsend localhost 11000 /live/clip/get/color ii 0 0

# Get notes from a MIDI clip (returns note data)
oscsend localhost 11000 /live/clip/get/notes ii 0 0
```

### Devices & Parameters

```bash
# List devices on track 0
oscsend localhost 11000 /live/track/get/devices/name i 0

# Get device parameters (track 0, device 0)
oscsend localhost 11000 /live/device/get/name ii 0 0
oscsend localhost 11000 /live/device/get/parameters/name ii 0 0
oscsend localhost 11000 /live/device/get/parameters/value ii 0 0

# Set device parameter (track, device, param, value)
oscsend localhost 11000 /live/device/set/parameter/value iif 0 0 0.5
```

### Browser & Samples (Limited)

```bash
# Note: AbletonOSC doesn't expose browser/sample library directly
# But you can query what's loaded in drum racks:

# Get drum pad info (if device 0 is a Drum Rack)
oscsend localhost 11000 /live/device/get/drum_pads ii 0 0
```

### Python Query Script

Save as `query-session.py`:

```python
#!/usr/bin/env python3
"""Query Ableton session state via OSC"""

import json
import time
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import threading

class AbletonQuery:
    def __init__(self, host="127.0.0.1", send_port=11000, recv_port=11001):
        self.client = SimpleUDPClient(host, send_port)
        self.responses = {}
        self.dispatcher = Dispatcher()
        self.dispatcher.set_default_handler(self._handle_response)
        self.server = BlockingOSCUDPServer((host, recv_port), self.dispatcher)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def _handle_response(self, address, *args):
        self.responses[address] = args

    def query(self, address, *args, timeout=0.5):
        self.responses.pop(address, None)
        self.client.send_message(address, list(args))
        time.sleep(timeout)
        return self.responses.get(address)

    def get_session_info(self):
        return {
            "tempo": self.query("/live/song/get/tempo"),
            "num_tracks": self.query("/live/song/get/num_tracks"),
            "num_scenes": self.query("/live/song/get/num_scenes"),
        }

    def get_track_info(self, track_idx):
        return {
            "name": self.query("/live/track/get/name", track_idx),
            "volume": self.query("/live/track/get/volume", track_idx),
            "mute": self.query("/live/track/get/mute", track_idx),
            "solo": self.query("/live/track/get/solo", track_idx),
            "arm": self.query("/live/track/get/arm", track_idx),
        }

    def get_all_tracks(self):
        num = self.query("/live/song/get/num_tracks")
        if not num:
            return []
        tracks = []
        for i in range(int(num[0])):
            tracks.append(self.get_track_info(i))
        return tracks

    def get_clip_slots(self, track_idx):
        """Get all clip slot states for a track"""
        clips = self.query("/live/track/get/clips/name", track_idx)
        return clips

if __name__ == "__main__":
    import sys
    q = AbletonQuery()

    if len(sys.argv) > 1 and sys.argv[1] == "tracks":
        print(json.dumps(q.get_all_tracks(), indent=2))
    else:
        print(json.dumps(q.get_session_info(), indent=2))
```

-----

## MIDI Building Blocks

### SendMIDI & ReceiveMIDI

These CLI tools from Geert Bevin are essential for MIDI scripting:

```bash
# List MIDI devices
sendmidi list
receivemidi list

# Send notes (channel 1 by default)
sendmidi dev "IAC Driver Bus 1" on 60 100    # Note on: C4, velocity 100
sendmidi dev "IAC Driver Bus 1" off 60       # Note off

# Send CC
sendmidi dev "IAC Driver Bus 1" cc 1 64      # Mod wheel to 64

# Send program change
sendmidi dev "IAC Driver Bus 1" pc 5         # Program 5

# Chained commands (chord)
sendmidi dev "IAC Driver Bus 1" on 60 100 on 64 100 on 67 100

# With timing (milliseconds)
sendmidi dev "IAC Driver Bus 1" on 60 100 sleep 500 off 60
```

### Basic MIDI Patterns (Shell Scripts)

Save as `midi/kick.sh`:
```bash
#!/bin/bash
# 4-on-the-floor kick pattern (C1 = 36)
DEV="${MIDI_DEV:-IAC Driver Bus 1}"
sendmidi dev "$DEV" on 36 127 sleep 125 off 36 \
                    on 36 127 sleep 125 off 36 \
                    on 36 127 sleep 125 off 36 \
                    on 36 127 sleep 125 off 36
```

Save as `midi/hihat.sh`:
```bash
#!/bin/bash
# 8th note hi-hats (F#1 = 42)
DEV="${MIDI_DEV:-IAC Driver Bus 1}"
for i in {1..8}; do
    sendmidi dev "$DEV" on 42 80 sleep 62 off 42
done
```

Save as `midi/chord.sh`:
```bash
#!/bin/bash
# Play a chord: root + intervals
DEV="${MIDI_DEV:-IAC Driver Bus 1}"
ROOT=${1:-60}  # Default C4
VEL=${2:-100}

# Major chord
sendmidi dev "$DEV" on $ROOT $VEL on $((ROOT+4)) $VEL on $((ROOT+7)) $VEL
sleep 1
sendmidi dev "$DEV" off $ROOT off $((ROOT+4)) off $((ROOT+7))
```

Save as `midi/arp.sh`:
```bash
#!/bin/bash
# Simple arpeggiator
DEV="${MIDI_DEV:-IAC Driver Bus 1}"
ROOT=${1:-60}
SPEED=${2:-100}  # ms between notes
VEL=100

NOTES=($ROOT $((ROOT+4)) $((ROOT+7)) $((ROOT+12)))

for note in "${NOTES[@]}"; do
    sendmidi dev "$DEV" on $note $VEL sleep $SPEED off $note
done
```

### Python MIDI with mido

```python
#!/usr/bin/env python3
"""MIDI building blocks using mido"""

import mido
import time

def list_ports():
    print("Input ports:", mido.get_input_names())
    print("Output ports:", mido.get_output_names())

def play_note(port_name, note=60, velocity=100, duration=0.5):
    with mido.open_output(port_name) as port:
        port.send(mido.Message('note_on', note=note, velocity=velocity))
        time.sleep(duration)
        port.send(mido.Message('note_off', note=note, velocity=0))

def play_chord(port_name, notes, velocity=100, duration=1.0):
    with mido.open_output(port_name) as port:
        for note in notes:
            port.send(mido.Message('note_on', note=note, velocity=velocity))
        time.sleep(duration)
        for note in notes:
            port.send(mido.Message('note_off', note=note, velocity=0))

def play_pattern(port_name, pattern, bpm=120):
    """
    Pattern format: [(note, velocity, duration_beats), ...]
    duration_beats: 1 = quarter note, 0.5 = eighth, etc.
    """
    beat_duration = 60 / bpm
    with mido.open_output(port_name) as port:
        for note, vel, dur in pattern:
            if note is not None:
                port.send(mido.Message('note_on', note=note, velocity=vel))
                time.sleep(beat_duration * dur)
                port.send(mido.Message('note_off', note=note, velocity=0))
            else:
                time.sleep(beat_duration * dur)  # Rest

# Example patterns
KICK_PATTERN = [(36, 127, 1), (36, 127, 1), (36, 127, 1), (36, 127, 1)]
SNARE_PATTERN = [(None, 0, 1), (38, 100, 1), (None, 0, 1), (38, 100, 1)]
HIHAT_PATTERN = [(42, 80, 0.5)] * 8

if __name__ == "__main__":
    list_ports()
```

### MIDI Note Reference

```
# Drum Map (General MIDI)
C1  (36) = Kick
D1  (38) = Snare
F#1 (42) = Closed Hi-Hat
A#1 (46) = Open Hi-Hat
C#2 (49) = Crash
D#2 (51) = Ride

# Notes
C4 = 60 (Middle C)
A4 = 69 (Concert A, 440Hz)

# Octave: C=0, C#=1, D=2, D#=3, E=4, F=5, F#=6, G=7, G#=8, A=9, A#=10, B=11
# MIDI note = (octave + 1) * 12 + semitone
```

-----

## Clip Launcher Patterns

### Fire Clips in Sequence

```bash
#!/bin/bash
# Play through scenes
for scene in 0 1 2 3; do
    echo "Firing scene $scene"
    oscsend localhost 11000 /live/song/fire_scene i $scene
    sleep 8  # Wait 8 seconds (adjust for your arrangement)
done
```

### Build Energy (Layer Tracks)

```bash
#!/bin/bash
# Gradually unmute tracks to build energy
TRACKS=(1 2 3 4 5)
DELAY=4  # bars at 120 BPM = 8 seconds

for track in "${TRACKS[@]}"; do
    echo "Bringing in track $track"
    oscsend localhost 11000 /live/track/set/mute iii "$track" 0
    sleep $((DELAY * 2))
done
```

### Random Clip Triggering

```bash
#!/bin/bash
# Fire random clips for generative composition
TRACKS=4
CLIPS=8

while true; do
    track=$((RANDOM % TRACKS))
    clip=$((RANDOM % CLIPS))
    echo "Firing track $track, clip $clip"
    oscsend localhost 11000 /live/clip/fire ii $track $clip
    sleep $((RANDOM % 4 + 2))
done
```

-----

## Example Workflow with Claude Code

```bash
# 1. Check current state
$ ./ableton-cli status
status {:peers 1 :bpm 120.0 :start 73746356220 :beat 2453.7 :playing true}

# 2. Listen to 4 bars and get analysis
$ ./ableton-cli listen 4
{
  "tempo": 120.0,
  "estimated_key": "A",
  "energy": {"mean": 0.34, "max": 0.78},
  "brightness": {"centroid_mean": 2847.3},
  "danceability": 0.72
}

# 3. Claude interprets: "Energy is low, let's add some drive"
# Claude executes:
$ ./ableton-cli fire 2 0   # Fire a drum loop
$ ./ableton-cli volume 2 0.8

# 4. Listen again to verify
$ ./ableton-cli listen 4
# Energy increased, mood shifted...
```

-----

## Extending for Mood-Based Composition

For deeper mood analysis, download Essentia's pre-trained models:

```bash
# Download mood models
wget https://essentia.upf.edu/models/classification-heads/mood_sad/mood_sad-msd-musicnn-1.pb
wget https://essentia.upf.edu/models/classification-heads/mood_aggressive/mood_aggressive-msd-musicnn-1.pb
wget https://essentia.upf.edu/models/classification-heads/mood_relaxed/mood_relaxed-msd-musicnn-1.pb
wget https://essentia.upf.edu/models/classification-heads/mood_happy/mood_happy-msd-musicnn-1.pb
wget https://essentia.upf.edu/models/feature-extractors/musicnn/msd-musicnn-1.pb
```

Then extend `analyze.py` to use TensorFlow predictions for mood classification.

-----

## Related Ideas

- **audiome** - Personal audio corpus manager using similar librosa analysis

## Resources

- **Carabiner:** https://github.com/Deep-Symmetry/carabiner
- **AbletonOSC:** https://github.com/ideoforms/AbletonOSC
- **Ableton Link:** https://github.com/Ableton/link
- **Essentia:** https://essentia.upf.edu/
- **librosa:** https://librosa.org/
- **jack_capture:** https://github.com/kmatheussen/jack_capture
- **SendMIDI/ReceiveMIDI:** https://github.com/gbevin/SendMIDI

## Log

- 2026-02-04 - Added brew install commands, MIDI building blocks, Ableton query section
- 2026-02-04 - Created idea with full architecture documentation
