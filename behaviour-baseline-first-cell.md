---
id:
title: One local command runs a real agent on a rebuilt stage dispatch at the released and the candidate package, for one cell, and reports what each arm did
status: ideation
variant: kc-dev-flow-2
profile: pilot
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:behaviour-baseline-first-cell:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:behaviour-baseline-first-cell-backlog-1
              briefing:
                id: briefing:behaviour-baseline-first-cell:backlog:attempt-1:revision-1
                digest: sha256:b5664e5209c5d2fac6204d5ca3778145ad19aafa70dfdaa2431d11c3afe2a0b8
                room-ref: ./behaviour-baseline-first-cell/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:behaviour-baseline-first-cell:backlog:1
                briefing: briefing:behaviour-baseline-first-cell:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-11-14T04:42:39.866073Z"
                decision: approve
                reason: Inside scope 1 item C given by the reform session under the Captain's grant; profile pilot justified in the Scope; seed check exit 0; no excluded matter (public merge, outward action, outcome definition, suspected key) is involved in admission.
                conn:
                    quote: 改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。
                    source: the Captain, chat with the second dev2 FO, 2026-11-14; scope 1 item C from the reform session, Paseo messages 6ee7ee5b-9ccc-4ef2-8cb6-35f25bfd4e1e and a8df76d7-63cb-4352-9c4b-f44b6004d7f5
              application:
                target-stage: ideation
                state: consumed
started: 2026-11-14T04:43:45Z
---

The package has no check that runs a model and looks at what its instructions cause. An earlier attempt (task validation-reads-pr-review-comments) had 7 valid runs of 12, two runs at the 1800-second cap, and a base that already passed 3 of 3, so it could show nothing (figures from `.context/dev2-reform/改革總計劃.md`, not re-measured here).

## Scope

- Source: the Captain 「同意重建核心：先做行為基準，再從空白頁逐條准入，做成同一個套件的新版本，狀態一開始就放私有。」 (chat with the reform session, Paseo 26215d96, 2026-11-14; relayed, not a ruling here). Admission is recorded by FO under the Captain's grant to the second dev2 FO (chat, 2026-11-14) and the reform session's scope 1 item C. Design input: `.context/dev2-reform/behaviour-ci-design.md` sections B, C and D, a research output with its own stated limits.
- Outcome: a person can run one local command that rebuilds a real stage dispatch at two package refs (the last released tag and a candidate), runs a real agent on each in an isolated home, and reports per cell: base k/n, candidate k/n, the no-skill control, valid/n, minutes, tool calls, tokens and the model id as served. This task delivers the thin runner and ONE cell.
- Where the work lands: the private working repository, not this repository. This task file and its records refer to it only as "the private working repository" and pin it by commit SHA. Run evidence, case bundles and the result table stay there or outside any repository; nothing from a run, a case or a private adopter is written to this state branch, and nothing from that repository is pushed anywhere public.
- Reuse: the package's `scripts/replay_dispatch.py` builds the dispatch; the procedure text in the maintain-flow skill; Spacedock's isolation approach for its live tests as the model for an empty home and config directory. New code is the runner only: launch, hard stop, manifest, grade, table.
- First cell: ideation flags a criterion whose proof the validator cannot produce. Prefer a frozen public archived task cut before the record that caught it; plant a case only if none fits. Cases come from public package tasks on an allowlist.
- Rules for the cell: 3 trials per arm; a wall-clock cap and a tool-call cap per run, set and recorded before the first run; two invalid trials halt the cell; graded on artifacts the model cannot author (workspace bytes, commits, structured stage-report fields), never on its own claim; the transcript shows no read of an installed copy of the skill or of the operator's personal configuration; the model id as served, effort, package refs and Spacedock version are recorded.
- Spend: the operator's own login on this machine; no credential goes into CI; minutes, tool calls and tokens of the first run are recorded and no dollar figure is estimated.
- Profile: pilot. It adds a check at the release boundary of one package; no production data, credential in CI, migration or unattended operation.
Non-goals: the other seven cells; cloud replay; a CI workflow; First Officer behaviour journeys; deleting any existing test; carrying or proving resumable state (Spacedock's capability); tuning the cell until it shows a difference.
Budget: 2 cycles per stage
Stop condition: 18 paid agent runs in total including reruns; two invalid trials in the cell; the cell cannot be made to fail on any arm within the cap (that is a result: report it); the workflow's scripts would force run or case content onto this public branch; a suspected key is found.

## Acceptance criteria

**AC-1**: The one command produces, for one cell, a table with base k/n, candidate k/n, no-skill control, valid/n, minutes, tool calls, tokens and the model id as served, from real agent runs.
Verified by: the validator runs the command's grading and table steps on the stored run manifests in the private working repository at the pinned commit and compares the table; the run count is read from the manifests. Limit: one cell, 3 trials per arm.

**AC-2**: The cell is shown failing on at least one arm, or the report states it could not be made to fail within the cap, with the runs spent.
Verified by: the graded artifacts of the failing trial, read by the validator; or the manifest count against the cap of 18.

**AC-3**: Each run was isolated: no read of an installed copy of the skill or of personal configuration appears in its transcript.
Verified by: a scan of each stored transcript for those path classes, exit code recorded, re-run by the validator.

**AC-4**: Nothing from a run, a case or a private adopter is on this state branch or in any public repository.
Verified by: a scan of this task's folder on the state branch and of the public repository's refs for the case and run markers, with the list held outside any repository.

## FO alignment

Alignment: not needed before ideation: outcome, caps and proof are stated in the scope the reform session gave under the Captain's grant; the design returns at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: package tooling with no release on a journey map.
