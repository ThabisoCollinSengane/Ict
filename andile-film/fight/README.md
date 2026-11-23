# Fight scene — Andile vs The Bouncer (Hemingway's)

1. Empty club plates: `cd .. && node render.js --w=1920 --h=1080 '--q=empty=1&prim=1' --out=<plates> --frames=230,389,456,516,624,696`
2. Bouncer cutouts: `cd ../teaser && python3 cutout.py bouncer_body bouncer_h1 bouncer_h2 bouncer_h3`
3. Start frames: `python3 compose_starts.py <plates> .` → `start_F1..F6.png` (gitignored)
4. `shots.json` holds the six motion prompts; clips are generated image-to-video on kie.ai (Kling 3.0).
