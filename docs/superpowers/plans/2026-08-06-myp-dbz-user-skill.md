# Skill user-level `myp-dbz-scan` + refit `myp-scan` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar o skill user-level `myp-dbz-scan` (wrapper fino do skill canônico `scan-myp-dbz` do repo) e reescrever o `myp-scan` Pokémon no mesmo padrão, curando o drift 5×6 grupos.

**Architecture:** Wrapper fino — cada skill user-level carrega só gatilhos + menu de rótulos dos 6 grupos + delegação dura pro SKILL.md canônico dentro de `~/myp-arbitrage-scanner` (única fonte de verdade, travada por teste no caso DBZ). Nenhuma lista de edições é copiada.

**Tech Stack:** Arquivos markdown de skill do Claude Code (frontmatter YAML `name`/`description`). Sem código, sem dependências.

## Global Constraints

- Spec aprovado: `~/scanners-commons/docs/superpowers/specs/2026-08-04-myp-dbz-user-skill-design.md`.
- `~/.claude/skills/` NÃO é repo git — os SKILL.md não têm commit; só este plano e o spec são versionados (repo `scanners-commons`).
- PROIBIDO copiar listas de edições/substrings pros wrappers (é a causa do drift que o spec cura).
- Nomes: skill novo = `myp-dbz-scan`; skill existente mantém `name: myp-scan` e os gatilhos atuais ("roda o MYP", "scan MYP", "escaneia a MYP").
- Alvos da delegação (têm que existir): `~/myp-arbitrage-scanner/.claude/skills/scan-myp-dbz/SKILL.md` e `~/myp-arbitrage-scanner/.claude/skills/scan-myp/SKILL.md`.
- Invariantes da frota repetidos nos wrappers: entrega verbatim via ferramenta (`myp_dbz_summary.py` / `myp_summary.py`), 2 links por linha em todo bucket, um grupo por vez / nunca 2 scans no mesmo IP, threshold 30 percent inteiro, sem recomendação de compra.

---

### Task 1: Criar `~/.claude/skills/myp-dbz-scan/SKILL.md`

**Files:**
- Create: `C:\Users\mathe\.claude\skills\myp-dbz-scan\SKILL.md`

