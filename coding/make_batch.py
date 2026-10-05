# Usage: python3 make_batch.py <batch_name> [max_people]
# Takes every downloaded portrait not yet assigned to a batch, shuffles them, and
# writes 24-portrait contact sheets labelled 0-23 by position only.
import json, os, random, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps
from facecrop import load_cropped
name = sys.argv[1]; cap = int(sys.argv[2]) if len(sys.argv) > 2 else 10**9
assigned = set()
for f in os.listdir('batches'):
    if f.endswith('.json'): assigned |= set(json.load(open('batches/' + f)))
people = sorted(f[:-4] for f in os.listdir('img') if f.endswith('.jpg') and f[:-4] not in assigned)
people = [q for q in people if os.path.getsize(f'img/{q}.jpg') > 1000][:cap]
random.seed(name); random.shuffle(people)
json.dump(people, open(f'batches/{name}.json', 'w'))
out = f'sheets_{name}'; os.makedirs(out, exist_ok=True)
CW, CH, COLS, ROWS = 200, 250, 6, 4; per = COLS * ROWS
font = ImageFont.load_default(size=22)
for s in range(0, len(people), per):
    sheet = Image.new('RGB', (CW * COLS, CH * ROWS), 'white'); d = ImageDraw.Draw(sheet)
    for k, q in enumerate(people[s:s + per]):
        try:
            im, _ = load_cropped(f'img/{q}.jpg'); im.thumbnail((CW - 8, CH - 34))
        except Exception:
            im = Image.new('RGB', (CW - 8, CH - 34), (200, 200, 200))
        cx, cy = (k % COLS) * CW, (k // COLS) * CH
        sheet.paste(im, (cx + (CW - im.width) // 2, cy + 30))
        d.rectangle([cx + 2, cy + 2, cx + 42, cy + 28], fill='black'); d.text((cx + 6, cy + 3), str(k), fill='white', font=font)
    sheet.save(f'{out}/{s // per:03d}.jpg', quality=85)
print(name, len(people), 'people', (len(people) + per - 1) // per, 'sheets')
