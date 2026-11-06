"""Cuts each character's full-body panel and face close-up from the locked cast sheet into public/ (3-4x upscaled)."""
from PIL import Image, ImageFilter
im = Image.open('../cast/cast_sheet_v2_locked.png').convert('RGB')
BOXES = {  # (body box, top-head box) in sheet pixels
    'C01_andile': ((2, 2, 186, 505), (183, 4, 333, 212)),
    'C02_futhi': ((352, 2, 488, 505), (485, 8, 628, 196)),
    'C03_sib': ((636, 2, 800, 505), (795, 16, 938, 190)),
    'C04_lee': ((941, 2, 1077, 505), (1074, 24, 1235, 220)),
    'C05_bouncer': ((1239, 2, 1395, 505), (1393, 6, 1534, 180)),
    'C06_matriarch': ((2, 512, 190, 1020), (183, 512, 346, 700)),
    'C07_customs': ((351, 512, 496, 1020), (498, 514, 630, 692)),
    'C08_driver': ((636, 512, 776, 1020), (772, 514, 936, 694)),
    'C09_tailor': ((941, 512, 1092, 1020), (1083, 514, 1236, 702)),
    'C10_reporter': ((1239, 512, 1395, 1020), (1385, 514, 1534, 722)),
}
up = lambda x, k: x.resize((x.width * k, x.height * k), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=2))
for n, (b, h) in BOXES.items():
    up(im.crop(b), 3).save(f'public/{n}_body.png')
    up(im.crop(h), 4).save(f'public/{n}_head.png')
print('art ok')
