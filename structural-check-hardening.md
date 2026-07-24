---
id: c34e06qvceahcykvs7hqcjgk
title: Structural check hardening (validation residuals)
status: backlog
source: validation residuals, workflow-verification-bootstrap (te82apnehg989v4enz9e6wf6), 2026-07-24
started:
completed:
verdict:
worktree:
issue:
pr:
design:
---

Three named residuals from the bootstrap task's validation stage (see
`_archive/workflow-verification-bootstrap.md`, `### Residuals`). All fail in
the safe direction (over-strict false-reject or local-dev-only noise) — none
reaches a fail-open path in this repo's CI. Optional hardening, low priority.

1. Hand-rolled frontmatter parser mishandles an embedded `---` inside a
   block-scalar description and a bare multi-line plain scalar (both
   false-reject direction; zero occurrences across today's 35 SKILL.md files).
2. `os.walk` in the skill-frontmatter lint lacks a `.worktrees` exclusion —
   local-dev count inflation (35→105 reproduced), invisible to CI's fresh
   checkout.
3. Enumeration assumes directory-name == marketplace `name` and single-level
   plugin dirs — pre-existing convention (commit 82140138), consistent with
   today's 6 plugins.

## Acceptance criteria

**AC-1 — Each residual is either closed with a RED-first fixture or explicitly re-accepted with a recorded rationale.**
Verified by: per-residual fixture failing before / passing after the fix, or a named re-acceptance line in the stage report. Falsified by: a residual neither fixed nor re-accepted.
