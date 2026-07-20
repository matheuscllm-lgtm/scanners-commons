# HANDOFF — Scanner ONE PIECE (CardTrader → TCGplayer)

**Status:** ✅ **CONCLUÍDO em 2026-07-18** — `op_scanner.py` construído conforme
este handoff, com a aceitação integral cumprida: chave real `onepiece_language`
provada com oferta JP ao vivo, filtro de singles por `collector_number` (+ fix
retroativo v1.1 no `dbs_scanner.py`), 37 testes offline espelhando o dbs, prova
real `--expansions op01` com validação manual das linhas. Mergeado no
card-trader-scanner via **#58** (2026-07-20, empilhado no #57). Primeira
varredura do catálogo completo (93 expansões) entregue em 2026-07-20. Backlog
registrado lá: extrair o núcleo comum `ct_tcg_core.py` (dbs+op). *(O texto
abaixo é o handoff original, preservado como registro.)*

> **Para a próxima sessão (local ou nuvem):** construir o `op_scanner.py` — a
> MESMA coisa que o `dbs_scanner.py` (Dragon Ball, PR #57), porém para o
> **One Piece Card Game**. Pedido do operador em 2026-07-17.
>
> **Onde o código nasce:** no repo `matheuscllm-lgtm/card-trader-scanner`, ao
> lado do `dbs_scanner.py` (lá handoffs são gitignored — por isso este arquivo
> mora AQUI no scanners-commons, o lar de handoffs da frota).
>
> Este arquivo registra tudo que JÁ FOI verificado com dados reais nesta data —
> não re-descubra; valide apenas o que estiver marcado como pendente.

## 0. O que é "a mesma coisa" (modelo pronto: `dbs_scanner.py`)

O scanner de referência está mergindo pelo PR
[#57](https://github.com/matheuscllm-lgtm/card-trader-scanner/pull/57)
(`dbs_scanner.py` + `tests/test_dbs_scanner.py` + seção no CLAUDE.md). Ele já
resolve, TESTADO (34 testes offline, CI verde):

- Ofertas AO VIVO do marketplace CT por expansão (`/marketplace/products?expansion_id=`),
  menor oferta **NM exato** + EN/sem-idioma + não-graded + não-assinada;
- Referência = **TCGplayer market** via tcgcsv.com com cache 20h + data do dump;
- **Join primário** determinístico `blueprint.tcg_player_id == productId`;
- **Join secundário** (nome EXATO normalizado + cauda do número, match ÚNICO,
  só blueprint SEM versão) para blueprints sem `tcg_player_id`;
- Guardas de honestidade: **anti-lixo** (oferta <50% da ref → 🚨 REVISAR) e
  **referência volátil** (market vs menor anúncio >2× em qualquer direção →
  COMPRA rebaixada pra 🚨 REVISAR com motivo na coluna Flag);
- `--threshold` em **FRAÇÃO** com trava (`30` aborta); piso `--min-price-usd 10`;
- Câmbio real (`--fx` ou open.er-api.com) com falha-alta;
- **Parciais cumulativos** a cada expansão (`⏳ PARCIAL — N/M`) + sidecar
  `<out>_semref.csv` (todo blueprint com oferta viva sem referência, com motivo);
- Entrega canônica da frota (🟢 COMPRA / 🚨 REVISAR / 🔎 Quase, 2 links por
  linha, `|` escapado em célula) + CSV completo em `outputs/` (gitignored).

**Receita mínima:** copiar `dbs_scanner.py` → `op_scanner.py` e parametrizar o
que está na seção 1; copiar/adaptar `tests/test_dbs_scanner.py`. Se preferir
extrair um núcleo comum (`ct_tcg_core.py`) para dbs+op, é refactor legítimo —
mas NÃO bloqueie a v1 por isso (registre como backlog).

## 1. IDs e schema — VERIFICADOS via API em 2026-07-17 (não re-descobrir)

| O quê | Valor | Prova |
|---|---|---|
| CT `game_id` One Piece | **15** | 93 expansões; ex.: `op01` = "OP-01: Romance Dawn" (expansion_id 3332), "OP-02: Paramount War", starters `ST-xx`, promos por set |
| tcgcsv categoria | **68** ("One Piece Card Game") | `GET tcgcsv.com/tcgplayer/categories` |
| Raridade no blueprint | `fixed_properties["onepiece_rarity"]` | ex.: "Common", "Alternate Art" |
| Número de coleção | `fixed_properties["collector_number"]` | `OP01-064`; alt arts com sufixo `a`/`b` (`OP01-001a`, `OP01-064b`) |
| Cobertura `tcg_player_id` (OP-01) | **97%** (160/165 blueprints) | join primário deve dominar |
| Singles | `category_id` **192** (2 outliers em 255 no OP-01 — inspecionar: provável DON!!/token) | |
| Selados/acessórios | `category_id` **193/194**, `fixed_properties` **vazio** (sem collector_number) | "Romance Dawn Booster Box" etc. vêm MISTURADOS nos blueprints da expansão |

## 2. Diferenças vs Dragon Ball — as pegadinhas específicas do One Piece

1. **⚠️ Selados misturados nos blueprints (CONFIRMADO no OP-01):** booster box,
   booster e afins vêm como blueprints da expansão. **Filtrar singles por
   `collector_number` presente** (e registrar/contar os pulados). *Nota: essa
   classe vazou no scan DBS — a linha "Collector's Selection Vol.2" apareceu na
   entrega do catálogo completo como se fosse carta. Fix retroativo no
   `dbs_scanner.py` é bem-vindo no mesmo PR do op_scanner.*
2. **⚠️ Versões "Asian"** de selados (tcg_player_id None) — nunca podem casar
   com o catálogo EN; o filtro de singles acima já as elimina (são selados),
   mas fique atento a singles JP/Asian se aparecerem.
3. **⚠️ RISCO ALTO — idioma japonês:** o CT vende MUITO One Piece JP; a
   categoria 68 do tcgcsv é o catálogo **INGLÊS** do TCGplayer. O filtro
   genérico de idioma do dbs_scanner (`qualquer chave contendo "language"` na
   `properties_hash` da oferta ≠ EN → rejeita) deve cobrir — **MAS é aceitação
   OBRIGATÓRIA provar com uma oferta JP real** que a chave existe no game 15
   (esperado: algo como `onepiece_card_language`). Se ofertas OP não carregarem
   chave de idioma, JP vaza pra referência EN e TODA margem sai errada —
   investigar antes de confiar (lição do guard JP do ebay-arbitrage-scanner,
   PR #19 de lá).
4. **Alt arts / Parallel / Manga:** no CT são blueprints separados com `version`
   ('Alternate Art', 'Alternate Art | Fixed Reprint') e número com sufixo —
   o join primário cobre (ex. real: OP01-064b → tcg_player_id 453518). No
   TCGplayer os paralelos são produtos próprios; a escolha de subtipo
   (`pick_subtype`) do dbs deve funcionar sem mudança.
5. **DON!! cards** existem como singles baratos — o piso US$10 já os corta;
   nada a fazer além de conferir que não explodem o semref.

## 3. Invariantes da frota (não negociar)

Margem BRUTA base compra `(TCG_BRL − CT_BRL)/CT_BRL` · threshold **fração**
(0.30) · **NM por match exato** `== "Near Mint"` · graded/assinada nunca ·
**nunca inventar preço** (sem ref → fora com contagem + semref) · **nunca
recomendar compra** · entrega = tabela markdown gerada pela ferramenta, colada
verbatim, TODAS as linhas, `[oferta](CT) · [TCG](tcgplayer)` em toda linha ·
outputs/dados de scan **gitignored** (repo público) · segredo `CT_JWT` via env
var/.env, sanitizado contra BOM/zero-width, nunca versionado/logado.

## 4. Aceitação da v1 (checklist — nada de "verde sem prova")

- [ ] Suíte offline nova (copiar shape do `test_dbs_scanner.py`; ~30 testes) +
      suíte COMPLETA do repo verde com saída colada; CI pytest verde pós-push.
- [ ] Filtro de singles provado (booster box do OP-01 NUNCA vira linha).
- [ ] Filtro JP provado com oferta real (ver item 2.3) — teste offline com a
      chave real de idioma descoberta.
- [ ] Run real `--expansions op01` com contagens plausíveis; validar 2–3 linhas
      manualmente nos links (oferta CT + página TCG, versão certa).
- [ ] Parciais + semref + CSV funcionando; entrega canônica colada no chat.
- [ ] Seção nova no CLAUDE.md (datada) + PR **draft** na branch designada da
      sessão — nunca push direto na `main`; PR #57 como referência de arquitetura.

## 5. Armadilhas operacionais da sessão DBS (pra não pagar de novo)

- `pkill -f "op_scanner"` mata o PRÓPRIO shell se o padrão estiver no comando —
  use colchete: `pkill -f "[o]p_scanner"`.
- Pipe pra `head` num script Python que grava arquivo no fim = SIGPIPE mata o
  script ANTES de gravar — rode sem pipe e filtre depois.
- Runs longos: background gerenciado + monitor por progresso; parcial cumulativo
  já resolve entrega no meio do caminho.
- Cache tcgcsv em `outputs/op_cache/` (TTL 20h) — NÃO reaproveitar o
  `dbs_cache/` (categorias diferentes).
- AwesomeAPI de câmbio estoura cota (429) — open.er-api.com é a primária.
- CT API: 1 chamada de blueprints + 1 de ofertas por expansão, sleep ~0.5s.

## 6. Estado em 2026-07-17 (quem escreve este handoff)

- `dbs_scanner.py` completo na branch `claude/trading-card-inventory-jbzhml`
  (PR #57 draft, CI verde, 243 testes no repo). Catálogo DBS inteiro varrido
  (164 expansões / 13.944 blueprints / 822 avaliadas → 79 COMPRA).
- One Piece: NADA implementado — só as verificações de schema/IDs acima
  (amostra real do OP-01 via API em 2026-07-17).
