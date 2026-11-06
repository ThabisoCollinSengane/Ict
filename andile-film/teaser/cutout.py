"""Cut characters out of the locked sheet with transparent backgrounds (flood-fill from the panel border,
stopped by the ink outlines), then upscale. Usage: python3 cutout.py"""
from PIL import Image, ImageFilter
import numpy as np
from collections import deque
SHEET = Image.open('../cast/cast_sheet_v2_locked.png').convert('RGB')
PARTS = {  # name: (box, upscale)
    'andile_body': ((2, 2, 186, 505), 3), 'andile_h1': ((183, 4, 333, 212), 4), 'andile_h2': ((183, 212, 333, 362), 4), 'andile_h3': ((183, 362, 333, 505), 4),
    'lee_body': ((941, 2, 1077, 505), 3), 'lee_h1': ((1074, 20, 1235, 220), 4), 'lee_h2': ((1074, 220, 1235, 390), 4), 'lee_h3': ((1074, 390, 1235, 506), 4),
}
def cut(img, step=34, far=150):
    a = np.asarray(img).astype(np.int32); h, w, _ = a.shape
    bgref = np.median(np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]), 0)
    ok = (a.sum(2) > 230) & (np.abs(a - bgref).sum(2) < far)   # not ink, roughly background-coloured
    seen = np.zeros((h, w), bool); q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if ok[y, x]: q.append((y, x)); seen[y, x] = True
    for y in range(h):
        for x in (0, w - 1):
            if ok[y, x] and not seen[y, x]: q.append((y, x)); seen[y, x] = True
    while q:  # grow while neighbouring pixels change smoothly (follows the studio gradient, stops at ink)
        y, x = q.popleft(); p = a[y, x]
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not seen[ny, nx] and ok[ny, nx] and np.abs(a[ny, nx] - p).sum() < step:
                seen[ny, nx] = True; q.append((ny, nx))
    alpha = Image.fromarray(np.where(seen, 0, 255).astype(np.uint8))
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    rgba = img.convert('RGBA'); rgba.putalpha(alpha); return rgba
for name, (box, k) in PARTS.items():
    c = cut(SHEET.crop(box))
    c = c.resize((c.width * k, c.height * k), Image.LANCZOS)
    rgb = c.convert('RGB').filter(ImageFilter.UnsharpMask(radius=2, percent=110, threshold=2)); rgb.putalpha(c.split()[3])
    rgb.save(f'public/s1/{name}.png'); print(name, rgb.size)
