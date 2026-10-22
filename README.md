# claude-setup

My Claude Code setup: global `CLAUDE.md`, `settings.json`, subagents, plugins and skills, installable with one command.

## Prerequisites
- [Claude Code](https://docs.claude.com/en/docs/claude-code), `git`, `python3`
- Optional: [`bun`](https://bun.sh) for the gstack skills, [`uv`](https://docs.astral.sh/uv/) for graphify. The installer skips them, with a warning, if they're missing.

## Install
```bash
git clone https://github.com/PulkitBansal2/claude-setup.git ~/claude-setup
~/claude-setup/scripts/install.sh
```
Then start a new Claude Code session.

What the installer does:
- Symlinks `CLAUDE.md` and the agent folders into `~/.claude`, so the clone stays the source of truth.
- Writes `~/.claude/settings.json` from `settings.json`, replacing `__HOME__` with your home directory.
- Adds the plugin marketplaces and installs the enabled plugins listed in `settings.json`.
- Installs third-party skills from their upstream repos: gstack, graphify, apple-design-skill, grill-me, code-review, find-skills.

Your existing files are moved to `~/.claude/backups/install-<time>/`, never deleted. To undo:
```bash
~/claude-setup/scripts/uninstall.sh ~/.claude/backups/install-<time>
```

## Versions
Each version is a git tag. To switch, check out the tag and re-run the installer:
```bash
cd ~/claude-setup && git checkout v1-original && ./scripts/install.sh
```
| Tag | What it is |
|---|---|
| `v1-original` | The setup as it was before the lean rework |

Back to the newest version: `git checkout main && ./scripts/install.sh`.

## Keeping it in sync
`settings.json` is a rendered copy, because Claude Code rewrites it. Your personal `autoMode` block is never committed; the installer keeps the one already on your machine. After changing settings in Claude Code, run `scripts/sync.sh` to copy them back into the repo, then commit.

## Credits
Most persona agents come from [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) (MIT). Third-party skills and plugins are installed from their own repos, under their own licenses.
