---
title: "Repair POC close measurement ordering"
status: backlog
product: kc-dev-flow
sprint: S8
sprint-readiness: ready
id: aznp6gpr6zanmr8argy0jcdj
gates:
    version: 1
    records:
        - id: gate:aznp6gpr6zanmr8argy0jcdj:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:aznp6gpr6zanmr8argy0jcdj-backlog-1
              briefing:
                id: briefing:aznp6gpr6zanmr8argy0jcdj:backlog:attempt-1:revision-1
                digest: sha256:7854bae80bb4b2b34cc41b5831dc80f8190b3a16db29a67ad8637b947ff91f79
                room-ref: ./review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:aznp6gpr6zanmr8argy0jcdj:backlog:1
                briefing: briefing:aznp6gpr6zanmr8argy0jcdj:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T13:40:31.144358Z"
                decision: approve
                reason: Kent approved the bounded phase-aware close repair and selected the proposed Pilot profile with 同意 in the current conversation; no product commit, release, new cloud run, or terminal POC approval is implied.
              application:
                target-stage: ideation
                state: pending
---

# Repair phase-aware POC close measurements

Kent approved this bounded repair and selected Pilot in the current conversation with "同意". This is a standalone Captain-approved Development Brief; no provider-backed planning admission is claimed. S8 is execution grouping only.

## The problem

At exact main c2c62bf9dff5c3af1e27eb643a15eadf9023485f, poc-close-guard.py validates final captain-wait and terminal-cleanup measurements before review, prepare, and consume. A real POC cannot truthfully provide future final values before the human close decision and cleanup. The admitted event-query cloud experiment reached this boundary and remains in implementation. This is distinct from merged PR390 (stage-pin authority) and PR407 (durable prepare and selected report review).

Two read-only reproductions against the real task snapshot establish the defect: valid YAML with pending durations is refused as non-integer; zero incurred durations with cleanup_status pending is refused as invalid. Evidence: .context/poc-close-phase-reproduction.json.

## Accepted outcome

An existing POC can prepare and present a real human gate while future measurements remain explicitly pending, preserve native approval authority, and record actual waiting and cleanup after they occur. Complete close reporting must distinguish pending or failed cleanup from successfully completed cleanup. Existing completed records remain usable without migration.

## Non-goals

No automatic human approval, gate bypass, new generic workflow/state engine, recurring automation, fresh cloud/model run, provider or GitHub mutations, unrelated profile changes, release/version bump, or implicit publication. Do not rewrite old stage-pin history or alter the existing cloud case outputs. Product commit requires Kent confirmation of exact changed files.

## Acceptance criteria

- **AC-1** Review and prepare accept a concrete valid outcome with explicitly pending close measurements, without fabricated zero/final values, for direct and fresh proof routes. Malformed supplied measurements still refuse.
- **AC-2** Native Spacedock integration proves prepare leaves an open manual gate; attempting consumption without approval fails without advancing the task.
- **AC-3** The full existing approval/consumption/cleanup/reporting order can reach truthful final measurements without invalidating an approval merely by recording those measurements. State transitions and one-use approval remain owned by Spacedock; cleanup pending or failed cannot be represented as successfully complete.
- **AC-4** Existing completed measurement records and negative POC outcomes retain compatible behavior; existing selected-report and acceptance-coverage regressions pass.
- **AC-5** The repair is applied to a preserved snapshot of the blocked event-query task with real Spacedock to demonstrate that the original blocker is gone. The live task waits for Kent's real outcome decision; no cloud workload rerun is needed for this guard repair.

## Route-back conditions

Return to Kent if correctness requires consumer record migration, a new approval authority, broader delivery/cleanup ownership, a new standing enforcement system, or replaying the cloud workload. Preserve current runtime and original task evidence until the repair is validated and adoption is explicitly within approved scope.

## Delivery and validation boundary

Implement in an isolated worktree based on exact remote main. Begin with failing phase/order regressions, then the smallest backward-compatible repair in existing guard, tests, and required profile/continuation instructions. Independently review the exact patch and native integration proof. Prepare the concrete diff for Kent's commit confirmation; do not commit/push product code automatically. State-tracking commits remain authorized.

## Engineering question for shaping

Determine which measurements must be available at each lifecycle boundary and where final completion is checked. Exercise native artifact freshness and terminal cleanup order before settling the interface; a parser-only fix can otherwise create a stale approval or another circular dependency. Reuse the existing POC guard/state owner rather than inventing another authority.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: A bounded retained repair of the existing POC close tool, with backward-compatible adoption and independent verification; no new operational or release commitment.
  route: [shape, build, verify-deliver]
  obligations:
    architecture: [Reuse the existing POC guard and Spacedock approval owner; prove lifecycle ordering and approval freshness.]
    implementation: [Phase-aware close measurements in the smallest existing surface; preserve completed records and original experiment evidence.]
    testing: [Native human-gate and cleanup-order regressions plus original blocked snapshot; independent patch review.]
  scope_boundary: No automatic approval, new workflow engine, cloud rerun, external posting, version bump, product commit without Kent confirmation, merge or release.
  semantics_unchanged: false
  promote_when: [Consumer record migration or wider lifecycle ownership is required.]
  decision:
    authority: Kent
    at: "2026-09-10T13:39:12Z"
```
