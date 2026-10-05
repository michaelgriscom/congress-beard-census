"""Download the member lists the coding scripts expect, into this directory.

leg.json  - legislators-historical.yaml, converted to JSON
cur.yaml  - legislators-current.yaml
Both come from github.com/unitedstates/congress-legislators (public domain).
Requires: pip install pyyaml
"""
import json
import urllib.request

import yaml

BASE = "https://raw.githubusercontent.com/unitedstates/congress-legislators/main/"
UA = {"User-Agent": "congress-beard-census (https://github.com/michaelgriscom/congress-beard-census)"}


def fetch(name):
    return urllib.request.urlopen(urllib.request.Request(BASE + name, headers=UA), timeout=120).read()


hist = yaml.load(fetch("legislators-historical.yaml"), Loader=yaml.SafeLoader)
json.dump(hist, open("leg.json", "w"), default=str)
open("cur.yaml", "wb").write(fetch("legislators-current.yaml"))
print(len(hist), "historical legislators; current list saved to cur.yaml")
