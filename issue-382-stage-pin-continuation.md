---
title: "fix(kc-dev-flow): resume pinned reports and authorized corrections"
status: implementation
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
                state: consumed
started: 2026-09-06T14:29:01Z
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/issue-382-flow.hNPqy3/.worktrees/spacedock-ensign-issue-382-stage-pin-continuation
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

## Stage Report: implementation

- DONE: Retain the approved six-file continuation candidate, bind a clean code commit to AC-1 through AC-5, and map each retained change to its obligation without changing installed packages or legacy state.
  Signed-off code commit `587ca1ef07b7e2edcc1eec89d34b89305e1800bf`; base `dc4c8b13c0d86d81e4d79679d8ccb735117a9e52`; exact diff SHA-256 `f4a57ae605125f45bc105bf654eada7c6a1e82a14d7c6c81aab435c130a240bc`; six files, 592 additions / 13 deletions, clean worktree.
- FAILED: Prove the correction/report journey and refusal boundaries with actual checks and a without-it failure, preserve exact commands/results and candidate identity, and apply the selected Production build obligations.
  Fresh behavior checks pass; Production project-context maintenance is blocked by the seven-versus-six-file scope conflict below. Implementation exit and its observation remain pending; no validation verdict is claimed.
- DONE: Write and durably commit the implementation Stage Report with checklist accounting, AC evidence, project-context classification, bounded build observation and remaining evidence; do not push code, create a PR, merge, release or mark validation passed.
  Accounting: 2 DONE / 1 FAILED (scope-blocked). This report preserves the accepted brief/frontmatter and separates implemented evidence from fresh independent validation.

### Candidate and fresh evidence

Code worktree: `/Users/kent/conductor/workspaces/kc-claude-plugins/issue-382-flow.hNPqy3/.worktrees/spacedock-ensign-issue-382-stage-pin-continuation`; branch: `spacedock-ensign/issue-382-stage-pin-continuation`.
Evidence directory: the code worktree's `.context/implementation-382/`; `README.md` preserves exact commands and outcomes. `loader-green.log`: exit 0, 22.24s; `contract-green.log`: exit 0, 63.93s; `marketplace.log`: parity/schema/eight isolated installs pass, 12.11s.
- AC-1 implemented: report/runtime resume retains the pin; accepted-authority/package drift refuses. Without only the loader repair, the same CLI test fails with `ACTIVE_STAGE_PIN_MISMATCH` (`without-loader.log`, expected exit 1, 5.04s); restoring it makes the test pass.
- AC-2 implemented: the real Spacedock fixture builds a correction assignment containing the unchanged validated receipt while the entity stays at validation; removing feedback binding/forwarding makes the test fail.
- AC-3 implemented: two repair reports resume, return to validation retains predecessor evidence, and stale feedback replay refuses; discarding history or accepting replay makes these assertions fail.
- AC-4 implemented: ordinary forward transition admits the declared equivalence evidence, while same-stage changes refuse; using whole-authority comparison at every boundary or dropping same-stage binding fails the suite.
- AC-5 implemented: legacy exact bytes resume and changed legacy bytes refuse; removing legacy equality fails the negative case. The original legacy task is not migrated or recovered.
All five criteria have implementation evidence, not independent validation. Scoped loader E4/E7/E9/F lint, 44 skill frontmatters, release contract, and diff checks pass. Expanded root-script lint finds pre-existing F541 at candidate line 2241/base line 2240, reproduced on the fixed base; prior default-Ruff 37-warning evidence is not represented as a fresh clean run. Sanitize: zero REJECT/BLOCK, 28 WARN matches; new matches are SHA-256 and AC-99.

### Retained change mapping

- Loader: AC-1–AC-5 authority/report projection, feedback binding, predecessor preservation, ordinary-boundary evidence, and legacy refusal.
- Loader test: AC-1–AC-5 public CLI refusals and real dispatch-artifact journey; no live worker is spawned.
- Continuation SKILL: AC-1/AC-2 conditional protocol entry; MIGRATION: AC-1–AC-5 protocol/trust/legacy contract and rollback boundary.
- Contract manifest and root contract test: bind MIGRATION bytes and enforce the existing resource inventory.
No added product file/dependency or unmapped surface. Retained-document policy applies to in-place prose, not document addition/deletion; MIGRATION is the explanatory home and SKILL links to it. Kept the two loader docstrings for the unverified-identity boundary and unknown-authority retention; cut none because the accepted candidate adds no redundant narrative block.

### Scope decision and pending observation

```yaml
project_context:
  impact: update
  authority: "Root PRODUCT.md, ARCHITECTURE.md, and CLAUDE.md (Local Profile binding)"
  claim_locator: "ARCHITECTURE.md: kc-dev-flow profile-native loading, sentences beginning It takes through explicit README/local-mod refit"
  surface: "New-pin same-stage continuation"
  stale_claim: "Same-stage drift fails closed"
  approved_change: "Report/runtime-only continuation is approved; extending the file set to document it is pending Kent"
  landed_change: pending
  planned_check: "Run loader report-resume and authority/legacy refusal cases; compare the replacement paragraph with those outcomes"
  validation_evidence: pending
```

Proposed exact replacement paragraph, not applied: The loader's envelope hashes the complete current work item, keeping profile selection item-local. New state-owned pins also bind the active attempt to accepted authority, plugin version, contract digest, and Local Profile bytes and interface. Same-stage report/runtime-only updates resume without replacing the pin; `bind_stage_pin` refuses accepted-authority, package, Local Profile, or attempt drift. Legacy pins without the authority digest retain exact-work-item-byte refusal. Compatible installed upgrades take effect at ordinary next-stage boundaries; incompatible interfaces stop before pin write or dispatch for an explicitly accepted README/local-mod refit. Authorized validation-to-implementation correction uses the bound feedback receipt and preserves rejected-pin evidence; see `kc-dev-flow/MIGRATION.md#stage-pin-continuation`.

RoboRev observation: pending, not UNAVAILABLE; the First Officer stopped before implementation exit because context scope is unresolved. Capability preflight found v0.62.0, supported help/JSON, authenticated Codex, reachable daemon, and an empty exact-branch job list; no state claim or review request, request/confirmation counts 0/0, no verdict or measured cost. The unfiltered status scratch file was replaced with minimal capability fields. Declared limits remain one Codex gpt-5.6-terra request, medium reasoning/severity, no panel, 1200s, at most one changed-tip confirmation.
Delivery caveat from the First Officer: open PR #321 shares five files; it was not absorbed and the approved base was not changed. Recheck overlap/base under the dependency-aware local delivery policy before eventual PR work.

### Summary

The six-file source candidate is preserved, signed off, and freshly exercised, including an actual without-it failure. Implementation remains scope-blocked until Kent decides the one-paragraph ARCHITECTURE.md delta; independent validation and build observation remain pending. No code push, PR creation, package upgrade, legacy migration, merge, release, issue close, or stage advancement occurred.
