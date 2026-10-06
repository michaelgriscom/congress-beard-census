import json, urllib.request, urllib.parse, time
from collections import Counter
UA={"User-Agent":"beard-research/0.1 (personal blog research; https://github.com/michaelgriscom)"}
def get(sparql):
    wait=60
    while True:
        try:
            req=urllib.request.Request('https://query.wikidata.org/sparql', data=urllib.parse.urlencode({'query':sparql,'format':'json'}).encode(), headers=UA)
            return json.loads(urllib.request.urlopen(req,timeout=120).read())
        except urllib.error.HTTPError as e:
            if e.code!=429: raise
            print('429, sleeping',wait,flush=True); time.sleep(wait); wait=min(wait*2,900)
rows=[r for r in json.load(open('union_generals.json')) if r['file']]
pages=[r['page'] for r in rows]
res={}
for i in range(0,len(pages),100):
    vals=' '.join('"%s"@en' % p.replace('"','\\"') for p in pages[i:i+100])
    sparql=f"""SELECT ?title ?p ?stateLabel ?countryLabel WHERE {{
      VALUES ?title {{ {vals} }}
      ?a schema:name ?title ; schema:isPartOf <https://en.wikipedia.org/> ; schema:about ?p .
      OPTIONAL {{ ?p wdt:P19 ?pl . OPTIONAL {{ ?pl wdt:P131* ?state . ?state wdt:P31 wd:Q35657 . }} OPTIONAL {{ ?pl wdt:P17 ?country }} }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }} }}"""
    for b in get(sparql)['results']['bindings']:
        t=b['title']['value']; d=res.setdefault(t, dict(qid=b['p']['value'].rsplit('/',1)[1], states=set(), countries=set()))
        if 'stateLabel' in b: d['states'].add(b['stateLabel']['value'])
        if 'countryLabel' in b: d['countries'].add(b['countryLabel']['value'])
    print(i, len(res), flush=True); time.sleep(3)
for t,d in res.items():
    us={'United States','United States of America'}
    d['state']=sorted(d['states'])[0] if d['states'] else (('abroad:'+sorted(d['countries']-us)[0]) if d['countries']-us else None)
    d['states']=sorted(d['states']); d['countries']=sorted(d['countries'])
json.dump(res,open('born.json','w'),indent=0)
print('missing title match', [p for p in pages if p not in res][:30], len([p for p in pages if p not in res]))
print(Counter(res[p]['state'] if p in res else 'NO MATCH' for p in pages).most_common(30))
