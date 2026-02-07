# ableton-cli: Music Composition Guide

You are controlling Ableton Live through a CLI. You can write MIDI notes, fire clips, tweak parameters, capture audio, see spectrograms, and analyze what you hear. This makes you a composer, producer, and mix engineer — from the terminal.

## The Golden Rule

**Always listen after you change something.** The feedback loop is:

1. Make a musical change (write notes, fire clips, tweak params)
2. `listen -s -t -e 4` — capture 4 bars with full analysis
3. Read the spectrogram PNGs to *see* the sound
4. Interpret the JSON — energy, chords, brightness, onsets
5. Decide what to change next
6. Repeat

Never make more than 2-3 changes without listening. You are composing blind without the feedback loop.

## Running Commands

All commands go through `uv run bin/ableton-cli <command>`. Ableton must be open with AbletonOSC enabled.

### Quick Reference — Most Used Commands

```
set-tempo <bpm>                    # Set tempo (NOT "bpm" or "tempo" — those are Link-only)
play / pause                       # Start/stop playback
fire <track> <clip>                # Fire a clip
fire-scene <scene>                 # Fire all clips in a scene row
stop-clip <track> <clip>           # Stop a clip
create-clip <t> <s> [beats]        # Create empty MIDI clip (default 4 beats)
add-notes <t> <s> P:S:D[:V] ...   # Add MIDI notes to a clip
clear-notes <t> <s>               # Remove all notes from a clip
delete-clip <t> <s>               # Delete a clip
set-clip-name <t> <s> <name>      # Name a clip
volume <track> <0.0-1.0>          # Set track volume
solo <track> / unsolo <track>     # Solo/unsolo
mute <track> / unmute <track>     # Mute/unmute
device-param <t> <d> <p> <v>      # Set device parameter
query params <t> [d]              # Discover device parameter names
query session                      # Get tempo, track count, time sig
query tracks                       # List all tracks
listen [-s] [-t] [-e] [bars]      # Capture + analyze (default 4 bars)
template band [bpm]               # Create 8-track band scaffold
probe <track> [bars]              # Map sounds across octaves
sweep <t> <d> <p> [start end steps] # Parameter sweep with capture
mix-check [tracks] [bars]         # Per-track analysis
```

**Common mistakes:** The command is `set-tempo`, not `bpm` or `tempo`. The command is `pause`, not `stop` (which is Link-only). Track and clip indices are 0-based.

## Song Notes

Song-specific notes live in `compositions/<song-name>.md`. Before starting work on a song, read its file. After a session, update it with what changed. The format:

```markdown
# Song Name

**Key:** Am | **BPM:** 120 | **Time Sig:** 4/4

## Concept
One paragraph describing the vibe, genre, references.

## Session Layout
| Track | Name | Instrument | Role |
|-------|------|------------|------|
| 0 | Drums | Upright Bass | Main beat |
| ... | | | |

## Structure
| Scene | Name | Bars | Description |
|-------|------|------|-------------|
| 0 | Intro | 4 | Sparse drums + pad |
| ... | | | |

## Current State
What's working, what needs attention.

## Session Log
- [date] What was done and what was learned
```

## How to Compose

### Starting a New Song

