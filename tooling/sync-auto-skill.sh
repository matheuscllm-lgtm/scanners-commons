#!/usr/bin/env bash
# Sincroniza a versão canônica do skill /auto (tooling/auto.md) para os 8 repos
# da frota. Roda do diretório scanners-commons. Idempotente: só copia se mudou.
#
# Uso:
#   bash tooling/sync-auto-skill.sh           # aplica e mostra o que mudou
#   bash tooling/sync-auto-skill.sh --check    # só compara, não escreve (dry-run)
set -euo pipefail

MASTER="$(cd "$(dirname "$0")" && pwd)/auto.md"
HOME_DIR="${HOME:-/c/Users/mathe}"

REPOS=(
  card-trader-scanner
  ebay-arbitrage-scanner
  integrated-scanner
  liga-pokemon-scanner
  myp-arbitrage-scanner
  pokemon-longterm-outlook
  scanner-comc
  sealed-arbitrage-scanner
)

CHECK_ONLY=0
[ "${1:-}" = "--check" ] && CHECK_ONLY=1

[ -f "$MASTER" ] || { echo "ERRO: master não encontrado: $MASTER" >&2; exit 1; }
master_hash="$(md5sum "$MASTER" | cut -d' ' -f1)"
echo "master tooling/auto.md  md5=$master_hash"
echo

changed=0
for r in "${REPOS[@]}"; do
  dest="$HOME_DIR/$r/.claude/commands/auto.md"
  if [ ! -d "$HOME_DIR/$r/.claude/commands" ]; then
    printf "%-30s SKIP (sem .claude/commands)\n" "$r"; continue
  fi
  if [ -f "$dest" ] && [ "$(md5sum "$dest" | cut -d' ' -f1)" = "$master_hash" ]; then
    printf "%-30s ok (já igual)\n" "$r"; continue
  fi
  if [ "$CHECK_ONLY" = 1 ]; then
    printf "%-30s DIFERENTE (precisa sync)\n" "$r"; changed=$((changed+1)); continue
  fi
  cp "$MASTER" "$dest"
  printf "%-30s ATUALIZADO\n" "$r"; changed=$((changed+1))
done

# Cópias de USUÁRIO: fazem o /auto existir FORA dos repos da frota.
# - Claude Code: ~/.claude/commands/auto.md  = master + cabecalho de precedencia
#   (o auto.md do repo vence; sem repo, perguntar antes de agir). Montado aqui
#   em vez de virar um 2o arquivo versionado, pra nao existir copia pra divergir.
# - Cowork: ~/.claude/skills/auto/SKILL.md   = tooling/auto-cowork/SKILL.md
#   (skill, nao comando: o Cowork nao tem barra; e a descricao e travada pra so
#   acionar quando o operador pedir modo autonomo explicitamente).
HEADER="$(cd "$(dirname "$0")" && pwd)/auto-user-header.md"
COWORK="$(cd "$(dirname "$0")" && pwd)/auto-cowork/SKILL.md"
USER_CMD="$HOME/.claude/commands/auto.md"
USER_SKILL="$HOME/.claude/skills/auto/SKILL.md"

sync_user() {
  local label="$1" dest="$2"; shift 2
  local tmp; tmp="$(mktemp)"
  "$@" > "$tmp"
  if [ -f "$dest" ] && cmp -s "$tmp" "$dest"; then
    printf "%-30s ok (ja igual)\n" "$label"; rm -f "$tmp"; return
  fi
  if [ "$CHECK_ONLY" = 1 ]; then
    printf "%-30s DIFERENTE (precisa sync)\n" "$label"; rm -f "$tmp"; changed=$((changed+1)); return
  fi
  mkdir -p "$(dirname "$dest")"
  mv "$tmp" "$dest"
  printf "%-30s ATUALIZADO\n" "$label"; changed=$((changed+1))
}

build_user_cmd() { head -n 4 "$MASTER"; cat "$HEADER"; tail -n +5 "$MASTER"; }

echo
if [ -f "$HEADER" ]; then
  sync_user "~/.claude/commands (code)" "$USER_CMD" build_user_cmd
else
  printf "%-30s SKIP (sem auto-user-header.md)\n" "~/.claude/commands (code)"
fi
if [ -f "$COWORK" ]; then
  sync_user "~/.claude/skills (cowork)" "$USER_SKILL" cat "$COWORK"
else
  printf "%-30s SKIP (sem auto-cowork/SKILL.md)\n" "~/.claude/skills (cowork)"
fi

echo
if [ "$CHECK_ONLY" = 1 ]; then
  echo "dry-run: $changed destino(s) precisariam de sync."
else
  echo "sync concluido: $changed destino(s) atualizado(s). Commit+push em cada repo e manual."
  echo "Cowork: a copia em ~/.claude/skills nao instala no perfil da conta --"
  echo "  empacote com skill-creator (package_skill) e clique 'Save skill' no card."
fi
