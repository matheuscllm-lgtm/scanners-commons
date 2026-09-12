import json, math, statistics as st, collections, re
from datetime import date
P=json.load(open('products3.json'))
G={g['groupId']:g for g in json.load(open('groups3.json'))['results']}
dates=open('dates.txt').read().split()
D={d: json.load(open(f'cat3/{d}.json')) for d in dates}

def era(gid):
    g=G.get(int(gid)); 
    if not g: return 'unknown'
    d=g['publishedOn'][:10]; n=g['name']
    if d=='2026-09-05' and g['groupId']<24000: return 'misc'
    if d<'2003-06-18': return 'vintage_wotc'
    if d<'2007-05-23': return 'ex_era'
    if d<'2011-04-25': return 'dp_hgss'
    if d<'2017-02-03': return 'bw_xy'
    if d<'2020-02-07': return 'sm'
    if d<'2023-03-31': return 'swsh'
    if d<'2025-09-26': return 'sv'
    return 'me'
T1={'Special Illustration Rare','Secret Rare','Hyper Rare','Rainbow Rare','Shiny Ultra Rare','Mega Hyper Rare','Black White Rare'}
T2={'Illustration Rare','Ultra Rare','Shiny Holo Rare','Shiny Rare','Mega Attack Rare','Classic Collection'}
T3={'Holo Rare','Double Rare','Rare BREAK','Prism Rare','Radiant Rare','ACE SPEC Rare','Rare Ace','Amazing Rare','Futuristic Rare'}
T4={'Common','Uncommon','Rare','Code Card','None','Unconfirmed',None}
def tier(r):
    if r in T1: return 'T1_chase'
    if r in T2: return 'T2_art_ultra'
    if r in T3: return 'T3_mid'
    if r=='Promo': return 'promo'
    if r in T4: return 'T4_bulk'
    return 'other'
def sealed_type(n):
    n=n.lower()
    if any(k in n for k in ['case','sleeve','binder','playmat','code card','deck box','portfolio','dice','coin','damage counter']): return None
    if 'booster box' in n and 'half' not in n: return 'booster_box'
    if 'elite trainer' in n: return 'etb'
    if 'booster bundle' in n: return 'bundle'
    if 'booster pack' in n and 'art bundle' not in n: return 'pack'
    if any(k in n for k in ['tin','blister','collection','premium','box','bundle','kit','deck','set of']): return 'other_sealed'
    return None
seg_of={}
for pid,p in P.items():
    if p['rar'] is None:
        stp=sealed_type(p['n'] or '')
        if stp: seg_of[pid]=('sealed',stp,era(p['g']))
    else:
        seg_of[pid]=('single',tier(p['rar']),era(p['g']))
def price(d,pid):
    r=D[d].get(pid)
    if not r: return None
    best=None
    for stn,(m,lo) in r['v'].items():
        if 'reverse' in (stn or '').lower(): continue
        if isinstance(m,(int,float)) and m>0 and (best is None or m>best): best=m
    return best
def stats(pairs):
    if not pairs: return None
    ratios=[b/a for a,b in pairs]
    lr=[math.log(r) for r in ratios]
    ratios_s=sorted(ratios)
    n=len(ratios)
    q=lambda p: ratios_s[min(n-1,int(p*n))]
    return {'n':n,'median':(st.median(ratios)-1)*100,'p25':(q(0.25)-1)*100,'p75':(q(0.75)-1)*100,
            'vw':(sum(b for a,b in pairs)/sum(a for a,b in pairs)-1)*100,'share_up':100*sum(1 for r in ratios if r>1.0)/n,
            'share_down20':100*sum(1 for r in ratios if r<0.8)/n}
def window(d0,d1,filt,floor=5.0):
    pairs=[]
    for pid,seg in seg_of.items():
        if not filt(seg): continue
        a=price(d0,pid); b=price(d1,pid)
        if a and b and a>=floor: pairs.append((a,b))
    return stats(pairs)
