# HANDOFF — CardTrader: instabilidade da fonte de preço (pokemontcg.io) e proposta de fonte alternativa

**Status: ABERTO** · Criado em 2026-08-22 (sessão Claude Code na nuvem) ·
Repo-alvo: `matheuscllm-lgtm/card-trader-scanner`

> **Para a próxima sessão, em uma frase:** um scan `/scan` do grupo G6 foi
> pausado no meio porque a **pokemontcg.io** (fonte primária de preço de
> referência do CardTrader scanner) entrou em instabilidade (erros 500/502 em
> ~80% das requisições), e o operador pediu para **buscarmos outra fonte de
> referência de preço** — a proposta técnica já mapeada é expor o
> `tcgcsv.com` (que JÁ existe no código como fallback) como **provider
> primário selecionável** (`--provider tcgcsv`), seguindo o precedente do MYP
> v5.15. Nada foi implementado ainda; a decisão de caminho está com o operador.

---

## 1. O que aconteceu (cronologia da sessão de 2026-08-22, horários UTC)

1. Operador acionou `/scan`; escolheu rodar **só o G6** (EX inicial + e-Card +
   WotC, 22 sets) via AskUserQuestion. Grupos 1–5 ficaram de fora por escolha.
2. **Pré-voo:** `CT_JWT` presente e limpo (sem BOM, len 619).
   `POKEMONTCG_API_KEY` **ausente do environment de nuvem** (é opcional; o
   operador perguntou o que era — foi explicado: chave grátis em
   dev.pokemontcg.io, só acelera; para persistir, configurar como env var do
   environment em code.claude.com).
3. **20:40** — G6 lançado com os valores canônicos do skill
   (`--threshold 0.30 --validate-top 30 --min-net-margin 0.20
   --max-consecutive-misses 40`), output
   `outputs/scan_g6_20260822_2040.xlsx`. Gotcha operacional registrado: em
   clone limpo a pasta `outputs/` não existe e o redirect de log em background
   falhou → relançado com `mkdir -p` + caminhos absolutos (o `write_xlsx` do
   scanner já garante o diretório, mas o redirect do shell não).
4. **20:49** — `bs` (Base Set) estourou o per-set-timeout de 8 min com só
   **36/133 listings precificados** → skip-list
   (`per_set_timeout_480s_at_36_of_133`).
5. **20:57** — `ju` (Jungle) idem: **88/131** em 8,3 min → skip-list.
6. **Diagnóstico da causa raiz:** NÃO era throttle por falta da
   `POKEMONTCG_API_KEY`. O log mostrou **58× HTTP 500 + 30× HTTP 502** da
   pokemontcg.io em 17 min ("transiente", com retry/backoff de até 30s — é o
   backoff que come o orçamento de 8 min do set). Sonda direta confirmou:
   4 de 5 requisições a `api.pokemontcg.io/v2/cards` falhavam com 500.
   **Era instabilidade do servidor DELES** — uma API key não resolveria.
7. **~20:58** — scan **pausado de propósito** (matar o processo) para não
   gastar ~3h entregando cobertura parcial em 22 sets. Regra da frota
   respeitada: nunca inventar preço; melhor esperar a fonte real.
8. Um vigia (poll de saúde a cada 5 min) detectou a **recuperação da API às
   ~21:10** (4/5 sondas OK).
9. **Direção do operador (2026-08-22):** *"então vamos buscar outro lugar
   para referência de preço"*. Em seguida pediu este handoff em vez de
   decidir na hora entre re-rodar / implementar — **a decisão de caminho
   segue em aberto**.

## 2. Estado que a próxima sessão herda

- **Nenhum scan entregue**: o G6 não terminou; nenhum postprocess foi rodado.
- **Skip-list do scanner contém `bs` e `ju`** (motivo: timeout durante a
  queda). Um re-scan do G6 precisa de `--ignore-skip-list` (flag existente)
  para reprocessá-los — senão saem pulados sem culpa deles.
- Artefatos parciais locais da sessão de 22/08 (gitignored, só existiam no
  container efêmero — provavelmente já não existem): `outputs/scan_g6_*.xlsx`
  parcial + `.checkpoint.jsonl` + log. Nada disso é confiável para entrega.
- `POKEMONTCG_API_KEY` continua fora do environment de nuvem (pendência de
  qualidade de vida, não causa deste incidente).

## 3. O problema de fundo (o que o operador quer resolver)

