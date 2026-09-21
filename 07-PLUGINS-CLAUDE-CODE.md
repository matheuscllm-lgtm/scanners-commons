# 07 — Plugins, skills e proxies do Claude Code (setup global do operador)

> Pra você, Matheus: este arquivo diz **o que instalar no Claude Code para
> valer em todos os scanners e no Cowork**, por qual canal cada coisa se
> instala, e por que "instalei aqui" nem sempre significa "vale ali". Cópia-mãe
> da frota; o `CLAUDE.md` de cada scanner só aponta pra cá.

## Regra de ouro: são 3 canais diferentes, e o canal decide onde vale

| Canal | Como instala | Onde vale | Onde NÃO vale |
|---|---|---|---|
| **Plugin do CLI** | `claude plugin install <nome>@<marketplace>` (scope `user`, default) | todo repo do Claude Code no PC: terminal, VS Code, sessão web | **Cowork** (catálogo próprio, não lê `~/.claude/settings.json`) |
| **Skill no claude.ai** | upload do `.skill`/`.zip` em claude.ai → Settings → Capabilities → Skills | **tudo**: chat, Cowork, Claude Code (chega em `~/.claude/skills/synced/`, até em sessão remota) | — (sentido único claude.ai → Claude Code; skill só em `~/.claude/skills/` do PC **não** sobe) |
| **Proxy/gateway local** (`ANTHROPIC_BASE_URL`) | variável de ambiente no shell que abre o Claude | só a sessão aberta naquele shell | Cowork e sessão na nuvem (não enxergam `127.0.0.1`) |

Consequência prática: **skills sincronizam, plugins não.** Se algo precisa
existir no Cowork *e* no Claude Code, tem que ser skill enviada pelo claude.ai.

Decisão do operador (2026-09-11): plugins ficam em scope **`user`** (default do
CLI, grava em `C:\Users\mathe\.claude\settings.json`). **Não** declarar em
`.claude/settings.json` de repo: vira segunda fonte de verdade e depende do
prompt de workspace trust.

## Os "5 plugins" do reel (@99hud, 2026-08-05) — o que cada um é de fato

O reel vende os cinco como "plugins"; só **dois** são plugins no sentido do CLI.

| # | Ferramenta | O que é | Como instala (global) | Vale no Cowork? |
|---|---|---|---|---|
| 1 | **OmniRoute** | gateway local (porta 20128) que troca de modelo quando a cota acaba | `npm i -g omniroute` + `ANTHROPIC_BASE_URL` no shell — manual em `OMNIROUTE.md` do repo Liga | Não |
| 2 | **Claude Mem** | plugin do CLI (memória entre sessões) | `claude plugin install claude-mem@thedotmack` | Não automaticamente |
| 3 | **Headroom** | proxy local Python (Apache 2.0) que comprime saída de ferramenta | `pip install "headroom-ai[proxy]"` → `headroom wrap claude` | Não |
| 4 | **Claude Code Setup** | plugin **oficial** da Anthropic (analisa o repo e sugere hooks/skills/MCP) | `claude plugin install claude-code-setup@claude-plugins-official` | Não automaticamente |
| 5 | **Task Observer** | **skill** (CC BY 4.0, Eoghan Henn / rebelytics.com) que observa o trabalho e propõe melhorias nas skills | upload de `task-observer.skill` no claude.ai | **Sim** — o único global de verdade |

Mais o **`cartographer`** (terceiro, `kingbootoshi`), que não está no reel mas
faz parte do setup: mapeia o codebase com subagents → `docs/CODEBASE_MAP.md`.

## Instalação no PC (uma vez) — `tooling/setup_claude_plugins.ps1`

O script faz tudo abaixo de uma vez. Equivalente manual no PowerShell:

