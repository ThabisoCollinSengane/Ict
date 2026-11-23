# ANDILE: "Meet the Cast" teaser (Remotion)

A 21.6-second teaser built from the locked cast sheet (`../cast/cast_sheet_v2_locked.png`), in 16:9 and 9:16.

```bash
npm install
python3 prep_art.py        # cut body + face panels from the locked sheet into public/
python3 teaser_audio.py    # soundtrack timed from src/teaser.json (one drum bar per character)
BX=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
npx remotion render src/index.ts CastTeaser ../out/andile_cast_teaser_16x9.mp4 --browser-executable=$BX --concurrency=4 --crf=20
npx remotion render src/index.ts CastTeaserVertical ../out/andile_cast_teaser_9x16.mp4 --browser-executable=$BX --concurrency=4 --crf=20
```

`src/teaser.json` holds the cast (name, role, origin, side, colours) and the timing, shared by the picture and the sound. To rename a character, edit its `name` there and re-render.

## Scene 1 — "Bad Dream" (Episode 1 opening, 30 s)

Andile's call-centre nightmare (red endless aisle, IVR voices, giant Lee, dolly-zoom panic, "VUKA!")
then waking at his desk in the Umhlanga office with Lee standing over him.

Characters move as **mesh-warp puppets** (`src/Puppet.tsx`): each drawing from the locked cast sheet is
cut out (`cutout.py`) and mapped onto a subdivided plane; a vertex shader bends head (tilt about the neck),
chest (breathing), upper body (lean about the waist) and squash/jolt — Live2D-style motion from single images.

Rebuild:
```bash
python3 cutout.py                               # cast-sheet crops -> public/s1/*.png
cd ../scene1 && for s in N1 N2 N4; do node render_bg.js --shot=$s --out=../teaser/public/s1/bg/$s --from=0 --to=$([ $s = N4 ] && echo 120 || echo 100); done
for s in N3 W1 W2 W3; do node render_bg.js --shot=$s --out=../teaser/public/s1/bg/$s --frames=0; done; cd ../teaser
python3 scene1_audio.py                         # espeak-ng IVR/dream voices + synthesized SFX -> public/s1/scene1.wav
npx remotion render src/index.ts Scene1 ../out/andile_ep1_scene1_bad_dream_16x9.mp4 --gl=swangle
```
Shot timing and dialogue live in `src/scene1.json`. Wake-up dialogue is subtitles only — drop recorded voice
lines into the audio script when available.
