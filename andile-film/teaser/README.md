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
