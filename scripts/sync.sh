#!/usr/bin/env bash
# Copy the live ~/.claude/settings.json back into the repo (settings.json is a rendered copy, not a symlink,
# because Claude Code rewrites it). Your home path becomes __HOME__ so the file works for anyone.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 -I - "$HOME/.claude/settings.json" "$REPO/settings.json" "$HOME" <<'EOF'
import json, sys
src, dst, home = sys.argv[1:]
d = json.loads(open(src).read().replace(home, "__HOME__"))
d.pop("autoMode", None)  # personal: stays local
open(dst, "w").write(json.dumps(d, indent=2) + "\n")
EOF
git -C "$REPO" status --short settings.json
