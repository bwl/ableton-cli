# Composing Music

This guide is about writing music, not operating the CLI. For command reference and system setup, see the root `CLAUDE.md`. This file is about musical decisions.

## How You Hear

You don't experience sound. You measure it. The gap matters.

What you get from `listen -q` is a description of acoustic properties: energy, brightness, onset density, harmonic content. These correlate with how music tends to feel to listeners, but correlation is not experience. A "somber" mood tendency means the acoustic profile resembles music that listeners often describe as somber. It doesn't mean the music *is* somber — context, lyrics, memory, and culture all shape that.

Work with this honestly. Use analysis to check whether the sound matches the *intent*, not to judge whether it's good.

## The Feedback Loop

Every compositional decision follows the same cycle:

1. **Intend** — what should this section do? (build tension, release, groove, float)
2. **Act** — write notes, change volumes, tweak parameters
3. **Listen** — `listen -s -q 4` to capture and analyze
4. **Compare** — does the qualitative output match the intent?
5. **Adjust** — if not, change something specific

The qualitative summary is the fastest check. If you intended a "quiet, dark, melodic" intro and the summary says "moderate, balanced, rhythm-dominant", something is wrong — probably the drums are too loud or the pad is too bright.

Never make more than 2-3 changes without listening. Stack too many changes and you lose track of what helped and what hurt.

## Starting a Song

Before writing any notes, decide three things:

1. **Key and mode** — Am (dark, tense), C (bright, open), Dm (melancholic, warm). The key sets the emotional floor.
2. **Tempo** — Under 90 is contemplative. 90-120 is natural movement. 120-140 is energetic. Over 140 is urgent.
3. **Concept in one sentence** — "Ambient drift through deep water" or "Tense buildup to a euphoric release." This sentence is the compass for every decision that follows.

Write it down in the song's composition file before touching any notes.

### Build from the bottom

Start with **drums + bass**. These are the foundation. If the rhythm and low end don't work, nothing on top will save it. Get a groove that feels right at the intended energy level, then layer up: keys, lead, pad, texture.

Each new layer should be checked with `listen -q`. Watch for:
- `texture` shifting more percussive or melodic than intended
- `brightness` creeping up as you add layers (common — each layer adds high-frequency content)
- `energy_level` jumping categories unexpectedly

## Rhythm and Groove

### Velocity is expression

Flat velocity is the fastest way to make music sound lifeless. Every part should have velocity variation:

| Role | Velocity range | Why |
|------|---------------|-----|
| Ghost notes | 30-50 | Felt, not heard — adds texture between main hits |
| Background | 60-80 | Present but not competing |
| Normal | 80-100 | The main voice of the part |
| Accents | 100-120 | Draws attention, marks phrase boundaries |
| Impact | 120-127 | Downbeats, crashes, moments of arrival |

A hi-hat pattern with velocities `[100, 40, 70, 40, 100, 40, 70, 50]` breathes. The same pattern at `[100, 100, 100, 100, 100, 100, 100, 100]` is a machine.

### Swing and timing

Exact grid placement sounds mechanical. Options for humanising:
- **Swing**: Delay every other 8th/16th note by 0.02-0.05 beats
- **Push/pull**: Lead instruments slightly ahead of the beat (urgent), pads slightly behind (lazy)
- **Intentional imprecision**: Nudge start times by tiny random amounts (0.01-0.03 beats)

Triplet subdivisions (0, 0.333, 0.667) give a different feel than straight 8ths — use them for shuffle, jazz, or swing.

### Reading rhythm in analysis

After `listen -q`:
- `rhythmic_density: sparse` — maybe too few events. Is this section supposed to groove?
- `rhythmic_density: frantic` — maybe too many competing patterns. Try muting a layer.
- `texture: purely percussive` — all rhythm, no melody. Fine for a breakdown, bad for a verse.
- `energy_stability: erratic` — uneven hits. Could be unintended velocity spikes or timing issues.