```powershell
# 1) marketplaces-fonte — nenhum dos tres vive em anthropics/claude-code (repo de DEMOS)
claude plugin marketplace add anthropics/claude-plugins-official
claude plugin marketplace add thedotmack/claude-mem
claude plugin marketplace add kingbootoshi/cartographer

# 2) plugins — sem --scope de proposito: default 'user' = todos os repos
claude plugin install claude-code-setup@claude-plugins-official
claude plugin install claude-mem@thedotmack
claude plugin install cartographer@cartographer-marketplace
claude plugin list          # conferir; depois reabrir o Claude (ou /reload-plugins)

# 3) Headroom (pacote Python, roda 100% local, sem conta)
python -m pip install --upgrade "headroom-ai[proxy]"
```

> ✅ Passos 1 e 2 **validados de ponta a ponta** em sessão remota (2026-09-14,
> Claude Code 2.1.270): marketplaces clonam, plugins instalam em scope `user`
> (`claude-code-setup` 1.0.0, `claude-mem` 13.24.23, `cartographer` 1.4.0) e
> gravam `enabledPlugins` + `extraKnownMarketplaces` no `settings.json`.
> Sessão remota é efêmera: a instalação que vale é a do PC.

### Task Observer (skill) — upload + ativação

1. Gerar o bundle a partir do repo canônico (ele **não publica release**,
   checado em 2026-09-14):
   ```bash
   git clone --depth 1 https://github.com/rebelytics/one-skill-to-rule-them-all
   mkdir -p bundle/task-observer
   cp one-skill-to-rule-them-all/SKILL.md bundle/task-observer/
   cp -r one-skill-to-rule-them-all/references one-skill-to-rule-them-all/scripts bundle/task-observer/
   python3 one-skill-to-rule-them-all/scripts/validate-skill-bundle.py bundle/task-observer --pack task-observer.skill
   ```
2. Upload em claude.ai → Settings → Capabilities → Skills. Some em chat, Cowork
   e Claude Code.
3. **Ativar**: a descrição da skill sozinha dispara pouco. Colar o bloco de
   ativação (texto completo em `references/environments.md` do bundle, seção
   "The activation block") nas **preferências pessoais do claude.ai** — não no
   `CLAUDE.md` de um repo, senão só vale naquele repo. O essencial do bloco:
   invocar `task-observer` antes da primeira chamada de ferramenta de qualquer
   sessão e antes de propor plano, e fixar um **workspace absoluto** para o log
   de observações, fora de qualquer repo, p. ex.
   `C:\Users\mathe\task-observer-workspace`. Workspace derivado do cwd se perde
   em worktree/clone temporário (aviso do próprio projeto).
4. Conferir numa sessão **nova**: se depois de algumas sessões de trabalho não
   existir `skill-observations/observation-log/` no workspace, a ativação não
   pegou.

O bundle **não é versionado** em nenhum repo da frota (conteúdo de terceiro,
CC BY 4.0; os repos de scanner são públicos e minimalistas de propósito).
Regerar do clone quando quiser atualizar.

### `grill-me` (skill da frota) — upload

Skill própria, cópia-mestra versionada em `tooling/grill-me/SKILL.md`: faz o
Claude te entrevistar (uma pergunta por vez) até a decisão fechar, antes de
executar. Empacotar e subir:

```bash
python3 -m scripts.package_skill tooling/grill-me   # a partir da pasta da skill-creator
# → grill-me.skill  (é um zip com grill-me/SKILL.md dentro)
```

Upload em claude.ai → Settings → Capabilities → Skills. Aí vale em **tudo**
(chat, Cowork, Claude Code, inclusive sessão remota) — mesmo canal do Task
Observer, pelo mesmo motivo da regra de ouro acima: skill sincroniza, plugin não.

Diferente do Task Observer, **não precisa de bloco de ativação**: ela dispara
pela própria descrição quando você pede "me grelha" / "me faz perguntas" /
"me ajuda a decidir". O `.skill` não é versionado (é artefato gerável); a fonte
de verdade é o `SKILL.md` deste repo — editou aqui, reempacota e sobe de novo.

## Headroom + OmniRoute: encadeiam (Headroom na frente, OmniRoute atrás)

