# Review: ANDILE cold open

## Gate 3: v1 scores (16:9, full 30 s render)
| Criterion | Score | Notes |
|---|---|---|
| Hook | 6/10 | The ocean opener looks good, but the camera barely moves in the first second (ease-in) and the audio sits at -28 dB for 3 s. |
| Readability | 6/10 | The cel shader and rim light make characters read. The S13 catch is shot from behind, so the "cool button" has no face. Subtitles are small in 16:9. |
| Continuity | 7/10 | One fight axis (x) holds across S06–S11; the Bouncer's flight continues across the S10→S11 cut. The door state persists after S12. |
| Motion | 7/10 | Real rigged animation: walk cycles, hook/duck, rising punch, spin kick, launch, landing. Minor foot slide on the Bouncer's walk. |
| Sound sync | 8/10 | Impacts, whooshes, door, clink and title hit come from the same `timeline.json` as the flashes and shake; footsteps use the rig's walk period. |

## Gate 4: three worst defects → fixed and re-rendered
1. **S10: the Bouncer flies out of the top-left of frame**, so the payoff of the kick is lost. *Fix:* the camera now tracks the Bouncer's actual position after impact (characters are evaluated before the camera), and the frame widens slightly. Re-rendered frames 396–455.
2. **S13: the catch is shot from behind Andile**, so the button lands without his face. *Fix:* the reverse angle comes from his front-left, so the glass slides into frame and into his hand. Re-rendered frames 564–623.
3. **S01: a weak hook** (static first second, quiet audio). *Fix:* linear skim from frame 1, ocean and pad raised about 6 dB. Re-rendered frames 0–71 and regenerated the audio.
Also: subtitles enlarged (S12, frames 504–563 re-rendered).