O scanner do CardTrader depende da **pokemontcg.io como fonte primária** de
preço por listing. Quando ela degrada (500/502 intermitente), o run inteiro
degrada junto: cada set estoura o timeout com preço parcial e cai na
skip-list. O fallback `tcgcsv.com` (v2.23) **não cobre esse cenário**: pelos
gatilhos atuais, ele só entra quando a pokemontcg.io devolve **zero preço para
o set inteiro** (caso `asc`) ou via cap de misses consecutivos — erros 500
intermitentes com retry não disparam nenhum dos dois.

## 4. Proposta técnica já mapeada (NÃO implementada — precisa de decisão)

**Expor o tcgcsv.com como provider primário selecionável:** `--provider
tcgcsv` no `cardtrader_scanner.py`.

Fatos verificados no código em 2026-08-22 que tornam isso barato:

- Existe a abstração `PricingProvider` ("trocar fonte = trocar 1 classe",
  linha ~1158) e o dict `PROVIDERS` (linha ~2151) hoje com: `pokemontcg`
  (default), `justtcg` (stub PAGO, `NotImplementedError` — não serve),
  `tcgplayer` (stub; API oficial fechada para novos devs — não serve).
- A classe **`TcgCsvFallbackProvider` já existe e funciona** (linha ~1923):
  carrega o set inteiro em bulk (`/{groupId}/products` + `/prices`), usa a
  **mesma escada de variante** da pokemontcg.io
  (`select_tcgplayer_variant_price` — nunca colapsa pro subtype mais barato),
  rotula `price_source="tcgcsv"` e desde v2.25 resolve productId para o link
  TCGplayer real. Falta "promovê-la" a opção de provider primário no CLI.
- **Precedente da frota:** MYP v5.15+ usa tcgcsv como fonte do CI
  (divergência comprovada de 0–0,3% vs pokemontcg.io; é o MESMO preço
  TCGplayer). dbs/op/comc/sealed também usam tcgcsv. Fonte gratuita, sem key.

Cuidados obrigatórios se implementar (invariantes do repo/frota):

- **Branch + PR, nunca push direto na `main`**; testes verdes
  (`python -m pytest`, 281 testes) antes do PR.
- **Não mudar o default**: `--provider pokemontcg` continua o default e o
  skill `/scan` continua com os comandos canônicos inalterados (mudança de
  flag canônica = decisão explícita do operador, travada em
  `tests/test_scan_skill_profiles.py`).
- Manter fidelidade de variante, rotulagem `price_source`/coluna `Fonte
  Preço`, contrato de 2 links e a validação per-blueprint (`--validate-top`)
  — o guard final continua valendo.
- Sets vintage no tcgcsv: conferir cobertura de groupId dos sets WotC/EX
  (G5/G6) antes de prometer que o G6 roda 100% via tcgcsv — o mapa de
  resolução de set é unique-match-only e pode não cobrir tudo; o que não
  resolver deve sair rotulado sem preço, nunca inventado.
- Alternativa menor (se o operador preferir não mexer em provider): gatilho
  novo no fallback por **taxa de erro 5xx** (ex.: set com >N falhas 5xx
  aciona o resgate tcgcsv) — mais cirúrgico, porém mais acoplado ao loop de
  pricing. A opção `--provider tcgcsv` é mais simples e mais previsível.

## 5. Próximos passos sugeridos (a decisão é do operador)

1. **Decidir o caminho**: (a) só re-rodar o G6 canônico (pokemontcg.io já se
   recuperou); (b) implementar `--provider tcgcsv` via PR e depois scanar;
   (c) os dois em paralelo (scan agora + PR em seguida).
2. Se re-rodar o G6: comando canônico do skill `/scan` **+
   `--ignore-skip-list`** (para reprocessar `bs`/`ju`), novo stamp no
   `--output`, em background com monitor. Lembrete honesto: WotC/EX é
   mercado eficiente — pode legitimamente vir 0 deal (auditoria SWSH
   2026-06-08 deu 0), e a entrega near-miss do postprocess cobre isso.
3. Se implementar: seguir §4; smoke sugerido = 1 set pequeno via
   `--provider tcgcsv --dry-run`/set único antes do G6 completo.
4. Qualidade de vida: operador configurar `POKEMONTCG_API_KEY` no
   environment de nuvem (code.claude.com) — elimina o throttle em dias
   normais (não relacionado ao incidente 500/502).

## 6. Referências rápidas

- Skill do scan: `card-trader-scanner/.claude/commands/scan.md` (G6 = `exma
  dr ss rs skg aq ex lc si n4 n3 n2 n1 g2 g1 tr b2 fo ju bs wiz bog`).
- Fallback tcgcsv e gotchas: `card-trader-scanner/CLAUDE.md` (seções "Como
  rodar" e histórico v2.23/v2.25).
- Referências e fallbacks da frota: `02-REFERENCIAS-E-FALLBACKS.md` deste
  repo.
