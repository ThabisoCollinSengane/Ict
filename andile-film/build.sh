#!/usr/bin/env bash
# Repeatable render: ./build.sh [16x9|9x16|both] [workers]
set -euo pipefail
cd "$(dirname "$0")"
FMT=${1:-both}; WK=${2:-3}; N=$(python3 -c "import json;d=json.load(open('timeline.json'));print(int(d['duration']*d['fps']))")
render_fmt () {
  local tag=$1 w=$2 h=$3; local per=$(( (N + WK - 1) / WK )); local pids=()
  for ((k=0; k<WK; k++)); do
    local a=$((k*per)) b=$(((k+1)*per)); (( b > N )) && b=$N
    node render.js --w=$w --h=$h --out=frames/$tag --from=$a --to=$b > logs/render_${tag}_$k.log 2>&1 & pids+=($!)
  done
  for p in "${pids[@]}"; do wait $p; done
  ffmpeg -y -loglevel error -framerate 24 -i frames/$tag/f%04d.png -i out/audio.wav -c:v libx264 -preset slow -crf 16 \
    -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart out/andile_s1e1_coldopen_$tag.mp4
  python3 contact.py frames/$tag out/contact_$tag.jpg $([ "$tag" = 16x9 ] && echo 4 || echo 7)
  python3 posters.py frames/$tag $tag
}
mkdir -p logs out
python3 audio.py timeline.json out/audio.wav
[[ $FMT == 16x9 || $FMT == both ]] && render_fmt 16x9 1280 720
[[ $FMT == 9x16 || $FMT == both ]] && render_fmt 9x16 720 1280
echo "build complete"