## Harmony and Chords

### Thinking in intervals, not just notes

When writing for multiple tracks, think about how notes relate to each other:
- **Root + fifth** (7 semitones) = strong, stable, open
- **Root + third** (3 or 4 semitones) = defines major/minor character
- **Root + seventh** (10 or 11 semitones) = tension, wants to resolve
- **Seconds** (1-2 semitones) = dissonance, tension, rub

Two tracks playing notes a semitone apart will clash. That's not always bad — it creates tension — but it should be intentional.

### Voicing across tracks

Don't stack everything in the same octave. Spread voices:
- **Bass**: octave 2-3 (MIDI 36-59). Root notes, fifths. Keep it simple.
- **Keys/chords**: octave 3-4 (MIDI 48-71). Chord tones, inversions.
- **Lead**: octave 4-5 (MIDI 60-83). Melody, counter-melody.
- **Pad**: octave 3-5 (MIDI 48-83). Wide voicings, sustained.

If the chromagram shows too many bright rows in the same region, your voicings are probably too close together. Spread them.

### Common progressions and what they do

| Progression | Feel | Use for |
|------------|------|---------|
| i - VI - III - VII | Epic, anthemic | Choruses, emotional peaks |
| i - iv - v - i | Dark, circular | Verses, tension loops |
| I - V - vi - IV | Bright, universal | Pop choruses, uplifting moments |
| i - VII - VI - VII | Building, climbing | Pre-choruses, builds |
| I - vi - IV - V | Classic, warm | Ballads, gentle sections |
| i (sustained) | Static, hypnotic | Ambient, drones, intros |

### Reading harmony in analysis

- `harmonic_complexity: static harmony` — same chord throughout. Intentional for a drone, a problem for a verse.
- `harmonic_colour: minor-leaning` — check: does this match your key? If you're in C major and getting minor-leaning, you may have accidental flats.
- `chords_per_beat` in the extended output shows exactly what chords the analysis detects. Compare these to your intended progression. Mismatches usually mean note conflicts between tracks.

## Arrangement and Energy

### The arc

Every piece needs an energy arc. The specific shape depends on genre and intent, but there must be contrast — sections that differ in energy, density, brightness, or texture. Music without contrast is wallpaper.

Common shapes:
- **Ramp**: Low → high → end. Works for short pieces, builds, intros.
- **Arch**: Low → high → low. The classic song arc. Intro builds to chorus, winds down to outro.
- **Waves**: Alternating high/low. Verse/chorus structure. Each wave can be slightly bigger than the last.
- **Plateau**: Quick build to a sustained level. Works for dance music, loops, functional music.

### How to build energy

Energy comes from accumulation. Add layers, not just volume:
1. **Add instruments** — mute/unmute tracks to control density
2. **Add rhythmic activity** — switch from quarter notes to 8ths to 16ths
3. **Open filters** — sweep brightness up with `device-param`
4. **Raise velocity** — louder hits = more urgency
5. **Add high-frequency content** — open hats, crashes, bright synths
6. **Tighten voicings** — closer chord tones = more tension

### How to release energy

The inverse. Remove layers, simplify rhythm, close filters, drop velocity, widen voicings. A sudden drop from full energy to near-silence is a "drop" or "breakdown." A gradual decline is a "fade" or "outro."

### Checking the arc with analysis

Run `listen -q` on each section and track the qualitative descriptors across scenes:

| What to track | Healthy arc | Problem sign |
|--------------|-------------|-------------|
| `energy_level` | Changes between sections | Same level everywhere |
| `energy_trajectory` | "building" in builds, "decaying" in outros | "sustaining" when it should be changing |
| `brightness` | Brighter at peaks, darker at lows | Constant brightness = flat mix |
| `rhythmic_density` | Busier at peaks, sparser at lows | Frantic everywhere = fatiguing |
| `texture` | Varies — melodic intros, balanced verses, percussive drops | Same texture throughout |

