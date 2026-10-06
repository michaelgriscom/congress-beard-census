"""Sample members of Congress and download their portraits for facial-hair coding.

1. Reads legislators-historical.yaml from github.com/unitedstates/congress-legislators.
2. For each snapshot year (1836, 1846, ... 1936), takes everyone whose term covers
   Feb 1 of that year. Terms began in December of odd years, so Feb 1 of an even
   year falls mid-session.
3. Looks up each member's portrait (Wikidata P18) on Wikimedia Commons.
4. Draws 60 random members with a portrait per snapshot (seed 1861), plus every
   Ohio member from 1856 to 1906 for the Ohio comparison.
5. Downloads 250px thumbnails into img/. The official Bioguide photo server
   refuses automated requests, so Commons is the source.

Requires: pip install pyyaml
Then run contact_sheets.py and code each numbered portrait by eye.
"""

import datetime
import json
import os
import random
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "beard-research/0.1 (personal blog research; https://github.com/michaelgriscom)"}
SNAPSHOTS = range(1836, 1937, 10)


def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()


def members():
    import yaml

    if not os.path.exists("leg.yaml"):
        open("leg.yaml", "wb").write(
            fetch("https://raw.githubusercontent.com/unitedstates/congress-legislators/main/legislators-historical.yaml")
        )
    out, seen = [], set()
    for p in yaml.load(open("leg.yaml"), Loader=yaml.SafeLoader):
        name = p["name"].get("official_full") or f"{p['name'].get('first', '')} {p['name'].get('last', '')}"
        for t in p.get("terms", []):
            start = datetime.date.fromisoformat(str(t["start"]))
            end = datetime.date.fromisoformat(str(t["end"]))
            for y in SNAPSHOTS:
                key = (y, p["id"]["bioguide"])
                if start <= datetime.date(y, 2, 1) <= end and key not in seen:
                    seen.add(key)
                    out.append(dict(snap=y, bioguide=p["id"]["bioguide"], wikidata=p["id"].get("wikidata"),
                                    name=name, type=t["type"], state=t["state"], party=t.get("party", "")))
    return out


def portraits(qids):
    images = {}
    qids = sorted(q for q in qids if q)
    for i in range(0, len(qids), 250):
        values = " ".join("wd:" + q for q in qids[i:i + 250])
        query = f"SELECT ?p ?img WHERE {{ VALUES ?p {{ {values} }} ?p wdt:P18 ?img }}"
        data = json.loads(fetch("https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(query)))
        for b in data["results"]["bindings"]:
            images.setdefault(b["p"]["value"].rsplit("/", 1)[1], b["img"]["value"])
        time.sleep(1)
    return images


def main():
    rows = members()
    images = portraits({r["wikidata"] for r in rows})
    random.seed(1861)
    sample = []
    for s in SNAPSHOTS:
        pool = [r for r in rows if r["snap"] == s and r["wikidata"] in images]
        sample += [{**r, "why": "random"} for r in random.sample(pool, min(60, len(pool)))]
        if 1856 <= s <= 1906:
            sample += [{**r, "why": "ohio"} for r in pool if r["state"] == "OH"]
    json.dump(sample, open("sample.json", "w"))
    json.dump(images, open("images.json", "w"))

    os.makedirs("img", exist_ok=True)
    for q in sorted({r["wikidata"] for r in sample}):
        path = f"img/{q}.jpg"
        if os.path.exists(path):
            continue
        name = urllib.parse.unquote(images[q].rsplit("/", 1)[1])
        url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(name) + "?width=250"
        for attempt in range(4):
            try:
                open(path, "wb").write(fetch(url))
                break
            except Exception:  # Commons rate-limits bursts with HTTP 429
                time.sleep(2 * (attempt + 1))
        time.sleep(1)


if __name__ == "__main__":
    main()
