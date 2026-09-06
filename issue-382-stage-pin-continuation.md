---
title: "fix(kc-dev-flow): resume pinned reports and authorized corrections"
status: backlog
product: kc-dev-flow
sprint: S7
sprint-readiness: ready
provenance: https://github.com/iamcxa/kc-claude-plugins/issues/382
id: dntn9z2nd2gkdcsjbbc9m4pv
gates:
    version: 1
    records:
        - id: gate:dntn9z2nd2gkdcsjbbc9m4pv:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:dntn9z2nd2gkdcsjbbc9m4pv-backlog-1
              briefing:
                id: briefing:dntn9z2nd2gkdcsjbbc9m4pv:backlog:attempt-1:revision-1
                digest: sha256:406f5d8b6c966567084943c9514f76aba8cf505ca86915c4ee2626230f8e58e5
                room-ref: ./issue-382-stage-pin-continuation/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:dntn9z2nd2gkdcsjbbc9m4pv:backlog:1
                briefing: briefing:dntn9z2nd2gkdcsjbbc9m4pv:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-06T14:28:31.950404Z"
                decision: approve
                reason: 'Kent explicitly approved the presented initial briefing 406f5d8b6c: admit the same six-file Production recovery repair; legacy migration remains separate, with no merge or release grant.'
              application:
                target-stage: ideation
                state: pending
---

Resume valid report updates and explicitly authorized corrections without
weakening accepted-authority or pinned-contract boundaries.

## The problem

The installed loader rejects a pinned stage after normal report additions and
blocks the existing validation-to-implementation feedback handoff. Replacing
the pin alone would repeat the failure after the next report. The issue's
read-only reproductions establish the failure; they are not successful recovery.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: production
  recommended: production
  basis: Supported public loader contract with persistent pin history and an authorization boundary.
  route: [build, verify]
  obligations:
    architecture: [Separate accepted authority from reports, preserve predecessor and rejection evidence, keep authorization verification with its existing owner]
    implementation: [Reuse the accepted six-file candidate, repair only concrete in-scope findings, preserve legacy exact-byte checks]
    testing: [Fresh independent exact-candidate validation, public CLI positive and refusal cases, real dispatch artifact handoff, without-it evidence, repository pre-merge checks]
  scope_boundary: Only kc-dev-flow/scripts/profile-contract-loader.py, kc-dev-flow/scripts/profile-contract-loader.test.py, kc-dev-flow/skills/continue-dev-flow/SKILL.md, kc-dev-flow/MIGRATION.md, kc-dev-flow/contract-manifest.json, and scripts/kc-dev-flow-contract-test.py; no legacy task migration or installation change.
  recovery_failure: Valid report updates and explicitly authorized validation correction are refused before the existing dispatch handoff.
  recovery_falsifier: python kc-dev-flow/scripts/profile-contract-loader.test.py and python scripts/kc-dev-flow-contract-test.py must accept the in-scope continuations and refuse authority drift; an accepted unauthorized change falsifies recovery.
  recovery_rollback: Before release or adoption, revert only the repair commit if validation fails; preserve legacy pins and snapshots. After consumer adoption, require a separately reviewed compatibility rollback rather than rewriting pins.
  review_risks: [behavior, contract-schema, state-concurrency, security-privacy, runtime-platform, delivery]
  promote_when: [Any need for legacy migration, shared-state rewrites, new authentication infrastructure, a new workflow, or changes outside the six-file repair]
  decision:
    authority: Kent
    at: 2026-09-06T14:20:45Z
```

Kent approved Production recovery in this session with "同意" after the explicit
proposal "Production 修復路線（修復→獨立驗收）". The timestamp above records capture
of that decision, not a claim about an unavailable exact message timestamp.
This selection grants neither validation approval nor merge/release authority.

This is standalone Captain-approved work: no Planning Receipt is present and
no provider admission/reconcile is requested. S7 is the existing kc-dev-flow
plugin-owned-runtime execution group, not a new planning window or priority.

## Accepted outcome

Deliver the six-file source repair in one PR so new stage pins support report
continuation and explicitly authorized correction with preserved evidence and
refusal boundaries. Reuse the existing candidate and fix only concrete gaps.

## Non-goals

- Migrating, rewriting, or unlocking the original task's legacy 4.1.1 pin.
- Altering the original task, its PR-review product, shared working trees, or
  another task's state. New records for this task use an isolated state holder.
- Updating installed packages, release versions, CI workflows, standing gates,
  or performing a live worker/cloud run as product acceptance evidence.
- Adding authentication, evidence-truth, or Git-ancestry infrastructure.
- Claiming review-speed gains, automatic approval, merge, release, or closing
  issue 382 in this first delivery.

Legacy recovery is explicitly a separate delivery after the repair release:
https://github.com/iamcxa/kc-claude-plugins/issues/382#issuecomment-5559766497

## Acceptance criteria

- **AC-1** Normal report/runtime updates resume without replacing an active pin;
  accepted authority and package changes remain refused.
- **AC-2** The explicit correction path binds rejected revision, snapshot, pin,
  repair scope and existing authorization; preserves history; and hands the
  unchanged validated receipt to the existing dispatch contract.
- **AC-3** Two subsequent repair reports resume, return to validation preserves
  evidence, and an old correction receipt cannot authorize a new validation pin.
- **AC-4** Ordinary forward stages can supply their declared equivalence evidence
  without weakening same-stage or correction binding.
- **AC-5** Legacy pins keep exact-byte refusal. Documentation, PR evidence and
  issue status do not claim the original stranded task is recovered.

## Route-back conditions

Stop and return to Kent if the accepted outcome or non-goals change, any
criterion requires legacy migration or shared-state rewrites, authentication or
ancestry infrastructure becomes necessary, a new workflow is proposed, or the
repair must expand beyond the six-file boundary. No automatic full-route change.

## Existing candidate and evidence

The candidate was implemented and reviewed before this formal work item; those
artifacts are inputs, not retrospective stage approvals. Base is
dc4c8b13c0d86d81e4d79679d8ccb735117a9e52 and the six-file uncommitted patch SHA-256
is f4a57ae605125f45bc105bf654eada7c6a1e82a14d7c6c81aab435c130a240bc.
Its previous independent review resolved a required-evidence transition defect
and stale documentation link. The formal validator still judges the exact
committed candidate and fresh evidence.

The source repair is not a new version or a legacy pin migration. Keep the
original evidence and pin unchanged. The implementation worker records the exact
candidate, changed-file-to-obligation mapping, falsifier/without-it evidence,
comment necessity, applicable project-context classification and bounded build
observation in its own report. A fresh validation worker owns verification.