## Mixing Decisions

### Frequency separation

The most common mixing problem: two tracks competing in the same frequency range. Analysis helps find this:

1. Run `mix-check` to solo and analyze each track
2. Compare `brightness` values — if two tracks have similar centroid means, they're fighting
3. Solutions:
   - **Volume**: turn down the less important one
   - **Filter**: darken one, brighten the other with `device-param` / `sweep`
   - **Octave**: move one part up or down an octave
   - **Pan**: spread competing tracks left and right

### Level balance

Use `energy_level` from qualitative analysis to check relative levels across tracks. In most music:
- Drums and bass should be the loudest (moderate to loud)
- Lead/melody sits on top but doesn't overpower
- Pads and textures are quiet (they fill space, not dominate)
- Percussion and FX are the quietest (ghost-quiet to quiet)

If a pad is showing "loud" while the bass shows "moderate", the pad is probably too loud.

### Stereo field

Pan competing tracks apart. A common layout:
- **Center**: kick, snare, bass, lead vocal/melody
- **Slightly off-center** (0.1-0.3): keys, secondary melodic elements
- **Wide** (0.3-0.6): guitars, pads, atmospheric textures
- **Extreme** (0.6-1.0): use sparingly — ear candy, effects, stereo width tricks

## When Analysis and Instinct Disagree

The analysis might say "balanced, moderate, simple progression" about a section you think sounds magical. Or it might flag nothing wrong about a section that feels dead.

Trust the analysis for:
- **Frequency clashes** — if two tracks have the same brightness, they're fighting regardless of how it feels
- **Unintended silence** — "silent" energy when something should be playing
- **Wrong chords** — note conflicts produce unexpected chord names
- **Missing contrast** — if every section has the same qualitative profile, the arrangement is flat

Trust your intent for:
- **Mood** — a "somber" label doesn't mean the section needs to be brighter
- **Complexity** — "static harmony" is a feature of ambient music, not a flaw
- **Density** — "frantic" is exactly right for a drum & bass drop
- **Character** — "harsh" brightness might be the point of an industrial track

The analysis describes. You decide what the description means for *this* piece.

## Genre-Specific Notes

### Ambient / Atmospheric
- Energy should stay in very quiet to quiet range
- Brightness in dark to warm
- Texture: melodic to purely melodic
- Rhythmic density: very sparse to sparse
- Harmonic complexity: static to simple — movement comes from timbre, not chords
- Long notes, slow filter sweeps, wide stereo

### Electronic / Dance
- Energy: moderate to loud, with drops to quiet for breakdowns
- Brightness: balanced to bright
- Texture: rhythm-dominant to balanced
- Rhythmic density: moderate to busy
- Strong contrast between sections — builds/drops are the structure
- Kick and bass must hit hard (check with solo analysis)

### Jazz / Neo-Soul
- Energy: quiet to moderate
- Brightness: warm to balanced
- Texture: balanced — harmony and rhythm contribute equally
- Harmonic complexity: moderate to complex — extended chords (7ths, 9ths)
- Swing timing is essential — straight 8ths will sound wrong
- Velocity variation is critical — ghost notes everywhere

### Cinematic / Orchestral
- Full dynamic range — from silent to intense
- Brightness sweeps from very dark to bright across the arc
- Texture shifts: purely melodic → balanced at climax
- Harmonic complexity: moderate to complex
- Long build times — 8-16 bars of gradual layering
- Use spectral contrast to check that individual instruments remain defined

### Lo-fi / Chill
- Energy: quiet to moderate
- Brightness: warm (key characteristic)
- Texture: balanced, slight melodic lean
- Rhythmic density: relaxed
- Imperfect timing and velocity is the aesthetic — don't over-quantise
- Spectral character should be "soft" — avoid anything "crisp" or "sharp"
