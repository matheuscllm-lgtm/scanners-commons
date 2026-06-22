# 02 — Referência de preço e fallbacks por scanner

"Referência de preço" = o valor de mercado contra o qual o preço de compra é comparado pra calcular a margem. "Fallback" = a fonte secundária quando a principal não tem o dado.

> **Mudança importante (2026-06):** `tcgcsv.com` virou a fonte de **preço real preferida na nuvem**, porque `api.pokemontcg.io` é bloqueado nos servidores do GitHub Actions. MYP migrou (v5.15) e COMC já nasceu assim. Os demais ainda usam pokemontcg.io/PriceCharting — honesto e funcional, mas avaliar migração é backlog.

---

## MYP — `myp-arbitrage-scanner`
- **Compra:** ofertas na MYP Cards (Brasil, R$).
- **Referência (cadeia, flag `--tcg-source`):**
  1. **`tcgcsv.com`** (real) — usado na nuvem (`--tcg-source tcgcsv`). Casa o set por `abbreviation` exata; nome só aceita match ÚNICO (ambíguo → não casa, cai pro fallback). (v5.15)
  2. **`pokemontcg.io`** (real) — secundário, no modo `auto`/local (usa `POKEMONTCG_API_KEY`).
  3. **`.estat-tcg`** = última venda estatística do próprio MYP — **FALLBACK, rotulado como tal**, nunca tratado como real.
- **Honestidade:** portão `_is_real` reconhece `tcgcsv` e `pokemontcg` como reais; `.estat-tcg` fica no balde de fallback. Cada preço leva a etiqueta da origem.
- **Guarda anti-inflação:** sanity via `.estatistica-ultimo` + flag `tcg_suspect`.

## CardTrader — `card-trader-scanner`
- **Compra:** listings no CardTrader (Europa; preço em € convertido, e US$).
- **Referência:** **`pokemontcg.io`** (`POKEMONTCG_API_KEY`), preço *per-expansion* cru **validado per-blueprint** (a versão exata da carta).
- **Fallbacks:** não há fallback de preço; `JustTCG` e `TCGplayer` são **stubs** (não implementados, lançam erro de propósito). Sem PriceCharting.
- **Plano B real = validação:** o guard contra falso positivo é o `validate_per_blueprint` (casa NM + variante exata), não uma 2ª fonte de preço.
- **Cobertura fraca em sets novos** (ponto cego histórico do pokemontcg.io). Avaliar tcgcsv é **backlog**.
- **Guardas anti-inflação:** `_rarity_is_holo` (variante), filtro `TG##` (e `GG##` no pós-processo), cache versionado (`PRICE_LOGIC_VERSION`).

## Liga — `liga-pokemon-scanner`
- **Compra:** ofertas na Liga Pokémon (Brasil, R$), coletadas ao vivo (navegador headful + decodificação de sprite de preço).
- **Referência (cadeia):**
  1. **`pokemontcg.io`** — `tcgplayer.prices.<variante>.market`, prioridade holofoil→normal→reverse, pega o menor market quando ambíguo. ⚠️ **hoje roda ANÔNIMO** (não usa `POKEMONTCG_API_KEY` — limita a taxa de requisições; ligar a chave é melhoria fácil de backlog).
  2. **Sets ME/SV-novos** (que o pokemontcg.io ainda não tem): `resolve_refs.py` → **API do MYP (`tcg_price`)** primeiro → **PriceCharting** como fallback (só pra cartas ≥ R$50 que o MYP não cobre). Cada linha leva a etiqueta da origem (`MYP`/`PriceCharting`).
- **Honestidade:** se não acha preço, deixa `usd=None`/`margin=None`; coletor levanta erro em vez de inventar.

## COMC — `scanner-comc`
- **Compra:** listings no COMC (US, US$), coletados via navegador headful (grátis).
- **Referência:** **`tcgcsv.com` apenas** (alinhado ao canon desde o início).
- **Fallback (dentro do tcgcsv):** campo de preço `market` → `mid` → `low`, e o campo realmente usado é rastreado como `price_field` (vai no CSV/JSON). ⚠️ Hoje a tabela do chat **não** mostra `price_field` — então um deal apoiado em `mid`/`low` (fallback) parece igual a um apoiado em `market` (real). Melhoria de honestidade no backlog: revelar `price_field` no chat.
- Não usa pokemontcg.io nem PriceCharting.

## eBay — `ebay-arbitrage-scanner`
- **Compra:** anúncios no eBay (US, US$) via **eBay Browse API** (grátis).
- **Referência:** **PriceCharting** (scrape público, cache de 24h) — valor justo por raw NM e por nota (graded: PSA 10/9/8…).
- **Fallback:** **nenhum** — se uma nota não tem preço no PriceCharting, o anúncio é **descartado** (não inventa). Não usa tcgcsv/pokemontcg.io (modelo estruturalmente diferente: raw+graded vs PriceCharting).
- **Guarda de honestidade:** "referência desalinhada" — se o valor justo diverge >1,5× ou <0,6× da mediana de ≥3 anúncios eBay limpos, marca **REVISAR** em vez de aprovar.

## Selados — `sealed-arbitrage-scanner`
- **Compra:** Liga / OLX / Amazon BR / Mercado Livre (produtos selados, R$).
- **Referência:** **TCGplayer US** (preço de selado).
- **Fallback / rotas:** OLX tem WAF Cloudflare → rota `firecrawl`; guards FP-safe de referência US; gate de condição selado/usado.
- **Chave:** `FIRECRAWL_API_KEY`.

---

## Resumo (quem usa o quê)

| Scanner | Fonte real principal | Fallback / 2ª fonte | Não-inventa-preço? |
|---|---|---|---|
| MYP | tcgcsv.com | pokemontcg.io → `.estat-tcg` (rotulado) | ✅ |
| CardTrader | pokemontcg.io | — (validação per-blueprint é o guard) | ✅ |
| Liga | pokemontcg.io (anônimo) | MYP API → PriceCharting (sets novos) | ✅ |
| COMC | tcgcsv.com (market) | tcgcsv mid → low | ✅ |
| eBay | PriceCharting | — (descarta se faltar) | ✅ |
| Selados | TCGplayer US | Firecrawl (OLX/WAF) | ✅ |
