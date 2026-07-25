---
id: 24dgw0cqh3bs3p895b8qehfz
title: Vendor a fixture corpus so measured ACs reproduce off this machine
status: backlog
source: FO finding while gating xn/3t/gz, 2026-07-25 — captain agreed the harnesses should NOT be committed, which leaves the limitation standing and worth its own entity
started:
completed:
verdict:
worktree:
issue:
pr:
design:
---

## Problem

Sprint-1's compiler entities (xn, 3t, gz) all carry value ACs verified by running the real
resolver over a 100-flow corpus. Every one of those ACs is machine-local and cannot be
reproduced by anyone else, or by CI.

Two independent reasons:

1. The harnesses live in `.context/`, which is git-excluded. Deliberately so — see below.
2. `flow-corpus.txt` is 3286 absolute paths under `/Users/kent/Project` and
   `/Users/kent/conductor`, i.e. flow files belonging to other repos on one machine.

Reason 2 is the binding one. Committing the harnesses was considered and rejected at xn's
close: it would make the ACs *look* CI-reproducible while still failing on a fresh clone,
which is worse than an honest gap. The affected entity bodies now state the limitation
explicitly instead.

The real fix, if it is worth doing, is a small fixture corpus vendored into the repo —
enough real flow shapes to exercise the resolver's pattern table, ambiguity path, and
page-qualifier behaviour — so the measured ACs can run in CI against a stable input.

Open question this entity must answer first: whether that is worth it. A vendored fixture
drifts from the live corpus, and the numbers that made xn/3t/gz decidable (368 deferred,
630 errors, 9 tier-1 repairable, 20 of 100 flows clean) came precisely from the *real*
distribution. A fixture that is easy to maintain may be too clean to catch what the live
corpus caught. Consider whether the honest scope is "CI-reproducible regression fixture"
rather than "replacement for the measurement corpus" — the two are different jobs.
