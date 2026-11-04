# ANDILE — Style Guide (code-rendered cold open)

**Film:** ANDILE S1·E1 cold open, "Hemingway's" — 30 s, 24 fps.
**Audience:** YouTube anime / action viewers, South African + global.
**The viewer should remember:** *Andile is the quiet Durban spy who finishes the fight before the music comes back.*

## Renderer
three.js r160 (WebGL2) in headless Chromium with SwiftShader, so it runs on a CPU-only cloud box with no GPU and no paid tools.
- Real 3D: rigged characters, a moving camera and real angles. These are not cut-outs over stills.
- Deterministic: `renderAt(frame)` derives everything from `t = frame / 24`, and all randomness uses seeded PRNGs, so any frame can be re-rendered on its own.
- One timeline: `timeline.json` drives shots, walk cycles (footsteps), impact cues (flash, shake, sound) and text. The audio synth reads the same file.

## Look: "cel-shaded anime in 3D"
- **Shading:** `MeshToonMaterial` with a 3-step ramp (shadow / mid / light). No textures on characters, only flat colour.
- **Line:** inverted-hull outlines (#120C18, about 1.1 cm world size) on characters and hero props. No outlines on skies or distant city.
- **Light:** one key, one hemisphere fill and at most three coloured practicals per set. Neon is pushed above 1.0 so bloom catches it.
- **Post:** soft bloom → anime grade (slight saturation lift, purple shadow lift) → film grain → vignette → 2.0:1 letterbox (16:9 only).
- **Impact language:** 1 inverted "impact frame", then a white flash decay, radial speed lines, chromatic split and a camera shake.

## Palette
| Set | Key colours |
|---|---|
| Ocean at dusk | sky #1F1D5E → #6B4AA6 → #F0789A → #FFB36A, sea #1D2F6B / #2E5AA8 / #5A8FD6, foam #F2F4FF, sun path #FFD08A |
| Street at night (rain) | asphalt #1B1E2C, facade #2C4D58, neon pink #FF4FA3, neon cyan #3FD8FF, lamp #FFB070, fog #1A1838 |
| Club interior | walls #2A1640, floor tiles magenta / cyan / violet, bar wood #4A1C22, haze #160C26 |
| Accent / titles | #E2563C (ANDILE orange), text #F4F1EC |

## Locked cast (built procedurally, so identical in every frame)
| Character | Silhouette | Colours |
|---|---|---|
| **Andile** (lead) | lean, short fade, stern brows, hands in pockets | steel-blue jacket #3D6B8F, grey hoodie #B8B8BC, black tie, black trousers, navy shoes |
| **Futhi** (bartender) | slim, long braids, gold hoops | navy tank #1F2A44, jeans #4A6FA5 |
| **Sib** (comic backup) | short and stocky, curly crop, chain | black tracksuit with white stripes, white sneakers |
| **The Bouncer** (antagonist) | huge, bald, beard, shades | red jacket #8C2A2A, black shirt and trousers |

## Camera grammar
- Establish wide → then go low and close for threat → orbit for the hero move → top-down for consequence.
- Lenses: 24–34° for close-ups, 38–44° for wides and 50° for impact distortion. Use a Dutch tilt only for the tension beat.
- Each shot has one clear subject. The cut lands on motion or on an audio hit.

## Type
DejaVu Sans Bold, letter-spaced caps. Name cards use a slanted orange bar. Subtitles are isiZulu first, with English underneath.

## Sound
Everything is synthesised from the timeline: ocean, rain, amapiano groove (log drum, shaker, clap), a tension drone, impacts, whooshes, footsteps and a title hit. Every visual impact has a matching audio cue at the same timestamp.
