# Design — Skill user-level `myp-dbz-scan` (+ refit do `myp-scan`)

- **Data:** 2026-08-04
- **Status:** aprovado pelo operador (sessão de brainstorming)
- **Escopo:** só arquivos de skill do Claude Code + este doc. Nenhum código de scanner é tocado.

## Contexto (por que isso existe)

O scanner de Dragon Ball do MYP já existe e está mergeado na main do repo
`myp-arbitrage-scanner` (PR #95, 2026-08-03): `myp_dbz_scanner.py`,
`myp_dbz_summary.py` (entrega), workflow `dbz-scan.yml` (rota nuvem), 34 testes
e um **skill dentro do repo** (`.claude/skills/scan-myp-dbz/SKILL.md`) com as
123 edições divididas em 6 grupos — partição travada por teste
(`test_scan_dbz_skill_profiles.py`).

O que falta: um skill em **nível de usuário** (`~/.claude/skills/`). Skill de
repo só é visível quando a sessão trabalha dentro daquela pasta; o operador
pede scans de qualquer sessão ("roda o DBZ"), então precisa do gatilho global —
exatamente o papel que o `myp-scan` cumpre para o Pokémon.

## Decisão de arquitetura: wrapper fino (uma fonte de verdade só)

*Glossário: "wrapper" = embrulho — um skill curto que aponta para o documento
oficial em vez de copiar o conteúdo. "Drift" = deriva — quando a mesma
informação vive em dois lugares e as cópias divergem com o tempo.*

O skill user-level **não copia** listas de edições, comandos nem contrato de
entrega. Ele carrega só: gatilhos, menu de rótulos dos 6 grupos, e a ordem de
ler e seguir o skill canônico do repo. Motivo (evidência real): o `myp-scan`
user-level do Pokémon foi criado como cópia completa e **já drifou** — diz
"5 grupos" enquanto o `scan-myp` do repo tem 6 desde 2026-07-02. As listas do
DBZ são travadas por teste **dentro do repo**; qualquer cópia fora fica órfã
da trava. Alternativas rejeitadas: cópia completa (recria o drift, não ganha
independência — rodar o scan exige o repo de qualquer jeito) e híbrido com
menu detalhado (mais superfície de drift por pouca conveniência).

## Item 1 — skill novo `myp-dbz-scan`

**Arquivo:** `C:\Users\mathe\.claude\skills\myp-dbz-scan\SKILL.md` (~40 linhas).

**Frontmatter:** `name: myp-dbz-scan`; `description` com os gatilhos — "roda o
DBZ", "scan dragon ball", "roda o MYP DBZ", "escaneia Fusion World", "DBS
Masters no MYP" — e a instrução de SEMPRE perguntar o grupo antes de rodar.

**Corpo — 3 blocos:**

1. **Pergunta obrigatória** (AskUserQuestion, multiSelect) com o menu de
   rótulos dos 6 grupos: G1 Fusion World recente · G2 Fusion World
   inicial+promos · G3 Masters moderno/Zenkai · G4 Masters 2021-22 ·
   G5 Masters 2019-20 · G6 Masters clássico 2017-19. Rótulos apenas — as
   listas de edições vivem no repo.
2. **Delegação dura:** dar `git pull` na main de `~/myp-arbitrage-scanner`,
   LER `.claude/skills/scan-myp-dbz/SKILL.md` e segui-lo à risca: listas
   verbatim de edições por grupo, rota local (`myp_dbz_scanner.py --resume`
   detached) vs rota nuvem (workflow `dbz-scan.yml`), e entrega via
   `myp_dbz_summary.py` colada VERBATIM.
3. **Invariantes repetidos por segurança** (mesmo contrato da frota): nunca
   montar tabela à mão; 2 links (`[oferta] · [TCG]`) em toda linha de todo
   bucket; um grupo por vez, nunca 2 scans no mesmo IP; threshold 30 percent
   inteiro; sem recomendação de compra.

## Item 2 — refit do `myp-scan` (Pokémon) para o mesmo padrão

Reescrever `C:\Users\mathe\.claude\skills\myp-scan\SKILL.md` como wrapper fino
apontando para `~/myp-arbitrage-scanner/.claude/skills/scan-myp/SKILL.md`
(6 grupos — cura o drift 5×6). Mantém os gatilhos atuais ("roda o MYP",
"scan MYP", "escaneia a MYP") e os mesmos 3 blocos do Item 1, com menu de
rótulos lido do skill do repo no momento do refit.

## Registro e verificação

- **Memória:** atualizar `myp_scanner_location.md` (skill user-level novo +
  refit) e o índice `MEMORY.md`.
- **Verificação (manual — skill não tem suite de teste):** (a) os dois
  SKILL.md têm frontmatter válido e caminhos que existem no disco; (b) numa
  sessão nova, a listagem de skills mostra `myp-dbz-scan` e o `myp-scan`
  atualizado; (c) leitura cruzada: cada afirmação do wrapper confere com o
  skill do repo correspondente.
- **Fora de escopo:** qualquer mudança nos skills do repo, no scanner ou nos
  workflows; o commit local não-pushado do `myp_summary.py` (percent-encoding)
  é pendência separada.
