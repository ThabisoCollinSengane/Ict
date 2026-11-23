# Scene 1 — AI video pass (Kling)

The puppet version of Scene 1 stays the master edit (timing, subtitles, sound, N5 glitch, title card).
Seven shots get regenerated as image-to-video clips, each starting from the exact puppet frame so the
characters stay on-model with the locked cast sheet.

- `shots.json` — shot id, frame range in the 900-frame edit, start frame, motion prompt, shared style/negative prompt.
- Start frames (gitignored, rebuild):
  ```bash
  cd andile-film/teaser
  for row in N1:3 N2:105 N3:230 N4:300 W1:555 W2:582 W3:715; do id=${row%%:*}; fr=${row##*:}
    npx remotion still src/index.ts Scene1 ../scene1/kling/start_$id.png --frame=$fr --gl=swangle --props='{"clean":true}'; done
  ```
  `clean` hides subtitles, grain, letterbox, eyelids and UI overlays so only the drawn scene goes to the model.

## Using generated clips
Put each clip at `andile-film/teaser/public/s1/kling/<id>.mp4` (gitignored) and set its value in
`andile-film/teaser/src/kling.json` to a playback rate (e.g. `1.5` fits a 5 s clip into a 3.3 s slot), or `false`
to keep the drawn shot. If a clip file is missing, set its entry back to `false` before rendering.
Generated so far (kie.ai, `kling-3.0/video`, std, 5 s, ~75 credits each): N2.
