---
name: new-project
description: Use when scaffolding or initialising a project (a new app/repo/package, or running git init, npm init, cargo new, uv init, create-* and similar). Creates the root CLAUDE.md and README.md once the stack is in place.
---

# New project

When you scaffold or initialise a project, create the root CLAUDE.md without asking, once the stack is in place.

- Verify every command you list actually runs.
- Aim for about 40 lines or fewer: one-line purpose; stack and versions; commands (install, dev/run, build, test, single test, lint/format); layout (non-obvious dirs only); conventions and gotchas; definition of done.
- Omit anything the code or README already says. No placeholder sections: leave out what you don't know yet.
- Add `CLAUDE.local.md` to `.gitignore`.
- Create a README.md at the same time, following the README rules in the global CLAUDE.md (name, one-line description, prerequisites, install, run, test, minimal usage example; verified commands only).
- Mention both files in your reply, and offer agent definitions for recurring roles: explorer (`haiku`, `low`, read-only), implementer (`sonnet`, `medium`), reviewer (`opus`, `high`, read-only), each with a trigger-style `description` ("Use proactively when ...").
