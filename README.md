# claude-setup

My Claude Code setup: global `CLAUDE.md`, `settings.json`, subagents, plugins and skills, installable with one command.

## Prerequisites
- [Claude Code](https://docs.claude.com/en/docs/claude-code), installed and logged in: `curl -fsSL https://claude.ai/install.sh | bash`, then run `claude` once
- `git`, `python3`
- Optional: [`bun`](https://bun.sh) for the gstack skills, [`uv`](https://docs.astral.sh/uv/) for graphify. The installer skips them, with a warning, if they're missing.

## Install
```bash
git clone https://github.com/PulkitBansal2/claude-setup.git ~/claude-setup
~/claude-setup/scripts/install.sh
```
Then start a new Claude Code session.

What the installer does:
- Symlinks `CLAUDE.md`, `agents/` (active subagents), `agents-archive/` (inactive, restorable) and the repo's own skills into `~/.claude`, so the clone stays the source of truth.
- Merges `settings.json` into your `~/.claude/settings.json`: your existing values (model, theme, permissions, env vars) win on conflicts, and hooks, plugins and lists are added alongside yours. Use `install.sh --replace` to write this version's settings exactly instead.
- Adds the plugin marketplaces and installs the enabled plugins listed in `settings.json`.
- Installs third-party skills from their upstream repos: gstack, graphify, apple-design-skill, grill-me, code-review, find-skills.
- Runs `scripts/hide-manual-skills.sh`, which keeps on-purpose-only gstack skills (`/ship`, `/retro`, …) out of automatic use. They still run when you type them. Re-run it after `/gstack-upgrade`.

Your existing files are moved to `~/.claude/backups/install-<time>/`, never deleted. To undo:
```bash
~/claude-setup/scripts/uninstall.sh ~/.claude/backups/install-<time>
```

## Versions
Each version is a git tag. To switch, check out the tag and re-run the installer:
```bash
cd ~/claude-setup && git checkout v1-original && ./scripts/install.sh --replace
```
| Tag | What it is |
|---|---|
| `v1-original` | The setup as it was before the lean rework: 89 active agents |
| `v2-lean` | 21 active agents (the rest in `agents-archive/`), a routing table in `CLAUDE.md`, manual-only skills hidden, auto-compact at 70% |
| `v2.1` | Installer merges settings into an existing setup instead of replacing them; clear message when Claude Code is missing |

Back to the newest version: `git checkout main && ./scripts/install.sh --replace`. Use `--replace` when switching versions, so settings from the other version aren't merged in.

To bring back an archived agent: `git mv agents-archive/<name>.md agents/`.

## Benchmark
`bench/run.py <label>` runs 10 fixed tasks headless against the installed setup (about $3–4 per run). `bench/compare.py <a> <b>` writes [`bench/results.md`](bench/results.md).

## Keeping it in sync
`settings.json` is a rendered copy, because Claude Code rewrites it. Your personal `autoMode` block is never committed; the installer keeps the one already on your machine. After changing settings in Claude Code, run `scripts/sync.sh` to copy them back into the repo, then commit.

## Credits
Most persona agents come from [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) (MIT). Third-party skills and plugins are installed from their own repos, under their own licenses.
