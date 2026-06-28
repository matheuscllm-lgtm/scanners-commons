# HANDOFF — Integração DoubleHolo na frota de scanners

> 🔗 **RECONCILIAÇÃO (2026-06-27, sessão paralela):** existe uma 2ª ferramenta em
> `C:\Users\mathe\doubleholo-scraper\` (HANDOFF.md lá) feita em paralelo. Ela é a
> **fonte canônica de leitura premium**: raspa o **DOM logado** (console F12),
> **sem token**, já validada em 5 cartas. **Isso SUPERA a abordagem API+Bearer-token
> deste tool** (`doubleholo_signals.py`) — o harvest de token é bloqueado pelo
> classificador (corretamente), e o DOM-scrape não precisa de token. 
> **Divisão de trabalho:** premium read = JS DOM-scraper (canônico); este lado Python =
> descoberta headless de `card_id` (Firecrawl) + **glue de pipeline** (juntar sinais
> aos deals dos scanners / ao outlook), a ser moldado quando o caminho for escolhido.
> Os 2 backlogs são os mesmos nos 2 docs: (1) 2ª análise de deals, (2) enriquecer outlook.

**Data:** 2026-06-27 (revisado após investigação ao vivo + reconciliação)
**Status:** PROTÓTIPO parcial. Descoberta de `card_id` FUNCIONA. Leitura premium → usar o DOM-scraper paralelo (a meia-parte API+token deste tool está SUPERADA).
**Origem:** operador tem acesso **premium** ao https://doubleholo.com e quer usá-lo pra melhorar resultados da frota.
**Arquivo do tool:** `~/scanners-commons/tooling/doubleholo_signals.py`

> **CORREÇÃO IMPORTANTE (vs. 1ª versão deste doc):**
> A ideia **NÃO** é tirar preço/ofertas do DoubleHolo. **Preço de referência continua sendo TCGplayer** (inclusive o próprio DoubleHolo só re-exibe comps do TCGplayer na aba "Market Prices").
> O alvo é a **camada de ANÁLISE premium**: gem rate / população PSA, recomendação de grading + ROI, forecast/trend, sentimento (Reddit), supply & demand.

> **Glossário** (pro Matheus, médico não-programador):
> - **Gem rate / gem mint rate** = % das cartas enviadas que voltam PSA 10. É exatamente a "probabilidade de PSA 10" que o scanner PSA usa.
> - **População (pop)** = quantas cartas já foram gradeadas em cada nota (ex.: 392 em PSA 10).
> - **Sentiment** = humor da comunidade (Reddit) sobre a carta — sinal de demanda.
> - **Forecast / trend / RSI** = projeção e indicadores técnicos de para onde o preço vai.
> - **Bearer token / JWT** = uma "senha temporária" que o site usa pra provar que você está logado.

---

## 1. O que o DoubleHolo entrega (e pra quem serve na frota)

| Dado DoubleHolo (premium) | Consumidor na frota | Por que importa |
|---|---|---|
| **Gem rate (% PSA 10) + População** | **psa-arbitrage** | É literalmente o `--psa10-prob` que o psa-agent recebe de fora hoje. Vira input real, não modelado. |
| **Recomendação de grading + ROI** (PSA/BGS/CGC/TAG) | **psa-arbitrage** | Cross-check do EV/ROI que o scanner calcula. |
| **Forecast / trend / RSI** | **pokemon-longterm-outlook** | O `--trend` pendente / 5ª componente do score 0-100. |
| **Reddit sentiment / menções** | outlook + CT chase-tier | Camada de demanda. |
| **Supply & demand (eBay)** | outlook | Pressão de oferta. |

**Preço:** NÃO. Fica no TCGplayer (já resolvido na frota — ver `02-REFERENCIAS-E-FALLBACKS.md`).

---

## 2. Arquitetura descoberta (investigação ao vivo, DevTools da conta premium)

- **API REST limpa:** `https://api.doubleholo.com/api/v1/`
- **Endpoint dos sinais premium:** `GET /premium/grading_roi/card/{card_id}`
  - Devolve o bloco "AI Analysis": grade-rec, melhor grader + ROI, **pop PSA 10**, signal, hold rating.
