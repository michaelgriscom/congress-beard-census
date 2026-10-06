# Usage: python3 analysis/followups/fetch_wikidata.py  (resumable; caches in this folder)
# Birth year, birthplace (resolved to a U.S. state), military branch and Civil War service
# for every census person and Union general. Saves progress after each batch.
import csv, json, os, time, urllib.request, urllib.parse
UA={"User-Agent":"congress-beard-census (https://github.com/michaelgriscom/congress-beard-census)"}
def sparql(q):
    wait=30
    for _ in range(8):
        try:
            req=urllib.request.Request('https://query.wikidata.org/sparql',data=urllib.parse.urlencode({'query':q,'format':'json'}).encode(),headers=UA)
            return json.loads(urllib.request.urlopen(req,timeout=180).read())['results']['bindings']
        except Exception as e:
            print('retry',e,flush=True); time.sleep(wait); wait=min(wait*2,600)
    raise SystemExit('gave up')
REPO=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..'))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
qids=[r['wikidata'] for r in csv.DictReader(open(f'{REPO}/data/facial_hair_census.csv'))]
gen=json.load(open(f'{REPO}/coding/generals/born.json'))
qids=sorted(set(qids+[v['qid'] for v in gen.values() if v.get('qid')]))
out=json.load(open('wd_people.json')) if os.path.exists('wd_people.json') else {}
todo=[q for q in qids if q not in out]
for i in range(0,len(todo),400):
    chunk=todo[i:i+400]
    b=sparql("SELECT ?p ?born ?pl ?branch ?cw WHERE { VALUES ?p { %s } OPTIONAL { ?p wdt:P569 ?born } OPTIONAL { ?p wdt:P19 ?pl } OPTIONAL { ?p wdt:P241 ?branch } OPTIONAL { ?p wdt:P607 ?cw . FILTER(?cw = wd:Q8676) } }" % ' '.join('wd:'+q for q in chunk))
    for q in chunk: out.setdefault(q,dict(born=None,places=[],branches=[],civil_war=False))
    for x in b:
        d=out[x['p']['value'].rsplit('/',1)[1]]
        if 'born' in x and not d['born']:
            try: d['born']=int(x['born']['value'][:4].lstrip('+'))
            except ValueError: pass
        for k,f in (('pl','places'),('branch','branches')):
            if k in x:
                v=x[k]['value'].rsplit('/',1)[1]
                if v not in d[f]: d[f].append(v)
        if 'cw' in x: d['civil_war']=True
    json.dump(out,open('wd_people.json','w')); print('people',len(out),'of',len(qids),flush=True); time.sleep(1)
# resolve birthplaces to states
places=sorted({p for d in out.values() for p in d['places']})
pst=json.load(open('wd_places.json')) if os.path.exists('wd_places.json') else {}
todo=[p for p in places if p not in pst]
for i in range(0,len(todo),300):
    chunk=todo[i:i+300]
    b=sparql("SELECT ?pl ?stateLabel WHERE { VALUES ?pl { %s } ?pl wdt:P131* ?state . ?state wdt:P31 wd:Q35657 . SERVICE wikibase:label { bd:serviceParam wikibase:language \"en\". } }" % ' '.join('wd:'+p for p in chunk))
    for p in chunk: pst.setdefault(p,[])
    for x in b:
        s=x['stateLabel']['value']; p=x['pl']['value'].rsplit('/',1)[1]
        if s not in pst[p]: pst[p].append(s)
    json.dump(pst,open('wd_places.json','w')); print('places',len(pst),'of',len(places),flush=True); time.sleep(1)
final={q:dict(born=d['born'],states=sorted({s for p in d['places'] for s in pst.get(p,[])}),branches=d['branches'],civil_war=d['civil_war']) for q,d in out.items()}
json.dump(final,open(f'{REPO}/data/wikidata_people.json','w'),indent=0,sort_keys=True); print('done',len(final))
