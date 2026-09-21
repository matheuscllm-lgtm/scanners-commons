# HANDOFF — Outlook Pokémon: modo LOW POP (escassez + demanda medidas, slabs PSA 10)

**Status: ABERTO — PR draft aguardando merge + calibração das faixas** ·
Criado em 2026-09-21 (sessão Claude Code na nuvem) ·
Repo-alvo: `matheuscllm-lgtm/pokemon-longterm-outlook` ·
PR: https://github.com/matheuscllm-lgtm/pokemon-longterm-outlook/pull/27
(branch `claude/gracious-lamport-w3gsp4`, draft, CI a conferir)

> **Para a próxima sessão, em uma frase:** o operador pediu um "scanner do
> eBay de cartas low pop com potencial de chase, só slabs PSA"; a entrevista
> (`grill-me`) mostrou que o alvo real é **melhorar o `pokemon-longterm-outlook`**
> — trocar os dois componentes cegos do score (Supply por idade, Preço por
> faixa) por dois **medidos** (Escassez = nº de PSA 10 no censo, Demanda =
> vendas/mês da PSA 10), com a **fonte sendo o PriceCharting** (não o eBay).
> Isso está implementado, testado e provado ao vivo no PR #27. Falta: merge,
> calibrar as faixas sobre o universo inteiro e responder a pergunta de
> critério de sucesso que ficou em aberto.

## 0. Regras que valem nesta frente (não re-perguntar)

- **Só slabs PSA 10**; **teto US$600 por carta** (vale sobre o PSA 10, não a
  crua); **vintage entra**; entrega = tabela de prioridade no molde do
  outlook, gerada por `run_outlook.py` e colada VERBATIM.
- **Low pop = poucas PSA 10 + demanda observável** (pop baixa sem demanda não
  é escassez — o próprio `LONGO_PRAZO.md` do ebay-scanner registra isso).
- Fonte = **PriceCharting**, página da carta: censo embutido no HTML
  (`VGPC.pop_data`, PSA e CGC por nota 1..10), vendas por nota, mediana,
  preço da crua e **TCGPlayer ID** (chave de join com o tcgcsv). Acessível da
  nuvem, sem navegador, ~3 s/carta. O eBay (painel *Price Guide* / *Pop
  report* no anúncio) tem o mesmo dado mas **bloqueia requisição sem
  navegador** (testado: página de erro) — descartado como fonte.
- Censo do PriceCharting é **mensal**: velocidade de pop exige 2 leituras
  (os campos já vão no snapshot diário do outlook pra isso).
