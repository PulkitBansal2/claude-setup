#!/usr/bin/env bash
# Install this Claude Code setup into ~/.claude.
# Anything it replaces is moved to ~/.claude/backups/install-<time>/ first (undo: scripts/uninstall.sh <that dir>).
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
C="$HOME/.claude"
BK="$C/backups/install-$(date +%Y%m%d-%H%M%S)"
LINKED="CLAUDE.md agents agents-archive agents-disabled agents-removed"
# settings.json: merged into yours by default (your values win on conflicts); --replace writes this version's exactly.
MODE=merge
[ "${1:-}" = "--replace" ] && MODE=replace

warn() { printf '  ! %s\n' "$*" >&2; }
have() { command -v "$1" >/dev/null 2>&1; }

for cmd in claude git python3; do
  have "$cmd" && continue
  echo "Missing required command: $cmd" >&2
  [ "$cmd" = claude ] && echo "Install Claude Code first: curl -fsSL https://claude.ai/install.sh | bash   (then run 'claude' once to log in)" >&2
  exit 1
done
mkdir -p "$C/skills" "$BK"

# Move a real file/dir out of the way; drop a stale symlink.
park() {
  local t="$1"
  if [ -L "$t" ]; then rm "$t"
  elif [ -e "$t" ]; then mkdir -p "$BK/$(dirname "${t#"$C"/}")"; mv "$t" "$BK/${t#"$C"/}"; fi
}

echo "== Linking files from $REPO"
for item in $LINKED; do
  if [ -e "$REPO/$item" ]; then
    [ "$(readlink "$C/$item" 2>/dev/null)" = "$REPO/$item" ] || { park "$C/$item"; ln -s "$REPO/$item" "$C/$item"; }
  elif [ -L "$C/$item" ] && [[ "$(readlink "$C/$item")" == "$REPO/"* ]]; then
    rm "$C/$item"   # left over from another version of this repo
  fi
done
# Own skills shipped in this repo; drop links to skills this version no longer has.
for link in "$C"/skills/*; do
  [ -L "$link" ] && [[ "$(readlink "$link")" == "$REPO/skills/"* ]] && [ ! -e "$link" ] && rm "$link"
done
if [ -d "$REPO/skills" ]; then
  for d in "$REPO"/skills/*/; do
    d="${d%/}"; t="$C/skills/$(basename "$d")"
    [ "$(readlink "$t" 2>/dev/null)" = "$d" ] || { park "$t"; ln -s "$d" "$t"; }
  done
fi

echo "== Writing settings.json ($MODE)"
[ -e "$C/settings.json" ] && cp "$C/settings.json" "$BK/settings.json"
python3 -I - "$REPO/settings.json" "$C/settings.json" "$HOME" "$MODE" <<'EOF'
import json, sys
src, dst, home, mode = sys.argv[1:]
ours = json.loads(open(src).read().replace("__HOME__", home))
try:
    theirs = json.load(open(dst))
except (OSError, ValueError):
    theirs = {}

def merge(mine, other):
    """Their value wins on conflicts; dicts merge key by key; lists are unioned without duplicates."""
    if isinstance(mine, dict) and isinstance(other, dict):
        out = dict(other)
        for k, v in mine.items():
            out[k] = merge(v, other[k]) if k in other else v
        return out
    if isinstance(mine, list) and isinstance(other, list):
        return other + [x for x in mine if x not in other]
    return other

if mode == "replace":
    result = ours
    if "autoMode" in theirs:  # personal, machine-specific: never shipped in the repo
        result["autoMode"] = theirs["autoMode"]
else:
    result = merge(ours, theirs)
open(dst, "w").write(json.dumps(result, indent=2) + "\n")
EOF

echo "== Plugins"
python3 -I - "$C/settings.json" > "$BK/.plugins" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
for m in d.get("extraKnownMarketplaces", {}).values():
    s = m.get("source", {})
    if s.get("source") == "github": print("M", s["repo"])
for p, on in d.get("enabledPlugins", {}).items():
    if on: print("P", p)
EOF
while read -r kind val; do
  if [ "$kind" = M ]; then claude plugin marketplace add "$val" >/dev/null 2>&1 || warn "marketplace $val (may already exist)"
  else claude plugin list 2>/dev/null | grep -q "❯ $val\$" || claude plugin install "$val" >/dev/null 2>&1 || warn "plugin $val failed"; fi
done < "$BK/.plugins"
rm "$BK/.plugins"

echo "== Third-party skills"
clone_skill() {  # repo, path inside repo ("" = whole repo), skill name
  local t="$C/skills/$3"; [ -e "$t" ] && return 0
  local tmp; tmp="$(mktemp -d)"
  if git clone -q --depth 1 "https://github.com/$1.git" "$tmp/r"; then
    if [ -n "$2" ]; then cp -r "$tmp/r/$2" "$t"; else mv "$tmp/r" "$t"; fi
  else warn "skill $3 ($1) failed"; fi
  rm -rf "$tmp"
}
clone_skill dickwu/apple-design-skill "" apple-design-skill
clone_skill mattpocock/skills skills/productivity/grill-me grill-me
clone_skill mattpocock/skills skills/engineering/code-review code-review
clone_skill vercel-labs/skills skills/find-skills find-skills

if [ ! -d "$C/skills/gstack" ]; then
  if have bun; then
    git clone -q --single-branch --depth 1 https://github.com/garrytan/gstack.git "$C/skills/gstack" \
      && (cd "$C/skills/gstack" && ./setup) || warn "gstack setup failed"
  else warn "bun not found: skipping gstack (install bun, then re-run)"; fi
fi

if ! have graphify; then
  if have uv; then uv tool install graphifyy >/dev/null || warn "graphify install failed"
  else warn "uv not found: skipping graphify (install uv, then re-run)"; fi
fi
[ -d "$C/skills/graphify" ] || { have graphify && graphify install --platform claude >/dev/null || warn "graphify skill not installed"; }

[ -x "$REPO/scripts/hide-manual-skills.sh" ] && "$REPO/scripts/hide-manual-skills.sh"

rmdir "$BK" 2>/dev/null && echo "Done. Nothing needed backing up." || echo "Done. Replaced files saved in $BK (undo: $REPO/scripts/uninstall.sh $BK)"
echo "Start a new Claude Code session to load the setup."
