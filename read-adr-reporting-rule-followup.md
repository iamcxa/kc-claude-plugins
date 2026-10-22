---
id:
title: read-adr reports the verified cited version and any newer in-force ruling, then waits
status: ideation
variant: kc-dev-flow-2
profile: pilot
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:read-adr-reporting-rule-followup:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:read-adr-reporting-rule-followup-backlog-1
              briefing:
                id: briefing:read-adr-reporting-rule-followup:backlog:attempt-1:revision-1
                digest: sha256:1d3884edafa013314037e6f6447fd3586dcb41e4ad5ea66dd50bee5c6f400906
                room-ref: ./read-adr-reporting-rule-followup/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:read-adr-reporting-rule-followup:backlog:1
                briefing: briefing:read-adr-reporting-rule-followup:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-22T03:50:59.529593Z"
                decision: approve
                reason: Captain replied 「同意」 (2026-10-22) to a two-item batch whose item 2 was this backlog gate; accepts the corrected premise, scope, non-goals, half-day budget and AC-1..AC-2 as filed.
              application:
                target-stage: ideation
                state: consumed
---

Follow-up to `kc-decision-log-cli` (archived done; kc-adr v0.1.0 released). In scenario S11 a ruling is cited at an older commit where it is Accepted, and at head it is superseded by ADR 0023. The shipped skill's Accepted branch says "report both commits and both Statuses; the head governs, the cited commit is what the sender saw". Both skill runs then reported only the in-force 0023 with its own digest, not the verified cited version; the no-skill runs reported the cited version. The cause is the Accepted branch's "the head governs" (verified against the skill text on main, 2026-10-22), not two conflicting rules as first filed. The harness answer also has a single ruling slot that cannot hold both records.

The Captain asked for this follow-up (amendment 6 of `kc-decision-log-cli`): 「把兩條回報規則統一成「回報你核對過的引用版本和指紋；如果最新版本裡有別筆生效，也一併回報，等人決定再動作」，並只重跑相關情境。」 He approved starting it on this corrected premise on 2026-10-22 (「可以」).

## Scope

In `kc-adr/skills/read-adr/SKILL.md`, rewrite the Accepted branch (and align the chain-end line) so the worker reports the cited commit, its verified digest and its Status; if a different record is in force at head, reports that record, its commit and digest as well; and takes no action on either until a person decides. Change the harness answer schema so it can hold both the cited record and an in-force record. Rerun only S6, S7, S9 and S11 with the skill on Claude and Codex, reusing the `kc-decision-log-cli` harness; the run count is declared before launch. Release the change as the next kc-adr version through release-please.

Non-goals: other skill changes; the writing-tool ownership (dev2 task `kc-adr-tools-with-dev2-copy`).

Budget: half a working day of active effort; stop if the declared runs would be exceeded.

## Acceptance criteria

**AC-1**: The skill's Accepted branch states the rule above. A worker given a citation superseded at head reports the cited commit, its digest and its Status, names the in-force record with its commit and digest, and takes no action on either.
Verified by: reruns of S11 and S9 on Claude and Codex, scored by the harness against expectations written before the runs.

**AC-2**: S6, S7 and S9 results do not regress against `kc-decision-log-cli`'s stored runs.
Verified by: the same harness regrade, compared cell by cell.

## FO alignment

Not needed before ideation: the Captain asked for this follow-up and stated its rule (amendment 6 of kc-decision-log-cli, 2026-10-22, 「按推薦」). Release review: not needed: the task belongs to no release (the map was skipped for kc-adr by the Captain's authorization).
Surfaces: none
Visible change: none
