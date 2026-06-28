# HANDOFF — Integração DoubleHolo na frota (RETOMAR AQUI)

**Última sessão:** 2026-06-28 · **Status:** ✅ **CONCLUÍDO E PUSHADO.** Caminhos 3→2→1 implementados, testados, **revisados (review adversarial + code-review merge gate)**, **MERGEADOS nas defaults** (commons `master`@`628f267`, CT `main`@`9de93f7`, outlook `main`@`3c7d83c`, merge `--no-ff`) e **PUSHADOS pro GitHub**. Feature branches deletadas. Testes verdes: pipeline 14 · outlook 68 · CT 201. (Caminho Python pronto; o que resta são EXPANSÕES — §3.)

> **Sessão 2026-06-28 (ultracode):** rodei uma review adversarial multi-agente do
> SISTEMA inteiro (pipeline+CT+outlook+scraper) — 9 achados brutos, **3 reais
> confirmados** (4 telemetria = falsos-positivos; já cobertos). Implementei os 3
> follow-ups antigos (#3 `_percentish`, #4 gate resolver, #5 telemetria) **e** os
> 3 achados reais da review. Todos test-first. **Testes: pipeline 13 · outlook 68
> · CT 200.** Novos commits abaixo. Detalhe no §4-bis.

> **Em uma frase:** o DoubleHolo (premium) entrega ANÁLISE DE MERCADO (gem rate, população PSA, ROI de gradação, forecast, sinal IA, sentimento) — **não preço** (preço = TCGplayer, já resolvido). Construímos uma coluna "DH" (2ª opinião, nota 0-100) no `pokemon-longterm-outlook` e no `card-trader-scanner`, alimentada por um pipeline canônico, com join determinístico por **productId do TCGplayer**.

---

## 0. O que está PRONTO (commitado em branch, sem push)

| Repo | Branch | Commit | O quê |
|---|---|---|---|
| `scanners-commons` | `feat/doubleholo-integration` | `bc3a50d` | pipeline `tooling/doubleholo_signals.py` (discover+ingest, `dh_score` SINGLE SOURCE), testes, este handoff. **2026-06-28:** dh_score exige sinal premium + `_percentish` + flag ref-url genérica |
| `pokemon-longterm-outlook` | `feat/doubleholo-dh-column` | `6b26c93` | coluna DH via `--doubleholo`; `outlook/doubleholo.py`; testes (review 2026-06-28 = SEM bug, nada a mudar) |
| `card-trader-scanner` | `feat/doubleholo-dh-column` | `ed61a2c` | coluna DH + resolver productId (Fix 1/2); `doubleholo_join.py`, `tcgcsv_productid.py`; testes. **2026-06-28:** `resolve_mask` gate (deals+near-miss) + telemetria |

**Testes (todos verdes):** pipeline **13** · outlook **68** · CardTrader **200**.
**Rodar:** `cd <repo> && PYTHONIOENCODING=utf-8 .venv\Scripts\python.exe -m pytest tests/ -q` (no scanners-commons: `cd tooling && python -m pytest test_doubleholo_signals.py -q`).

**A 4ª peça (NÃO commitada, fica local):** o **DOM-scraper** em `~/doubleholo-scraper/doubleholo_scraper.js` — leitor premium que raspa o DOM logado (sem token). Ver `~/doubleholo-scraper/HANDOFF.md`. **2026-06-28:** `referenceUrl` agora PREFERE `tcgplayer.com/product/` (fallback genérico) — não dropa mais a chave de join caladamente. Edição local (repo não-git).

---

## 1. Arquitetura (as 4 peças e como se ligam)

```
[1] DOM-scraper JS (~/doubleholo-scraper/)   →  lê o DOM premium logado (F12), SEM token
        ↓ baixa JSON cru {cardId,name,number,marketPrice,referenceUrl,premium{...}}
[2] pipeline (scanners-commons/tooling/doubleholo_signals.py)
        ingest --json  →  registro CANÔNICO: {tcg_product_id, dh_score, signals{...}}
        ↓ (dh_score calculado AQUI, single source)
[3] outlook / [4] CardTrader   →  --doubleholo <json>  →  coluna DH
        join por productId TCGplayer (tcg_product_id == card_id no outlook /
        == productId da linha no CT). Determinístico, sem casar por nome.
```

**Decisões de design travadas:**
- **Preço = TCGplayer.** DoubleHolo NÃO é fonte de preço. O `[TCG]` continua apontando pro `prices.pokemontcg.io` (fluxo de validação do operador) — **opção B confirmada**; productId fica só na coluna própria `tcg_product_id` pro join.
- **`dh_score` é SINGLE SOURCE no pipeline** (emitido no JSON). Outlook e CT só LEEM (não há fórmula duplicada — removida na revisão).
- **Coluna DH NÃO entra no score/margem/decisão.** É 2ª opinião à parte. Rodapé sempre diz "não é conselho de compra".
- **Anti-invenção:** sem productId resolvido → DH "—". Nunca chuta.

### Fórmula `dh_score` (0-100, 50=neutro) — em `doubleholo_signals.py`
```
base 50
+ forecast_dir : buy +20 · sell -20 · neutral 0
+ ai_signal    : Buy +12 · Sell -12 · Hold 0
+ ai_grade     : Yes +8 · Maybe +4
+ best_roi_pct : ≥300 +10 · ≥150 +7 · ≥50 +4
+ price_change : ≥+10% +8 · >0 +4 · ≤-10% -8 · <0 -4
→ clamp 0-100. Sem sinal utilizável → None ("—").
```

---

## 2. Loop de uso REAL (como acender a coluna DH)

1. **Raspar** os cards no DoubleHolo logado (Chrome): abrir `/card/<id>`, F12 → Console → colar `doubleholo_scraper.js` → `await dhCard()` por card (ou navegar e rodar a extração; ver snippet no §6). Junta num JSON array.
2. **Ingest:** `cd ~/scanners-commons/tooling && python doubleholo_signals.py ingest raw.json --json > canon.json`
3. **Rodar com a coluna DH:**
   - Outlook: `.venv\Scripts\python.exe run_outlook.py --eras "Mega Evolution" --doubleholo canon.json --max-price 2000` (⚠ join SÓ funciona com `--source tcgcsv`, o default).
   - CardTrader: `cardtrader_postprocess.py --input scan.xlsx --output rel.xlsx --doubleholo canon.json`

**Validação feita (2026-06-27):** 3 cards reais de Ascended Heroes (Pikachu #276 DH=85, Mega Gengar #284 DH=100, Lillie's Clefairy #280 DH=100) casaram 3/3 por productId no outlook; cards-irmãos (#277, #269) ficaram "—" corretamente (precisão do join). Artefatos: `~/.claude/jobs/<job>/tmp/dh_ascended_{raw,canon}.json` (efêmeros).

---

## 3. PRÓXIMOS PASSOS (o que falta)

**Imediato:**
1. [x] **MERGEADO + PUSHADO 2026-06-28** (merge `--no-ff` nas defaults, push pro GitHub público, feature branches deletadas). Fluxo de integração encerrado.
2. [ ] **Cobertura real do join no CT:** numa run modern, 100% das linhas vêm via pokemontcg (redirect, sem productId) → dependem do **resolver offline Fix(2)**. Falta medir a % real de resolução numa run ao vivo (precisa chamada tcgcsv online). Os sets de fallback tcgcsv (ME/asc) casam direto via Fix(1).

**Follow-ups menores — TODOS RESOLVIDOS em 2026-06-28:**
3. [x] `_pct` exige `%` literal → criado `_percentish` (aceita número puro p/ campos %, rejeita cifrão).
4. [x] `attach_product_ids` roda I/O em linhas NÃO no `--all-sets` → `resolve_mask` gateia o resolver OFFLINE pras linhas da entrega (deals OU near-miss); Fix(1) sem I/O segue p/ todas.
5. [x] contagem "N casaram" inclui `dh_score=None` → telemetria separa "casaram" de "com nota DH".

**Expansões possíveis (caminho 1 além do CT):**
6. [ ] Levar a coluna DH a outros scanners (MYP/Liga/integrated). MYP/Liga hoje só têm redirect `prices.pokemontcg.io/tcgplayer/{cardId}` (sem productId) → precisariam da mesma ponte tcgcsv (cardId→productId) que o CT já tem em `tcgcsv_productid.py`.
7. [ ] Alimentar o **psa-arbitrage** com o `gem_rate` (= `--psa10-prob`) — o uso original mais valioso pro PSA. O pipeline já entrega `signals.gem_rate` (fração). Falta o adapter no psa-agent (ver `psa_agent_scope_boundary`).
8. [ ] Extrair mais sinais no scraper: forecast detalhado (7-14/30-60/90d, RSI), Reddit sentiment (Bullish +35, menções), supply&demand eBay — hoje só pega forecast direcional/AI/ROI/pop.

---

## 4. APRENDIZADOS-CHAVE (não repetir / não re-descobrir)

- **Acesso premium = DOM-scrape, NUNCA harvest de token.** A API `api.doubleholo.com/api/v1/` usa Bearer JWT; tentar extrair o token do localStorage é **bloqueado pelo classificador (corretamente)**. O DOM-scraper lê a tela renderizada da sessão logada — não precisa de token.
- **População PSA: `.` é separador de MILHAR** no site (`3.392` = 3392). Ler a GRADE do DOM (rótulo→valor irmão), não regex de innerText. (Bug já corrigido no scraper.)
- **Join SÓ por productId** (determinístico). productId vem do `reference_url` do DoubleHolo (`tcgplayer.com/product/<id>`) == `card_id` do outlook (fonte tcgcsv) / coluna `tcg_product_id` no CT. **Nunca casar por nome** (irmãos #276 vs #277 colidiriam).
- **CT real NÃO tinha productId na saída** (era suposição de fixtures): pokemontcg → redirect sem id; tcgcsv → vazio. Fix(1) (tcgcsv emite product URL) + Fix(2) (resolver offline pokemontcg) resolveram. productId é **só identidade p/ link/join — nunca toca preço/margem**.
- **Achado de review #2 era falso-positivo:** `_pid_index` e `_set_index` são last-wins na MESMA iteração → o `[TCG]` aponta sempre pro produto precificado. Não "consertar".
- **Windows cp1252:** todo entry-point que imprime não-ascii (⚠/→/emoji) precisa do guard `sys.stdout.reconfigure(utf-8)` (ver `windows_python_setup`).
- **Outlook join só com `--source tcgcsv`** (lá `card_id`=productId). Com `--source ptcg` o id é `sv1-25` → casa 0 (agora avisa).

---

## 4-bis. Review adversarial multi-agente (2026-06-28) — 3 achados REAIS corrigidos

Revisão do SISTEMA (não só do diff) com 4 revisores + verificação adversarial. 9 brutos → 3 reais:

1. **[MEDIO] `dh_score` de momentum PÚBLICO sozinho** (achado nº1, 2 revisores). `price_change_pct`
   é lido FORA do bloco premium do scraper (existe deslogado). O guard antigo só dava None se
   `mom` também fosse None → uma carta com `premiumRendered=false` ganhava nota "premium" fake
   (ex.: 58) **E** a flag "premium NÃO renderizou" ao mesmo tempo (contradição). **Fix:** `dh_score`
   exige ≥1 sinal PREMIUM (forecast/ai_signal/ai_grade/best_roi); momentum só MODIFICA. Cinto-e-
   suspensório: `normalize_record` força `None` se `premiumRendered=false`.
2. **[BAIXO] scraper `referenceUrl` pegava 1º link tcgplayer sem exigir `/product/`** → um link
   genérico (busca/parceiro/rodapé) antes do de produto dropava a chave de join caladamente.
   **Fix:** prefere `tcgplayer.com/product/`, fallback genérico. + flag no pipeline quando ref-url
   presente mas sem productId (fecha o gap de telemetria silenciosa).
3. **[BAIXO] gate do #4 apagava DH no near-miss** — sem nenhum deal, `deal_mask` ficava toda False,
   o resolver rodava em 0 linhas e a tabela near-miss entregue perdia a coluna DH. **Fix:**
   `_delivery_resolve_mask` cobre deals OU (sem deal) os top_md near-miss. All Listings (XLSX) fica
   best-effort por design (DH = 2ª opinião de DEAL, não de listing rejeitado).

**4 falsos-positivos** (telemetria "N casaram" inflada): refutados — a contagem já é honesta
(`matched` vs `scored` no CT; "por productId" explícito no outlook). NÃO mexer.

**Não-bug confirmado:** `discover_set` regex slugful está CERTO (URLs reais do DoubleHolo têm slug
com número no fim, ex. `/card/52333/pikachu-ex-pokemon-ascended-heroes-276`).

## 5. Estado por caminho (resumo)

- **Caminho 3 (consolidar)** ✅ pipeline único, pop fix, `dh_score` single-source, `pop_mismatch`.
- **Caminho 2 (outlook)** ✅ coluna DH; validado com dado real ME.
- **Caminho 1 (deals/CT)** ✅ coluna DH + Fix(1)/(2); falta medir cobertura real + decidir push/PR.

---

## 6. Snippet de extração (cola no Console F12 da página /card/<id>, devolve JSON cru)

> Versão com o fix da população (DOM-anchored). Use `JSON.stringify(o)` no fim. O `doubleholo_scraper.js` completo (com `dhCard()`/`dhSetLinks()`/download) está em `~/doubleholo-scraper/`.

Campos do JSON cru que o `ingest` consome: `cardId, name, set, number, marketPrice, priceChangePct, offerUrl, referenceUrl, premium{psa10,totalGraded,gemRate,bestROI,forecast,aiGrade,aiSignal}, premiumRendered`.

---

## 7. Memórias relacionadas
`doubleholo_scraper_tool` (leitor JS) · `pokemon_longterm_outlook_location` · `psa_agent_scope_boundary` (gem_rate→--psa10-prob) · `feedback_delivery_myp_table_model` (2 links/linha) · `firecrawl_api_key_setup` · `scanners_commons_folder` · `windows_python_setup` · `cardtrader_scanner_location`.