**Interfaces:**
- Consumes: skill canônico `~/myp-arbitrage-scanner/.claude/skills/scan-myp-dbz/SKILL.md` (já existe, PR #95).
- Produces: skill user-level que dispara de qualquer sessão; Task 4 valida seu frontmatter e alvos.

- [ ] **Step 1: Escrever o arquivo com este conteúdo exato**

````markdown
---
name: myp-dbz-scan
description: Use when the operator wants to run the MYP Dragon Ball arbitrage scanner ("roda o DBZ", "scan dragon ball", "roda o MYP DBZ", "escaneia Fusion World", "DBS Masters no MYP"). As 123 edições estão divididas em 6 grupos por recência; PERGUNTE qual(is) grupo(s) rodar (AskUserQuestion), depois dê git pull na main de ~/myp-arbitrage-scanner, LEIA .claude/skills/scan-myp-dbz/SKILL.md daquele repo e siga-o VERBATIM — listas de edições, comandos e entrega via myp_dbz_summary.py moram lá.
---

# MYP Dragon Ball — wrapper do skill canônico do repo

Este skill é um WRAPPER FINO: reconhece o pedido e aponta pra fonte de
verdade. Todo o conteúdo operacional (listas verbatim de edições por grupo,
comandos, contrato de entrega) vive no skill canônico DENTRO do repo —
partição travada por teste (`test_scan_dbz_skill_profiles.py`). NÃO duplique
aquele conteúdo aqui: cópia é como nasce drift.

**Fonte de verdade:** `~/myp-arbitrage-scanner/.claude/skills/scan-myp-dbz/SKILL.md`
(se este wrapper divergir dela, ela manda).

## Passo 1 — SEMPRE perguntar o grupo primeiro

`AskUserQuestion` (multiSelect, header "Grupo") com os 6 rótulos:

1. G1 · Fusion World recente
2. G2 · Fusion World inicial + promos
3. G3 · Masters moderno + Zenkai
4. G4 · Masters 2021-2022
5. G5 · Masters 2019-2020
6. G6 · Masters clássico 2017-2019

Rótulos são SÓ o menu — as listas de edições de cada grupo estão no skill do
repo; nunca deduzir/inventar substrings de cabeça.

## Passo 2 — atualizar o repo e seguir o skill canônico

```bash
cd ~/myp-arbitrage-scanner && git pull origin main
```

Depois LEIA `.claude/skills/scan-myp-dbz/SKILL.md` e siga-o à risca: rota
local (`myp_dbz_scanner.py … --resume`, detached) vs rota nuvem (workflow
`dbz-scan.yml`), listas verbatim do grupo escolhido, um grupo por vez.

## Invariantes (contrato da frota — repetidos por segurança)

- Entrega SEMPRE via `myp_dbz_summary.py`, colada VERBATIM — nunca tabela à mão.
- 2 links (`[oferta] · [TCG]`) em TODA linha de TODO bucket.
- Um grupo por vez; nunca 2 scans no mesmo IP (403 Cloudflare).
- `--threshold 30` é percent INTEIRO (convenção MYP; CardTrader usa fração).
- Sem recomendação de compra — a decisão de capital é do operador.
````

- [ ] **Step 2: Verificar que o arquivo foi criado e o alvo da delegação existe**

Run (PowerShell): `Test-Path "$HOME\.claude\skills\myp-dbz-scan\SKILL.md"; Test-Path "$HOME\myp-arbitrage-scanner\.claude\skills\scan-myp-dbz\SKILL.md"`
Expected: `True` duas vezes.

*(Sem commit — `~/.claude` não é repo git.)*

### Task 2: Reescrever `~/.claude/skills/myp-scan/SKILL.md` como wrapper fino

**Files:**
- Modify: `C:\Users\mathe\.claude\skills\myp-scan\SKILL.md` (substituição completa do conteúdo)

**Interfaces:**
- Consumes: skill canônico `~/myp-arbitrage-scanner/.claude/skills/scan-myp/SKILL.md` (6 grupos, 2026-07-02).
- Produces: `myp-scan` sem o conteúdo drifado (5 grupos); Task 4 valida.

- [ ] **Step 1: Sobrescrever o arquivo com este conteúdo exato**

````markdown
---
name: myp-scan
description: Use when the operator wants to run the MYP Cards arbitrage scanner ("roda o MYP", "scan MYP", "escaneia a MYP"). O catálogo (~112 edições com preço TCG real) está dividido em 6 grupos por recência; PERGUNTE qual(is) grupo(s) rodar (AskUserQuestion), depois dê git pull na main de ~/myp-arbitrage-scanner, LEIA .claude/skills/scan-myp/SKILL.md daquele repo e siga-o VERBATIM — listas de edições, comandos e entrega via myp_summary.py moram lá.
---

# MYP Scan (Pokémon) — wrapper do skill canônico do repo

Este skill é um WRAPPER FINO: reconhece o pedido e aponta pra fonte de
verdade. Todo o conteúdo operacional (listas verbatim de edições por grupo,
rotas de execução, contrato de entrega) vive no skill canônico DENTRO do
repo. NÃO duplique aquele conteúdo aqui: a versão anterior deste arquivo
copiava tudo e drifou (dizia 5 grupos; o repo tem 6 desde 2026-07-02) —
wrapper fino desde 2026-08-06.

**Fonte de verdade:** `~/myp-arbitrage-scanner/.claude/skills/scan-myp/SKILL.md`
(se este wrapper divergir dela, ela manda).

## Passo 1 — SEMPRE perguntar o grupo primeiro

`AskUserQuestion` (multiSelect, header "Grupo") com os 6 rótulos:

1. G1 · Mega Evolution + SV recente
2. G2 · SV restante + Black Bolt/White Flare + SWSH moderno
3. G3 · SWSH antigo + Pokémon GO + Sun & Moon recente
4. G4 · Sun & Moon restante + XY + HGSS
5. G5 · Black & White + DP/Platinum + EX final
6. G6 · EX restante + e-Card + WOTC

Rótulos são SÓ o menu — as listas de edições de cada grupo estão no skill do
repo; nunca deduzir/inventar substrings de cabeça.

## Passo 2 — atualizar o repo e seguir o skill canônico

```bash
cd ~/myp-arbitrage-scanner && git pull origin main
```

Depois LEIA `.claude/skills/scan-myp/SKILL.md` e siga-o à risca: rota local
(`myp_arbitrage_scanner.py … --resume`, detached) vs rota nuvem (workflow
`quick-scan.yml`, `chunk_total=6`), listas verbatim do grupo escolhido, um
grupo por vez.

## Invariantes (contrato da frota — repetidos por segurança)

- Entrega SEMPRE via `myp_summary.py --type daily` (não existe `--type
  quick`), colada VERBATIM — nunca tabela à mão.
- 2 links (`[oferta] · [TCG]`) em TODA linha de TODO bucket.
- Um grupo por vez; nunca 2 scans no mesmo IP (403 Cloudflare).
- `--threshold 30` é percent INTEIRO (convenção MYP; CardTrader usa fração).
- Cheque a linha "Cobertura de preço TCG real" — nunca tratar fallback como real.
- Sem recomendação de compra — a decisão de capital é do operador.
````

- [ ] **Step 2: Verificar que o alvo da delegação existe**

Run (PowerShell): `Test-Path "$HOME\myp-arbitrage-scanner\.claude\skills\scan-myp\SKILL.md"`
Expected: `True`.

*(Sem commit — fora de git. O conteúdo antigo fica preservado no histórico da conversa/spec.)*

### Task 3: Atualizar a memória persistente

**Files:**
- Modify: `C:\Users\mathe\.claude\projects\C--Users-mathe\memory\myp_scanner_location.md`
- Modify: `C:\Users\mathe\.claude\projects\C--Users-mathe\memory\MEMORY.md` (linha do MYP)

**Interfaces:**
- Consumes: skills criados nas Tasks 1–2.
- Produces: memória que aponta sessões futuras pros wrappers + skill canônicos.

- [ ] **Step 1: Ler `myp_scanner_location.md` e acrescentar/ajustar** o fato: repo main inclui o scanner paralelo DBZ (PR #95: `myp_dbz_scanner.py` + `myp_dbz_summary.py` + `dbz-scan.yml` + skill repo `scan-myp-dbz`, 6 grupos travados por teste); skills user-level `myp-dbz-scan` e `myp-scan` agora são WRAPPERS FINOS (2026-08-06) que delegam pros skills canônicos do repo — nunca re-copiar listas pros wrappers. Registrar também a pendência: commit local não-pushado do fix percent-encoding no `myp_summary.py`.
- [ ] **Step 2: Atualizar a linha correspondente no `MEMORY.md`** mencionando DBZ + wrappers user-level.

### Task 4: Verificação final

**Files:**
- Nenhum novo — só leitura/checagem dos criados.

**Interfaces:**
- Consumes: os dois SKILL.md user-level + os dois canônicos do repo.
- Produces: veredito de conformidade com o spec.

- [ ] **Step 1: Rodar o check de frontmatter + alvos** (Python):

```python
import re, os
skills = [os.path.expanduser(p) for p in (
    "~/.claude/skills/myp-dbz-scan/SKILL.md",
    "~/.claude/skills/myp-scan/SKILL.md")]
targets = [os.path.expanduser(p) for p in (
    "~/myp-arbitrage-scanner/.claude/skills/scan-myp-dbz/SKILL.md",
    "~/myp-arbitrage-scanner/.claude/skills/scan-myp/SKILL.md")]
for p in skills:
    t = open(p, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    assert m, f"frontmatter ausente: {p}"
    assert re.search(r"^name: [a-z0-9-]+$", m.group(1), re.M), f"name invalido: {p}"
    assert "description:" in m.group(1), f"description ausente: {p}"
    assert "--editions" not in t, f"lista de edicoes vazou pro wrapper: {p}"
for p in targets:
    assert os.path.exists(p), f"alvo nao existe: {p}"
print("OK")
```

Expected: `OK`.

- [ ] **Step 2: Leitura cruzada** — conferir que cada afirmação dos wrappers confere com o skill canônico correspondente (6 rótulos = 6 grupos reais; nomes de arquivos/workflows citados existem: `myp_dbz_summary.py`, `dbz-scan.yml`, `quick-scan.yml`, `myp_summary.py`).
- [ ] **Step 3: Registrar a checagem de sessão nova** — a listagem de skills só recarrega em sessão nova; anotar na entrega final que o operador verá `myp-dbz-scan` na próxima sessão ("roda o DBZ" deve disparar).
