# 02 — Referência de preço e fallbacks por scanner

"Referência de preço" = o valor de mercado contra o qual o preço de compra é comparado pra calcular a margem. "Fallback" = a fonte secundária quando a principal não tem o dado.

> **Mudança importante (2026-06):** `tcgcsv.com` virou a fonte de **preço real preferida na nuvem**, porque `api.pokemontcg.io` é bloqueado nos servidores do GitHub Actions. MYP migrou (v5.15; v5.16 ampliou o mapa de sets 26→106) e COMC já nasceu assim. O CardTrader passou a usar `tcgcsv.com` como **fallback** (v2.23) pros sets que a pokemontcg.io não precifica. Os demais (Liga/eBay/Selados) ainda usam pokemontcg.io/PriceCharting/TCGplayer — honesto e funcional; avaliar migração é backlog.

---

## MYP — `myp-arbitrage-scanner`
- **Compra:** ofertas na MYP Cards (Brasil, R$).
- **Referência (cadeia, flag `--tcg-source`):**
  1. **`tcgcsv.com`** (real) — usado na nuvem (`--tcg-source tcgcsv`). Casa o set por `abbreviation` exata; nome só aceita match ÚNICO (ambíguo → não casa, cai pro fallback). (v5.15; mapa ampliado na v5.16)
  2. **`pokemontcg.io`** (real) — secundário, no modo `auto`/local (usa `POKEMONTCG_API_KEY`).
  3. **`.estat-tcg`** = última venda estatística do próprio MYP — **FALLBACK, rotulado como tal**, nunca tratado como real.
- **Honestidade:** portão `_is_real` reconhece `tcgcsv` e `pokemontcg` como reais; `.estat-tcg`/`myp_estat` fica no balde de fallback. Cada preço leva a etiqueta da origem (coluna "TCG Source"). Deal apoiado em fallback sai do balde "limpos" pra um balde dedicado (v5.14.3).
- **Guarda anti-inflação:** sanity via `.estatistica-ultimo` + flag `tcg_suspect` (boundary inclusivo `>=`, pega exatamente-10×, v5.14.4).

