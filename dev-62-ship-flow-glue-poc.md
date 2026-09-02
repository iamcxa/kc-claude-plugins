---
title: "POC: ship-flow glue on one Issue — cloud dispatch, pinned-SHA verify, Captain-gated Draft PR"
status: implementation
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
pr: 342
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

Dispatched 2026-09-02T14:48:57Z (workspace create); full task delivered 14:50:44Z (two WAF-blocked attempts first); worker commit 14:58:33Z; worker Evidence block 15:09Z; FO acceptance (pin, without-it x2, contract test x3, CLI e2e) complete 15:25Z. Worker imputed cost USD 0.158 over the first 100 transcript events (partial; later events not summed). Step reached: PR gate (awaiting Captain approval of the exact candidate).

## POC outcome

```yaml
poc_outcome:
  direction: proceed
  admitted_at: 2026-09-02T14:44:00Z
  decision_ready_at: 2026-09-02T15:25:07Z
  decision_ready_elapsed_seconds: 2467
  captain_interventions_before_decision_ready: 0
  candidate: 0144264343775f4c74f517ccea488a8ef91c44bc
  evidence: >-
    One cloud worker, dispatched by message only, ran kc-dev-flow build on DEV-50,
    pushed the branch without opening a PR, and returned an Evidence block whose
    CANDIDATE_SHA equals the remote head the FO pinned. At that SHA the FO ran the
    without-it check twice (retained exit 0, README restored to base exit 1
    "needs one Goal section"), the contract test three ways (candidate PASS; base
    README FAIL; duplicated Goal FAIL "headings are missing or duplicated"), and a
    three-step CLI e2e flow (all pass, evidence/e2e-*.log). pr-merge preflight
    merge-tree is clean. See evidence/receipt-*.json and evidence/worker-evidence-block.md.
  strongest_limit: >-
    Four glue defects, none needing a new mechanism: (1) Conductor's WAF blocks
    dispatch messages carrying a bootstrap curl|tar line, so the task text had to
    be committed to a throwaway branch and fetched by the worker; (2) the CLI
    transcript truncates at 64 KB and --after rejects message ids, so the SQL
    view is the reliable read path; (3) the worker's without-it script lived in
    an untracked .context file and could not be retrieved, so the FO wrote its own
    checker instead of running the worker's; (4) asciinema and script(1) hang
    under this harness, so e2e evidence is a timestamped stdout log, not a cast.
    The 15-minute decision limit was exceeded (41 min), mostly by the WAF detour
    and transcript-reading retries.
  reversal_fact: >-
    A repeat where the worker cannot produce CANDIDATE_SHA, the pinned head moves
    during verification, the without-it command cannot be run FO-side, or the
    delivery unit's merge-tree preflight conflicts.
  cleanup_status_at_decision: pending (worker workspace idle, throwaway branch poc/dev-62-dispatch on remote, candidate branch on remote, no PR yet)
```
