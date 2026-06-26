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

echo
if [ "$CHECK_ONLY" = 1 ]; then
  echo "dry-run: $changed repo(s) precisariam de sync."
else
  echo "sync concluído: $changed repo(s) atualizado(s). Commit+push em cada repo é manual."
fi
