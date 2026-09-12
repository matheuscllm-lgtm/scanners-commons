#!/usr/bin/env bash
# Testes do tooling/sync-auto-skill.sh contra um HOME falso (nunca toca o HOME real).
# Uso: bash tooling/tests/test_sync_auto_skill.sh
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
TOOLING="$(cd "$HERE/.." && pwd)"
fail=0; pass=0
ok()   { pass=$((pass+1)); echo "  ok   $1"; }
nok()  { fail=$((fail+1)); echo "  FAIL $1"; }
check(){ if eval "$2"; then ok "$1"; else nok "$1"; fi; }
has_cr(){ [ "$(od -c "$1" | grep -c '\\r')" -gt 0 ]; }

# Sandbox: cópia do tooling + HOME falso com 2 repos da frota.
SB="$(mktemp -d)"; trap 'rm -rf "$SB"' EXIT
cp -r "$TOOLING" "$SB/tooling"
FH="$SB/home"; mkdir -p "$FH/card-trader-scanner/.claude/commands" "$FH/scanner-comc/.claude/commands"
SCRIPT="$SB/tooling/sync-auto-skill.sh"
run() { HOME="$FH" TMPDIR="$SB/tmp" bash "$SCRIPT" "$@"; }
mkdir -p "$SB/tmp"

echo "T1 aplicar sem --user: repos sincronizados, HOME/.claude intocado"
run >/dev/null 2>&1; rc=$?
check "rc=0" '[ "$rc" = 0 ]'
check "repo copiado" 'cmp -s <(tr -d "\r" < "$SB/tooling/auto.md") "$FH/card-trader-scanner/.claude/commands/auto.md"'
check "sem ~/.claude/commands/auto.md" '[ ! -e "$FH/.claude/commands/auto.md" ]'
check "sem ~/.claude/skills/*" '[ ! -e "$FH/.claude/skills" ]'

echo "T2 idempotência com CRLF no destino"
sed -i 's/$/\r/' "$FH/card-trader-scanner/.claude/commands/auto.md"
out="$(run --check 2>&1)"
check "--check nao acusa drift por CRLF" 'grep -q "card-trader-scanner.*ok" <<<"$out" && ! grep -q "card-trader-scanner.*DIFERENTE" <<<"$out"'
check "--check nao escreve" 'has_cr "$FH/card-trader-scanner/.claude/commands/auto.md"'

echo "T3 --user: copia de usuario montada com frontmatter intacto mesmo com chave extra"
sed -i '3a argument-hint: <tarefa>' "$SB/tooling/auto.md"
run --user >/dev/null 2>&1; rc=$?
U="$FH/.claude/commands/auto.md"
check "rc=0" '[ "$rc" = 0 ]'
check "usuario existe" '[ -f "$U" ]'
check "frontmatter fecha na linha 5" '[ "$(sed -n 5p "$U")" = "---" ]'
check "argument-hint dentro do frontmatter" '[ "$(sed -n 4p "$U")" = "argument-hint: <tarefa>" ]'
check "cabecalho de precedencia vem DEPOIS do frontmatter" 'grep -n "Cópia de USUÁRIO" "$U" | head -1 | cut -d: -f1 | xargs -I{} test {} -gt 5'
check "cabecalho presente uma vez" '[ "$(grep -c "Cópia de USUÁRIO" "$U")" = 1 ]'
check "corpo do master preservado" 'grep -q "^## 0. Pré-voo" "$U"'
check "sem CR na copia de usuario" '! has_cr "$U"'

echo "T4 --user: skill do Cowork nao se chama 'auto' (nao sombreia o comando)"
check "instalada como auto-cowork" '[ -f "$FH/.claude/skills/auto-cowork/SKILL.md" ]'
check "frontmatter name: auto-cowork" 'grep -q "^name: auto-cowork$" "$FH/.claude/skills/auto-cowork/SKILL.md"'
check "nenhuma skill chamada auto" '[ ! -e "$FH/.claude/skills/auto/SKILL.md" ]'

echo "T5 --user remove a instalacao legada ~/.claude/skills/auto (so se for a nossa)"
mkdir -p "$FH/.claude/skills/auto"; cp "$SB/tooling/auto-cowork/SKILL.md" "$FH/.claude/skills/auto/SKILL.md"
sed -i 's/^name: auto-cowork$/name: auto/' "$FH/.claude/skills/auto/SKILL.md"
run --user >/dev/null 2>&1
check "legada removida" '[ ! -e "$FH/.claude/skills/auto/SKILL.md" ]'
mkdir -p "$FH/.claude/skills/auto"; printf -- '---\nname: auto\ndescription: outra coisa\n---\n' > "$FH/.claude/skills/auto/SKILL.md"
run --user >/dev/null 2>&1
check "skill 'auto' de terceiros preservada" '[ -f "$FH/.claude/skills/auto/SKILL.md" ]'

echo "T6 HOME ausente: usa fallback, nao aborta"
env -u HOME TMPDIR="$SB/tmp" bash "$SCRIPT" --check >/dev/null 2>&1; rc=$?
check "rc=0 sem HOME" '[ "$rc" = 0 ]'

echo "T7 insumo ausente falha alto e nao deixa temporario"
mv "$SB/tooling/auto-user-header.md" "$SB/tooling/auto-user-header.md.bak"
run --user >/dev/null 2>&1; rc=$?
check "rc!=0 sem header" '[ "$rc" != 0 ]'
check "sem temporario orfao" '[ -z "$(ls -A "$SB/tmp")" ]'
mv "$SB/tooling/auto-user-header.md.bak" "$SB/tooling/auto-user-header.md"

echo "T8 segunda aplicacao e idempotente (tudo 'ok')"
out="$(run --user --check 2>&1)"
check "nenhum DIFERENTE" '! grep -q DIFERENTE <<<"$out"'
check "resumo diz 0" 'grep -q "0 destino" <<<"$out"'

echo; echo "passou=$pass falhou=$fail"; [ "$fail" = 0 ]
