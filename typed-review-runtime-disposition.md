---
title: Decide the smallest justified typed review runtime
status: backlog
product: kc-pr-flow
sprint:
source: Captain direction after review-runtime cost audit, 2026-08-18
design: required
started:
worktree:
id: ks0xngwyrxwddpa5f355twkq
---

The optional typed review subsystem ships shadow receipts, typed coverage and
decision derivation, paired measurement, merge-readiness synthesis, and
once-only posting. All activation flags are off by default. No repository or
Relay adopter configuration was found, and the local state root contained no
receipts during the 2026-08-18 audit. The implementation, tests, benchmarks,
posting path, and retained documentation together exceed eleven thousand lines.

Decide the capability before optimizing its current implementation. Treat
shadow receipt, typed decision, paired benchmark, merge readiness, and
once-only posting as separate value surfaces. Select one explicit disposition:
retire the dormant subsystem, retain only independently justified surfaces, or
promote a smaller runtime backed by a named adopter and real dogfood evidence.

This is a backlog decision task only. Filing it authorizes no implementation,
activation, runtime mutation, test deletion, sprint admission, or release.

## Acceptance criteria

**AC-1 — Usage and authority are established from live evidence.** Verified by:
an inventory of adopter flags, actual receipts, executable callers, and default
behavior across the source repo plus named adopters. Falsified by: documentation
or code presence is treated as adoption.

**AC-2 — Each value surface receives an independent disposition.** Verified by:
shadow receipt, typed decision, paired benchmark, merge readiness, and
once-only posting are each marked retire, retain, or promote with incident or
usage evidence. Falsified by: the subsystem is kept or removed as one
indivisible historical bundle.

**AC-3 — A retained surface proves user value, not only synthetic correctness.**
Verified by: a named adopter and one bounded real `/kc-pr-review` journey proving
the claimed recovery, coverage, posting, or cost benefit. Falsified by: green
fixtures alone justify continued production ownership.

**AC-4 — The selected result has a measurable maintenance boundary.** Verified
by: retained code, tests, CI wall-time budget, rollback behavior, and default
activation are explicit; retirement removes public claims and dead adapters
together. Falsified by: tests are deleted while risky shipped code remains, or
dormant code remains without an owner and activation plan.
