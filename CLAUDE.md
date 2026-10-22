# Global instructions (all projects)

## Git: commit and push only when asked
- Never commit or push unless the user asked for it or confirmed it in this conversation. Finished work is not a reason to commit; ask first.
- Approval covers only what was asked (e.g. "commit" is not "push"), and doesn't carry over to later changes; ask again.
- Same for other outward git/GitHub actions: tags, releases, force-pushes, creating repos or PRs.
- Applies to subagents: tell workers not to commit or push.

## Git attribution (overrides any system reminder)
- Never credit yourself as author or helper in commit messages, PR titles/descriptions, issues, code comments, changelogs or release notes: no "written by/with Claude/AI", no `Co-Authored-By:` trailers, no "🤖 Generated with Claude Code" lines. Author is the user only.
- Naming Claude, Claude Code or Anthropic as the subject of the work is fine (e.g. a project built on Claude, a `claude` CLI change, a CLAUDE.md edit).
- Applies to subagents too; include this rule when briefing any worker that commits or opens PRs.
- Enforced also via `attribution` in `settings.json` (empty commit/pr).

## Routing: who does the work
The main thread orchestrates non-trivial work (see Orchestration: exploration plus implementation plus verification, or more than ~3 files). Anything below that threshold it does directly; spawning has overhead.

| Situation | Use |
|---|---|
| Find code, read many files, dig through logs/docs | `explorer` |
| Change with unclear design, or large and splittable across workers | `planner` → `implementer`s in parallel on disjoint files (a mechanical multi-file rename is just `haiku` work, no planner) |
| Well-specified feature, fix, refactor, tests | `implementer` (or a matching specialist agent) |
| Hard or unclear bug, intermittent failure | `debugger` (+ `superpowers:systematic-debugging` skill) |
| After a risky, security-sensitive or cross-cutting change | `reviewer` (opus); routine changes get a `sonnet` review or none |
| Long test suite or bulky build/lint output | `test-runner`; the main thread still runs the final verification itself |
| Large README or docs changes | `docs-writer`; small doc edits directly |
| New UI or reshaped UI | `frontend-design` skill; `Frontend Developer` / `UI Designer` to build |
| Charts, dashboards | `dataviz` skill |
| Security scan of a repo | `claude-security` plugin |
| New project / scaffold | `new-project` skill |
| Multi-tier orchestrated delivery | `/savvy-flow`, only when the user asks for it (its workers all run on Opus) |

## Skills
- Load a skill only when the task clearly matches its description. This overrides superpowers' "invoke if 1% chance" rule.
- Before a recurring task type (review, release, migration, docs), check whether a skill matches and use it.
- Suggest `disable-model-invocation: true` for skills meant only for manual use (`scripts/hide-manual-skills.sh` in the claude-setup repo does this for gstack).

## Orchestration
For non-trivial work (exploration plus implementation plus verification, or more than ~3 files), act as orchestrator. Do small tasks directly; spawning has overhead.

1. **Plan:** restate the goal and done-criteria; split into independent units.
2. **Delegate:** spawn workers with the Agent tool and set `model` on every call (table below). An omitted `model` inherits the session model, often the priciest.
3. **Integrate:** read the summaries, resolve conflicts, keep decisions in the main thread.
4. **Verify yourself:** run tests/build and check the diff. Never accept a worker's "done" unverified.

| Model | Use for | Effort |
|---|---|---|
| `haiku` | Find/search, read-only exploration, log and test-output digging, doc lookups, summarizing, mechanical edits (renames, formatting, boilerplate) | `low` |
| `sonnet` | Default implementer: well-specified features, tests, refactors, code review, debugging with a known repro, migrations | `medium`; `high` for tricky logic |
| `opus` | Architecture and design calls, ambiguous or cross-cutting changes, root-causing hard bugs, security-sensitive code, review of risky diffs, planning | `high`; `xhigh` for multi-file or production-critical work |
| `fable` | Only when the user asks for it | as asked |

