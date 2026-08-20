# 📐 Contrato de dados — o que o dashboard pode consumir

**Público:** o GPT que constrói o dashboard integrativo (e qualquer outro
consumidor). **Autoridade:** este arquivo + `schemas/` são a lei do canal; o
código mergeado de cada scanner é a fonte de verdade por trás dele. Divergiu?
o código vence e **este arquivo é corrigido no mesmo PR**.

Última revisão: **2026-08-20** (rodada 2 — mapeamento dos campos pedidos pelo GPT; ver §3.1).

---

## 1. Invariantes — o dashboard NÃO pode violar (não negociável)

Estes são os invariantes da frota (texto canônico no `README.md` deste repo).
Eles não são preferência de UI: são o que impede a ferramenta de mentir.

1. **Margem BRUTA** — `(revenda − compra) / compra`, **sem nenhuma taxa embutida**
   (frete, cartão, IOF são calculados por fora, pelo operador). O dashboard
   **não** pode somar taxa e chamar de margem, nem exibir "margem líquida"
   derivada por conta própria.
2. **Piso R$50 (~US$10) só para SINGLES.** Produtos **selados não têm piso**
   (decisão do operador, 2026-06-27).
3. **Só Near Mint** nos scanners de singles (match EXATO, nunca substring). Em
   selados o equivalente é o gate selado-vs-aberto/usado.
4. **Nunca inventar preço.** Fonte falhou → o campo vem vazio/rotulado como
   fallback, e o dashboard **mostra isso**. Nada de interpolar, estimar ou
   "completar" preço que a fonte não deu.
5. **Nunca recomendar compra.** O dashboard ranqueia, flagea e explica. Não
   existe coluna/botão "COMPRAR" — a decisão de capital é do operador.
6. **Mostrar TODAS as linhas**, não uma amostra curada: aprovadas **e**
   rejeitadas/em revisão, com o motivo visível.
7. **Dois links por linha**, sempre: `[oferta]` (onde comprar) e
   `[TCG]`/`[referência]` (onde validar o preço). URLs vêm do artefato — **nunca
   fabricadas**. Falta uma? a célula mostra só a que existe.
8. **Real vs fallback é explícito.** Toda linha declara a fonte do preço de
   referência (ex.: `real (tcgcsv)` · `real (pokemontcg)` · `fallback
   (.estat-tcg)`), e fallback **nunca** é apresentado como preço real.

> Os invariantes 4, 7 e 8 têm cicatriz: preço estimado tratado como real e alias
> de set deduzido por LLM já produziram margem fantasma na frota. Ver
> `01-ERROS-COMUNS.md`.

---

## 2. Tabela-mãe — o que cada ferramenta produz

| Ferramenta (repo) | O que é | Artefato canônico do resultado | Formato | Threshold | Base da margem |
|---|---|---|---|---|---|
| **integrated-scanner** | orquestrador das 4 fontes de singles (MYP, CT, COMC, Liga) | `outputs/deals_store.json` + **API HTTP** (`api.py`) | JSON | percent inteiro (`30`) | **compra** (recalculada) |
| **myp-arbitrage-scanner** | MYP (BR) vs TCGplayer | XLSX do scan → entrega por `myp_summary.py` | XLSX → markdown | percent inteiro (`30`) | compra |
| **card-trader-scanner** | CardTrader (EU) vs TCGplayer | XLSX do scan → `cardtrader_postprocess.py` | XLSX → markdown | **fração** (`0.30`) | **revenda** ⚠️ |
| **scanner-comc** | COMC vs TCGplayer | `results/comc_deals_<era>_latest.json` (+ `.csv`) → `comc_summary.py` | JSON/CSV → markdown | **fração** (`0.30`) | **revenda** ⚠️ |
| **liga-cards-scanner** | Liga Pokémon (BR) vs TCGplayer | `reports/report_<stamp>.{json,csv,xlsx}` → `build_markdown` | JSON/CSV/XLSX → markdown | percent inteiro (`30`) | compra |
| **ebay-arbitrage-scanner** | eBay (graded + raw opt-in) vs PriceCharting/TCGplayer | `results/last_scan.json` → `ebay_summary.py` | JSON → markdown | percent inteiro (`30`) | compra |
| **sealed-scanner** | selados BR (Liga/OLX/ML/Amazon) vs TCGplayer + ref. eBay | `results/[<jogo>/]unified_*/unified_deals.csv` (+ `run_meta.json`) → `scripts/snapshot.py`; **painel local** (`panel.py`, `/api/*`) | CSV/JSON → markdown | **fração** (`0.30`) | compra |
| **pokemon-longterm-outlook** | triagem de valorização de longo prazo (não é arbitragem) | `outputs/*.md` + snapshots em `data/snapshots/` | markdown/JSON | — (score 0-100) | — |

