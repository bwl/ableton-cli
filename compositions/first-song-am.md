# First Song (Am)

**Key:** Am | **BPM:** 120 | **Time Sig:** 4/4

## Concept
The first composition made with ableton-cli. A 32-bar piece in A minor exploring the Am-F-C-G progression. Starts sparse, builds to a climax, then resolves. Cinematic, electronic feel.

## Session Layout
| Track | Name | Instrument | Role |
|-------|------|------------|------|
| 0 | Drums | Upright Bass (drum rack) | Main beat — evolves from sparse quarter hats to full 16th grooves |
| 1 | Bass | 2-Way Boom | Walking/melodic bass lines following chord roots |
| 2 | Keys | Grand Piano | Chord voicings — block chords and rhythmic comps |
| 3 | Synth Lead | Creeper Lead | Counter-melody, sparse ornamental phrases |
| 4 | Synth Pad | Exoplanet Rain | Long sustained washes, one chord per section |
| 5 | Guitar | MPE Dulcimatica | Melodic guitar lines, call-and-response with lead |
| 6 | Perc | Percussion Core Kit | Rhythmic accents, shakers, clicks |
| 7 | Vox / FX | Mega Vox Kit | Vocal stabs, breath sounds, atmosphere |

## Structure
| Scene | Name | Bars | Chord | Description |
|-------|------|------|-------|-------------|
| 0 | Intro (Am) | 4 | Am | Sparse drums (quarter hats), gentle pad, guitar enters |
| 1 | Opening (F) | 4 | F | 8th hats, ghost snares, bass walks, keys enter |
| 2 | Build (C) | 4 | C | Full groove, open hats, ghost snares, all melodic layers |
| 3 | Tension (G) | 4 | G | Ride cymbal, tom fills, syncopated lead |
| 4 | Energy (Am) | 4 | Am | Crash on 1, driving beat, peak bass activity |
| 5 | Peak (F) | 4 | F | Maximum drums, active perc fills, vocal stabs |
| 6 | Climax (C) | 4 | C | Crash + toms, max velocity, densest arrangement |
| 7 | Resolution (G) | 4 | G | Pull back to quarter hats, fade dynamics, final whisper |

## Qualitative Arc (expected from `listen -q 4` per scene)
| Scene | Expected Character | Mood Tendency |
|-------|-------------------|---------------|
| 0 Intro (Am) | quiet, warm, melodic, sparse | melancholic |
| 1 Opening (F) | moderate, warm, balanced, relaxed | neutral |
| 2 Build (C) | moderate, balanced, balanced, moderate | neutral / uplifting |
| 3 Tension (G) | loud, balanced, rhythm-dominant, busy | driving |
| 4 Energy (Am) | loud, bright, rhythm-dominant, busy | energetic, driving |
| 5 Peak (F) | very loud, bright, percussion-heavy, frantic | energetic |
| 6 Climax (C) | intense, bright, percussion-heavy, frantic | energetic |
| 7 Resolution (G) | quiet, warm, melodic, sparse | melancholic |

The energy trajectory across the full arrangement should read: building (scenes 0-3) → sustaining (4-6) → decaying (7). Re-verify with `listen -q 4` after any changes.

## Current State
- All 8 sections composed and arranged via `scripts/arrange_sections.py`
- Perc one-shots and vocal FX added via `scripts/add_fx.py`
- Energy arc works: sparse intro → climax → resolution
- Lead counter-melody is intentionally sparse to leave space for guitar
- Device parameter control verified on Creeper Lead (filter sweeps work)
- Qualitative arc not yet verified with `-q` flag — run `listen -q 4` per scene to confirm

## Session Log
- Composed initial 32-bar arrangement across 6 tracks
- Split into 8 scene sections (4 bars each) for scene-based playback
- Added percussion and vocal FX one-shots across all scenes
- Verified feedback loop: listen → analyze → adjust cycle works
