---
title: Let truthful all-unknown token rows pass the ledger lifecycle gate
status: backlog
source: blocked n9 at the accepted-validation boundary after PR #81 landed, 2026-07-29
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: s6943mgrss28mygnm1wjb408
---

PR #81 made accepted validation upsert and verify a complete ledger row before the product PR. The shipped contract contradicts itself for runtimes that expose no per-dispatch token usage: `docs/dev/README.md:1149-1152` says an all-unknown set is recorded as `tokens_if_known=n/a`, while `ledger_verify` at `README.md:1295-1315` accepts only numeric token notation and the later bar text at `README.md:1569-1571` says a done transition may not leave tokens at `n/a`.

For n9, all five Codex dispatches truthfully recorded `tokens: n/a (Codex runtime did not expose per-worker usage)`. Substituting `0+` or an invented number would make the ledger pass by falsifying its evidence. The captain approved the contract direction: an all-unknown `n/a` row is complete and terminalizable, but excluded from baseline and bar comparisons; blank or missing evidence remains incomplete.

**AC-1 — A fully instrumented all-unknown token row passes both ledger lifecycle phases without inventing a number.**
Verified by: extending the disposable ledger fixture with one `tokens_if_known=n/a` row that returns `ledger:exact` in `premerge`, then finalizes its sentinels and returns `ledger:exact` in `terminal`. Falsified by: either phase returning 43.

**AC-2 — Missing token evidence still fails closed.**
Verified by: a distinct fixture row with a blank token cell still returns 43 in `premerge`; the change must not make blank, malformed, or duplicate rows valid. Falsified by: any such row returning 0.

**AC-3 — The prose and executable gate state the same policy.**
Verified by: the lifecycle text says all-unknown `n/a` is complete but excluded from baselines, and no remaining done-transition clause forbids the value the roll-up clause requires. Falsified by: a contradictory `done` prohibition or baseline inclusion claim remaining.
