# Assets list

All assets are procedural: there are no external images, models, fonts or samples.

| Asset | Source | Notes |
|---|---|---|
| Andile, Futhi, Sib, The Bouncer, 3 dancers | `src/rig.js` (`CAST`) | Built from primitives; 17-joint rig each; colours locked in `style-guide.md` |
| Ocean at dusk set | `src/sets.js` `oceanSet` | GLSL ocean (waves, foam, sun path), sky dome, toon clouds, 48-building skyline, palms, ships |
| Rainy street set | `src/sets.js` `streetSet` | Hemingway's facade, neon sign (canvas texture), palms, lamps, car, 2,600-drop rain, wet reflections |
| Club interior set | `src/sets.js` `clubSet` | Bar, bottles, stools, booths, a 100-tile reactive dance floor, light cones, disco ball, door, glass prop |
| Fonts | System DejaVu Sans / DejaVu Serif | Swap for a licensed display font for broadcast |
| Score + SFX | `audio.py` | Amapiano-style groove (log drum, shaker, clap, keys), pads, tension drone, impacts, whooshes, footsteps, rain, ocean |
| Window/neon textures | `src/toon.js` | Generated on canvas from a seeded RNG |

# What still needs human review
1. **Voice:** Sib's line ("Haibo! Ngiphuthelwe futhi?") is subtitles only. Record a VO, check the isiZulu with a native speaker, and add lip movement (the rig's `mouth` channel is ready).
2. **Character appeal:** faces and hair are deliberately simple primitives. An artist pass (hair shapes, hands, clothing folds) or swapping in rigged GLB models would lift the close-ups most (S05, S07).
3. **Foot contact:** small foot sliding on the Bouncer's heavy walk (S06) and in Andile's spin (S10).
4. **Rim glow:** light-coloured clothing (Andile's hood) picks up a strong cyan rim in the club. Lower `cel.rimAmt` in `clubSet` if it reads as too glowy.
5. **Music:** synthesised amapiano is a placeholder bed. Replace it with a licensed or commissioned track before publishing; keep the cue points in `timeline.json`.
6. **Brand and story:** check names and roles on the name cards, and the "Hemingway's" signage, against the series bible.