- Invariantes da frota: nunca inventar preço, nunca recomendar compra,
  sem check-in/subscribe de PR (a assinatura automática do #27 foi cancelada).
- Estilo de resposta: teto de 200 palavras de prosa, Objetivo → O que foi
  feito → Dependências. (O skill `grill-me` foi corrigido e re-upado pelo
  operador em 2026-09-21 pra obedecer o teto também na entrevista.)

## 1. O que está no PR #27 (mergeável; 203 testes passando)

| Arquivo | Mudança |
|---|---|
| `outlook/psa10.py` | `parse_pop_report`, `parse_tcgplayer_product_id` (link de afiliado URL-encoded), `parse_raw_price`; `pick_search_result` (página de RESULTADOS: link absoluto, sem `[1st Edition]`/`[Shadowless]` — a página sem colchetes é a unlimited); `fetch_psa10` devolve também `pop_psa/pop_cgc/raw_usd/tcg_product_id`; **cache em disco 1 dia** em `data/cache/pricecharting/` (gitignored) |
| `outlook/scoring.py` | `scarcity_points` (pop de PSA 10, log: ≤50=25 · ≤200=22 · ≤500=18 · ≤2000=12 · ≤10000=7 · else 3), `demand_points` (vendas/mês: ≥30=25 · ≥10=20 · ≥3=14 · ≥1=8 · else 3), `pop_trust_issue` (guards), `apply_lowpop`, `lowpop_pool` (rodízio por era); campos novos em `ScoredCard` (`lowpop`, `pop_psa`, `pop_issue`, `pts_scarcity`, `pts_demand`, propriedades `pop_psa10/pop_total/gem_rate/psa10_premium`) |
| `outlook/tcgcsv_api.py` | `VINTAGE_SETS` (WotC, EX, Diamond & Pearl, HGSS, Black & White, XY, Sun & Moon — mapa explícito por nome, sem kits/POP/decks), `expand_eras` com aliases `vintage` / `all` |
| `run_outlook.py` | `--lowpop`; `--max-price` sobre o PSA 10; pool em rodízio por era **preenchido até N cartas dentro do teto** (orçamento 3×N consultas); só o pool consultado entra no ranking |
| `outlook/report.py` | colunas `Pop PSA10 / total (gem)` e `Prêmio`; balde **"⚠️ Sem censo confiável — validar manualmente"** separado do ranking |
| `outlook/history.py` | campos do modo no snapshot |
| `tests/test_lowpop.py` | 40 testes (parsers com HTML real, faixas, guards, fallbacks, pool, entrega, eras) |
| `CLAUDE.md`, skill `pokemon-longterm` | régua vigente + comando canônico + limitação nº 6 |

**Comando canônico:**
```bash
python run_outlook.py --lowpop --eras all --max-price 600 --graded-pool 300
```

## 2. Achados reais (não re-descobrir)

- **Páginas finas/duplicadas no PriceCharting**: Venusaur 15 (Base Set) com
  censo 4, Blastoise 2 com censo 229 mas 2 PSA 10 e 4,3 vendas/mês, Gardevoir
  ex 233 (Paldean Fates) com censo 2, Mew ex 205 (151) vazia. Guard:
  censo total < 25 **ou** vendas/mês > nº de PSA 10 → "pop não confiável" →
  balde à parte. Sem o guard, a Gardevoir empatava no topo com 87.
- **Pool por score cru sai 100% SV** (Raridade é cega a era: "Holo Rare" de
  1999 = 3 pts, SIR de 2025 = 25). Por isso o rodízio por era.
- **Vintage notório em PSA 10 fica quase todo acima de US$600** (Charizard
  Base 12k, Lugia Neo 32k, Skyridge Charizard 100k; no smoke, 42 de 60
  consultas estouraram o teto). É o mercado, não a régua — o operador decide
  se o teto muda.
- **Auditoria crítica do outlook (2026-09-21)**: a régua antiga nunca foi
  validada como previsão (calibração transversal contra o preço, que é
  componente = circular; backtest sem snapshots); no ebay-scanner a mesma
  heurística deu +0,43 com preço e ~0 com o prêmio da PSA 10. Registrado
  como limitação nº 6 no `CLAUDE.md` do outlook.
- Sonda de 30 cartas (10 vintage / 10 SWSH / 10 SV): 29/30 com censo; tabela
  completa ficou no chat da sessão de origem — reproduzível com o scanner.

## 3. Próximos passos, em ordem

1. **Merge do PR #27** (decisão do operador). Conferir CI (`tests` em 3.11).
2. **Calibrar as faixas** de Escassez/Demanda sobre o universo inteiro: rodar
   o comando canônico (1ª vez ~15 min; depois cache), olhar a distribuição de
   `pop_psa10` e `psa10_sales_per_month` no snapshot (`data/snapshots/`) e
   ajustar `SCARCITY_POP10_BANDS` / `DEMAND_SALES_BANDS` com dado, não de
   cabeça. Documentar a calibração no `CLAUDE.md`.
3. **Prêmio PSA 10 sobre a crua**: hoje é coluna informativa + nota (< 1,5×).
   Decidir com o operador se entra no score (ele definiu demanda = vendas +
   prêmio; ficou fora até calibrar).
4. **Velocidade de pop**: com ≥2 snapshots mensais, Δpop10/mês vira sinal
   (quanto o censo cresce = quanto ainda gradam = pressão de oferta).
5. **Pergunta em aberto pro operador**: critério de sucesso em 6 meses —
   "as cartas do topo subiram de preço" ou outro observável? Sem isso o
   backtest não tem alvo.
6. Pendência herdada do ebay-scanner (`SESSION-HANDOFF.md` lá): o "coletor de
   população PSA" listado como próximo passo **já existe agora** no outlook
   (`psa10.fetch_psa10` traz `pop_psa`); reaproveitar em vez de duplicar.

## 4. Como retomar em 3 comandos

```bash
cd pokemon-longterm-outlook && git fetch origin && git checkout claude/gracious-lamport-w3gsp4
python3 -m pytest tests/ -q                      # 203 passed
python3 run_outlook.py --lowpop --eras "Scarlet & Violet" --top 15 --graded-pool 20 --max-price 600 --no-snapshot
```
