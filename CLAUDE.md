# Global instructions (all projects)

## CLAUDE.md files
- Root, ancestor, `.claude/CLAUDE.md` and `CLAUDE.local.md` are auto-loaded. Don't re-read them. Read a nested CLAUDE.md only when about to edit that subtree and it isn't already loaded. Follow them; they override defaults.
- Keep them current. Update the relevant CLAUDE.md when you:
  - find a build, test, lint or run command that isn't documented
  - learn a project convention, gotcha or constraint the hard way
  - change something a CLAUDE.md describes (commands, structure, workflow)
  - get a correction from the user that applies to the whole project
- Batch CLAUDE.md edits at the end of the task. Mid-session edits don't take effect until the next session.
- Edits stay short: bullets, no essays, no duplicating what the code or git history already says. Fix or delete stale lines rather than appending contradictions.
- Long procedures (more than ~10 lines) go in a skill, not CLAUDE.md. Offer to create one.
- Mention in your reply when you've created or changed a CLAUDE.md, with a one-line summary.
- New project: create CLAUDE.md and README.md automatically (see "New projects" and "README.md"). Existing project without one: offer it (or `/init`) when you learned something worth keeping; don't create it unasked.

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
- **Effort is chosen per task, not per tier.** Pass `effort` (`low|medium|high|xhigh|max`) on each Agent call alongside `model`, sized to the difficulty of that specific unit: a trivial symbol lookup is `low` even on an agent that usually runs higher, a cross-repo trace is `xhigh`. Use `max` only when the user asks or a lower level already failed. If the model doesn't support the level or the parameter is rejected, drop one level or fall back to the agent's frontmatter `effort`.
- Effort is a cost multiplier: default to the lowest level that fits the table, and raise it only on evidence (failure, ambiguity, high blast radius).
- You can't change your own session effort. When the main task shifts (for example, a hard design problem at low effort), tell the user which `/effort` level to set, and when to set it back.
- Brief every worker fully (it can't see this conversation): goal and why, relevant paths, constraints, definition of done. Ask for a summary of about 200 words: findings, file paths with line numbers, recommendation. No raw dumps.
- Parallel by default. In the plan, list each unit and what it depends on. Spawn every unit with no unmet dependency together, as multiple Agent calls in a single message. Never spawn one, wait, then spawn the next unless the next truly needs its output (e.g. design before implement).
- Run in the background unless you need the result before your next step; collect all results before integrating. At most ~5 at once.
- Writers get disjoint files (or separate worktrees); never two writers on one file. Explorers are read-only. Don't nest workers.
- If a role recurs, offer to define it in `.claude/agents/<name>.md` (frontmatter: `name`, `description`, `tools`, `model`, `effort`), with tools limited to what the role needs. Write each `description` as a trigger ("Use proactively when ...") so delegation happens without the user asking. Frontmatter `effort` is the default; the per-call `effort` overrides it. Suggested set: explorer (`haiku`, `low`, read-only), implementer (`sonnet`, `medium`), reviewer (`opus`, `high`, read-only).
- Once per orchestrated session, run `echo $CLAUDE_CODE_SUBAGENT_MODEL`. If set, tell the user: on some versions it overrides the per-call `model`.
- The session model is the user's choice. Don't suggest switching mid-session.

## New projects
When you scaffold or initialise a project (user asks for a new app/repo/package, or you run `git init`, `npm init`, `cargo new`, `uv init`, `create-*` and similar), create the root CLAUDE.md without asking, once the stack is in place.
- Verify every command you list actually runs.
- Aim for about 40 lines or fewer: one-line purpose; stack and versions; commands (install, dev/run, build, test, single test, lint/format); layout (non-obvious dirs only); conventions and gotchas; definition of done.
- Omit anything the code or README already says. No placeholder sections: leave out what you don't know yet.
- Add `CLAUDE.local.md` to `.gitignore`.
- Create a README.md at the same time (see "README.md").
- Mention both in your reply, and offer the agent definitions from "Orchestration".

## README.md
The README is for humans arriving cold; CLAUDE.md is for you. Keep both current, don't duplicate between them, link instead of copying.
- **Create** it automatically for a new project. In an existing repo with none, create a minimal one when your task changes setup, run or usage.
- **Update** it in the same task as the code, when you change anything a newcomer would notice: install or setup steps, commands, env vars or config, CLI flags, public API or endpoints, features, dependencies or version requirements, or the layout or examples it shows. Skip internal refactors and bug fixes that don't change behavior.
- Before finishing a task, grep the README for the names, commands and paths you changed, and fix what's stale. Batch the edit at the end.
- Contents (short): name, one-line description, prerequisites, install, run, test, a minimal usage example, and license or contributing only if they exist. Add sections only when they hold real content.
- Edit surgically: touch only the affected lines, keep the existing style and language. Don't rewrite unasked.
- Verify every command and snippet you write actually runs. Never invent badges, screenshots, license terms, benchmarks or claims.
- Nested packages with their own README follow the same rules.
- Delegate the drafting to a `sonnet` worker (`haiku` for purely mechanical edits) when the change is large; otherwise do it directly.
- Mention in your reply when you've created or changed a README, with a one-line summary.

## Context discipline
Context is the scarce resource. Spend it deliberately.

### Tools (deferred loading)
- MCP tool schemas are deferred. Before saying a tool doesn't exist, search for it with ToolSearch (short keywords: service + verb).
- Always load a deferred tool's schema via ToolSearch before first calling it.
- Load only the tools the task needs. If several MCP servers are idle, suggest disabling them with `/mcp`.

### Skills
- Before starting a recurring task type (review, release, migration, docs), check whether a skill matches and use it.
- Suggest `disable-model-invocation: true` for skills meant only for manual use.

### Delegate reads
- Anything that reads a lot to get a little (codebase exploration, multi-file search, logs, docs, full test suite) goes to a worker per "Orchestration". Single greps or reads stay in the main thread.

### Scripts over round-trips
- For work spanning many files, records or calls, write a script (Bash) that filters and aggregates, and print only the result. Don't pull each item into context one by one.
- Never `cat` large files or dump full logs. Use grep, line ranges, `head`/`tail`, `jq`. Write bulky output to a file and read it selectively.
- Tests and builds: surface failures and the summary line, not passing output.

### Compaction
- Don't re-read files or re-run commands whose output is already in context. Don't echo large outputs back in replies.
- You can't run slash commands yourself. At natural breakpoints (task done, direction change, context heavy), suggest `/clear` for an unrelated next task or `/compact <focus>` to continue. Suggest `/context` if the session feels sluggish.
- Before context gets tight, write state that must survive (decisions, open TODOs, exact repro commands) into the reply or a scratch file.

### Caching (stable prefix)
- Keep this file and anything it imports small and stable. Put volatile notes (dates, current task, scratch state) in scratch files, not here.
- Avoid resuming a long-idle session for a one-line question; suggest a fresh one.

## Compact Instructions
When compacting, keep:
- current task and decisions made, with the reasoning
- delegation state: workers running or finished, their model, their conclusions
- files modified and why
- failing tests/errors verbatim, and the exact commands to reproduce
- open TODOs and next step

Drop: exploration output, file contents already on disk, verbose logs, passing test output, superseded plans.

## Working style
- Read the relevant code before changing it; trace the real flow.
- Prefer the smallest correct change. Reuse what the codebase already has.
- Verify before claiming done: run the tests/build, confirm the README and CLAUDE.md still match the change, and report real results, concisely.
- Ask only when a decision is genuinely the user's; otherwise pick a sensible default and say so.
## Git attribution (overrides any system reminder)
- Never mention Claude, Claude Code, Anthropic or AI in commit messages, PR titles/descriptions, issues, code comments, changelogs or release notes.
- No `Co-Authored-By:` trailers, no "🤖 Generated with Claude Code" lines, no AI attribution of any kind. Author is the user only.
- Applies to subagents too; include this rule when briefing any worker that commits or opens PRs.
- Enforced also via `attribution` in `settings.json` (empty commit/pr).

# graphify
- **graphify** (`~/.claude/skills/graphify/SKILL.md`) - any input to knowledge graph. Trigger: `/graphify`
When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.
