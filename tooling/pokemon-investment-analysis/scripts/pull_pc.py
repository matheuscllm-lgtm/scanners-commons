import re, json, time, html, urllib.request, urllib.parse, sys
from pathlib import Path
UA = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36'}
OUT = Path('pc'); OUT.mkdir(exist_ok=True)
BASKET = [
 # (label, query, must_have_tokens(lower), segment)
 ("Charizard Base Set unlimited #4 (1999)", "charizard base set 4", ["charizard","base-set"], "vintage_single"),
 ("Charizard Base Set 1st Edition #4", "charizard 1st edition base set", ["charizard","1st"], "vintage_single"),
 ("Charizard Base Set Shadowless #4", "charizard shadowless base set", ["charizard","shadowless"], "vintage_single"),
 ("Blastoise Base Set #2", "blastoise base set 2", ["blastoise","base-set"], "vintage_single"),
 ("Lugia Neo Genesis #9", "lugia neo genesis 9", ["lugia","neo-genesis"], "vintage_single"),
 ("Pikachu Base Set #58 (common)", "pikachu base set 58", ["pikachu","base-set"], "vintage_single_common"),
 ("Espeon Gold Star #16 (POP 5)", "espeon gold star pop series 5", ["espeon","gold"], "midera_single"),
 ("Charizard Gold Star #100 Dragon Frontiers", "charizard gold star dragon frontiers", ["charizard","gold"], "midera_single"),
 ("Umbreon VMAX #215 Evolving Skies (alt art)", "umbreon vmax 215 evolving skies", ["umbreon","215"], "modern_chase"),
 ("Rayquaza VMAX #218 Evolving Skies (alt art)", "rayquaza vmax 218 evolving skies", ["rayquaza","218"], "modern_chase"),
 ("Charizard ex #199 151 (SIR)", "charizard ex 199 151", ["charizard","199"], "modern_chase"),
 ("Umbreon ex #161 Prismatic Evolutions (SIR)", "umbreon ex 161 prismatic evolutions", ["umbreon","161"], "modern_chase"),
 ("Giratina V #186 Lost Origin (alt art)", "giratina v 186 lost origin", ["giratina","186"], "modern_chase"),
 ("Charizard ex #223 Obsidian Flames (SIR)", "charizard ex 223 obsidian flames", ["charizard","223"], "modern_chase"),
 ("Pikachu VMAX #188 Vivid Voltage (rainbow)", "pikachu vmax 188 vivid voltage", ["pikachu","188"], "modern_chase"),
 ("Charizard VMAX #SV107 Shining Fates (shiny)", "charizard vmax sv107 shining fates", ["charizard","107"], "modern_chase"),
 ("Iono #269 Paldea Evolved (SIR)", "iono 269 paldea evolved", ["iono","269"], "modern_chase"),
 ("Pikachu ex #238 Surging Sparks (SIR)", "pikachu ex 238 surging sparks", ["pikachu","238"], "modern_chase"),
 ("Charizard ex #125 Obsidian Flames (double rare, playable)", "charizard ex 125 obsidian flames", ["charizard","125"], "modern_playable"),
 ("Dragapult ex #130 Twilight Masquerade (double rare)", "dragapult ex 130 twilight masquerade", ["dragapult","130"], "modern_playable"),
 ("Gardevoir ex #86 Scarlet & Violet (double rare)", "gardevoir ex 86 scarlet violet", ["gardevoir","86"], "modern_playable"),
 ("Evolving Skies Booster Box", "evolving skies booster box", ["evolving-skies","booster-box"], "sealed_swsh"),
 ("Evolving Skies Elite Trainer Box", "evolving skies elite trainer box", ["evolving-skies","elite-trainer"], "sealed_swsh"),
 ("Crown Zenith Elite Trainer Box", "crown zenith elite trainer box", ["crown-zenith","elite-trainer"], "sealed_swsh"),
 ("Vivid Voltage Booster Box", "vivid voltage booster box", ["vivid-voltage","booster-box"], "sealed_swsh"),
 ("Brilliant Stars Booster Box", "brilliant stars booster box", ["brilliant-stars","booster-box"], "sealed_swsh"),
 ("Sword & Shield Base Booster Box", "sword shield base set booster box", ["sword","booster-box"], "sealed_swsh"),
 ("Hidden Fates Elite Trainer Box", "hidden fates elite trainer box", ["hidden-fates","elite-trainer"], "sealed_sm"),
 ("Champion's Path Elite Trainer Box", "champions path elite trainer box", ["champion","elite-trainer"], "sealed_swsh"),
 ("Celebrations Ultra-Premium Collection", "celebrations ultra premium collection", ["celebrations","ultra"], "sealed_swsh"),
 ("151 Booster Bundle", "151 booster bundle", ["151","bundle"], "sealed_sv"),
 ("151 Elite Trainer Box", "151 elite trainer box", ["151","elite-trainer"], "sealed_sv"),
 ("151 Ultra-Premium Collection", "151 ultra premium collection", ["151","ultra"], "sealed_sv"),
 ("Obsidian Flames Booster Box", "obsidian flames booster box", ["obsidian-flames","booster-box"], "sealed_sv"),
 ("Paldean Fates Elite Trainer Box", "paldean fates elite trainer box", ["paldean-fates","elite-trainer"], "sealed_sv"),
 ("Surging Sparks Booster Box", "surging sparks booster box", ["surging-sparks","booster-box"], "sealed_sv"),
 ("Prismatic Evolutions Elite Trainer Box", "prismatic evolutions elite trainer box", ["prismatic","elite-trainer"], "sealed_sv"),
 ("Prismatic Evolutions Booster Bundle", "prismatic evolutions booster bundle", ["prismatic","bundle"], "sealed_sv"),
 ("Journey Together Booster Box", "journey together booster box", ["journey-together","booster-box"], "sealed_sv"),
 ("Destined Rivals Booster Box", "destined rivals booster box", ["destined-rivals","booster-box"], "sealed_sv"),
 ("Destined Rivals Elite Trainer Box", "destined rivals elite trainer box", ["destined-rivals","elite-trainer"], "sealed_sv"),
 ("Mega Evolution Elite Trainer Box", "mega evolution elite trainer box", ["mega-evolution","elite-trainer"], "sealed_me"),
 ("Phantasmal Flames Booster Box", "phantasmal flames booster box", ["phantasmal","booster-box"], "sealed_me"),
 ("Base Set Booster Box (1999, unlimited)", "base set booster box", ["base-set","booster-box"], "sealed_vintage"),
]
def get(url):
    for i in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.geturl(), r.read().decode('utf-8','ignore')
        except Exception as e:
            err=e; time.sleep(3)
    print('FAIL', url, err); return None, None
