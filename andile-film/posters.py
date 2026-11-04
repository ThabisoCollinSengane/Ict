# Poster frames: hero moments as PNG.  python3 posters.py <frames_dir> <tag>
import sys, os
from PIL import Image
fd, tag = sys.argv[1], sys.argv[2]
picks = {'S01_ocean': 40, 'S07_closeup': 330, 'S09_impact': 379, 'S10_kick': 420, 'S12_sib': 545, 'S14_title': 690}
os.makedirs('out/posters', exist_ok=True)
for name, f in picks.items():
    src = os.path.join(fd, f'f{f:04d}.png')
    if os.path.exists(src): Image.open(src).convert('RGB').save(f'out/posters/poster_{tag}_{name}.jpg', quality=93)
print('posters', tag, len(picks))
