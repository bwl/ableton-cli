# ableton-cli

CLI-based music composition with Ableton Live — tempo sync, remote control, audio capture, AI analysis.

Built to be used with [Claude Code](https://github.com/anthropics/claude-code). Claude can control Ableton, listen to the output, analyze what it hears, and iteratively improve the song — a full creative feedback loop from the terminal.

## How It Works

```
┌──────────────┐    OSC (python-osc)     ┌──────────────────┐
│              │ ◄─────────────────────► │                  │
│  Claude Code │    TCP (stdlib socket)   │   Ableton Live   │
│              │ ◄─────────────────────► │                  │
│              │                          │   + AbletonOSC   │
│  ableton-cli │    Audio (BlackHole)     │   + Link enabled │
│              │ ◄──────────────────────  │                  │
└──────┬───────┘                          └──────────────────┘
       │
       ▼
  librosa analysis
  (tempo, key, energy,
   brightness, timbre)
       │
       ▼
  Claude interprets →  adjusts → listens again
```

Claude writes MIDI patterns, fires clips, tweaks device parameters, captures the audio output through a virtual loopback, analyzes what it hears, and decides what to change next. No GUI needed.

## Setup

### Prerequisites

- **Ableton Live** (11 or 12)
- **[AbletonOSC](https://github.com/ideoforms/AbletonOSC)** — installed as a Control Surface in Ableton
- **[Carabiner](https://github.com/Deep-Symmetry/carabiner)** — Ableton Link bridge (optional, for tempo sync)
- **Python 3.12+**
- **[uv](https://github.com/astral-sh/uv)** — Python package manager

### Install

```bash
git clone https://github.com/bwl/ableton-cli.git
cd ableton-cli
uv sync
```

### AbletonOSC

```bash
git clone https://github.com/ideoforms/AbletonOSC.git
cp -r AbletonOSC ~/Music/Ableton/User\ Library/Remote\ Scripts/
```

In Ableton: **Preferences → Link/Tempo/MIDI → Control Surface → AbletonOSC**

### Carabiner (optional)

```bash
brew install --cask carabiner
carabiner &
```

Enable Link in Ableton: **Preferences → Link/Tempo/MIDI → Enable Link**

### Audio Loopback (for listen/capture)

This is what lets Claude hear Ableton's output. Install BlackHole, a virtual audio driver:

```bash
brew install --cask blackhole-2ch
# Reboot required after install
```

After reboot, set up a **Multi-Output Device** so you hear audio AND Claude can capture it:

1. Open **Audio MIDI Setup** (in /Applications/Utilities)
2. Click **+** in the bottom left → **Create Multi-Output Device**
3. Check both **BlackHole 2ch** and your speakers/headphones
4. In Ableton: **Preferences → Audio → Audio Output Device → Multi-Output Device**

Now Ableton's audio goes to both your speakers and BlackHole. The CLI captures from BlackHole.

### Verify

```bash
uv run bin/ableton-cli status          # Check Carabiner/Link
uv run bin/ableton-cli query session   # Check AbletonOSC connection
uv run bin/ableton-cli set-tempo 120   # Change tempo live
```

## Quick Start

### 1. Create a band template

```bash
uv run bin/ableton-cli template band 120
```

This creates 8 named tracks with pre-programmed MIDI clips in A minor. You need to add instruments to each track in Ableton (AbletonOSC can't load devices yet):

| Track | Name | Suggested Instrument |
|-------|------|---------------------|
| 0 | Drums | Drum Rack |
| 1 | Bass | Analog / Operator |
| 2 | Keys | Electric / Grand Piano |
| 3 | Synth Lead | Wavetable / Drift |
| 4 | Synth Pad | Wavetable / Drift |
| 5 | Guitar | Simpler |
| 6 | Perc | Drum Rack (second kit) |
| 7 | Vox / FX | Audio track |

### 2. Fire clips and layer

```bash
uv run bin/ableton-cli play
uv run bin/ableton-cli fire 0 0          # Drums: Basic Beat
uv run bin/ableton-cli fire 1 0          # Bass: Root Pulse
uv run bin/ableton-cli fire 2 0          # Keys: Chords
uv run bin/ableton-cli fire-scene 0      # Fire everything in row 0
```

### 3. Tweak parameters live

```bash
# Discover what knobs are available
uv run bin/ableton-cli query params 3 0

# Sweep a filter
uv run bin/ableton-cli device-param 3 0 1 40    # Filter Cutoff → 40
uv run bin/ableton-cli device-param 3 0 4 80    # Reverb → 80
```

### 4. Program new patterns on the fly

```bash
# Create an empty 4-beat clip on track 1, slot 5
uv run bin/ableton-cli create-clip 1 5 4

# Add a bass line (pitch:start_beat:duration[:velocity])
uv run bin/ableton-cli add-notes 1 5  33:0:0.5:110  33:1:0.5:100  36:2:0.5:110  40:3:0.5:100

# Name it and fire it
uv run bin/ableton-cli set-clip-name 1 5 "New Bass"
uv run bin/ableton-cli fire 1 5
```

## The Feedback Loop: Listen → Analyze → Improve

This is the core idea. With the audio loopback set up, Claude can hear what Ableton is playing, analyze the audio, and make informed musical decisions.

### How it works

```bash
# Capture 4 bars of audio and analyze it
uv run bin/ableton-cli listen 4
```

This captures audio from BlackHole, runs it through librosa, and returns JSON:

```json
{
  "file": "captures/capture_1738800000.wav",
  "librosa": {
    "tempo": 120.0,
    "estimated_key": "A",
    "energy": {
      "mean": 0.0834,
      "max": 0.3412,
      "std": 0.0567
    },
    "brightness": {
      "centroid_mean": 2847.3,
      "rolloff_mean": 5891.2
    },
    "dynamics": {
      "zcr_mean": 0.0823
    },
    "key_profile": [0.42, 0.11, 0.28, ...],
    "mfcc_summary": { ... }
  }
}
```

### What Claude does with this

Claude reads the analysis and makes musical judgments:

- **Energy too low?** → Fire more clips, increase volumes, switch to a driving drum pattern
- **Too bright?** → Sweep filter cutoffs down, reduce high-frequency tracks
- **Tempo feels off?** → Adjust BPM, switch to half-time drums
- **Key conflict?** → Rewrite a clip's notes to resolve dissonance
- **Needs more movement?** → Add arpeggiated patterns, automate device parameters
- **Building to a drop?** → Mute tracks one by one, fire the buildup drum pattern, then fire-scene

### Example session with Claude Code

```
You:    "Make it groovier"

Claude: *listens to 4 bars*
        Analysis: energy 0.08, brightness high, straight 8th hats

        *switches drums to funky beat*
        *switches bass to funky pattern*
        *sweeps lead filter down*
        *adds percussion shaker*

        *listens again*
        Analysis: energy 0.14, syncopation detected

Claude: "Swapped to syncopated drums and bass, pulled the lead filter
         back, added shaker. Energy doubled. Want me to keep pushing it?"
```

### The listen-react loop in practice

When you give Claude Code access to this CLI, it can run an iterative loop:

1. **`listen 4`** — capture and analyze 4 bars
2. **Interpret** — Claude reads the JSON and understands the musical state
3. **Act** — fire clips, write new patterns, adjust params, change tempo
4. **`listen 4`** — hear the result
5. **Evaluate** — did energy increase? did the key resolve? is it groovier?
6. **Repeat** — keep refining until it sounds right

This works because every action is a simple CLI command that Claude can call directly. No mouse, no GUI, no DAW expertise needed — just musical intent translated to OSC messages.

## Command Reference

### Link (Carabiner)
| Command | Description |
|---------|-------------|
| `status` | Show Link session status |
| `tempo <bpm>` | Set Link tempo |
| `start` | Start transport |
| `stop` | Stop transport |

### Transport
| Command | Description |
|---------|-------------|
| `play` | Start playback |
| `pause` | Stop playback |
| `set-tempo <bpm>` | Set Ableton tempo via OSC |

### Tracks
| Command | Description |
|---------|-------------|
| `create-midi-track [index]` | Create MIDI track (-1 = append) |
| `create-audio-track [index]` | Create audio track |
| `delete-track <track>` | Delete a track |
| `set-track-name <t> <name>` | Rename a track |

### Clips
| Command | Description |
|---------|-------------|
| `fire <track> <clip>` | Fire clip |
| `stop-clip <track> <clip>` | Stop clip |
| `fire-scene <scene>` | Fire entire scene |
| `create-clip <t> <s> [len]` | Create empty MIDI clip (default 4 beats) |
| `delete-clip <t> <s>` | Delete clip |
| `set-clip-name <t> <s> <name>` | Rename clip |
| `add-notes <t> <s> P:S:D[:V] ...` | Add MIDI notes |
| `clear-notes <t> <s>` | Remove all notes |

### Mixer
| Command | Description |
|---------|-------------|
| `mute / unmute <track>` | Mute/unmute |
| `solo / unsolo <track>` | Solo/unsolo |
| `volume <track> <0.0-1.0>` | Set volume |
| `pan <track> <-1.0 to 1.0>` | Set panning |
| `arm / disarm <track>` | Arm/disarm recording |
| `device-param <t> <d> <p> <v>` | Set device parameter |

### Query
| Command | Description |
|---------|-------------|
| `query session` | Tempo, track count, time sig |
| `query tracks` | All track names, volumes, mute/solo/arm |
| `query track <n>` | Single track detail |
| `query clips <n>` | Clip slots for a track |
| `query devices <n>` | Device names on a track |
| `query params <t> [d]` | Device parameter names and values |

### Capture & Analysis
| Command | Description |
|---------|-------------|
| `capture <seconds>` | Capture N seconds of audio |
| `capture-bars [n]` | Capture N bars (auto-calculates from BPM) |
| `analyze <file.wav>` | Analyze audio → JSON |
| `listen [bars]` | Capture + analyze (default: 4 bars) |

### Templates
| Command | Description |
|---------|-------------|
| `template band [bpm]` | Create 8-track band with starter patterns |
| `template list` | List available templates |

### MIDI
| Command | Description |
|---------|-------------|
| `midi list` | List MIDI devices |
| `midi note <n> [vel] [ms]` | Send note |
| `midi chord <root> [type]` | Send chord |
| `midi cc <num> <val>` | Send CC |
| `midi pattern <name\|list>` | Play/list patterns |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CARABINER_HOST` | `localhost` | Carabiner host |
| `CARABINER_PORT` | `17000` | Carabiner port |
| `OSC_HOST` | `127.0.0.1` | AbletonOSC host |
| `OSC_PORT` | `11000` | AbletonOSC port |
| `CAPTURE_DIR` | `./captures` | Audio capture directory |
| `MIDI_DEV` | `IAC Driver Bus 1` | MIDI output device |

## Licensing

All runtime Python dependencies are permissively licensed (MIT, ISC, BSD, Unlicense):

| Package | License | Role |
|---------|---------|------|
| python-osc | Unlicense | OSC client (Ableton control) |
| mido | MIT | MIDI I/O |
| python-rtmidi | MIT | MIDI backend |
| librosa | ISC | Audio analysis |
| numpy | BSD-3 | Numerical computing |

External tools invoked as subprocesses (not linked):
- **Carabiner** (GPL-2.0) — Link bridge, talked to over TCP
- **ffmpeg** / **sox** (LGPL/GPL) — audio capture
- **BlackHole** (GPL-3.0) — macOS virtual audio driver
