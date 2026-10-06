#!/usr/bin/env python3
"""Download the remaining Congress and governor portraits from Wikimedia Commons.

Run on your own computer (Python 3, no extra packages):

    python3 download_portraits.py portrait_list.tsv

It fetches one 250px thumbnail per line, one at a time with a 1-second pause
(well inside Wikimedia's robot policy), backs off if Commons asks it to slow
down, and can be stopped and re-run: it skips files it already has. When done it
writes portraits_1.zip, portraits_2.zip, ... (about 1,000 images each) in the
current folder. Upload those zips to a Google Drive folder and tell Claude the
folder name.
"""
import os, sys, time, urllib.parse, urllib.request, zipfile

UA = {"User-Agent": "beard-research/0.1 (personal blog research; https://github.com/michaelgriscom)"}
OUT = "portraits"

def main(list_path):
    os.makedirs(OUT, exist_ok=True)
    rows = [line.rstrip("\n").split("\t") for line in open(list_path, encoding="utf-8") if "\t" in line]
    todo = [(q, fn) for q, fn in rows if not os.path.exists(os.path.join(OUT, q + ".jpg"))]
    print(f"{len(rows)} portraits listed, {len(todo)} still to download")
    pause = 60
    for i, (q, fn) in enumerate(todo, 1):
        url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(fn) + "?width=250"
        for attempt in range(4):
            try:
                data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
                with open(os.path.join(OUT, q + ".jpg"), "wb") as f:
                    f.write(data)
                pause = 60
                break
            except Exception as e:
                if "429" in str(e):
                    print(f"  Commons asked us to slow down; waiting {pause}s")
                    time.sleep(pause)
                    pause = min(pause * 2, 900)
                else:
                    print(f"  skipped {q} ({e})")
                    break
        time.sleep(1)
        if i % 100 == 0:
            print(f"{i}/{len(todo)} done")
    files = sorted(os.listdir(OUT))
    for n in range(0, len(files), 1000):
        name = f"portraits_{n // 1000 + 1}.zip"
        with zipfile.ZipFile(name, "w", zipfile.ZIP_STORED) as z:
            for f in files[n:n + 1000]:
                z.write(os.path.join(OUT, f), f)
        print("wrote", name)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "portrait_list.tsv")
