---
id:
title: read-adr reports the verified cited version and any newer in-force ruling, then waits
status: backlog
variant: kc-dev-flow-2
profile: pilot
merge: pr
worktree:
pr:
---

Follow-up to `kc-decision-log-cli`, from its validation (2026-10-22). The kc-adr `read-adr` skill gives two conflicting reporting rules: "report the digest you computed" and "report the end's own digest, not the cited one's". In scenario S11, a ruling is cited at an older commit and superseded at head. Both skill runs reported the in-force ADR 0023 instead of the verified cited version. The no-skill runs reported the cited version. The Captain accepted shipping 0.1.0 with the design's path, under amendment 6 of `kc-decision-log-cli`, and asked for this follow-up: 「把兩條回報規則統一成「回報你核對過的引用版本和指紋；如果最新版本裡有別筆生效，也一併回報，等人決定再動作」，並只重跑相關情境。」

## Scope

Unify the two reporting rules in `kc-adr/skills/read-adr/` into one: report the cited version and digest you verified; if a different record is in force at head, report it too and take no action on either until a person decides. Rerun only the scenarios whose reporting the rule touches (S6, S7, S9, S11 with the skill, both hosts), reusing the `kc-decision-log-cli` harness. The run count is declared before launch.

Non-goals: other skill changes; the writing-tool ownership move (dev2 task `kc-adr-tools-with-dev2-copy`).

## Acceptance criteria

**AC-1**: The skill states one reporting rule. A worker given a citation that is superseded at head reports the cited commit and its digest, and also names the in-force record, without acting on either.
Verified by: reruns of S11 and S9 on Claude and Codex, scored by the harness with the rule's expectation written before the runs.

**AC-2**: S6, S7 and S9 results do not regress against `kc-decision-log-cli`'s stored runs.
Verified by: the same harness regrade, compared cell by cell.

## FO alignment

Not needed before ideation: the Captain asked for this follow-up and stated its rule (amendment 6 of kc-decision-log-cli, 2026-10-22, 「按推薦」). Release review: not needed: the task belongs to no release (the map was skipped for kc-adr by the Captain's authorization).
Surfaces: none
Visible change: none
