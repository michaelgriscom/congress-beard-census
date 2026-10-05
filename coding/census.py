# Merge all coded batches into one code per person and compute census rates.
import json, os, glob, datetime
from collections import defaultdict
code = {}
mine = json.load(open('pilot_codes.json'))           # my original sample coding
for f in sorted(glob.glob('codes_*.txt')):
    b = f.split('_')[1].split('.')[0]          # A, B, ... (agent files: codes_A_agent1.txt)
    if b == 'GEN' or not os.path.exists(f'batches/{b}.json'): continue
    order = json.load(open(f'batches/{b}.json'))
    for line in open(f):
        p = line.split(); s = int(p[0])
        for k, c in enumerate(p[1:]): code[order[s * 24 + k]] = c
over = json.load(open('recheck_codes.json')) if os.path.exists('recheck_codes.json') else {}
code.update(over)
for q, c in mine.items(): code.setdefault(q, c)  # sample portraits not re-coded in batches
L = json.load(open('leg.json'))
import yaml
C = json.loads(json.dumps(yaml.load(open('cur.yaml'), Loader=yaml.SafeLoader), default=str))
gov = json.load(open('governors.json')); gg = json.load(open('governor_gender.json'))
people = {}
for p in L + C:
    q = p['id'].get('wikidata')
    if not q: continue
    terms = [(int(str(t['start'])[:4]), int(str(t['end'])[:4]), t['type'], t['state'], t.get('party', '')) for t in p['terms']]
    people[q] = dict(gender=p.get('bio', {}).get('gender'), terms=terms, gov=[])
for g in gov:
    q = g['wikidata']
    s = int(g['start'][:4]) if g['start'] else None
    e = int(g['end'][:4]) if g['end'] else s
    d = people.setdefault(q, dict(gender=gg.get(q), terms=[], gov=[]))
    if d['gender'] is None: d['gender'] = gg.get(q)
    if s: d['gov'].append((s, e, g['position'].replace('Governor of ', ''), g['party']))
json.dump(dict(code=code), open('census_codes.json', 'w'))

def rates(years, who='congress', state=None, party=None):
    out = []
    for y in years:
        n = full = anyb = 0
        for q, d in people.items():
            if d['gender'] != 'M': continue
            spans = d['terms'] if who == 'congress' else [(s, e, 'gov', st, pa) for s, e, st, pa in d['gov']]
            hit = [t for t in spans if t[0] <= y <= t[1] and (state is None or t[3] == state) and (party is None or party in (t[4] or ''))]
            if not hit: continue
            c = code.get(q)
            if c in (None, 'X', 'W'): continue
            n += 1; full += c == 'F'; anyb += c in 'FBG'
        out.append((y, n, full, anyb))
    return out
if __name__ == '__main__':
    print('coded people', len(code))
    print('year  n   full  any   (Congress, men, coded)')
    for y, n, f, a in rates(range(1841, 1932, 4)):
        print(y, n, f'{100*f/max(n,1):4.0f}% {100*a/max(n,1):4.0f}%')
