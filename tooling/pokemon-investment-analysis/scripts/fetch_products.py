import json, time, urllib.request
from pathlib import Path
groups = json.load(open('groups3.json'))['results']
out = {}
for i,g in enumerate(groups):
    gid = g['groupId']
    for t in range(3):
        try:
            req = urllib.request.Request(f'https://tcgcsv.com/tcgplayer/3/{gid}/products', headers={'User-Agent':'research/0.1'})
            with urllib.request.urlopen(req, timeout=60) as r: rows = json.load(r).get('results', [])
            break
        except Exception as e:
            rows = None; time.sleep(2)
    if rows is None: print('FAIL', gid); continue
    for p in rows:
        ext = {e.get('name'): e.get('value') for e in (p.get('extendedData') or [])}
        out[str(p['productId'])] = {'g': gid, 'n': p.get('name'), 'cn': p.get('cleanName'),
            'num': ext.get('Number'), 'rar': ext.get('Rarity'), 'ct': ext.get('CardType'),
            'url': p.get('url'), 'pre': (p.get('presaleInfo') or {}).get('isPresale')}
    time.sleep(0.15)
json.dump(out, open('products3.json','w'), separators=(',',':'))
print('products', len(out))
