#!/usr/bin/env python3
"""Add one-shot sound effects across all 8 scenes.

Track 6 (Perc - Percussion Core Kit): rhythmic accents, shakers, clicks
Track 7 (Vox/FX - Mega Vox Kit): vocal stabs, breaths, atmosphere
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib import osc

CLIP_LENGTH = 16  # 4 bars per scene

# Perc one-shots (Track 6) — scattered rhythmic accents
# Using varied notes across 36-59 for different percussion colors
PERC_FX = {
    0: [  # Intro — one subtle accent, letting the song breathe
        (42, 7.5, 0.25, 60),   # light click before bar 3
    ],
    1: [  # Opening — shaker accents
        (38, 3.5, 0.25, 70),   # accent end of bar 1
        (44, 11.5, 0.25, 65),  # accent end of bar 3
    ],
    2: [  # Build — more accents, rising
        (36, 0, 0.25, 75),     # downbeat marker
        (40, 7.5, 0.25, 70),   # mid-section accent
        (48, 15, 0.25, 80),    # transition hit
    ],
    3: [  # Tension — syncopated accents building
        (50, 1.5, 0.25, 70),   # off-beat accent
        (46, 5.5, 0.25, 75),
        (52, 9.5, 0.25, 80),
        (54, 13.5, 0.25, 85),  # building intensity
    ],
    4: [  # Energy — strong downbeat, rhythmic punctuation
        (56, 0, 0.5, 100),     # impact on 1
        (38, 4, 0.25, 75),     # accent
        (44, 8, 0.25, 80),
        (50, 12, 0.25, 85),
    ],
    5: [  # Peak — active percussion fills
        (36, 0, 0.25, 90),
        (40, 2, 0.25, 80),
        (48, 4, 0.25, 85),
        (52, 7.5, 0.25, 90),
        (42, 10, 0.25, 80),
        (56, 14.5, 0.5, 95),   # big accent before climax
    ],
    6: [  # Climax — maximum percussion activity
        (58, 0, 0.5, 100),     # crash-like
        (36, 2, 0.25, 85),
        (44, 4, 0.25, 90),
        (50, 6, 0.25, 90),
        (38, 8, 0.25, 85),
        (46, 10, 0.25, 90),
        (54, 12, 0.25, 95),
        (56, 14, 0.5, 100),    # big transition hit
    ],
    7: [  # Resolution — sparse, dying away
        (42, 0, 0.25, 70),     # gentle accent
        (38, 8, 0.25, 50),     # very quiet
        (36, 14, 0.25, 40),    # final whisper
    ],
}

# Vox one-shots (Track 7) — vocal stabs and atmosphere
# Using spread notes to get variety from the Mega Vox Kit
VOX_FX = {
    0: [  # Intro — single breath/vocal at the start
        (40, 0, 0.5, 55),     # atmospheric vocal intro
    ],
    1: [  # Opening — subtle vocal stab
        (44, 8, 0.5, 60),     # mid-section vocal
    ],
    2: [  # Build — vocal accents building
        (36, 4, 0.5, 65),     # vocal hit
        (48, 12, 0.5, 70),    # higher vocal stab
    ],
    3: [  # Tension — call-out vocals
        (42, 2, 0.5, 70),
        (50, 10, 0.5, 75),
        (38, 15, 0.5, 80),    # vocal before transition
    ],
    4: [  # Energy — vocal shouts
        (52, 0, 0.75, 90),    # big vocal on the 1
        (46, 8, 0.5, 75),     # mid-section
    ],
    5: [  # Peak — vocal stab frenzy
        (54, 0, 0.5, 85),
        (40, 4, 0.5, 80),
        (48, 8, 0.5, 85),
        (56, 12, 0.5, 90),
    ],
    6: [  # Climax — maximum vocal activity
        (58, 0, 0.75, 100),   # biggest vocal hit
        (36, 3, 0.5, 80),
        (44, 6, 0.5, 85),
        (52, 9, 0.5, 90),
        (42, 12, 0.5, 85),
        (50, 15, 0.5, 95),
    ],
    7: [  # Resolution — fading vocal ghost
        (40, 2, 0.5, 50),     # quiet vocal
        (44, 10, 0.5, 35),    # ghost vocal
    ],
}

def create_fx_clips(track, fx_data, name_prefix):
    for scene in range(8):
        notes = fx_data.get(scene, [])
        if not notes:
            continue

        osc.create_clip(track, scene, CLIP_LENGTH)
        time.sleep(0.05)

        note_tuples = [(p, s, d, v, 0) for p, s, d, v in notes]
        osc.add_notes(track, scene, note_tuples)

        clip_name = f"{name_prefix} {scene+1}"
        osc.set_clip_name(track, scene, clip_name)
        print(f"  Scene {scene}: {clip_name} ({len(notes)} hits)")
        time.sleep(0.05)


def main():
    print("Adding one-shot FX across all scenes...\n")

    print("Track 6 (Perc Core Kit):")
    create_fx_clips(6, PERC_FX, "Perc FX")

    print("\nTrack 7 (Mega Vox Kit):")
    create_fx_clips(7, VOX_FX, "Vox FX")

    # Set volumes — FX should accent, not dominate
    osc.set_volume(6, 0.55)
    osc.set_volume(7, 0.50)

    print("\nDone! FX clips added to all 8 scenes.")
    print("Perc at 0.55 volume, Vox at 0.50")


if __name__ == "__main__":
    main()
