#!/usr/bin/env bash
# Hide on-purpose-only skills from automatic invocation: their descriptions leave the model's context,
# and they still run when you type /<name>. Safe to re-run; run again after gstack-upgrade.
set -euo pipefail

SKILLS="$HOME/.claude/skills"
MANUAL="
_gstack-command autoplan benchmark-models canary codex connect-chrome context-restore context-save cso
design-shotgun devex-review freeze unfreeze guard careful gstack-upgrade ios-clean ios-sync investigate
land-and-deploy landing-report learn office-hours open-gstack-browser pair-agent plan-ceo-review
plan-design-review plan-devex-review plan-eng-review plan-tune retro review setup-browser-cookies
setup-deploy setup-gbrain ship skillify sync-gbrain
"

hidden=0
for name in $MANUAL; do
  f="$SKILLS/$name/SKILL.md"
  [ -f "$f" ] || continue
  grep -q '^disable-model-invocation:' "$f" && continue
  # Insert the flag right after the opening '---' of the frontmatter.
  python3 -I - "$f" <<'EOF'
import sys
p = sys.argv[1]; s = open(p).read()
if s.startswith("---\n"):
    open(p, "w").write("---\ndisable-model-invocation: true\n" + s[4:])
EOF
  hidden=$((hidden + 1))
done
echo "== Manual-only skills: $hidden newly hidden"