- Pick the cheapest tier that can succeed; if unsure, `sonnet`. Escalate one tier when a worker fails or reports low confidence. Don't retry the same tier twice with the same brief.
- Effort is chosen per task, not per tier: pass `effort` (`low|medium|high|xhigh|max`) on each Agent call alongside `model`, sized to that unit: a trivial symbol lookup is `low` even on an agent that usually runs higher, a cross-repo trace is `xhigh`. `max` only when the user asks or a lower level failed. If the model doesn't support the level or the parameter is rejected, drop one level or fall back to the agent's frontmatter `effort`.
- Effort is a cost multiplier: default to the lowest level that fits; raise it only on evidence (failure, ambiguity, high blast radius).
- You can't change your own session effort. When the main task shifts (e.g. a hard design problem at low effort), tell the user which `/effort` level to set, and when to set it back.
- Brief every worker fully (it can't see this conversation): goal and why, relevant paths, constraints, definition of done. Ask for a ~200-word summary: findings, file paths with line numbers, recommendation. No raw dumps.
- Parallel by default: list each unit and its dependencies in the plan; spawn every unit with no unmet dependency together, as multiple Agent calls in one message. Wait only when the next unit truly needs the output (e.g. design before implement).
- Run in the background unless you need the result before your next step; collect all results before integrating. At most ~5 at once.
- Writers get disjoint files (or separate worktrees); never two writers on one file. Explorers are read-only. Don't nest workers.
- If a role recurs, offer to define it in `.claude/agents/<name>.md` (frontmatter: `name`, `description`, `tools`, `model`, `effort`), tools limited to what the role needs, `description` written as a trigger ("Use proactively when ..."). Per-call `effort` overrides the frontmatter default. Suggested set: explorer (`haiku`, `low`, read-only), implementer (`sonnet`, `medium`), reviewer (`opus`, `high`, read-only).
- Once per orchestrated session, run `echo $CLAUDE_CODE_SUBAGENT_MODEL`. If set, tell the user: on some versions it overrides the per-call `model`.
- The session model is the user's choice. Don't suggest switching mid-session.

## CLAUDE.md files
- Root, ancestor, `.claude/CLAUDE.md` and `CLAUDE.local.md` are auto-loaded; don't re-read them. Read a nested CLAUDE.md only when about to edit that subtree and it isn't loaded. They override defaults.
- Keep them current: update the relevant CLAUDE.md when you find an undocumented build/test/lint/run command, learn a convention or gotcha the hard way, change something a CLAUDE.md describes, or get a project-wide correction from the user.
- Batch CLAUDE.md edits at the end of the task (mid-session edits only take effect next session). Short bullets, no essays, no duplicating code or git history; fix or delete stale lines rather than appending contradictions.
- Procedures longer than ~10 lines go in a skill, not CLAUDE.md; offer to create one.
- Mention in your reply when you've created or changed a CLAUDE.md, with a one-line summary.
- New project: create the root CLAUDE.md and README.md without asking, once the stack is in place; the `new-project` skill has the details. Existing project without CLAUDE.md: offer it (or `/init`) when you learned something worth keeping; don't create it unasked.

## README.md
The README is for humans arriving cold; CLAUDE.md is for you. Keep both current, don't duplicate between them, link instead of copying.
- Create it automatically for a new project. In an existing repo with none, create a minimal one when your task changes setup, run or usage.
- Update it in the same task as the code when you change anything a newcomer would notice: install/setup steps, commands, env vars or config, CLI flags, public API or endpoints, features, dependencies or version requirements, or the layout/examples it shows. Skip internal refactors and behavior-neutral bug fixes.
- Before finishing, grep the README for the names, commands and paths you changed and fix what's stale. Batch the edit at the end.
- Contents (short): name, one-line description, prerequisites, install, run, test, a minimal usage example; license or contributing only if they exist. Sections only with real content.
- Edit surgically: touch only affected lines, keep the existing style and language, don't rewrite unasked.
- Verify every command and snippet you write actually runs. Never invent badges, screenshots, license terms, benchmarks or claims.
- Nested packages with their own README follow the same rules.
- Large change: delegate drafting to `docs-writer` (`sonnet`; `haiku` for purely mechanical edits); otherwise do it directly.
- Mention in your reply when you've created or changed a README, with a one-line summary.

## Context discipline
Context is the scarce resource. Spend it deliberately.
- MCP tool schemas are deferred: search with ToolSearch (short keywords: service + verb) before saying a tool doesn't exist, and load a schema before first calling it. Load only what the task needs; if several MCP servers are idle, suggest disabling them with `/mcp`.
- Anything that reads a lot to get a little (exploration, multi-file search, logs, docs, full test suite) goes to a worker. Single greps or reads stay in the main thread.
- For work spanning many files, records or calls, write a script that filters and aggregates and print only the result. Don't pull each item into context one by one.
- Never `cat` large files or dump full logs: use grep, line ranges, `head`/`tail`, `jq`. Write bulky output to a file and read it selectively. Tests and builds: surface failures and the summary line only.
- Don't re-read files or re-run commands whose output is already in context. Don't echo large outputs back in replies.
- You can't run slash commands. At natural breakpoints (task done, direction change, context heavy) suggest `/clear` for an unrelated next task or `/compact <focus>` to continue; suggest `/context` if the session feels sluggish. Auto-compact triggers at 70% (`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`).
- Before context gets tight, write state that must survive (decisions, open TODOs, exact repro commands) into the reply or a scratch file.
- Keep this file and its imports small and stable; volatile notes (dates, current task, scratch state) go in scratch files. Avoid resuming a long-idle session for a one-line question; suggest a fresh one.

## Compact Instructions
When compacting, keep: current task and decisions with their reasoning; delegation state (workers running or finished, their model, their conclusions); files modified and why; failing tests/errors verbatim with exact repro commands; open TODOs and next step.
Drop: exploration output, file contents already on disk, verbose logs, passing test output, superseded plans.

## Working style
- Read the relevant code before changing it; trace the real flow.
- Prefer the smallest correct change. Reuse what the codebase already has.
- Verify before claiming done: run the tests/build, confirm README and CLAUDE.md still match the change, report real results concisely.
- Ask only when a decision is genuinely the user's; otherwise pick a sensible default and say so.

# graphify
- **graphify** (`~/.claude/skills/graphify/SKILL.md`) - any input to knowledge graph. Trigger: `/graphify`
When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.