⚠️ **Duas armadilhas nesta tabela** (as duas já quebraram integração antes):

- **Threshold:** `30` no MYP/Liga/eBay significa 30%; **no CT/COMC/Selados 30
  significa 3.000%** (lá é fração `0.30`). Um dashboard que passe o mesmo número
  para todos gera "zero deals, sem erro nenhum".
- **Base da margem:** CardTrader e COMC dividem pelo preço de **revenda**; os
  demais, pelo de **compra**. Números de fontes diferentes **não são
  comparáveis** enquanto não forem recalculados na mesma base. Quem já resolve
  isso é o `integrated-scanner` (recalcula tudo na base compra) — **por isso ele
  é a fonte recomendada para o dashboard**, e não os XLSX crus de cada scanner.

---

## 3. Feed canônico recomendado: `deals_store.json` (integrated-scanner)

É o **único artefato já unificado** da frota: 4 fontes, mesmas colunas, margem
recalculada na base compra, status honesto por fonte. Schema formal em
`schemas/dashboard-feed.schema.json`; exemplo (dados **fictícios**) em
`exemplos/dashboard-feed.example.json`.

### Envelope

| Campo | Tipo | Significado |
|---|---|---|
| `schema_version` | int | versão do formato (hoje **1**) |
| `generated_utc` | string | `AAAA-MM-DDTHH:MM:SSZ` — quando o store foi gravado |
| `stamp` | string | carimbo do run (usado na cópia histórica) |
| `scope` | array\|string | códigos canônicos de set (`["PRE","SSP"]`) ou `"full"` |
| `fx` | number | câmbio USD→BRL do run |
| `min_margin_pct` | number | corte aplicado, em **percent** |
| `notorious_only` | bool | run filtrado só a Pokémon notórios |
| `deal_count` | int | nº de deals no feed |
| `sources` | array | status honesto por fonte (abaixo) |
| `deals` | array | as linhas (abaixo) |

### `sources[]` — status honesto (o dashboard **deve** exibir)

`source` · `status` (`ok` \| `falhou` \| `timeout` \| `pulado` \| `indisponível`) ·
`detail` · `deals_raw` (lidas da fonte) · `deals_kept` (passaram o corte) ·
`duration_s` · `output_path`.

> Fonte que falhou **não pode sumir** da tela: um painel que mostra só 3 fontes
> quando 4 rodaram sugere "não há deals lá", quando o real é "não sabemos".
> `ok (0 deals)` e `indisponível` são estados **diferentes**.

### `deals[]` — uma linha

| Campo | Tipo | Nota |
|---|---|---|
| `fonte` | string | `MYP` \| `CardTrader` \| `COMC` \| `Liga` |
| `carta` | string | nome da carta |
| `set_name` / `numero` | string | set e nº de coleção (a UI junta em `Carta` = nome + número) |
| `raridade` | string | ⚠️ pouco confiável no MYP (SIR já veio como "Comum") |
| `chase_tier` | string | tier nativo do CardTrader; `""` nas outras fontes |
| `notorio` | string | `"⭐ <nome>"` quando é Pokémon notório; `""` senão. **Informação, não ranking** |
| `compra_brl` / `compra_usd` | number | preço da oferta |
| `fx` | number | câmbio **daquela linha** |
| `ref_brl` / `ref_usd` | number | preço de referência (TCGplayer) |
| `margem_pct` | number | **percent**, base **compra**, bruta |
| `lucro_brl` | number | `ref_brl − compra_brl` |
| `qtd` | int\|null | **`null` = a fonte não informa estoque** (MYP e Liga). Renderizar `—`, nunca `0` |
| `valorizacao` | int\|null | heurística interna; **fora da entrega** por decisão do operador (2026-06-22) |
| `notas` | array\<string\> | flags/limitações da linha — **exibir**, é onde mora o "validar manualmente" |
| `link_oferta` / `link_tcg` | string | os 2 links (invariante 7) |

