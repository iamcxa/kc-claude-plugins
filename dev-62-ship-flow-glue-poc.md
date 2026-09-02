---
title: "POC: ship-flow glue on one Issue — cloud dispatch, pinned-SHA verify, Captain-gated Draft PR"
status: ideation
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: S9
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: mavxcgkp974vpfe4wakx78mj
gates:
    version: 1
    records:
        - id: gate:mavxcgkp974vpfe4wakx78mj:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:mavxcgkp974vpfe4wakx78mj-backlog-1
              briefing:
                id: briefing:mavxcgkp974vpfe4wakx78mj:backlog:attempt-1:revision-1
                digest: sha256:629a2e1f1e4b9f2a2ad7540091a121021e90e5528f10536c6831b3e68cbbd123
                room-ref: ./dev-62-ship-flow-glue-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:mavxcgkp974vpfe4wakx78mj:backlog:1
                briefing: briefing:mavxcgkp974vpfe4wakx78mj:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-02T14:45:35.716635Z"
                decision: approve
                reason: Captain admitted DEV-62 as a standalone poc-exploration item in sprint S9; POC route build -> prove maps to implementation -> validation; no Planning Receipt by Captain choice.
                conn:
                    quote: 直接進 SD 也可以，省掉儀式時間
                    source: Captain chat, this conversation, 2026-09-02, replying to the FO's question whether DEV-62 should be Linear-backed or standalone-admitted
              application:
                target-stage: ideation
                state: consumed
---

## The problem

The proposed ship-flow (dispatch one cloud worker per admitted Issue, verify each candidate at a pinned SHA, open the PR only after the Captain approves that exact SHA) was designed and reviewed twice by Codex on 2026-09-02 but has never run. Every piece is claimed to exist: `scripts/kc-dev-flow/linear-admission.py` emits the envelope, the `conductor` CLI creates a cloud workspace, kc-dev-flow runs inside it, `kc-pr-review` and `e2e-flow` verify, and the `pr-merge` delivery unit creates the Draft PR. The unproven assumption is that they connect with a dispatch message and nothing else. Measured 2026-09-02: cloud workspace round-trip about 20 s, in-session bootstrap of spacedock plus kc-dev-flow about 20 s, one haiku round about USD 0.05 imputed. Standalone brief; the Linear Issue DEV-62 mirrors this text for reference only and carries no Planning Receipt.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  route: [build, prove]
  basis: One disposable experiment on one docs-only Issue proves whether existing components connect through a dispatch message; no production state, provider write, compatibility promise, or continuing operation.
  poc_decision: Can ship-flow be built as glue over linear-admission.py, the conductor CLI, kc-dev-flow, kc-pr-review, e2e-flow, and the pr-merge delivery unit, or does any step need a new mechanism?
  poc_falsifier: Any step needs a new mechanism rather than glue — the worker cannot produce the evidence block, the without-it command cannot run on the First Officer side, the SHA cannot be pinned because the worker keeps pushing, or the delivery unit refuses the candidate.
  poc_budget: One cloud workspace, one Issue (DEV-50), two First Officer hours, no merge
  poc_stop_when: The first falsifier hit, or the Draft PR exists at the Captain-approved SHA, whichever comes first
  poc_artifact: disposable
  poc_safety_boundary: none
  poc_decision_ready_minutes: 15
```

## Accepted outcome

One real Issue, DEV-50 (docs-only, no UI), travels dispatch -> worker -> verify -> PR gate using only existing components plus the dispatch message. The First Officer on the Captain's machine produces the envelope and creates one cloud workspace whose first message carries the bootstrap, the envelope, and the instruction to push the branch, not open a PR, and report `CANDIDATE_SHA` with an evidence block. The worker runs kc-dev-flow and pushes. The First Officer pins the reported SHA in a local worktree, runs the without-it command from the evidence block so that it fails on the removed variant and passes on the retained one, runs `kc-pr-review` and a CLI e2e flow at that SHA, then presents the `pr-merge` delivery unit for Captain approval; on approval `pr-merge` creates the Draft PR.

## Non-goals

- No plan-flow, no batch, and no Linear write by the worker or by the First Officer during the run.
- No merge; the Draft PR stays draft and is closed at cleanup unless the Captain keeps it.
- No preinstalled image; bootstrap in the dispatch message is the POC expedient, not the design.
- No change to kc-dev-flow, `pr-merge`, or `linear-admission.py`; a needed change is a `stop` finding, not work.

## Acceptance evidence

- **AC-1** `poc_outcome` recorded as `proceed`, `stop`, or `change` with the step reached, minutes from dispatch to verdict, and imputed cost per step.
- **AC-2** The worker's evidence block quoted; its `CANDIDATE_SHA` equals the branch head the First Officer verified.
- **AC-3** The without-it command recorded twice at the pinned SHA: removed variant failing, retained variant passing.
- **AC-4** Cleanup recorded: workspace archived, branch and Draft PR deleted or explicitly kept by the Captain.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

## Measurement

Not yet measured. Build records per-step minutes and imputed cost, and the falsifier step if any.
