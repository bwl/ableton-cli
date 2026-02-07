# Deep Drift (Dm)

**Key:** Dm | **BPM:** 90 | **Time Sig:** 4/4

## Concept
Ambient/atmospheric piece in D minor at 90 BPM. Inspired by Tycho, Brian Eno, Stars of the Lid. Long evolving textures, sparse rhythms, wide stereo field. The piece should feel like drifting through deep water — slow harmonic movement, breath-like swells, occasional melodic fragments surfacing and dissolving. The Dm tonality keeps it contemplative without being dark.

## Harmonic Plan
**Progression:** Dm → Bbmaj7 → Gm7 → A7sus4 (i → VI → iv → V)

Each chord sustains for 4-8 bars. Movement is glacial. Tension builds through layering, not tempo or harmonic rhythm.

**D natural minor scale:** D E F G A Bb C D

Key note references (MIDI):
- D2=38, D3=50, D4=62, D5=74
- F2=41, F3=53, F4=65
- A2=45, A3=57, A4=69
- Bb2=46, Bb3=58, Bb4=70

## Session Layout
| Track | Name | Instrument | Role |
|-------|------|------------|------|
| 0 | Drums | Upright Bass (drum rack) | Minimal — soft kicks on 1, ghost hat textures, no snare until build |
| 1 | Bass | 2-Way Boom | Sub-bass drones on chord roots, long sustained notes, occasional octave shift |
| 2 | Keys | Grand Piano | Sparse Rhodes-like voicings, single notes or thin intervals, lots of space |
| 3 | Synth Lead | Creeper Lead | Melodic fragments — 2-3 note phrases that appear and dissolve, heavy reverb |
| 4 | Synth Pad | Exoplanet Rain | Foundation layer — huge sustained chords, slow filter movement, the "bed" |
| 5 | Guitar | MPE Dulcimatica | Delicate plucked arpeggios, harmonics, single-note textures |
| 6 | Perc | Percussion Core Kit | Subtle clicks, shakers, found-sound textures — very low velocity |
| 7 | Vox / FX | Mega Vox Kit | Breath sounds, whispered textures, atmosphere |

## Structure
| Scene | Name | Bars | Chord | Description |
|-------|------|------|-------|-------------|
| 0 | Void | 8 | Dm | Pad only — single Dm chord fading in from silence |
| 1 | Surface | 8 | Dm | Bass drone enters, first guitar harmonics, subtle percussion clicks |
| 2 | Drift | 8 | Bbmaj7 | Keys enter with sparse voicing, lead plays first melodic fragment |
| 3 | Current | 8 | Gm7 | Drums enter (soft kick), bass moves, arpeggiated guitar pattern |
| 4 | Depth | 8 | A7sus4 | Tension — all layers active, lead melody peaks, brightness increases |
| 5 | Undertow | 8 | Dm | Return to root — strip to pad + bass + perc, vox/FX textures |
| 6 | Resurface | 8 | Bbmaj7 | Rebuild with keys + guitar, drums return, second lead melody |
| 7 | Dissolve | 8 | Dm | Everything fades — pad sustains alone, final piano note rings out |

## Volume Plan (ambient needs careful levels)
| Track | Volume | Pan | Notes |
|-------|--------|-----|-------|
| Drums | 0.45 | C | Very quiet, felt not heard |
| Bass | 0.65 | C | Present but not boomy |
| Keys | 0.40 | L15 | Soft, slightly left |
| Lead | 0.35 | R20 | Quiet, right side |
| Pad | 0.55 | C | The foundation, center |
| Guitar | 0.50 | L30 | Wider left for space |
| Perc | 0.30 | R25 | Ghost-quiet, right side |
| Vox/FX | 0.35 | R10 | Subtle atmosphere |

## Energy Arc (verified via `listen -q 8`)
| Scene | Energy | Brightness | HPSS | Qualitative |
|-------|--------|------------|------|-------------|
| 0 Void | 0.012 | 1329 | 0.94 / 0.06 | very quiet, dark, purely melodic — somber |
| 1 Surface | 0.017 | 1426 | 0.69 / 0.31 | very quiet, dark, melodic — somber |
| 2 Drift | 0.024 | 1786 | 0.66 / 0.34 | quiet, warm, melody-dominant |
| 3 Current | 0.031 | 1608 | 0.42 / 0.58 | quiet, warm, rhythm-dominant |
| 4 Depth | 0.037 | 1967 | 0.34 / 0.66 | quiet, warm, percussion-heavy |
| 5 Undertow | ~0.015 | ~1200 | ~0.75 / 0.25 | very quiet, dark, melodic — somber |
| 6 Resurface | ~0.028 | ~1700 | ~0.55 / 0.45 | quiet, warm, balanced |
| 7 Dissolve | 0.015 | 1174 | 0.73 / 0.27 | very quiet, dark, melodic — somber |

## Current State
- All 8 scenes composed and programmed
- Tempo: 90 BPM (synced via both Link and OSC)
- Volumes and panning set for ambient stereo field
- Energy arc verified: smooth build 0.012 → 0.037 then dissolve back to 0.015
- Brightness peaks at Scene 4 (1967) and is darkest at Scene 7 (1174)
- Harmonic/percussive balance shifts: pure harmonic pad → rhythmic peak → harmonic fade
- Qualitative arc: somber/dark → warm/balanced → somber/dark (matches ambient intent)
- Mood tendency stays in somber/melancholic territory throughout — correct for the concept
- Texture shifts from purely melodic (pad only) through rhythm-dominant (drums enter) and back

## Session Log
- Created composition plan: ambient piece in Dm at 90 BPM, 64 bars total (8 scenes x 8 bars)
- Composed Scene 0 (Void): Dm pad wash, verified via spectrogram
- Composed Scene 1 (Surface): Bass D2 drone, guitar harmonics, perc ghost clicks
- Composed Scene 2 (Drift): Chord change to Bbmaj7, keys + lead enter
- Composed Scene 3 (Current): Drums enter, Gm7, guitar arpeggios, walking bass
- Composed Scene 4 (Depth): A7sus4 peak — all layers, arpeggiated piano, peak lead melody, vox/FX
- Composed Scene 5 (Undertow): Strip back to pad + bass + perc + vox whispers, Dm7
- Composed Scene 6 (Resurface): Bbmaj7 rebuild, descending lead melody, gentle drums return
- Composed Scene 7 (Dissolve): Dm fade — pad, dying bass, single piano D5 note, one guitar shimmer