### 3.1 Mapeamento para o vocabulário do dashboard (rodada 2026-08-20)

O GPT pediu a padronização de um conjunto de campos. Correspondência oficial:

| Vocabulário do dashboard | No feed v1 | Nota |
|---|---|---|
| `run_id` | `stamp` (envelope) | único por run; a cópia histórica usa o mesmo valor |
| `scanner` | `fonte` (por deal) | `MYP` \| `CardTrader` \| `COMC` \| `Liga` |
| `game` / `product_type` | **v1.1** (envelope, opcionais) | este feed é `pokemon`/`single` por construção; selados = feed próprio |
| fórmula da margem / `margin_basis` | contrato §1 + **v1.1** `margin_basis: "compra"` | o validador confere linha a linha |
| condição / idioma | invariantes de admissão + **v1.1** `condition: "NM"`, `language: "EN"` | linha fora de NM+EN nem entra no feed |
| fonte do câmbio | **v1.1** `fx_source` | requer PR no integrated-scanner; ausente = não informado |
| confiança do match | `notas[]` (por deal) | **não existe score numérico unificado e não será fabricado** — COMC tem `confidence` no feed próprio, Liga tem `match_score` fuzzy, MYP/CT não emitem score. Derivável: `precisa_validar` = "validar" ∈ notas |
| status / horário | `sources[].status` / `generated_utc` | já existem |

Os campos **v1.1** estão no schema como **opcionais** (retrocompatível,
`schema_version` continua 1) e só passam a ser gravados quando o PR
correspondente entrar no `integrated-scanner`. Detalhe e racional na mensagem
`mensagens/2026-08-20-frota-para-gpt-campos-padronizados.md`.

### API HTTP (mesma origem, já pronta)

`api.py` (FastAPI) serve o store: `GET /health` · `GET /` · `GET /sets` ·
`GET /sources` · `GET /status` · `GET /deals` (filtros `source`, `set`,
`min_margin`, `notorious`, `q`, `limit` ≤ 2000) · `POST /scan` (dispara run em
background → `job_id`) · `GET /scan/{job_id}`. Swagger em `/docs`.

⚠️ `POST /scan` **não é botão de UI inocente**: COMC e a coleta ao vivo da Liga
abrem **Chrome headful na máquina do operador** e exigem opt-in explícito no
corpo (`allow_comc`, `collect_liga`). Um dashboard remoto não deve oferecer isso
sem deixar a consequência clara.

---

## 4. Fontes fora do store unificado (o que existe hoje)

O `deals_store.json` cobre **singles das 4 fontes**. As demais ferramentas têm
artefato próprio — o dashboard as consome como **feeds separados**, não fingindo
que são a mesma coisa:

- **sealed-scanner** (selados): `unified_deals.csv` + sidecar `run_meta.json`
  (rota compra→venda + idade das referências) por run em
  `results/[<jogo>/]unified_*/`. Buckets **GREEN / YELLOW / RED** (YELLOW **não**
  é faixa de margem: é match ambíguo ou referência velha). Tem **painel local
  read-only** (`panel.py`, `:8078`) com `/api/deals`, `/api/products`,
  `/api/status`, `/api/routes` — servidos pelo **mesmo** agrupador da entrega, então
  os números batem por construção. Perfis por jogo: `?game=pokemon|onepiece`.
  A coluna/link **eBay é informativa e nunca classifica**.
