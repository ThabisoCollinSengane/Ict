# Poster frames: hero moments as PNG.  python3 posters.py <frames_dir> <tag>
import sys, os
from PIL import Image
fd, tag = sys.argv[1], sys.argv[2]
picks = {'S01_whales': 52, 'S01B_ocean': 100, 'S07_closeup': 378, 'S09_impact': 427, 'S10_kick': 468, 'S12_sib': 593, 'S14_title': 738}
os.makedirs('out/posters', exist_ok=True)
for name, f in picks.items():
    src = os.path.join(fd, f'f{f:04d}.png')
    if os.path.exists(src): Image.open(src).convert('RGB').save(f'out/posters/poster_{tag}_{name}.jpg', quality=93)
print('posters', tag, len(picks))
