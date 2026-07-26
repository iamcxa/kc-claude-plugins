---
id: szjpa5vnv5mhpmkh07s03j11
title: Five tracked tests only pass on one laptop, and CI would never notice
status: backlog
source: surfaced 2026-07-26 when 3t's validation ran on the mac mini instead of the MacBook — invisible while everything ran on one machine
started:
completed:
verdict:
worktree:
issue:
pr:
design:
---

## Problem

`e2e-pipeline/compiler/test/integration.test.js` hardcodes absolute paths into a different
project:

    var CORPUS_FLOW    = '/Users/kent/Project/carlove/.claude/e2e/flows/gate-login-flow.yaml';
    var CORPUS_MAPPING = '/Users/kent/Project/carlove/.claude/e2e/mappings';

Five tests under `Integration: migrate + compile real carlove flow` depend on them. On the
machine where `carlove` is checked out they pass; anywhere else the suite reports 654/659 with
five failures that read exactly like a regression in whatever change is being reviewed.

**Nothing catches this.** `grep -rn 'npm test' .github/workflows/` returns nothing — the
e2e-pipeline suite never runs in CI at all, so the defect has no way to surface through the
normal path.

It surfaced only because a validation leg ran on the mac mini, which has the plugin repo but not
`carlove`. On a single laptop this is structurally invisible.

Why it is worse than the sibling `.context/` limitation already filed as
[[corpus-fixture-for-reproducible-acs]]: that corpus is honestly git-excluded and the ACs
relying on it disclose the constraint. These five are ordinary tracked tests inside `npm test`,
so a reviewer on any other machine sees red and has no signal distinguishing "your change broke
it" from "you are not Kent".

Two independent defects here, and ideation should decide whether they are one entity or two:
1. Tests that reach outside the repo for fixtures. Options: vendor a fixture, skip with a clear
   reason when the path is absent, or read the path from an env var that defaults to skip.
2. A test suite that CI never runs, which is why (1) survived. Fixing (1) without (2) leaves the
   next instance equally invisible.

Do not fold this into the [[corpus-fixture-for-reproducible-acs]] entity without deciding
deliberately — that one is about measurement harnesses being machine-local by nature, which is
an accepted limitation. This one is about tracked tests lying, which is not.
