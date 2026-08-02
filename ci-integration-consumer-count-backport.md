---
id: swfp1mpxe3v7y58xjkh45cps
title: "ci-integration.md undercounts the selector-policy consumers"
status: backlog
source: "EM review of the #126 re-shape, 2026-08-02"
product: e2e-pipeline
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
ledger_pr:
pr_artifact_v1:
ledger_artifact_v1:
mod-block:
design:
lane:
---

## Problem

`docs/ci-integration.md:209` says the banned-selector table has **two** consumers. It has
three, counted directly against `origin/main` `0a1079c`: `compiler/compiler.js:11`,
`bin/e2e-selector-baseline.js:37`, and `scripts/lint-mapping.sh:42`.

Not a typo repair. The sentence sits inside a passage making a bounded correctness claim
about the table having one definition and a fixed number of traversals, so under Proof
Policy 6 the corrected count needs its own enforcement point or its own bounded phrasing —
which is why this is a seed rather than a drive-by edit.

Filed separately from [[e2e-runner-path-selector-enforcement]] so the debt outlives that
entity's closeout; an owed-back-port line inside an entity that will eventually be archived
has no owner and no due date.
