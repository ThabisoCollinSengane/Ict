# Contact sheet: one labelled frame per shot.  python3 contact.py <frames_dir> <out.jpg> [cols]
import json, sys, os
from PIL import Image, ImageDraw, ImageFont
fd, out = sys.argv[1], sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 4
TL = json.load(open(os.path.join(os.path.dirname(__file__) or '.', 'timeline.json')))
fps = TL['fps']
def mid(s): return int(round((s['start'] + (s['end'] - s['start']) * 0.55) * fps))
items = [(s['id'], mid(s), s) for s in TL['shots']]
ims = []
for sid, f, s in items:
    p = os.path.join(fd, f'f{f:04d}.png')
    if os.path.exists(p): ims.append((sid, f, s, Image.open(p).convert('RGB')))
w, h = ims[0][3].size
tw = 480 if w >= h else 270
th = int(h * tw / w)
rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (cols * tw, rows * (th + 26)), (14, 12, 20))
try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
except Exception: font = ImageFont.load_default()
d = ImageDraw.Draw(sheet)
for i, (sid, f, s, im) in enumerate(ims):
    x, y = (i % cols) * tw, (i // cols) * (th + 26)
    sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y + 26))
    d.text((x + 6, y + 5), f"{sid}  {s['start']:.1f}-{s['end']:.1f}s  ({s['set']})  f{f}", fill=(240, 220, 200), font=font)
sheet.save(out, quality=90)
print('contact sheet', out, len(ims), 'shots')
