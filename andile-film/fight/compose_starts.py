"""Compose the fight start frames: empty 3D club plates (render.js --q='empty=1&prim=1') + locked cast-sheet cutouts.
Usage: python3 compose_starts.py <plates_dir> <out_dir>"""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
PL, OUT = sys.argv[1], sys.argv[2]
ART = '../teaser/public/s1/'
def char(name, h, tint=(1.0, 0.82, 1.0), dark=0.9, flip=False):
    im = Image.open(ART + name + '.png').convert('RGBA')
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    r, g, b, a = im.split()
    r = r.point(lambda v: v * tint[0] * dark); g = g.point(lambda v: v * tint[1] * dark); b = b.point(lambda v: v * tint[2] * dark)
    return Image.merge('RGBA', (r, g, b, a))
def shadow(bg, cx, y, w):
    sh = Image.new('L', bg.size, 0); ImageDraw.Draw(sh).ellipse([cx - w // 2, y - w // 9, cx + w // 2, y + w // 9], fill=150)
    bg.paste(Image.new('RGB', bg.size, (10, 0, 15)), (0, 0), sh.filter(ImageFilter.GaussianBlur(18)))
def place(bg, im, cx, feet, shade=True):
    if shade: shadow(bg, cx, feet, int(im.width * 0.9))
    bg.paste(im, (cx - im.width // 2, feet - im.height), im)
def plate(f): return Image.open(f'{PL}/f{f:04d}.png').convert('RGB').resize((1920, 1080))
S = {}
# F1 standoff on the dance floor
bg = plate(230); place(bg, char('andile_body', 560), 760, 1010); place(bg, char('bouncer_body', 660), 1250, 1000); S['F1'] = bg
# F2 the charge (bar + door): bouncer big in foreground right, Andile mid left
bg = plate(389); place(bg, char('andile_body', 640), 620, 1060); place(bg, char('bouncer_body', 1000), 1380, 1160); S['F2'] = bg
# F3 dodge & counter: medium two-shot
bg = plate(456); place(bg, char('andile_body', 900), 760, 1240); place(bg, char('bouncer_body', 980), 1300, 1250); S['F3'] = bg
# F4 impact close-up face-off over the glowing floor
bg = ImageEnhance.Brightness(plate(516)).enhance(0.75)
a = char('andile_h1', 1250, tint=(1, 0.85, 0.95)); bg.paste(a, (40, 1080 - a.height + 320), a)
b = char('bouncer_h2', 1180, tint=(1, 0.85, 0.95)); bg.paste(b, (1920 - b.width - 20, 1080 - b.height + 300), b); S['F4'] = bg
# F5 the throw: bouncer at the bar, Andile foreground left
bg = plate(624); place(bg, char('bouncer_body', 760), 1180, 1000); place(bg, char('andile_body', 1100), 420, 1330, shade=False); S['F5'] = bg
# F6 aftermath: Andile outside Hemingway's in the rain
bg = plate(696); place(bg, char('andile_body', 700, tint=(0.95, 0.85, 1.0), dark=0.8), 1500, 1110); S['F6'] = bg
for k, im in S.items(): im.save(f'{OUT}/start_{k}.png'); print(k, im.size)
