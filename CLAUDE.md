# CLAUDE.md — scanners-commons

Instruções para qualquer sessão Claude Code (local ou nuvem) que trabalhe neste repo.

**O que é isto, em uma frase:** o **manual da frota** de scanners de arbitragem de
cartas Pokémon (repo **privado**) — o ponto único de consulta do que se repete entre
os scanners: erros comuns, referências de preço, chaves de API, GitHub Actions,
modelo de entrega e a cópia-mestra do skill `/auto`. **Não é um scanner** — aqui não
se roda scan nenhum; roda-se documentação e o tooling compartilhado.

## Papel deste repo na frota

- Cada scanner carrega no próprio `CLAUDE.md` um bloco **"🛰️ Convenções da frota"**
  (idêntico entre os repos); este manual é a **versão estendida** desses invariantes.
- Hierarquia em conflito: para detalhes de UM scanner, vale o `CLAUDE.md` + código
  daquele repo; para regras **cross-scanner** (margem, entrega, threshold, chaves),
  vale este manual — e mudanças cross-scanner devem ser atualizadas **primeiro aqui**
  e depois replicadas nos blocos dos scanners.
- Cópia-mestra local no PC do operador: `C:\Users\mathe\scanners-commons\` (manter
  espelhada com o GitHub).

## Invariantes da frota (resumo — texto canônico no `README.md`)

- **Margem BRUTA, mínimo 30%** — `(revenda − compra)/compra`, sem taxa embutida.
- **Piso R$50 (~US$10) SÓ para singles** — selados não têm piso (decisão do
  operador, 2026-06-27).
- **Só Near Mint** (match EXATO, nunca substring) · **nunca inventar preço** ·
  **nunca recomendar compra** · **entrega = tabela markdown no chat**, gerada pela
  ferramenta do repo, todas as linhas.
- ⚠️ **Threshold:** inteiro (`30`) = MYP/Liga/eBay; fração (`0.30`) = CT/COMC/Selados.

## Índice dos documentos

| Arquivo | Conteúdo |
|---|---|
| `README.md` | visão geral + tabela-mãe dos scanners + regras de ouro |
| `01-ERROS-COMUNS.md` | os erros que mais se repetem (BOM em chave, squash-merge, billing…) |
| `02-REFERENCIAS-E-FALLBACKS.md` | fonte de preço + fallbacks de cada scanner |
| `03-CHAVES-API.md` | todas as chaves: onde moram (PC × secrets GitHub), como conferir/setar |
| `04-GITHUB-ACTIONS.md` | workflows por scanner (scans só por dispatch manual) |
| `05-MODELO-ENTREGA.md` | o formato padrão da tabela de entrega (estilo MYP) |
| `06-AUTO-SKILL.md` | o que é o comando `/auto` e como manter as cópias em sincronia |
| `HANDOFF-DOUBLEHOLO.md` | handoff da integração DoubleHolo (status: concluído 2026-06-28) |

## ⚠️ Armadilha de nomes: pasta local ≠ repo GitHub

Dois scanners têm nome de pasta local (PC do operador) diferente do repo no GitHub:

| Pasta local (PC) | Repo GitHub (`matheuscllm-lgtm/…`) |
|---|---|
| `liga-pokemon-scanner` | `liga-cards-scanner` |
| `sealed-arbitrage-scanner` | `sealed-scanner` |

Ao editar os documentos: contexto de **GitHub** (secrets, Actions, URLs) usa o nome
do **repo**; contexto de **PC do operador** (caminhos, `sync-auto-skill.sh`) usa o
nome da **pasta local**. O `tooling/sync-auto-skill.sh` usa nomes de pasta local
**de propósito** — não "corrigir".

## Tooling compartilhado (`tooling/`)

- **`auto.md`** — cópia-mestra do skill `/auto` da frota. Editar SEMPRE aqui e
  sincronizar para os repos (no PC do operador, que tem as pastas irmãs):
  ```bash
  bash tooling/sync-auto-skill.sh --check   # dry-run: mostra o que difere
  bash tooling/sync-auto-skill.sh           # aplica nos 8 repos (idempotente)
  ```
- **`doubleholo_signals.py`** — lado Python canônico da integração DoubleHolo
  (subcomandos `discover` e `ingest`). A nota `dh_score` (0-100) é calculada **só
  aqui**; `card-trader-scanner` e `pokemon-longterm-outlook` apenas **leem** o JSON
  gerado (`ingest --json`) — nunca recalculam (evita fórmulas divergindo entre
  repos). Preço de referência continua sendo TCGplayer — este pipeline só trata
  SINAIS. Leitura premium = DOM-scraper JS (`~/doubleholo-scraper/`, PC do
  operador); harvest de token é bloqueado de propósito.
- **`test_doubleholo_signals.py`** — testes do pipeline.
- **`radar-tcg/`** — Radar·TCG (PR #7): painel visual interativo (um único
  `index.html`, sem dependência externa) dos scanners MYP + CardTrader. Monta o
  comando de scan a partir dos 6 grupos canônicos de cada scanner (verbatim das
  skills `scan-myp` / `/scan`), convertendo sozinho a convenção de threshold
  (inteiro no MYP, fração no CardTrader), e importa/filtra o resultado de um scan
  já rodado. Ver `tooling/radar-tcg/README.md`.

## Testes

```bash
cd tooling && python -m pytest test_doubleholo_signals.py -q   # 14 testes, offline
```

## Fluxo de desenvolvimento e segurança

- ⚠️ **Branch padrão deste repo é `master`** (diferente dos scanners, que usam `main`).
- Mudança não-trivial (tooling, reestruturação de doc) segue **branch + PR**; o
  histórico tem commits diretos de docs pequenos no `master`, mas prefira PR.
- **Nunca versionar VALOR de chave.** Este manual fala *sobre* as chaves
  (`03-CHAVES-API.md`) — nomes, onde moram, como setar sem BOM — e jamais contém
  um valor. Repo é privado, mas a regra vale igual.
- Ao registrar decisão nova do operador, sempre com **data** (padrão da frota).
