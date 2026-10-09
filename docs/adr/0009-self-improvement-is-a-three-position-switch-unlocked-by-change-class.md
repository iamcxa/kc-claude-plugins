# 0009. Self-improvement is a three-position switch, unlocked by change class

Date: 2026-10-09

## Status

Accepted

## Context

kc-dev-flow-2 improves itself by hand today. Problems surface in dogfooding, session
debriefs, `learn` no-change reasons, the manual FO-write reader trial (#569) and external
review. The Captain then approves an issue, a fix is written, and he merges it. On
2026-10-08/09 this loop shipped 0.10.5 to 0.12.0 and fixed eight package issues. Two
measurements bear on automating it:

- SWE-CC (arXiv 2610.06193) finds that agents violate 43.1% of applicable repository
  policies even when their code is correct, with nearly half the violations in the
  process, not the diff. The reader trial saw the same pattern in 14 observations.
- GTDD (arXiv 2610.02952) separates development feedback from acceptance evidence. In
  the roborev trial, a worker ran the local reviewer 12 times until it reported nothing.
  The Codex bot, which that worker never iterated against, then found nothing in one
  round.

## Decision

**Words:** 「這個架構：『自動發現問題 → 自動修 → 自動合併』我希望可以達成，它應該要是一個開關，分為手動（現在），半自動（自我發現自動修），全自動（加上自動合併）」; 「這個架構不是現在要做的，但是應該要是 dev2 的前進方向」; 「原則上我同意 「依類型解鎖」這個做法」 — Captain, chat, 2026-10-09.

**Options considered:**
- one switch for all package changes
- per change class: full-auto unlocks per class, from the Captain's own record (chosen)

**Recommended:** per change class

Package self-improvement runs in one of three positions, which the Captain sets:

- **manual** (current): people discover problems; the Captain approves each issue and
  merges.
- **semi-auto**: problems are discovered and filed automatically, and a worker writes
  the fix as a Draft PR. The Captain merges.
- **full-auto**: semi-auto plus automatic merge, only for change classes that are
  unlocked.

A change class is defined by what a change touches, not by which repository reported
the problem. Two examples: a script defect with a failing test, or an adopter workflow
sync. A class unlocks for full-auto only after its recent semi-auto PRs were merged by
the Captain unchanged and with no `Override:` against them, with N set when the
mechanism is built. It falls back to semi-auto on any regression or override. Changes
to authority, approval or merge rules, and to this switch itself, never unlock.
Before any automatic merge, a deterministic policy gate (CI, the package lints, tests)
must pass, and a reviewer the fixing worker never iterated against must report no P1 or
P2 finding.

## Consequences

Nothing here is built. Semi-auto first needs a trigger at task close; closure is a
Spacedock event, not a harness event, and that question is open. Full-auto per class
needs the `Override:` and `**Recommended:**` records from 0.11.0 to accumulate before
any class can show a track record. Until then the position is manual, and merging stays
the Captain's. Reopen this record if the per-class record cannot be measured, or if an
unlocked class ships a regression the policy gate did not catch.