- **ebay-arbitrage-scanner**: `results/last_scan.json` (todas as linhas, incl.
  rejeitadas). Vereditos **OPORTUNIDADE / REVISAR / SUSPEITO / REJEITADO**,
  `score` 0-100, `trust_score` **separado da margem**, `ref_kind`
  (`tcgplayer` \| `pricecharting`). ⚠️ Run degradado (sem chaves) **não grava**
  artefato — preserva o anterior; o dashboard precisa olhar `generated`/idade.
- **scanner-comc**: `results/comc_deals_<era>_latest.json`, com `count` no
  sidecar (é o que distingue `ok (0 deals)` de `indisponível`); flag `validar`
  quando a confiança do match < 0.90 e sufixo `preço:<campo>` quando a
  referência não é `market`.
- **pokemon-longterm-outlook**: **não é arbitragem** — é score 0-100 de
  potencial de longo prazo. Não misturar com margem na mesma coluna nem no mesmo
  ranking. Tendência é **informativa** e não entra no score.

---

## 5. Regras para quem consome (checklist do dashboard)

- [ ] Converteu threshold para a convenção **de cada** scanner antes de disparar scan?
- [ ] Está comparando margens na **mesma base** (compra)?
- [ ] Exibe `fonte do preço` (real vs fallback) em cada linha?
- [ ] Exibe **todas** as linhas, incl. rejeitadas com motivo?
- [ ] Exibe os **2 links** por linha, sem fabricar URL?
- [ ] Exibe `qtd = null` como `—` (e não `0`)?
- [ ] Exibe status de fonte que falhou, em vez de omitir a fonte?
- [ ] Exibe a **idade** do dado (`generated_utc`) — deal envelhece rápido, cópia barata some?
- [ ] Não recomenda compra em lugar nenhum?

## 6. Ingestão no dashboard (`POST /api/ingest`)

O dashboard aceita o `deals_store.json` v1 **inteiro, sem wrapper**, via
`POST /api/ingest` — spec normativa na mensagem
`mensagens/2026-08-20-gpt-para-frota-spec-post-api-ingest.md`, aceite (com 2
mudanças pedidas) em `mensagens/2026-08-20-frota-para-gpt-aceite-api-ingest.md`.
Pontos fixados:

- **Auth:** `Authorization: Bearer <DASHBOARD_SITE_BYPASS_TOKEN>` — o token
  vive SÓ como secret (GitHub Actions/env), nunca em arquivo; registrado no
  `03-CHAVES-API.md`. Setar sem BOM e sanitizar ao ler (family-error nº 1).
- **Idempotência:** reenvio do mesmo `stamp` faz upsert do run.
- **Nunca inventar:** linhas sem `compra_brl > 0` e `ref_brl > 0` não entram;
  URLs copiadas literalmente; `notas[]` preservado sem virar score.
- **Fechado (publicado no dashboard v7, 2026-08-20):** run com `deals: []` é
  aceito (`201`, `imported: 0`, upsert de run/`sources[]`, oportunidades do
  mesmo `stamp` substituídas — inclusive por conjunto vazio); todo `201` traz
  `skipped.linha_invalida` + `skipped.sem_preco_positivo` (descarte nunca
  silencioso); `400 No deals supplied` só para corpo sem a coleção/coleção
  não-array; o antigo `422` foi removido. Formato do `201`:
  `{"imported": N, "skipped": {...}, "runId": "<stamp>", "scanner":
  "integrated-scanner", "schemaVersion": 1}`.
- **Envio:** hoje é manual (`curl` da spec). Automação = backlog: passo
  opcional pós-run no `integrated-scanner` (decisão do operador).

## 7. Como pedir mudança de contrato

Abra uma mensagem em `mensagens/` (template em `mensagens/TEMPLATE.md`) dizendo
**o que falta, para qual tela, e o que o dashboard faria com o campo**. A frota
responde com o campo real do código — ou com o motivo de não existir. Campo
inventado do lado do dashboard vira número errado na tela do operador: **na
dúvida, pergunte em vez de deduzir** (a frota já perdeu dinheiro deduzindo alias
de set com LLM).
