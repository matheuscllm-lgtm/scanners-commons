#!/usr/bin/env bash
# Sincroniza a versão canônica do skill /auto (tooling/auto.md) para os 8 repos
# da frota e, sob --user, para as cópias de usuário fora dos repos.
# Roda do diretório scanners-commons. Idempotente: compara com CR normalizado
# (core.autocrlf não gera drift falso) e só escreve se o texto mudou.
#
# Uso:
#   bash tooling/sync-auto-skill.sh                 # aplica nos 8 repos
#   bash tooling/sync-auto-skill.sh --check         # dry-run: só compara
#   bash tooling/sync-auto-skill.sh --user          # repos + cópias de usuário (~/.claude)
#   bash tooling/sync-auto-skill.sh --user --check  # dry-run incluindo usuário
#
# Cópias de USUÁRIO (só com --user; escrevem fora do repo, por isso opt-in):
# - Claude Code terminal: ~/.claude/commands/auto.md = master + cabeçalho de
#   precedência (o auto.md do repo vence; sem repo, perguntar antes de agir).
#   Montado aqui, em vez de virar um 2º arquivo versionado, pra não existir
#   cópia pra divergir. O cabeçalho entra DEPOIS do frontmatter, seja qual for
#   o tamanho dele.
# - Cowork: ~/.claude/skills/auto-cowork/SKILL.md = tooling/auto-cowork/SKILL.md.
#   O nome é `auto-cowork` de propósito: uma skill pessoal chamada `auto`
#   sombreia o comando /auto do terminal (e o de cada repo). Uma instalação
#   legada em ~/.claude/skills/auto/ é removida SE for a nossa (marcador).
#   Esta cópia local NÃO instala no perfil da conta Cowork — para isso,
#   empacote com skill-creator e clique 'Save skill' no card.
set -euo pipefail

TOOLING_DIR="$(cd "$(dirname "$0")" && pwd)"
MASTER="$TOOLING_DIR/auto.md"
HEADER="$TOOLING_DIR/auto-user-header.md"
COWORK="$TOOLING_DIR/auto-cowork/SKILL.md"
HOME_DIR="${HOME:-/c/Users/mathe}"
USER_CMD="$HOME_DIR/.claude/commands/auto.md"
USER_SKILL="$HOME_DIR/.claude/skills/auto-cowork/SKILL.md"
LEGACY_SKILL="$HOME_DIR/.claude/skills/auto/SKILL.md"
COWORK_MARKER="Modo AUTÔNOMO da frota de scanners de arbitragem"

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

CHECK_ONLY=0; WITH_USER=0
for arg in "$@"; do
  case "$arg" in
    --check) CHECK_ONLY=1 ;;
    --user)  WITH_USER=1 ;;
    *) echo "ERRO: argumento desconhecido: $arg (use --check e/ou --user)" >&2; exit 2 ;;
  esac
done

TMPFILES=()
cleanup() { [ "${#TMPFILES[@]}" -gt 0 ] && rm -f "${TMPFILES[@]}"; return 0; }
trap cleanup EXIT

need() { [ -f "$1" ] || { echo "ERRO: insumo não encontrado: $1" >&2; exit 1; }; }
need "$MASTER"
if [ "$WITH_USER" = 1 ]; then need "$HEADER"; need "$COWORK"; fi

# Conteúdo sem CR: é o que se compara e o que se escreve (LF, como no índice do git).
lf() { tr -d '\r' < "$1"; }

# Master + cabeçalho de precedência inserido logo após o fechamento do frontmatter
# (2º `---`), qualquer que seja o número de chaves. Falha alto se não houver frontmatter.
build_user_cmd() {
  if [ "$(lf "$MASTER" | head -n 1)" != "---" ] || [ "$(lf "$MASTER" | awk 'NR>1 && $0=="---"{c++} END{print c+0}')" -lt 1 ]; then
    echo "ERRO: $MASTER sem frontmatter (--- ... ---); não dá pra montar a cópia de usuário" >&2
    return 1
  fi
  lf "$MASTER" | awk -v hdr="$HEADER" '
    NR==1 { print; next }
    !done && $0=="---" { print; while ((getline l < hdr) > 0) { sub(/\r$/, "", l); print l }; close(hdr); done=1; next }
    { print }'
}

# sync_one <rótulo> <destino> <comando que imprime o conteúdo desejado>
# Compara com CR normalizado; em --check só reporta; senão escreve via temporário
# no mesmo diretório (rename atômico) e o trap limpa se algo falhar no meio.
repo_changed=0; user_changed=0
sync_one() {
  local label="$1" dest="$2"; shift 2
  local tmp; tmp="$(mktemp "${TMPDIR:-/tmp}/sync-auto.XXXXXX")"; TMPFILES+=("$tmp")
  "$@" > "$tmp"
  if [ -f "$dest" ] && cmp -s "$tmp" <(lf "$dest"); then
    printf "%-32s ok (já igual)\n" "$label"; return 0
  fi
  if [ "$CHECK_ONLY" = 1 ]; then
    printf "%-32s DIFERENTE (precisa sync)\n" "$label"; return 1
  fi
  mkdir -p "$(dirname "$dest")"
  mv "$tmp" "$dest"
  printf "%-32s ATUALIZADO\n" "$label"; return 1
}

echo "master tooling/auto.md  md5(LF)=$(lf "$MASTER" | md5sum | cut -d' ' -f1)"
echo
for r in "${REPOS[@]}"; do
  dest="$HOME_DIR/$r/.claude/commands/auto.md"
  if [ ! -d "$HOME_DIR/$r/.claude/commands" ]; then
    printf "%-32s SKIP (sem .claude/commands)\n" "$r"; continue
  fi
  sync_one "$r" "$dest" lf "$MASTER" || repo_changed=$((repo_changed+1))
done

if [ "$WITH_USER" = 1 ]; then
  echo
  sync_one "~/.claude/commands (code)" "$USER_CMD" build_user_cmd || user_changed=$((user_changed+1))
  sync_one "~/.claude/skills (cowork)" "$USER_SKILL" lf "$COWORK" || user_changed=$((user_changed+1))
  if [ -f "$LEGACY_SKILL" ] && grep -q "$COWORK_MARKER" "$LEGACY_SKILL"; then
    if [ "$CHECK_ONLY" = 1 ]; then
      printf "%-32s LEGADA (sombreia /auto; será removida no apply)\n" "~/.claude/skills/auto"
    else
      rm -f "$LEGACY_SKILL"; rmdir "$(dirname "$LEGACY_SKILL")" 2>/dev/null || true
      printf "%-32s REMOVIDA (sombreava o comando /auto)\n" "~/.claude/skills/auto"
    fi
    user_changed=$((user_changed+1))
  fi
fi

echo
total=$((repo_changed+user_changed))
if [ "$CHECK_ONLY" = 1 ]; then
  echo "dry-run: $total destino(s) precisariam de sync ($repo_changed repo(s), $user_changed de usuário)."
else
  echo "sync concluído: $total destino(s) atualizado(s) ($repo_changed repo(s), $user_changed de usuário)."
  [ "$repo_changed" -gt 0 ] && echo "Repos alterados: commit+push em cada um (branch + PR)."
  [ "$WITH_USER" = 1 ] && echo "Cowork: a cópia em ~/.claude/skills/auto-cowork é local; para o perfil da conta, empacote com skill-creator e 'Save skill'."
fi
exit 0
