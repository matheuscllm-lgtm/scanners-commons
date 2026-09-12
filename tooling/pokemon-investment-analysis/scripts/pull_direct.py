import re, json, time, html, urllib.request, sys
sys.path.insert(0,'pc')
from pull_pc import get, parse
res=json.load(open('pc/basket.json'))
DIRECT = {
 "Charizard Base Set unlimited #4 (1999)": ("pokemon-base-set/charizard-4","vintage_single"),
 "Charizard Base Set 1st Edition #4": ("pokemon-base-set/charizard-1st-edition-4","vintage_single"),
 "Blastoise Base Set #2": ("pokemon-base-set/blastoise-2","vintage_single"),
 "Lugia Neo Genesis #9": ("pokemon-neo-genesis/lugia-9","vintage_single"),
 "Pikachu Base Set #58 (common)": ("pokemon-base-set/pikachu-58","vintage_single_common"),
 "Charizard Gold Star #100 Dragon Frontiers": ("pokemon-dragon-frontiers/charizard-gold-star-100","midera_single"),
 "Pikachu VMAX #188 Vivid Voltage (rainbow)": ("pokemon-vivid-voltage/pikachu-vmax-188","modern_chase"),
 "Charizard ex #125 Obsidian Flames (double rare, playable)": ("pokemon-obsidian-flames/charizard-ex-125","modern_playable"),
 "Gardevoir ex #86 Scarlet & Violet (double rare)": ("pokemon-scarlet-&-violet/gardevoir-ex-86","modern_playable"),
 "Evolving Skies Booster Box": ("pokemon-evolving-skies/booster-box","sealed_swsh"),
 "Evolving Skies Elite Trainer Box": ("pokemon-evolving-skies/elite-trainer-box","sealed_swsh"),
 "Crown Zenith Elite Trainer Box": ("pokemon-crown-zenith/elite-trainer-box","sealed_swsh"),
 "Vivid Voltage Booster Box": ("pokemon-vivid-voltage/booster-box","sealed_swsh"),
 "Celebrations Ultra-Premium Collection": ("pokemon-celebrations/ultra-premium-collection","sealed_swsh"),
 "151 Booster Bundle": ("pokemon-scarlet-&-violet-151/booster-bundle","sealed_sv"),
 "151 Elite Trainer Box": ("pokemon-scarlet-&-violet-151/elite-trainer-box","sealed_sv"),
 "Obsidian Flames Booster Box": ("pokemon-obsidian-flames/booster-box","sealed_sv"),
 "Paldean Fates Elite Trainer Box": ("pokemon-paldean-fates/elite-trainer-box","sealed_sv"),
 "Surging Sparks Booster Box": ("pokemon-surging-sparks/booster-box","sealed_sv"),
 "Prismatic Evolutions Elite Trainer Box": ("pokemon-prismatic-evolutions/elite-trainer-box","sealed_sv"),
 "Prismatic Evolutions Booster Bundle": ("pokemon-prismatic-evolutions/booster-bundle","sealed_sv"),
 "Journey Together Booster Box": ("pokemon-journey-together/booster-box","sealed_sv"),
 "Destined Rivals Booster Box": ("pokemon-destined-rivals/booster-box","sealed_sv"),
 "Destined Rivals Elite Trainer Box": ("pokemon-destined-rivals/elite-trainer-box","sealed_sv"),
 "Mega Evolution Elite Trainer Box": ("pokemon-mega-evolution/elite-trainer-box","sealed_me"),
 "Phantasmal Flames Booster Box": ("pokemon-phantasmal-flames/booster-box","sealed_me"),
 "Base Set Booster Box (1999, unlimited)": ("pokemon-base-set/booster-box","sealed_vintage"),
}
if __name__ == '__main__':
    for label,(slug,seg) in DIRECT.items():
        if res.get(label,{}).get('url'): continue
        url="https://www.pricecharting.com/game/"+slug
        final,body=get(url); time.sleep(1.3)
        if body is None or 'VGPC.chart_data' not in body:
            print('MISS', label, final); res[label]={'seg':seg,'url':None}; continue
        p=parse(body); p['seg']=seg; p['url']=final; res[label]=p
        print(label,'->',p['title'][:60],'| raw',p['prices'].get('used'),'| psa10',p['prices'].get('manual_only'))
    json.dump(res,open('pc/basket.json','w'))
