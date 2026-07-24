---
id: te82apnehg989v4enz9e6wf6
title: Workflow verification bootstrap
status: backlog
source: commission seed (lean SD workflow, 2026-07-24)
started:
completed:
verdict:
score: 0.7
worktree:
issue:
pr:
design:
---

Stand up this plugin monorepo's mechanical floors. Unlike a code repo, the
floor here is STRUCTURAL, not coverage: (1) audit what structural checks
already exist (marketplace sync tooling, sanitize-check, .githooks, CI
workflows) and wire a blocking plugin-structure lint — plugin.json manifest
validity and version consistency, marketplace manifest agreement, skill
frontmatter validity — fail-closed: a plugin directory missing required
manifest fields must go red, never silently skipped. (2) Initialize
`docs/dev/ledger.csv` with the measurement header. (3) Decide diff-coverage
feasibility for the thin executable layer (scripts/, hooks) and record the
determination either way.

## Acceptance criteria

**AC-1 — A blocking structural lint runs in CI and fails on a manifest/frontmatter defect.**
Verified by: a probe with a deliberately broken plugin manifest (or missing required frontmatter) shows the check red in a real CI run. Falsified by: the probe passes, or the check silently skips unknown plugin directories.

**AC-2 — ledger.csv exists with the schema header and the first row lands with this task.**
Verified by: `head -1 docs/dev/ledger.csv` matches the README's ledger schema byte-for-byte. Falsified by: header drift or missing file.
