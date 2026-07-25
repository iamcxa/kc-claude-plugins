---
id: fnebte1v31r1x3s26784fv90
title: Give executable diffs a diff-coverage ratchet
status: backlog
source: captain decision at xn's validation gate, 2026-07-25 — coverage was waived there because no tooling exists; filed as its own entity per the README's last-resort rule for standing enforcement
started:
completed:
verdict:
worktree:
issue:
pr:
design:
---

## Problem

The README requires an 85% diff-coverage bar on lines a task adds or changes to executable
surfaces (`scripts/`, hooks, compiler JS, MCP code), and says "the bootstrap task decides the
tooling". No tooling exists, so the bar has never actually been enforced — xn's validation
gate had to waive it and substitute a manual "these lines are exercised by these tests" check.

Smallest sufficient shape, if this is built: `node --test --experimental-test-coverage` over
`e2e-pipeline/compiler/`, plus a script intersecting its line data with
`git diff --unified=0 <trunk>...HEAD` ranges, failing under 85%. No new dependency, no new CI
vendor. Explicitly NOT in scope: bash coverage (kcov/bashcov) for `scripts/` and `hooks/` —
those are thin and I/O-dominated, and the harness would cost more than it catches.

Open question this entity must answer before building anything: whether the ratchet earns its
keep at all. xn's evidence argues the adversarial spot-check (claim-breaking edit -> suite must
go red) is strictly stronger than a coverage number, since a line can be covered without being
asserted. Do not build until a real executable diff is large enough that per-line review stops
being credible.
