---
id: 322pn9wktdnekgdw8fsw767r
title: "No CI job runs the e2e-pipeline test suite"
status: backlog
source: "found while assembling PR #135 evidence, 2026-08-01"
product: repo-platform
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

`e2e-pipeline` carries 949 tests and nothing in `.github/workflows/` runs them — grepped
across that directory, zero workflow files reference `e2e-pipeline`; `review-runtime-tests.yml`
is scoped to `kc-pr-flow/**`. That directory is the population for workflow-defined jobs, but
it is one tool over one path and no second strategy was run.

Separately, and read live from the platform API on 2026-08-01 rather than from workflow
files: `main` requires exactly **one** status context, `version parity (plugin.json /
marketplace.json / codex / README)`. GitGuardian runs on PRs but is **not** a required
context. Runs and is-required are different facts, and the ideation clause exists because
reading `.github/workflows/` conflates them.

The consequence is not hypothetical. The regression test that should have caught the #135
socket defect asserted against the same `daemon.sock` literal the implementation used, so
it could only confirm the code agreed with itself — and no CI run would have exposed that
either way.

One caveat for ideation rather than a blocker: this specific defect class is macOS-specific
(Linux `sun_path` is 108 bytes), so a Linux runner would have passed before and after the
fix. A CI job is worth having on its own merits; it should not be justified by this defect.