1. Decide key, BPM, vibe — ask the user if not specified
2. `template band <bpm>` to scaffold 8 tracks
3. User adds instruments manually in Ableton (we can't load devices via OSC)
4. Create `compositions/<name>.md` with the plan
5. Start with drums + bass — the foundation
6. Layer up: keys, then lead, then pad, then texture

### Writing MIDI Notes

Notes use the format `pitch:start_beat:duration[:velocity]`:

```bash
# Create a 4-beat clip on track 1, slot 5
create-clip 1 5 4

# Add notes (A1=33, C2=36, D2=38, E2=40)
add-notes 1 5  33:0:0.75:110  36:1:0.75:100  38:2:0.75:110  40:3:0.75:100

# Name and fire it
set-clip-name 1 5 "Walking Bass"
fire 1 5
```

MIDI note numbers: C4=60. Each octave is 12 semitones. Common reference points:
- Bass range: 28-55 (E1-G3)
- Mid range: 48-72 (C3-C5)
- High range: 60-96 (C4-C7)
- Drums: kick=36, snare=38, hat=42, open hat=46, crash=49, ride=51

### Clip Slot Strategy

- **Slots 0-7**: Scene sections (intro, verse, chorus, bridge, etc.)
- **Slot 127**: Reserved for `probe` command temp clips
- Fire entire scenes with `fire-scene <n>` for arrangement playback

### Velocity = Expression

Don't use flat velocity. Musical dynamics come from velocity variation:
- Ghost notes: 30-50
- Normal: 70-100
- Accents: 100-120
- Max impact: 127

Off-beat ghost notes on snare/hats make grooves feel human.

### Timing = Groove

Notes don't have to land exactly on the grid. Nudge start times by small amounts (0.01-0.05 beats) for swing. Or use exact subdivisions:
- Quarter notes: 0, 1, 2, 3
- 8th notes: 0, 0.5, 1, 1.5, ...
- 16th notes: 0, 0.25, 0.5, 0.75, ...
- Triplets: 0, 0.333, 0.667, 1, ...

### Building Arrangements

Think in 4-bar or 8-bar sections. A typical arrangement:

| Section | Bars | What Happens |
|---------|------|-------------|
| Intro | 4-8 | 1-2 elements, sparse |
| Verse | 8-16 | Core groove, most elements |
| Pre-chorus | 4 | Build energy — add layers, raise filter |
| Chorus | 8-16 | Full energy, all elements, peak brightness |
| Breakdown | 4-8 | Strip back to 1-2 elements |
| Build | 4 | Snare roll, filter sweep up |
| Drop/Chorus | 8-16 | Maximum energy |
| Outro | 4-8 | Wind down, strip layers |

Use scenes (rows of clips) for sections. `fire-scene <n>` transitions everything at once.

## Analysis: What the Numbers Mean

### listen / analyze flags

```bash
listen 4              # Basic: tempo, key, energy, brightness, MFCCs
listen -s 4           # + spectrogram PNGs (mel + chroma)
listen -t 4           # + per-beat energy/brightness/chroma arrays
listen -e 4           # + onsets, HPSS, spectral contrast, tonnetz, chords
listen -s -t -e 4     # Everything
```

### Reading the JSON

**Energy** — How loud/powerful the mix is.
- `mean < 0.02`: Nearly silent. Is anything playing?
- `mean 0.02-0.08`: Sparse/quiet. Good for intros, breakdowns.
- `mean 0.08-0.20`: Normal. Full arrangement, moderate levels.
- `mean > 0.20`: Loud/dense. Climax, drop, or potentially clipping.

**Brightness** — How much high-frequency content.
- `centroid_mean < 1500`: Dark, bassy. Sub-heavy, filtered sounds.
- `centroid_mean 1500-4000`: Balanced. Most well-mixed music lives here.
- `centroid_mean > 4000`: Bright/harsh. Lots of hats/cymbals, open filters.

**HPSS** (harmonic/percussive ratio) — Character of the sound.
- `harmonic_ratio > 0.7`: Melodic-dominant. Pads, strings, vocals.
- `percussive_ratio > 0.5`: Rhythm-dominant. Drums, percussion heavy.
- `~0.5/0.5`: Balanced mix of melodic and rhythmic.

**Onsets** — Rhythmic density.
- `density_per_sec < 2`: Sparse. Whole notes, pads.
- `density_per_sec 2-6`: Normal groove.
- `density_per_sec > 8`: Busy. 16th note patterns, fills, dense.

**Chords per beat** — What the harmony is doing.
- Confirms whether your notes are producing the intended chords
- Watch for unexpected chord names — could mean note conflicts between tracks

### Reading Spectrograms

After `listen -s`, read the PNG files with the Read tool:
- `*_mel.png`: Mel spectrogram — shows energy across frequency over time. Look for:
  - Bright horizontal bands = sustained notes/drones
  - Vertical lines = transients (drums, plucks)
  - Empty dark regions = silence or filtered frequencies
  - Even spread vs. clustered energy
- `*_chroma.png`: Chromagram — shows pitch class energy over time. Look for:
  - Which notes are loudest (bright rows)
  - Whether the harmony changes over time (vertical color shifts)
  - Note conflicts (too many bright rows = dense/muddy harmony)

### Per-Beat Time Series

With `-t`, you get arrays indexed by beat:
- `energy_per_beat[]`: Is the energy consistent or does it surge/drop?
- `brightness_per_beat[]`: Does the timbre change over time?
- `chroma_per_beat[][]`: 12-bin pitch class at each beat — the raw harmonic content

Use these to spot: unintentional volume drops, filter sweeps not working, timing issues.

## Procedures: Automated Workflows

### Probing a Track

```bash
probe <track> [bars]
```

Solos the track, plays chromatic notes across octaves (C1-C6), captures + analyzes each range. Returns spectrograms for each octave. Use this to map what sounds an instrument makes across its range — essential for drum racks where each note triggers a different sample.

### Parameter Sweeps

```bash
sweep <track> <device> <param> [start end steps] [bars]
```

Sweeps a device parameter from `start` to `end` in `steps` increments, capturing audio at each point. Use this to find the sweet spot for filter cutoffs, reverb amounts, etc.

First discover parameters: `query params <track> <device>`

### Mix Check

```bash
mix-check [track_count] [bars]
```

Solos each track in turn, captures and analyzes. Returns per-track analysis with spectrograms. Use this to understand what each track contributes to the mix — find frequency clashes, balance issues, tracks that are too quiet.

## Continuous Monitoring

```bash
monitor start 4    # Capture+analyze every 4 bars, runs until Ctrl-C
monitor latest     # Read latest analysis (from any terminal)
```

Run `monitor start` in background. Then `monitor latest` to check what's happening at any time. Useful during extended composition sessions.

## Common Recipes

### "Make it groovier"
1. `listen -e 2` — check onset density and HPSS ratio
2. Switch to syncopated drum pattern (ghost snares, swung hats)
3. Switch bass to funky pattern with off-beat accents
4. Add shaker/perc layer
5. `listen -e 2` — verify onset density increased, percussive ratio up

### "It sounds muddy"
1. `listen -s 4` — check mel spectrogram for energy pileup in low-mids
2. `mix-check` — find which tracks clash in the same frequency range
3. Lower volumes on competing tracks
4. Sweep filter cutoffs to separate: darken the pad, brighten the lead
5. Pan competing tracks apart

### "Build to a drop"
1. Start stripping layers: mute perc, mute guitar, mute pad
2. Add buildup drum pattern (accelerating snare)
3. Sweep filter up on remaining synth
4. Increase volume gradually
5. At the drop: `fire-scene <n>` — everything hits at once
6. Fire crash cymbal note on drums

### "Change the key"
1. Identify all clips with note data: check each track's slots
2. Calculate the transposition interval (e.g., Am to Cm = +3 semitones)
3. Rewrite each clip: clear-notes, add-notes with transposed pitches
4. `listen -e 4` — verify chords match the new key

### "Add movement"
1. Automate device parameters over time with `sweep` to find good ranges
2. Create arpeggiated patterns instead of block chords
3. Vary velocity across beats (accent beat 1, ghost beats 2-4)
4. Add a counter-melody on the lead track
5. Use filter modulation via device-param during playback

## Constraints

- **Cannot load instruments/devices via OSC.** The user must add instruments in Ableton manually. AbletonOSC PRs #173 and #183 exist but are unmerged.
- **Audio capture requires BlackHole 2ch** virtual audio driver configured as Multi-Output Device. Needs a reboot after first install.
- **Query responses need the bidirectional OSC server** (port 11001). The `query` command handles this automatically.
- **Delete tracks in reverse order** when clearing a session, or indices shift and you'll leave stray tracks.
- **Clip slot 127** is reserved for temp clips (used by `probe`). Don't store permanent clips there.
- **Short captures (< 1 bar)** may produce unreliable beat detection. Use at least 2 bars for analysis.
