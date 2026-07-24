---
id: fdkcs3m8jp2wnxh8bfd1cgzq
title: PRODUCT.md + ARCHITECTURE.md baseline
status: ideation
source: commission seed (lean SD workflow, 2026-07-24)
started: 2026-07-24T08:52:51Z
completed:
verdict:
score: 0.6
worktree:
issue:
pr:
design:
---

This repo has CLAUDE.md conventions but no PRODUCT.md or ARCHITECTURE.md,
and the workflow's doc-diff clause needs canonical docs to diff against.
Produce lightweight baselines describing the monorepo as it is: what each
plugin ships and for whom (PRODUCT), and the real structure — plugin layout,
marketplace publish flow, hooks/scripts surfaces, versioning scheme
(ARCHITECTURE). As-is only, no aspiration.

## Acceptance criteria

**AC-1 — Both files exist and describe the repo as it is.**
Verified by: every named plugin/surface spot-checked against a real directory or file:line. Falsified by: a described component with no corresponding artifact.
