---
title: Close six 0.15.1 workflow wording gaps found by Codex on qnow #1270
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined from round 2 of Codex's review of iamcxa/qnow#1270 (the 0.15.1 adopter sync, head c2bb84fd4, 2026-10-11), plus one gap the Captain discussed in this session. The Captain ruled 「可以」 (2026-10-11) on filing them here together, with an order, so that the 0.15.1 syncs merge without another release round. None is P1 or Material, and none lets a wrong change merge.

## Scope

First, because they bit or nearly bit:
- Reserved ADR numbers are not required at validation: `--since <base>` plus report-named `--require` misses an ADR that was reserved but neither written nor named. Build `--require` from the task's `## Number guards` `ADR:` lines (Codex P2; the same class as ADR 0022 missing 「也隱藏」 on 2026-10-10; this gap predates #590).
- After a repair push, the workflow never says to request `@codex review`, so `codex_review.py` stays at exit 4 and FO holds the merge ask (Codex P2; fails safe, but stalls).
- How FO tells whether Codex reviews a PR is unstated; on a repo without Codex the reader reports exit 4 forever. Treat a PR with no Codex trace at all as not Codex-reviewed (raised by the Captain in this session).
Then:
- The late-decline step shows `spacedock state commit` without `<slug>` and `--workflow-dir <dir>` (Codex P2; `## Workflow State` already requires both).
- `Not applied:` is not accepted as the validation deploy record, so a confirmed skipped deploy reads as a missing record (Codex P2).
- A finding repeated in a later round would be filed as a second backlog task; reuse the existing one (Codex P2).
Also, folded in from backlog task `review-followups-0102` (round 3 of qnow PR #1248, 2026-10-01; both still true on 0.15.1, checked 2026-10-11):
- The FO recovery step writes `status --workflow-dir <dir> --read <task> --stage <stage> --checklist` without the `spacedock` executable; write `spacedock status ...`.
- `## Number guards` applies when "its design lands an ADR", so an ADR first required by a ruling in an implementation report, a validation report or mid-stage feedback gets no reserved number. Apply the guard whenever the task lands an ADR, and reserve the number when the need appears.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Needed at ideation: none beyond the order above.
Surfaces: none
Visible change: none
