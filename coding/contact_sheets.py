"""Tile downloaded portraits into numbered contact sheets for blind coding.

Requires: pip install pillow
"""

# Contact sheets in random order, labelled only by index, so coding is blind
# to year, party and state.
import json, os, random
from PIL import Image, ImageDraw, ImageFont, ImageOps
people = sorted(f[:-4] for f in os.listdir('img') if f.endswith('.jpg'))
random.seed(42); random.shuffle(people)
json.dump(people, open('order.json', 'w'))
os.makedirs('sheets', exist_ok=True)
CW, CH, COLS, ROWS = 200, 250, 6, 4
font = ImageFont.load_default(size=22)
per = COLS * ROWS
for s in range(0, len(people), per):
    sheet = Image.new('RGB', (CW * COLS, CH * ROWS), 'white')
    d = ImageDraw.Draw(sheet)
    for k, q in enumerate(people[s:s + per]):
        try:
            im = Image.open(f'img/{q}.jpg'); im = ImageOps.exif_transpose(im).convert('RGB')
            im.thumbnail((CW - 8, CH - 34))
        except Exception:
            im = Image.new('RGB', (CW - 8, CH - 34), (200, 200, 200))
        cx, cy = (k % COLS) * CW, (k // COLS) * CH
        sheet.paste(im, (cx + (CW - im.width) // 2, cy + 30))
        d.rectangle([cx + 2, cy + 2, cx + 60, cy + 28], fill='black')
        d.text((cx + 6, cy + 3), str(s + k), fill='white', font=font)
    sheet.save(f'sheets/sheet_{s // per:02d}.jpg', quality=85)
print(len(people), 'people ->', len(os.listdir('sheets')), 'sheets')
