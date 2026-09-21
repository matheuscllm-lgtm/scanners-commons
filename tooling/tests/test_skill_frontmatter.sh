#!/usr/bin/env bash
# Valida o frontmatter de TODA skill versionada em tooling/*/SKILL.md com as
# mesmas regras do `quick_validate.py` do skill-creator (o que o package_skill
# barra no upload): name kebab-case = nome da pasta, description ≤ 1024 chars,
# sem < >, só chaves permitidas, exatamente um SKILL.md por skill. Offline.
# Uso: bash tooling/tests/test_skill_frontmatter.sh
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
TOOLING="$(cd "$HERE/.." && pwd)"
fail=0; pass=0
ok()  { pass=$((pass+1)); echo "  ok   $1"; }
nok() { fail=$((fail+1)); echo "  FAIL $1"; }

found=0
for skill_md in "$TOOLING"/*/SKILL.md; do
  [ -f "$skill_md" ] || continue
  found=$((found+1))
  dir="$(dirname "$skill_md")"; skill="$(basename "$dir")"
  echo "$skill"
  out="$(python3 - "$skill_md" "$skill" <<'EOF'
import re, sys
path, folder = sys.argv[1], sys.argv[2]
text = open(path, encoding="utf-8").read()
errs = []
m = re.match(r"^---\n(.*?)\n---", text, re.S)
if not m:
    print("frontmatter ausente"); sys.exit(1)
fm = m.group(1).split("\n")
keys, name, desc = [], "", []
i = 0
while i < len(fm):
    line = fm[i]
    km = re.match(r"^([A-Za-z-]+):\s*(.*)$", line)
    if km:
        key, val = km.group(1), km.group(2)
        keys.append(key)
        if key == "name":
            name = val.strip()
        elif key == "description":
            if val.strip() in (">-", ">", "|", "|-"):
                i += 1
                while i < len(fm) and (fm[i].startswith("  ") or fm[i] == ""):
                    desc.append(fm[i].strip()); i += 1
                continue
            desc = [val.strip().strip('"')]
    i += 1
description = " ".join(d for d in desc if d)
allowed = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
extra = set(keys) - allowed
if extra: errs.append(f"chave(s) nao permitida(s): {sorted(extra)}")
if not name: errs.append("name ausente")
elif not re.match(r"^[a-z0-9-]+$", name) or name.startswith("-") or name.endswith("-") or "--" in name:
    errs.append(f"name '{name}' nao e kebab-case")
elif name != folder: errs.append(f"name '{name}' != pasta '{folder}'")
if not description: errs.append("description ausente")
else:
    if "<" in description or ">" in description: errs.append("description contem < ou >")
    if len(description) > 1024: errs.append(f"description com {len(description)} chars (max 1024)")
print("\n".join(errs) if errs else f"ok name={name} desc={len(description)} chars")
sys.exit(1 if errs else 0)
EOF
)"; rc=$?
  if [ "$rc" = 0 ]; then ok "$out"; else while IFS= read -r l; do nok "$l"; done <<<"$out"; fi
  n="$(find "$dir" -name SKILL.md -not -path '*/__pycache__/*' -not -path '*/node_modules/*' -not -path "$dir/evals/*" | wc -l)"
  if [ "$n" = 1 ]; then ok "exatamente um SKILL.md"; else nok "$n SKILL.md dentro de $skill (esperado 1)"; fi
done
[ "$found" -gt 0 ] || nok "nenhuma tooling/*/SKILL.md encontrada"

echo; echo "passed=$pass failed=$fail"
[ "$fail" = 0 ]