def resolve(query, toks):
    url = "https://www.pricecharting.com/search-products?type=prices&q=" + urllib.parse.quote(query)
    final, body = get(url)
    if body is None: return None
    if '/game/' in final: return final
    links = re.findall(r'href="(/game/[^"]+)"', body)
    seen=[]
    for l in links:
        if l in seen: continue
        seen.append(l)
        ll = l.lower()
        if all(t in ll for t in toks): return "https://www.pricecharting.com"+l
    return None
def parse(body):
    m = re.search(r'VGPC\.chart_data\s*=\s*(\{.*?\});', body, re.S)
    chart = json.loads(m.group(1)) if m else {}
    t = re.search(r'<title>(.*?)</title>', body, re.S)
    title = html.unescape(t.group(1)).strip() if t else ''
    prices = {}
    for lab in ['used','complete','new','graded','box_only','manual_only']:
        mm = re.search(r'id="%s_price"[^>]*>(.*?)</td>'%lab, body, re.S)
        if mm:
            pm = re.search(r'\$([\d,]+\.\d{2})', mm.group(1))
            prices[lab] = float(pm.group(1).replace(',','')) if pm else None
    # sales volume per grade (order of columns)
    vols = re.findall(r'volume:&nbsp;</span>\s*([^<]*)<', body)
    return {'title': title, 'chart': chart, 'prices': prices, 'vols': [v.strip() for v in vols]}
if __name__ == '__main__':
    res = {}
    for label, q, toks, seg in BASKET:
        url = resolve(q, toks); time.sleep(1.2)
        if not url: print('NO MATCH', label); res[label]={'seg':seg,'url':None}; continue
        final, body = get(url); time.sleep(1.2)
        if body is None: res[label]={'seg':seg,'url':url}; continue
        p = parse(body); p['seg']=seg; p['url']=final; res[label]=p
        print(label, '->', final.split('/game/')[-1], '| raw', p['prices'].get('used'), '| psa10', p['prices'].get('manual_only'))
    json.dump(res, open('pc/basket.json','w'))
    print('done', len(res))