- **Order book público:** `GET /market/orders?include_filled=false&card_id={card_id}` (não usamos — é preço).
- **Telemetria a ignorar:** `doubleholo.com/api/card-data-v2/*` = PostHog (eventos/flags), não é dado de carta.
- **`card_id`:** descoberto pelo marketplace público (`/marketplace?sets=Pokemon <Set>`) via Firecrawl. **Isto já funciona** no protótipo.
- **Auth:** **Bearer JWT** guardado no lado-cliente. Sem token → `{"error":"auth_token_missing"}`. Cookie sozinho não basta.

**Campos confirmados na UI premium (Pikachu ex Ascended Heroes #276):**
pop PSA 10 = **392** · Grade? **Yes** (BGS 10B: 258% ROI) · Signal **Buy** · Hold **Excellent** · Forecast trend **Rising fast** (RSI 73.79; 7‑14d −5%, 30‑60d +5%, 90d+ +5%) · Reddit **Bullish +35**, 122 menções (14d), trend +8.1 · eBay listings +1%/semana.

---

## 3. Acesso aos dados premium = DOM-scrape (NÃO token)

Decisão consolidada: a leitura premium é feita pelo **DOM-scraper JS**
(`~/doubleholo-scraper/doubleholo_scraper.js`), que lê o **DOM já renderizado na
sua sessão logada** — **sem tocar no token**. Isso evita o harvest de token (que o
guard do Claude bloqueia, corretamente) e não tem JWT pra expirar/copiar.

- A meia-parte API+`DOUBLEHOLO_TOKEN` deste handoff foi **abandonada** (superada).
- ⚠️ **ToS:** é a SUA conta premium. Volume baixo, com cache; confirmar uso aceitável
  antes de automação recorrente (CI).

---

## 4. Estado consolidado (caminho 3 ✅ FEITO)

**Duas peças, uma pipeline:**

| Peça | Onde | Papel | Estado |
|---|---|---|---|
| DOM-scraper JS | `~/doubleholo-scraper/doubleholo_scraper.js` | LEITOR premium (console F12) | ✅ pop **corrigida** (sep. milhar "." + leitura DOM); verificado 138/3392/4.1% |
| Pipeline Python | `~/scanners-commons/tooling/doubleholo_signals.py` | `discover` (card_id via Firecrawl) + `ingest` (JSON→schema canônico) | ✅ testado |

**Schema canônico** (1 registro/carta) — `signals.gem_rate` em FRAÇÃO p/ `psa-arbitrage
--psa10-prob`; `forecast_dir` (buy/sell/neutral) + `best_roi_pct` p/ outlook; flag
`pop_mismatch` (gem exibido ≠ psa10/total).

**Comandos:**
```
python doubleholo_signals.py discover --set "Ascended Heroes" --numbers 276,284
python doubleholo_signals.py ingest dh_card_1513.json
python doubleholo_signals.py ingest doubleholo_5cards.json --json
```
Windows: prefixar `PYTHONIOENCODING=utf-8` (quirk cp1252, ver `windows_python_setup`).

---

## 5. Próximos passos (ordem do operador: 3 ✅ → 2 ✅ → 1)

**Caminho 2 — enriquecer `pokemon-longterm-outlook` ✅ FEITO (como COLUNA, decisão do operador):**
- Não mexe no score 0–100. Adiciona **uma coluna "DH"** = nota 0-100 (50=neutro) que
  avalia os dados Double Holo (forecast + sinal IA + ROI gradação + momentum).
- Calc em `outlook/doubleholo.py` (`dh_score`/`load_signals`/`attach_scores`);
  flag `--doubleholo dh.json` em `run_outlook.py`; coluna em `report.py` (condicional).
- **Join determinístico por productId TCGPlayer** (`tcg_product_id` extraído do
  `reference_url` no pipeline == `card_id` do outlook). Sem matching por nome.
- Testes: `tests/test_doubleholo.py` (12 casos) — suíte 72 passed / 2 skip.
- **DESCOBERTA-CHAVE reusável no caminho 1:** o join é por productId, então o
  matching difuso (nome+set+variante) NÃO é necessário quando a fonte tem o ref TCGplayer.

**Caminho 1 — 2ª análise de deals: IMPLEMENTADO no CardTrader (não commitado), mas join NÃO BINDA ainda.**
- Feito (working tree CT, via card-agent): `doubleholo_join.py` + flag `--doubleholo` + coluna **DH** no XLSX e markdown (2 links/linha preservados). Testes: 12 novos, suíte CT 184 passed. Lê `dh_score` precomputado.
- ⚠️ **BLOQUEIO REAL (corrige suposição anterior):** o CT **NÃO** carrega `tcgplayer.com/product/<id>` na saída real (aquilo veio de FIXTURES de teste). Dados reais:
  - via pokemontcg.io: `Link TCG` = `prices.pokemontcg.io/tcgplayer/{cardId}` (redirect pelo cardId pokemontcg, **sem productId numérico**).
  - via tcgcsv (fallback ME/asc): `last_tcg_url = None` (vazio).
  → join por productId casa ~0 linhas hoje (DH = "—"). Implementação correta/honesta; só falta a chave existir na saída.
- **FIX (1)+(2) IMPLEMENTADOS** (operador aprovou; working tree CT, SEM commit, 195 testes verdes):
  - **Fix(1)** — `TcgCsvFallbackProvider` agora seta `last_tcg_url = tcgplayer.com/product/{productId}` (pid_index paralelo ao de preço, last-wins). Sets ME/asc passam a ter link TCG (tapa furo do contrato) e casam DH. Não toca preço/margem.
  - **Fix(2)** — novo `tcgcsv_productid.py`: resolver OFFLINE de productId p/ linhas pokemontcg (índice tcgcsv `{número→{variante→productId}}` por set, reusa mapas de setcode + lógica de variante + unique-match-only). Anti-invenção: ambíguo → `None` (DH="—"). `--no-pid-resolve` desliga; resolver só roda com `--doubleholo`.
  - `doubleholo_join.attach_scores_df` casa por coluna `tcg_product_id` (fallback: extrai do link).
  - Numa run modern real: 100% das linhas são redirect pokemontcg → **Fix(2) é o que cobre**; Variant preenchida em 100% (desambiguação tem sinal). % exato de resolução não medível offline.
- **DECISÕES PENDENTES do operador (design, itens do card-agent):** (1) `[TCG]` continua apontando p/ prices.pokemontcg.io (fluxo de validação) + coluna nova `tcg_product_id` — OU repontar `[TCG]` p/ tcgplayer.com/product; (2) custo de rede do Fix(2) (só com `--doubleholo`); (3) nada commitado.
- `dh_score` é SINGLE SOURCE no pipeline (`doubleholo_signals.py`); outlook e CT só LEEM.
- **Loop de uso real:** raspar cards no DoubleHolo (DOM-scraper) → `ingest --json` → rodar CT/outlook `--doubleholo <json>` p/ a coluna DH acender.

**Transversal:**
6. [ ] Re-raspar `sample_gym_heroes.json` com o scraper corrigido (atual é pré-fix).
7. [ ] Extrair forecast detalhado + Reddit sentiment no scraper (hoje só `forecast`/AI/ROI/pop).
8. [ ] Confirmar ToS antes de automação recorrente.

**Memórias relacionadas:** `doubleholo_scraper_tool` (leitor JS), `psa_agent_scope_boundary` (PSA consome `--psa10-prob`), `pokemon_longterm_outlook_location` (`--trend` pendente), `feedback_delivery_myp_table_model`, `firecrawl_api_key_setup`, `scanners_commons_folder`, `windows_python_setup`.
