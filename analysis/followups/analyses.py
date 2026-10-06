"""Three follow-up analyses on the facial-hair census.

1. Ohio exported politicians: Ohio-born members of Congress serving other states, 1861-1901.
2. Generals vs congressmen of the same birth years (is the generals' beard gap just age?).
3. Civil War veterans vs non-veterans in Congress, 1865-1895, within birth cohorts.

Inputs: data/wikidata_people.json (from fetch_wikidata.py) plus the census data
and coding files. Run from anywhere: python3 analysis/followups/analyses.py
"""
import csv
import json
import math
from collections import Counter, defaultdict

import os

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
wd = json.load(open(f"{REPO}/data/wikidata_people.json"))
census = list(csv.DictReader(open(f"{REPO}/data/facial_hair_census.csv")))
gen_rows = list(csv.DictReader(open(f"{REPO}/data/union_generals_facial_hair.csv")))
gen_meta = {r["key"]: r for r in json.load(open(f"{REPO}/coding/generals/union_generals.json")) if r.get("file")}
gen_born = json.load(open(f"{REPO}/coding/generals/born.json"))

UNION = {"Q1752901", "Q115194", "Q3550003"}  # Union Army, U.S. Volunteers, Union Navy
REGULAR = {"Q9212"}  # U.S. Army (also covers Union regulars)
CSA = {"Q1125021"}
SOUTH = {"VA", "NC", "SC", "GA", "FL", "AL", "MS", "LA", "TX", "AR", "TN"}
ABBR = {
    "Alabama": "AL", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY",
    "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New York": "NY", "North Carolina": "NC", "Ohio": "OH", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
    "South Carolina": "SC", "Tennessee": "TN", "Texas": "TX", "Vermont": "VT", "Virginia": "VA", "West Virginia": "WV",
    "Wisconsin": "WI", "Montana": "MT", "Idaho": "ID", "Washington": "WA", "Wyoming": "WY", "Utah": "UT",
    "North Dakota": "ND", "South Dakota": "SD", "Oklahoma": "OK", "New Mexico": "NM", "Arizona": "AZ",
}


def terms(s):
    out = []
    for t in filter(None, s.split(";")):
        span, state, *_ = t.split(":")
        a, b = map(int, span.split("-"))
        out.append((a, b, state))
    return out


people = []
for r in census:
    d = wd.get(r["wikidata"], {})
    states = [ABBR[s] for s in d.get("states", []) if s in ABBR]
    people.append(dict(
        q=r["wikidata"], name=r["name"], gender=r["gender"], code=r["facial_hair"],
        born=int(r["birth_year"]) if r["birth_year"] else d.get("born"),
        birth_state=states[0] if len(set(states)) == 1 else None,  # skip ambiguous birthplaces
        congress=terms(r["congress_terms"]),
        branches=set(d.get("branches", [])), civil_war=d.get("civil_war", False),
    ))
usable = lambda p: p["gender"] == "M" and p["code"] not in ("unusable", "woman")
serves = lambda p, a, b: any(t[0] <= b and t[1] >= a for t in p["congress"])


def fisher_two_sided(a, b, c, d):
    n1, n2, k = a + b, c + d, a + c
    n = n1 + n2
    lg = lambda x: math.lgamma(x + 1)
    p = lambda x: math.exp(lg(k) - lg(x) - lg(k - x) + lg(n - k) - lg(n1 - x) - lg(n - k - n1 + x) - lg(n) + lg(n1) + lg(n - n1))
    p0 = p(a)
    return sum(p(x) for x in range(max(0, n1 - (n - k)), min(k, n1) + 1) if p(x) <= p0 * (1 + 1e-9))


def mantel_haenszel(strata):
    """strata: list of (a, b, c, d) = (exposed full, exposed other, unexposed full, unexposed other).
    Returns the MH common odds ratio and the CMH chi-square p-value (1 df, continuity-corrected)."""
    num = den = 0.0
    sa = se = sv = 0.0
    for a, b, c, d in strata:
        n = a + b + c + d
        if n < 2:
            continue
        num += a * d / n
        den += b * c / n
        n1, n0, m1, m0 = a + b, c + d, a + c, b + d
        sa += a
        se += n1 * m1 / n
        sv += n1 * n0 * m1 * m0 / (n * n * (n - 1)) if n > 1 else 0
    orr = num / den if den else float("inf")
    chi = (abs(sa - se) - 0.5) ** 2 / sv if sv else 0
    p = math.erfc(math.sqrt(chi / 2))
    return orr, p


pct = lambda k, n: f"{k}/{n} ({100 * k / n:.0f}%)" if n else "0/0"

# ---------------------------------------------------------------- 1. Ohio exports
print("=" * 70)
print("1. Members of Congress serving 1861-1901, by birth state vs state served")
era = [p for p in people if serves(p, 1861, 1901) and p["birth_state"]]
known = len(era)
print(f"   members with a single known U.S. birth state: {known}")
served_other = defaultdict(list)
home = Counter()
for p in era:
    states_served = {t[2] for t in p["congress"] if t[0] <= 1901 and t[1] >= 1861}
    if p["birth_state"] in states_served:
        home[p["birth_state"]] += 1
    else:
        served_other[p["birth_state"]].append(p)
exports = sorted(((len(v), k) for k, v in served_other.items()), reverse=True)
total_exports = sum(n for n, _ in exports)
print(f"   members serving a state other than their birth state: {total_exports}")
print("   top exporters (born there, served elsewhere / served at home):")
for n, k in exports[:8]:
    print(f"     {k}: {n} served elsewhere ({100 * n / total_exports:.0f}% of all such members), {home[k]} at home")