## CardTrader — `card-trader-scanner`
- **Compra:** listings no CardTrader (Europa; preço em € convertido, e US$).
- **Referência:** **`pokemontcg.io`** (`POKEMONTCG_API_KEY`), preço *per-expansion* cru **validado per-blueprint** (a versão exata da carta).
- **Fallback (v2.23):** **`tcgcsv.com`** — entra SÓ quando a pokemontcg.io não dá NENHUM preço no set inteiro (`set_tcg_hits == 0`), exatamente o caso de sets que ela lista mas não precifica (ex.: `asc`/Ascended Heroes, que sem isso cairia na skip-list e ficaria invisível). Resolução de set é *unique-match-only* (abbr exata; ambíguo → pula o fallback). O preço por carta reusa a MESMA escada de seleção de variante (`select_tcgplayer_variant_price`), **não** colapsa pro subtype mais barato. A fonte é rotulada (`price_source` / coluna `Fonte Preço`). Desliga com `--no-tcgcsv-fallback`. `JustTCG`/`TCGplayer` continuam sendo **stubs** (não implementados). Sem PriceCharting.
- **Plano B real = validação:** o guard contra falso positivo continua sendo o `validate_per_blueprint` (casa NM + variante exata) — o tcgcsv preenche cobertura, não substitui a validação.
- **Guardas anti-inflação:** `_rarity_is_holo` (variante), filtro Trainer/Galarian Gallery **em scan time** (regex `^(?:TG|GG)\d+` — antes só TG##), cache versionado (`PRICE_LOGIC_VERSION`).

## Liga — `liga-pokemon-scanner`
- **Compra:** ofertas na Liga Pokémon (Brasil, R$), coletadas ao vivo (navegador headful + decodificação de sprite de preço).
- **Referência (cadeia):**
  1. **`pokemontcg.io`** — `tcgplayer.prices.<variante>.market`. Varre TODAS as variantes presentes (holofoil, normal, reverseHolofoil…) e escolhe a de **MENOR market** (escolha conservadora anti-inflação; assume que o vendedor da Liga lista a versão regular barata, não a alt art cara). **Usa `POKEMONTCG_API_KEY` quando presente** (header `X-Api-Key`, sobe o limite de requisições); sem a chave, segue anônimo.
  2. **Sets ME/SV-novos** (que o pokemontcg.io ainda não tem): `resolve_refs.py` → **API do MYP (`tcg_price`)** primeiro → **PriceCharting** como fallback (só pra cartas ≥ R$50 que o MYP não cobre). Cada linha leva a etiqueta da origem (`MYP`/`PriceCharting`).
- **Honestidade:** se não acha preço, deixa `usd=None`/`margin=None`; coletor levanta erro em vez de inventar.

## COMC — `scanner-comc`
- **Compra:** listings no COMC (US, US$), coletados via navegador headful (grátis).
- **Referência:** **`tcgcsv.com`** (primário; campo de preço `market` → `mid` → `low`, rastreado em `price_field`).
- **Fallback (TCGdex):** se o tcgcsv cair (erro) ou vier vazio num set, o scanner degrada pro **TCGdex** (`tcgdex_client.py`) — que serve o **MESMO `marketPrice` do TCGplayer**, casado pelo MESMO `productId` (não é preço inventado nem estimativa; é outro espelho da mesma fonte). É fallback de emergência (1 request/carta → lento); liga sozinho só na falha do tcgcsv, por set; desliga com `TCGDEX_FALLBACK=0`. Se nenhuma das duas fontes precificar o set, o set é pulado (nunca inventa).
- **Honestidade no chat:** a tabela marca `· preço:<campo>` nas linhas apoiadas em `mid`/`low` (fallback dentro do tcgcsv) — uma linha de fallback fica visualmente diferente de uma apoiada em `market` real. Linhas `market` ficam limpas.
- Não usa pokemontcg.io nem PriceCharting.

## eBay — `ebay-arbitrage-scanner`
- **Compra:** anúncios no eBay (US, US$) via **eBay Browse API** (grátis).
- **Referência:** **PriceCharting** (scrape público, cache de 24h) — valor justo por raw NM e por nota (graded: PSA 10/9/8…).
- **Fallback:** **nenhum** — se uma nota não tem preço no PriceCharting, o anúncio é **descartado** (não inventa). Não usa tcgcsv/pokemontcg.io (modelo estruturalmente diferente: raw+graded vs PriceCharting).
- **Guarda de honestidade:** "referência desalinhada" — comparando o valor justo com a mediana de ≥3 anúncios eBay limpos da mesma nota: se o justo for >1,5× a mediana, marca **REVISAR** (referência possivelmente inflada); se for <0,6×, adiciona flag (referência possivelmente defasada pra baixo).

## Selados — `sealed-arbitrage-scanner`
- **Compra:** Liga / OLX / Amazon BR / Mercado Livre (produtos selados, R$).
- **Referência:** **TCGplayer US** (preço Market do selado, obtido via espelho `tcgcsv.com`).
- **Fallback / rotas:** OLX tem WAF Cloudflare → modo `firecrawl` (`config.olx.mode`, default `urllib`); guards FP-safe de referência US; gate de condição selado/usado.
- **Chave:** `FIRECRAWL_API_KEY`.

---

## Resumo (quem usa o quê)

| Scanner | Fonte real principal | Fallback / 2ª fonte | Não-inventa-preço? |
|---|---|---|---|
| MYP | tcgcsv.com | pokemontcg.io → `.estat-tcg` (rotulado) | ✅ |
| CardTrader | pokemontcg.io (validação per-blueprint) | tcgcsv.com (só em set 0-cobertura; mesma seleção de variante) | ✅ |
| Liga | pokemontcg.io (usa a key se houver) | MYP API → PriceCharting (sets novos) | ✅ |
| COMC | tcgcsv.com (market→mid→low) | TCGdex (mesmo marketPrice TCGplayer, por set, na falha) | ✅ |
| eBay | PriceCharting | — (descarta se faltar) | ✅ |
| Selados | TCGplayer US (via tcgcsv.com) | Firecrawl (OLX/WAF) | ✅ |
