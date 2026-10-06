# Compliant slow downloader: one connection, ~7 s between requests, and an
# exponential pause after each HTTP 429 (2 min doubling to 16 min) so a throttled
# address can recover instead of being kept throttled.
# Usage: python3 slow_download.py <scope>   scope = era | all
import json, os, random, sys, time, urllib.request, urllib.parse
UA={'User-Agent':'beard-research/0.1 (personal blog research; https://github.com/michaelgriscom; contact via GitHub)'}
scope=sys.argv[1]
img=json.load(open('images.json'))
L=json.load(open('leg.json')); gov=json.load(open('governors.json'))
try:
    import yaml; C=json.loads(json.dumps(yaml.load(open('cur.yaml'),Loader=yaml.SafeLoader),default=str))
except Exception: C=[]
def era_ok(s,e): return s<=1929 and e>=1849
want=set()
for p in L+C:
    if any(scope=='all' or era_ok(int(str(t['start'])[:4]),int(str(t['end'])[:4])) for t in p['terms']): want.add(p['id'].get('wikidata'))
for g in gov:
    if scope=='all' or (g['start'] and era_ok(int(g['start'][:4]), int(g['end'][:4]) if g['end'] else 9999)): want.add(g['wikidata'])
fails=set(json.load(open('slow_fails.json'))) if os.path.exists('slow_fails.json') else set()
todo=[q for q in want if q in img and not os.path.exists(f'img/{q}.jpg')]
random.seed(7); random.shuffle(todo)
todo.sort(key=lambda q: q in fails)          # never-tried first, previous failures last
print(scope,'to download',len(todo),'of which previously failing',sum(q in fails for q in todo),flush=True)
n=ok=0; backoff=120
for q in todo:
    fn=urllib.parse.unquote(img[q].rsplit('/',1)[1])
    u='https://commons.wikimedia.org/wiki/Special:FilePath/'+urllib.parse.quote(fn)+'?width=250'
    try:
        data=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30).read()
        open(f'img/{q}.jpg','wb').write(data); fails.discard(q); ok+=1; backoff=120
        time.sleep(random.uniform(6,8))
    except Exception as e:
        fails.add(q)
        if '429' in str(e):
            print(f'429 after {n} attempts; pausing {backoff}s',flush=True)
            time.sleep(backoff); backoff=min(backoff*2,960)
        else:
            time.sleep(7)
    n+=1
    if n%50==0:
        print(n,'attempted',ok,'ok',len(os.listdir('img')),'files',flush=True)
        json.dump(sorted(fails),open('slow_fails.json','w'))
json.dump(sorted(fails),open('slow_fails.json','w'))
print('pass finished',len([q for q in todo if not os.path.exists(f"img/{q}.jpg")]),'still missing',flush=True)
