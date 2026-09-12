import re, json, time, urllib.request
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36'}
def get(url):
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=60) as r: return r.read().decode('utf-8','ignore')
        except Exception as e: err=e; time.sleep(3)
    print('FAIL',url,err); return None
res=json.load(open('pc/basket.json')); vols={}
for label,item in res.items():
    url=item.get('url')
    if not url: continue
    body=get(url.split('?')[0]); time.sleep(1.3)
    if not body: continue
    m=re.search(r'<tr class="sales_volume">(.*?)</tr>', body, re.S); v={}
    if m:
        for tab,txt in re.findall(r'data-show-tab="completed-auctions-([a-z-]+)".*?<a href="#">([^<]*)</a>', m.group(1), re.S): v[tab]=txt.strip()
    vols[label]=v; print(label,'|',v)
json.dump(vols,open('pc/volumes2.json','w'),indent=1); print('done',len(vols))
