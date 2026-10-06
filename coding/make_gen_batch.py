# Generals (plus ~200 Congress controls from 1861-1869) on blind, shuffled contact sheets.
import json, os, random, urllib.parse
from PIL import Image, ImageDraw, ImageFont
from facecrop import load_cropped
from census import people, code
G = 'generals'
gen = [r for r in json.load(open(f'{G}/union_generals.json')) if r['file']]
imgs = json.load(open('images.json'))
gfiles = {r['file'].replace('_', ' ') for r in gen}
items = [('gen', r['key'], f"{G}/img/{r['key']}.jpg") for r in gen]
pool = []
for q, d in people.items():
    if d['gender'] != 'M' or code.get(q) in (None, 'X', 'W') or not os.path.exists(f'img/{q}.jpg'): continue
    if not any(t[0] <= 1869 and t[1] >= 1861 for t in d['terms']): continue
    if q in imgs and urllib.parse.unquote(imgs[q].rsplit('/', 1)[1]).replace('_', ' ') in gfiles: continue
    pool.append(q)
random.seed('generals'); ctrl = random.sample(sorted(pool), 200)
items += [('ctrl', q, f'img/{q}.jpg') for q in ctrl]
random.shuffle(items)
json.dump(items, open('batches/GEN.json', 'w'))
out = 'sheets_GEN'; os.makedirs(out, exist_ok=True)
CW, CH, COLS, ROWS = 200, 250, 6, 4; per = COLS * ROWS
font = ImageFont.load_default(size=22)
for s in range(0, len(items), per):
    sheet = Image.new('RGB', (CW * COLS, CH * ROWS), 'white'); d = ImageDraw.Draw(sheet)
    for k, (_, _, path) in enumerate(items[s:s + per]):
        try:
            im, _ = load_cropped(path); im.thumbnail((CW - 8, CH - 34))
        except Exception:
            im = Image.new('RGB', (CW - 8, CH - 34), (200, 200, 200))
        cx, cy = (k % COLS) * CW, (k // COLS) * CH
        sheet.paste(im, (cx + (CW - im.width) // 2, cy + 30))
        d.rectangle([cx + 2, cy + 2, cx + 42, cy + 28], fill='black'); d.text((cx + 6, cy + 3), str(k), fill='white', font=font)
    sheet.save(f'{out}/{s // per:03d}.jpg', quality=85)
print(len(items), 'items', len(pool), 'control pool', (len(items) + per - 1) // per, 'sheets', 'last sheet', len(items) % per)
