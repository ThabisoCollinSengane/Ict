#!/usr/bin/env bash
# Downloads the VRoid sample avatars used for the cast (licence embedded in each file:
# allowedUser=Everyone, commercial=Allow, violent=Allow; author: VRoid / pixiv Inc.).
set -euo pipefail
cd "$(dirname "$0")"; mkdir -p assets/vrm
for n in A B C; do
  [ -f assets/vrm/AvatarSample_$n.vrm ] || curl -fsSL -o assets/vrm/AvatarSample_$n.vrm "https://raw.githubusercontent.com/madjin/vrm-samples/master/vroid/stable/AvatarSample_$n.vrm"
done
echo assets ok
