#!/usr/bin/env bash
# Remove this setup's links from ~/.claude and restore a backup made by install.sh.
# Usage: scripts/uninstall.sh ~/.claude/backups/install-<time>
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
C="$HOME/.claude"
BK="${1:?usage: $0 <backup dir from install.sh>}"
[ -d "$BK" ] || { echo "No such backup: $BK" >&2; exit 1; }

# Drop every symlink that points into this repo.
for link in "$C"/* "$C"/skills/*; do
  [ -L "$link" ] && [[ "$(readlink "$link")" == "$REPO/"* ]] && rm "$link"
done

# Put the backed-up files back.
shopt -s nullglob dotglob
for src in "$BK"/* "$BK"/skills/*; do
  rel="${src#"$BK"/}"; [ "$rel" = skills ] && continue
  if [ "$rel" = settings.json ]; then cp "$src" "$C/settings.json"
  elif [ ! -e "$C/$rel" ]; then mkdir -p "$C/$(dirname "$rel")"; cp -a "$src" "$C/$rel"; fi
done
echo "Restored from $BK. Plugins and third-party skills were left installed (remove with: claude plugin uninstall <name>)."