- `headroom wrap claude` seta `ANTHROPIC_BASE_URL=http://127.0.0.1:8787` sozinho
  para a sessão e `headroom unwrap claude` desfaz. **Nunca** exportar
  `ANTHROPIC_BASE_URL` fixo pro Headroom no perfil do shell.
- O *upstream* do proxy vem de **`ANTHROPIC_TARGET_API_URL`** (default
  `api.anthropic.com`; lido em `headroom/providers/registry.py`). Para manter o
  fallback de modelo do OmniRoute:
  ```powershell
  $env:ANTHROPIC_TARGET_API_URL = "http://127.0.0.1:20128"; headroom wrap claude
  ```
- Efeito colateral documentado pelo próprio Headroom: com `ANTHROPIC_BASE_URL`
  custom, o Claude Code ≥ 2.1.196 **desliga o Remote Control** (`/rc`) e, sem
  `--1m`, cai pra janela de 200k. Dia de espelhar a sessão no celular = rodar o
  Claude sem o wrap.

## Ressalvas dos plugins

- **`claude-mem` é o caro**: ~2.000 tokens *always-on* + hook `PostToolUse`
  disparando um worker node a cada chamada de ferramenta. Em scan ao vivo
  headful (Liga, COMC, Selados) isso pesa — `claude plugin disable claude-mem`
  antes do scan se atrapalhar. Depende de disco persistente (`~/.claude-mem`) e
  de `node` no PATH; em sessão remota a memória morre com o container.
- **Podar skills fora de escopo** (opcional), em
  `C:\Users\mathe\.claude\settings.json` →
  `"skillOverrides": { "claude-mem:<skill>": "off" }` para `wowerpoint`,
  `design-is`, `standup`, `weekly-digests`, `timeline-report`, `oh-my-issues`,
  `version-bump`, `mode-creator`, `ccs-align`. Mantém o núcleo de memória
  (`mem-search`, `pathfinder`, `smart-explore`, `learn-codebase`, `make-plan`).
- **Dois plugins são de terceiros** e registram hooks que executam comandos
  locais; `claude plugin update <nome>` puxa código novo — atualizar de forma
  consciente.
- **`cartographer` gasta tokens de verdade** (subagents em paralelo sobre o
  codebase inteiro): sob demanda, não em loop.
- **Cowork**: se quiser `claude-mem`/`cartographer` lá, é pelo catálogo do app
  (Customize → Plugins), se o catálogo oferecer. Não confirmado se aceita
  marketplace de terceiro.

## ⏳ Pendências — retomar no PC do operador

> Aberto em **2026-09-14**. A receita acima está mergeada; a instalação é
> manual e **ainda não foi feita**. Qualquer sessão que retome no PC deve
> lembrar disto e conduzir na ordem. Ao concluir, apagar esta seção (e o item
> espelho em "Pendências vivas" do `CLAUDE.md` do repo Liga).

1. Rodar `tooling/setup_claude_plugins.ps1` no PowerShell e conferir com
   `claude plugin list` (3 plugins em scope `user`) e `headroom --version`.
2. Task Observer: regerar o bundle (receita na seção acima), upload em
   claude.ai → Settings → Capabilities → Skills, colar o bloco de ativação nas
   **preferências pessoais do claude.ai** com workspace
   `C:\Users\mathe\task-observer-workspace`. Validar numa sessão **nova**.
3. Decidir o uso diário do Headroom (`headroom wrap claude`, com
   `ANTHROPIC_TARGET_API_URL` apontando pro OmniRoute quando ele estiver
   ligado). Lembrete: base URL custom desliga o `/rc`.
4. Opcional: apagar no GitHub as branches já mergeadas
   `claude/install-model-skills-mlx4u6` (Liga) e
   `claude/plugins-claude-code-frota` (commons).

## Histórico

- **2026-09-14** — documento criado a partir da seção 🔌 Plugins do `CLAUDE.md`
  do repo Liga (PR #55 lá), com os 5 do reel @99hud e as regras de canal
  verificadas nas docs oficiais do Claude Code.
- **2026-09-11** — decisão do operador: plugins em scope `user`, nunca em
  `.claude/settings.json` de repo.
