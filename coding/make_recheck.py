# Usage: python3 make_recheck.py <name> <batch letters...>
# Uncropped, larger second-look sheets (12 per sheet) for cells queued in recheck.txt.
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps
name, letters = sys.argv[1], set(sys.argv[2:])
done = {tuple(l.split()[:3]) for l in open('recheck_done.txt') if l.strip()}
items, seen = [], set()
for l in open('recheck.txt'):
    p = l.split()
    if len(p) < 3 or p[0] not in letters: continue
    b, s, k = p[0], p[1], int(p[2])
    if (b, s, str(k)) in done or (b, s, k) in seen: continue
    seen.add((b, s, k))
    order = json.load(open(f'batches/{b}.json'))
    q = order[int(s) * 24 + k]
    items.append([b, s, k, q])
json.dump(items, open(f'recheck_{name}.json', 'w'))
out = f'sheets_recheck_{name}'; os.makedirs(out, exist_ok=True)
CW, CH, COLS, ROWS = 300, 400, 4, 3; per = COLS * ROWS
font = ImageFont.load_default(size=24)
for s in range(0, len(items), per):
    sheet = Image.new('RGB', (CW * COLS, CH * ROWS), 'white'); d = ImageDraw.Draw(sheet)
    for k, (_, _, _, q) in enumerate(items[s:s + per]):
        try:
            im = ImageOps.exif_transpose(Image.open(f'img/{q}.jpg')).convert('RGB'); im.thumbnail((CW - 8, CH - 36))
        except Exception:
            im = Image.new('RGB', (CW - 8, CH - 36), (200, 200, 200))
        cx, cy = (k % COLS) * CW, (k // COLS) * CH
        sheet.paste(im, (cx + (CW - im.width) // 2, cy + 32))
        d.rectangle([cx + 2, cy + 2, cx + 46, cy + 30], fill='black'); d.text((cx + 6, cy + 3), str(k), fill='white', font=font)
    sheet.save(f'{out}/{s // per:03d}.jpg', quality=88)
print(name, len(items), 'cells', (len(items) + per - 1) // per, 'sheets')
