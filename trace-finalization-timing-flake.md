---
id: 2wwrfw2b8tpp2xh5d5hkd636
title: "trace-finalization.test.js:445 fails under parallel load and passes in isolation"
status: backlog
source: "observed by EM while validating PR #135, 2026-08-01"
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

`compiler/test/trace-finalization.test.js:445` ("bounded recovery must run after timeout")
asserts on a 5.4 second wall-clock budget. It failed once during a full-suite run under
load and then passed 3/3 in isolation and on a clean full run.

A wall-clock assertion that depends on machine load reddens for reasons unrelated to the
behavior it guards, which trains readers to retry rather than diagnose.

Whether #135 contributed is **not established**. The file itself was not edited by that
change, but that is evidence about the file, not about the failure: #135 added tests, which
changes full-suite load, and load is exactly what this assertion is sensitive to. Settling
it needs per-failing-line blame against #135's commit range, which was not run.
