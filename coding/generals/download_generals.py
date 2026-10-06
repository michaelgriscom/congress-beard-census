import json, os, time, urllib.parse, urllib.request, hashlib
UA = {"User-Agent": "beard-research/0.1 (personal blog research; https://github.com/michaelgriscom)"}
rows = [r for r in json.load(open('union_generals.json')) if r['file']]
os.makedirs('img', exist_ok=True)
for i, r in enumerate(rows):
    key = hashlib.md5(r['file'].encode()).hexdigest()[:12]
    r['key'] = key
    path = f'img/{key}.jpg'
    if os.path.exists(path): continue
    url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(r['file'].replace(' ', '_')) + "?width=250"
    wait = 120
    for attempt in range(5):
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
            open(path, 'wb').write(data); break
        except urllib.error.HTTPError as e:
            print(i, r['name'], e.code, flush=True)
            if e.code == 404: break
            time.sleep(wait); wait = min(wait * 2, 960)
        except Exception as e:
            print(i, r['name'], e, flush=True); time.sleep(10)
    time.sleep(8)
json.dump(rows, open('union_generals.json', 'w'), indent=0)
print('done', len(os.listdir('img')), flush=True)
