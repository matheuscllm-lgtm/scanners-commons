import json, sys, time, shutil, tempfile, urllib.request, py7zr
from pathlib import Path
from datetime import date
BASE = Path('.')
ARCH = BASE/'arch'; ARCH.mkdir(exist_ok=True)
OUT = BASE/'cat3'; OUT.mkdir(exist_ok=True)
MAGIC = b"7z\xbc\xaf\x27\x1c"
def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'research/0.1'})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except Exception as e:
            err = e; time.sleep(2*(i+1))
    print('FAIL', url, err); return None
def extract(d):
    outp = OUT/f'{d}.json'
    if outp.exists(): return True
    ap = ARCH/f'prices-{d}.ppmd.7z'
    if not ap.exists():
        b = get(f'https://tcgcsv.com/archive/tcgplayer/prices-{d}.ppmd.7z')
        if not b or not b.startswith(MAGIC): print('no archive', d); return False
        ap.write_bytes(b)
    with py7zr.SevenZipFile(ap,'r') as z: names = z.getnames()
    targets = [n for n in names if n.split('/')[1:2]==['3'] and n.endswith('/prices')]
    if not targets: print('no cat3 in', d, names[:5]); return False
    tmp = Path(tempfile.mkdtemp())
    try:
        with py7zr.SevenZipFile(ap,'r') as z: z.extract(path=str(tmp), targets=targets)
        data = {}
        for fp in tmp.rglob('prices'):
            parts = fp.parts
            if parts[-3] != '3': continue
            gid = parts[-2]
            try: rows = json.loads(fp.read_text()).get('results', [])
            except Exception: continue
            for r in rows:
                pid = str(r.get('productId')); st = r.get('subTypeName') or ''
                m = r.get('marketPrice'); lo = r.get('lowPrice')
                data.setdefault(pid, {'g': gid, 'v': {}})['v'][st] = [m, lo]
        outp.write_text(json.dumps(data, separators=(',',':')))
        print(d, 'products', len(data))
        return True
    finally: shutil.rmtree(tmp, ignore_errors=True)
dates = sys.argv[1:]
for d in dates: extract(d)