W=[('2024-02-08','2026-09-05'),('2024-02-08','2025-02-08'),('2025-02-08','2026-02-08'),('2026-02-08','2026-09-05'),('2025-09-08','2026-09-05')]
segs={
 'Selado SWSH (2020-23) — booster box':lambda s:s[0]=='sealed' and s[1]=='booster_box' and s[2]=='swsh',
 'Selado SWSH — ETB':lambda s:s[0]=='sealed' and s[1]=='etb' and s[2]=='swsh',
 'Selado SWSH — todos':lambda s:s[0]=='sealed' and s[2]=='swsh',
 'Selado SM (2017-19) — todos':lambda s:s[0]=='sealed' and s[2]=='sm',
 'Selado XY/BW (2011-16) — todos':lambda s:s[0]=='sealed' and s[2]=='bw_xy',
 'Selado EX/DP/HGSS (2003-11) — todos':lambda s:s[0]=='sealed' and s[2] in ('ex_era','dp_hgss'),
 'Selado WotC (1999-2003) — todos':lambda s:s[0]=='sealed' and s[2]=='vintage_wotc',
 'Selado SV (2023-25) — booster box':lambda s:s[0]=='sealed' and s[1]=='booster_box' and s[2]=='sv',
 'Selado SV — ETB':lambda s:s[0]=='sealed' and s[1]=='etb' and s[2]=='sv',
 'Selado SV — bundle':lambda s:s[0]=='sealed' and s[1]=='bundle' and s[2]=='sv',
 'Selado SV — todos':lambda s:s[0]=='sealed' and s[2]=='sv',
 'Selado ME (2025-26) — todos':lambda s:s[0]=='sealed' and s[2]=='me',
 'Singles T1 chase (SIR/Secret/Hyper) — SWSH':lambda s:s[0]=='single' and s[1]=='T1_chase' and s[2]=='swsh',
 'Singles T1 chase — SV':lambda s:s[0]=='single' and s[1]=='T1_chase' and s[2]=='sv',
 'Singles T1 chase — SM':lambda s:s[0]=='single' and s[1]=='T1_chase' and s[2]=='sm',
 'Singles T1 chase — XY/BW':lambda s:s[0]=='single' and s[1]=='T1_chase' and s[2]=='bw_xy',
 'Singles T2 (IR/Ultra/Shiny) — SWSH':lambda s:s[0]=='single' and s[1]=='T2_art_ultra' and s[2]=='swsh',
 'Singles T2 — SV':lambda s:s[0]=='single' and s[1]=='T2_art_ultra' and s[2]=='sv',
 'Singles T3 mid (Holo/Double Rare/ACE) — SWSH':lambda s:s[0]=='single' and s[1]=='T3_mid' and s[2]=='swsh',
 'Singles T3 mid — SV':lambda s:s[0]=='single' and s[1]=='T3_mid' and s[2]=='sv',
 'Singles T4 bulk (C/U/R) — SV':lambda s:s[0]=='single' and s[1]=='T4_bulk' and s[2]=='sv',
 'Singles vintage WotC (1999-2003) — todos':lambda s:s[0]=='single' and s[2]=='vintage_wotc',
 'Singles vintage WotC — Holo Rare':lambda s:s[0]=='single' and s[2]=='vintage_wotc' and P and s[1]=='T3_mid',
 'Singles EX/DP/HGSS (2003-11) — todos':lambda s:s[0]=='single' and s[2] in ('ex_era','dp_hgss'),
 'Singles EX/DP/HGSS — T1/T2':lambda s:s[0]=='single' and s[2] in ('ex_era','dp_hgss') and s[1] in ('T1_chase','T2_art_ultra'),
 'Singles XY/BW (2011-16) — todos':lambda s:s[0]=='single' and s[2]=='bw_xy',
 'Singles SM (2017-19) — todos':lambda s:s[0]=='single' and s[2]=='sm',
 'Singles SWSH — todos ≥$5':lambda s:s[0]=='single' and s[2]=='swsh',
 'Singles SV — todos ≥$5':lambda s:s[0]=='single' and s[2]=='sv',
 'Promos (todas as eras) ≥$5':lambda s:s[0]=='single' and s[1]=='promo',
}
out={}
lines=[]
hdr='| Segmento | Janela | N | Mediana % | P25 % | P75 % | Ponderado por valor % | % subiu | % caiu >20% |'
lines.append(hdr); lines.append('|'+'---|'*9)
for name,f in segs.items():
    for d0,d1 in W:
        s=window(d0,d1,f)
        out.setdefault(name,{})[f'{d0}→{d1}']=s
        if s: lines.append(f"| {name} | {d0[:7]}→{d1[:7]} | {s['n']} | {s['median']:+.0f} | {s['p25']:+.0f} | {s['p75']:+.0f} | {s['vw']:+.0f} | {s['share_up']:.0f} | {s['share_down20']:.0f} |")
open('windows.md','w').write('\n'.join(lines))
json.dump(out,open('windows.json','w'),indent=1)
print('\n'.join(lines))
# ---- monthly index (median ratio vs base for fixed basket, floor $5 at base) for key segments
key=['Selado SWSH — todos','Selado SV — todos','Selado SM (2017-19) — todos','Singles T1 chase (SIR/Secret/Hyper) — SWSH','Singles T1 chase — SV','Singles vintage WotC (1999-2003) — todos','Singles T3 mid — SV','Singles T4 bulk (C/U/R) — SV','Singles EX/DP/HGSS — T1/T2']
base='2024-02-08'
rows=[]
for d in dates:
    row=[d[:7]]
    for k in key:
        f=segs[k]; pairs=[]
        for pid,seg in seg_of.items():
            if not f(seg): continue
            a=price(base,pid); b=price(d,pid)
            if a and b and a>=5: pairs.append((a,b))
        if pairs:
            row.append(f"{st.median([b/a for a,b in pairs])*100:.0f}")
        else: row.append('—')
    rows.append(row)
mi='| Mês | '+' | '.join(key)+' |\n|'+'---|'*(len(key)+1)+'\n'+'\n'.join('| '+' | '.join(r)+' |' for r in rows)
open('monthly_index.md','w').write(mi); print(mi)
# ---- SKU counts and groups per year
print('\nSKUs com preço por data:', {d:len(D[d]) for d in (dates[0],'2025-02-08','2026-02-08',dates[-1])})