oh = served_other.get("OH", [])
dest = Counter(t[2] for p in oh for t in p["congress"] if t[0] <= 1901 and t[1] >= 1861 and t[2] != "OH")
print("   where Ohio-born members served instead:", ", ".join(f"{k} {v}" for k, v in dest.most_common(10)))
for st in ["IN", "IL", "IA", "KS", "MI", "NE", "MN", "WI", "MO", "CA"]:
    members = [p for p in era if any(t[2] == st and t[0] <= 1901 and t[1] >= 1861 for t in p["congress"])]
    if members:
        o = sum(p["birth_state"] == "OH" for p in members)
        print(f"     share of {st}'s members born in Ohio: {pct(o, len(members))}")

# ---------------------------------------------------------------- 2. Generals vs same-cohort congressmen
print("=" * 70)
print("2. Union generals vs congressmen born in the same years (Congress 1857-1873)")
qid_of = {}
for key, r in gen_meta.items():
    b = gen_born.get(r["page"]) or {}
    if b.get("qid"):
        qid_of[key] = b["qid"]
generals = []
for r in gen_rows:
    if r["group"] != "union_general" or r["facial_hair"] in ("unusable", "woman"):
        continue
    by = wd.get(qid_of.get(r["id"]), {}).get("born")
    if by:
        generals.append(dict(born=by, full=r["facial_hair"] == "full_beard"))
gen_qids = set(qid_of.values())
controls = [p for p in people if usable(p) and p["born"] and serves(p, 1857, 1873) and p["q"] not in gen_qids]
print(f"   generals with a birth year: {len(generals)}; congressmen controls: {len(controls)}")
strata = []
print("   birth decade   generals          congressmen")
for dec in range(1790, 1850, 10):
    g = [x for x in generals if dec <= x["born"] < dec + 10]
    c = [p for p in controls if dec <= p["born"] < dec + 10]
    gf, cf = sum(x["full"] for x in g), sum(p["code"] == "full_beard" for p in c)
    if g or c:
        print(f"   {dec}s          {pct(gf, len(g)):17s} {pct(cf, len(c))}")
    strata.append((gf, len(g) - gf, cf, len(c) - cf))
# expected rate for each general from congressmen born within 3 years
exp = []
for x in generals:
    near = [p for p in controls if abs(p["born"] - x["born"]) <= 3]
    if len(near) >= 10:
        exp.append(sum(p["code"] == "full_beard" for p in near) / len(near))
if generals and exp:
    obs = sum(x["full"] for x in generals) / len(generals)
    print(f"   generals' full-beard rate {obs:.0%}; congressmen of the same birth years (+-3) {sum(exp) / len(exp):.0%}")
    orr, p = mantel_haenszel(strata)
    print(f"   age-adjusted (Mantel-Haenszel by birth decade): odds ratio {orr:.2f}, p = {p:.1e}")
    print(f"   median birth year: generals {sorted(x['born'] for x in generals)[len(generals) // 2]}, "
          f"controls {sorted(p['born'] for p in controls)[len(controls) // 2]}")

# ---------------------------------------------------------------- 3. Veterans vs non-veterans
print("=" * 70)
print("3. Civil War service and beards, men serving in Congress 1865-1895, born 1815-1845")
base = [p for p in people if usable(p) and p["born"] and 1815 <= p["born"] <= 1845 and serves(p, 1865, 1895)]


def side(p):
    if p["branches"] & CSA:
        return "confederate"
    if p["branches"] & (UNION | REGULAR) or (p["civil_war"] and not p["branches"] & CSA):
        return "union"
    return "none"


for label, sel in [("Union veterans", "union"), ("Confederate veterans", "confederate"), ("No recorded service", "none")]:
    grp = [p for p in base if side(p) == sel]
    print(f"   {label:22s} {pct(sum(p['code'] == 'full_beard' for p in grp), len(grp))}")


def compare(exposed, unexposed, label):
    rows = []
    for dec in (1815, 1825, 1835):
        e = [p for p in exposed if dec <= p["born"] < dec + 10]
        u = [p for p in unexposed if dec <= p["born"] < dec + 10]
        ef, uf = sum(p["code"] == "full_beard" for p in e), sum(p["code"] == "full_beard" for p in u)
        rows.append((ef, len(e) - ef, uf, len(u) - uf))
        print(f"     born {dec}-{dec + 9}: {pct(ef, len(e)):15s} vs {pct(uf, len(u))}")
    orr, p = mantel_haenszel(rows)
    print(f"   {label}: age-adjusted odds ratio {orr:.2f}, p = {p:.3f}")


north = [p for p in base if not any(t[2] in SOUTH for t in p["congress"])]
southern = [p for p in base if any(t[2] in SOUTH for t in p["congress"])]
print("   Northern members, Union veterans vs no recorded service:")
compare([p for p in north if side(p) == "union"], [p for p in north if side(p) == "none"], "North")
print("   ... excluding generals (are veterans bearded beyond the generals?):")
compare([p for p in north if side(p) == "union" and p["q"] not in gen_qids],
        [p for p in north if side(p) == "none"], "North, non-generals")
print("   Southern members, Confederate veterans vs no recorded service:")
compare([p for p in southern if side(p) == "confederate"], [p for p in southern if side(p) == "none"], "South")
print("   Note: 'no recorded service' means Wikidata lists none, not that the man never served.")
