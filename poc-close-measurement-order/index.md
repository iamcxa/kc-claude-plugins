---
title: "Repair POC close measurement ordering"
status: validation
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
                state: consumed
        - id: gate:aznp6gpr6zanmr8argy0jcdj:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:aznp6gpr6zanmr8argy0jcdj-ideation-1
              briefing:
                id: briefing:aznp6gpr6zanmr8argy0jcdj:ideation:attempt-1:revision-1
                digest: sha256:6b846f2baaf7b2d22c9730bb8d1a0c1889e04e971e141fa7fb9a85c50946ba9d
                room-ref: ./review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:aznp6gpr6zanmr8argy0jcdj:ideation:1
                briefing: briefing:aznp6gpr6zanmr8argy0jcdj:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T13:58:20.948302Z"
                decision: approve
                reason: Kent explicitly approved the presented ideation design with 批准 after the close-order explanation; proceed to bounded implementation, preserving separate product commit confirmation and real POC outcome approval.
              application:
                target-stage: implementation
                state: consumed
started: 2026-09-10T13:41:14Z
worktree: .worktrees/spacedock-ensign-poc-close-measurement-order
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

## Pilot shape: phase-aware close measurement

Scope is one retained guard repair for the First Officer closing a POC; `semantics_unchanged: false`. The accepted outcome and all non-goals above remain unchanged. Source/delivery base: exact `c2c62bf9dff5c3af1e27eb643a15eadf9023485f`; installed 4.3.0 bytes were loaded successfully with the unchanged state-owned `ideation/1` pin. No planning receipt exists, so no provider admission/read was invoked.

### Observed order and accepted journey

1. **OBSERVED:** current `poc-close-guard.py review/prepare` rejects explicit `pending` durations with exit 2. The preserved real task snapshot produces the same refusal; this is the without-this-change observation for AC-1 and AC-5.
2. **DESIGNED:** existing guard separates outcome validation from close-measurement validation. `review`, `prepare`, and `consume` accept literal `pending` for either future duration and cleanup status; supplied numeric values remain non-negative integers and malformed, duplicate, missing or unknown values refuse. Completed old records retain their meaning, without adding a required schema field.
3. **OBSERVED:** native `status --set` plus `state commit` makes the direct route durable before `gate prepare`; prepare returns `state=open`. Unapproved `gate consume` exits 1 and leaves validation unchanged. Fresh proof uses its existing validation report; it does not take the direct transition.
4. **OBSERVED:** `gate prepare` freezes the artifact as `git-root://main/<commit>/probe.md` plus a content hash in canonical Briefing `index.json`. Committed source measurement changes after prepare/approval do not change the frozen artifact. Tampering canonical Briefing bytes makes consume refuse with `bound canonical Briefing bytes do not match the frozen digest`. The original frozen outcome/report must not be replaced to update measurements.
5. **OBSERVED:** native synthetic approval followed by `gate consume` yields `route=approved-awaiting-merge`, `consumed=false`, application pending and status validation. Native `merge guard --verdict passed` alone spends the approval, records terminal state/verdict, and archives; repeat consumption refuses. No fixture decision is Kent approval.
6. **DESIGNED on OBSERVED seam:** the existing First Officer performs only separately authorized cleanup after the native terminal ceremony, records actual wait/cleanup in the archived task body, and preserves all frozen approval bytes/frontmatter. `state commit <archived-slug>` refuses dirty archived content, so the existing state/reporting owner must make a path-scoped body commit first, then call native `state commit` to resume publication. This exact local commit/publication sequence passed; split-root remote publication remains a build acceptance check. No new cleanup or publication authority is conferred.
7. **DESIGNED:** add one read-only `check-final` verb to the existing guard, taking the explicit terminal/archived work-item path. It distinguishes accepted outcome from fully complete close: terminal state plus concrete final durations and cleanup `complete`/`not-applicable` passes; `pending` or `failed` returns non-success with the recorded status. It neither changes state nor approves, cleans up, commits, publishes, or creates records. Existing `read_work_item` already reads an explicit archived path, so no archive search/state engine is needed.

No answer/hold/revise means retain pending observations and use native gate behavior. Death/interruption before final measurement leaves an honestly incomplete close; the existing owner resumes from the archived task and native state publication, without reusing approval or inventing zero. Failed cleanup is a recorded result, not successful completion; retries require existing authority and replace measurements only after actual observations. Outcome acceptance/terminal status is not a claim that cleanup/debrief completed.

### Necessary implementation and executable acceptance

- **AC-1:** add failing direct/fresh native tests using valid outcomes with both pending durations and cleanup; drive guard `review` and `prepare`, assert open gate and selected proof stage. Add missing/duplicate/negative/non-integer/unknown value controls. Keep outcome budget and timestamp checks untouched.
- **AC-2:** native prepared task without resolution must refuse guard consumption without status/application change. After a clearly synthetic decision, observe pending terminal application, not a guard-owned transition. This fails if guard invents approval or bypasses native delegation.
- **AC-3:** reproduce the full ordered native sequence; mutate canonical Briefing bytes to prove freshness refusal, then restore and complete the same gate once. Demonstrate source measurement updates preserve frozen approval; after merge/archive and simulated cleanup, use the existing owner's path-scoped state commit and publication. `check-final` rejects nonterminal, pending, failed and malformed records; accepts terminal completed/not-applicable records, with no bytes changed. Exercise inline plus local-bare-remote split-root publication, interruption and retry without another approval.
- **AC-4:** run existing `poc-close-guard.test.py`, `profile-contract-loader.test.py`, `profile-spacedock-route.test.py`, and repository `scripts/kc-dev-flow-contract-test.py`; retain old completed records and `proceed`/`stop`/`change`, direct/fresh selected reports, malformed/uncovered/unknown acceptance criteria. No migration is proposed.
- **AC-5:** copy the full blocked task plus only necessary referenced evidence into a disposable native workflow, preserving a byte hash of the original; insert explicit pending close YAML only in that fixture. Use test-only approval and synthetic cleanup; assert original main guard refuses and candidate guard reaches open gate and truthful final reporting. Do not claim its owner-reported 3/3 cases are newly verified, edit the live task, or rerun cloud.

### Where it touches

Paths are relative to product root; after counts are estimates, not targets. Task state/probe evidence is separate from retained product scope.

| Path | Lines now | Lines after estimate | Necessary reason |
|---|---:|---:|---|
| `kc-dev-flow/scripts/poc-close-guard.py` | 346 | 390-420 | AC-1/3: phase-aware parsing and read-only final completeness check |
| `kc-dev-flow/scripts/poc-close-guard.test.py` | 458 | 610-680 | AC-1 through AC-5: original refusal, native lifecycle and compatibility |
| `kc-dev-flow/skills/continue-dev-flow/SKILL.md` | 269 | 280-290 | Existing close/reporting owner must perform correct ordering and archive-body durability |
| `kc-dev-flow/references/profiles/poc-exploration/build.md` | 89 | 92-98 | Direct outcome records future measurements as pending |
| `kc-dev-flow/references/profiles/poc-exploration/prove.md` | 52 | 55-61 | Fresh proof distinguishes outcome acceptance from complete cleanup |

No new retained document, dependency, persistence store, state command, approval authority, manifest-version bump or cleanup automation is planned. If implementation proves a required contract-manifest binding update, report that scope change first. Stop and report if diff exceeds **5 product files**, **360 added plus deleted lines**, or **110 changed lines in the guard**, measured against the exact base above. One integrated slice and one independent reviewer are sufficient; at most one correction round if evidence warrants.

### Conditional-reference dispositions

`reverse_recovery`: the direct named broken seam already exists (`parse_outcome` eagerly validates final values); no absent capability/state engine is claimed. Recovery classification: guard validation EXISTS_BROKEN/REQUIRED, native gate/terminal archive WORKING/REQUIRED, existing state owner body commit WORKING/REQUIRED in local fixture. `check-final` is a bounded read-only check in that same owner, justified by terminal archive preceding final cleanup. No separate audit engine or journey-slice receipt is needed. Retained-document policy applies to the three existing instruction files; repair close instructions in place under Rule 8, with executable native checks rather than historical snapshots.

```yaml
project_context:
  impact: none
  authority: Root PRODUCT.md, ARCHITECTURE.md, CLAUDE.md
  claim_locator: ARCHITECTURE.md - v3 POC outcome and direct terminal gate; PRODUCT.md - profile-native authority
  surface: Existing close guard and Spacedock-owned terminal gate
  stale_claim: none
  approved_change: none
  landed_change: none
  planned_check: Native direct/fresh order and final read-only check preserve existing state and authority boundaries; inspect exact diff against these bound claims.
  validation_evidence: pending implementation and independent verification
```

## Stage Report: ideation

- DONE: Demonstrate the original pending-measurement failure and prove the proposed lifecycle ordering through native Spacedock, including denied unapproved consumption and approval freshness.
  AC-1, AC-2, AC-3, AC-5: `ideation-evidence.json` records guard exit 2, native open gate, denied unapproved consume, canonical Briefing tamper refusal, pending consume, native archive and path-scoped final observations. Falsifier: accepting the tampered Briefing or consuming without resolution fails this proof.
- DONE: Propose the smallest backward-compatible repair and executable acceptance plan for AC-1 through AC-5; distinguish outcome acceptance from final cleanup completeness.
  AC-1, AC-2, AC-3, AC-4, AC-5 mapped above to pending phase parsing plus existing-owner reporting and read-only `check-final`; baseline guard/native regressions pass, while candidate implementation tests are not yet run.
- DONE: Record the Pilot shape, assumptions, exact change surface, without-this-change evidence, and clear implementation assignment without editing product code.
  Five-file scope and stop counts above; existing exact-main guard refuses the original snapshot. Implementation belongs in the later isolated build worktree after the Captain shape gate.
- SKIPPED: Product implementation and AC implementation-pass claims.
  Ideation scope authorizes only shaping and disposable probes; no product files changed, cloud/model/provider runs, live task mutation, or real close approval occurred.

### Summary

The native sequence disproves a consume-only numeric fix: consume does not finish the task, and terminal archival precedes cleanup. Keep pending values through the human gate, preserve the immutable approved artifact, record final observations through the existing state/reporting owner, then verify completeness with one read-only guard command. Reproduce with `rtk proxy python3 <task>/ideation-probe.py <exact-main-product-root> <spacedock-binary> <output-json>`; the script creates only disposable local repositories and explicitly synthetic approvals.

Checklist total: 4 items (3 DONE, 1 SKIPPED, 0 FAILED); all five AC implementation verdicts remain pending. Captain recommendation: approve this one-slice shape for isolated implementation, retaining the exact-file product commit confirmation and separate real-experiment close decision.


## Stage Report: implementation

- DONE: Implement the approved five-file phase-aware close journey while preserving malformed-record refusal, native manual approval, and compatibility (AC-1 through AC-4).
  Guard separates outcome and measurement validation; pending values pass review/prepare/consume, while read-only check-final requires done and numeric durations plus complete/not-applicable cleanup. Missing/duplicate/negative/non-integer/unknown controls refuse; old completed outcomes remain accepted.
- DONE: Prove native direct/fresh approval, immutable briefing, terminal archive, final observations, split-root publication, interruption recovery, and blocked real snapshot without a cloud rerun (AC-1 through AC-5).
  Native lifecycle fixtures and implementation-native-evidence.json prove open manual gate, denied unapproved consume, tamper refusal, frozen source approval, pending native consumption, one-use merge/archive, final pending/failed refusal and successful existing-owner archive commit/publication; no synthetic decision is Kent approval.
- DONE: Run required regressions, surface map and instruction budget; report exact patch hashes, necessity, limitations and optional observation; leave product changes uncommitted for Kent.
  Four required suites pass; surface checker red/green controls cover all four non-test changed files through the disclosed exact-uncommitted-input adapter. Product HEAD and branch remain unchanged; independent validation and Captain product-commit confirmation remain pending.

### Summary

Implemented the approved five-file shape without migration, new approval/state authority, cloud rerun or product commit. The original blocked snapshot reaches the native close journey in a disposable repository; original workload assertions remain owner-reported. Final measurements follow native archival and existing-owner durability rather than redefining approval.

### Evidence

- AC-1/AC-4 refusal control: new measurement regression on original c2c62bf9 guard failed with captain_wait_seconds must be a non-negative integer; candidate passes pending direct/fresh and malformed-value controls. Budget and timestamp checks are unchanged; existing proceed/stop/change and selected-report/AC regressions pass.
- AC-2/AC-3 falsifiers: accepting an unapproved gate, changed canonical Briefing, incomplete cleanup or reused terminal approval breaks lifecycle_regressions; pending gate consumption still reports approved-awaiting-merge/consumed=false. A measurement-only body commit preserves the frozen Briefing. Native merge guard owns archival.
- AC-3 durability/recovery: direct inline and fresh split-root fixtures use real Spacedock 0.27.2; failed/pending archive checks refuse without writes; existing owner commits actual synthetic observations path-scoped then native state commit publishes to a local bare remote. Published archive bytes and state HEAD equal the remote ref; no real external fixture push.
- AC-5: implementation-probe.py copies the full source snapshot and necessary referenced cloud evidence; removes only test-native identity/gate/worktree bindings and inserts pending YAML in its disposable copy. Original source SHA-256 7d918157b36f8ee0b3fa087ffb1671c969cc8bafcaabea5fe38e4828e616900d is unchanged before/after; baseline refuses, candidate reaches open gate and final completed report. Cloud reruns: 0; the original task still awaits Kent.
- Reproduce: rtk proxy python3 kc-dev-flow/scripts/poc-close-guard.test.py; rtk proxy python3 kc-dev-flow/scripts/profile-contract-loader.test.py; rtk proxy python3 kc-dev-flow/scripts/profile-spacedock-route.test.py; rtk proxy python3 scripts/kc-dev-flow-contract-test.py — all exit 0. Exact root, remaining commands and results: implementation-checks.json; all commands ran against the dispatched worktree.
- Native snapshot command: rtk proxy python3 <task>/implementation-probe.py <worktree> <task> <original-task-index> /Users/kent/.local/bin/spacedock. Source preservation and command results: implementation-native-evidence.json; fixture is synthetic and local only.
- Surface command: rtk proxy python3 <task>/implementation-surface-check.py <worktree> <task>. Stock checker main/validators are unchanged; its commit-only diff input function is replaced in-memory with exact git diff --name-status against accepted HEAD. Missing mappings fail, four mapped files pass; stock commit-based CLI was not run on a committed candidate. implementation-surfaces.md maps obligations and without-it variants.
- Necessity/retained documents: no files, dependencies or abstractions added. Guard owns pending/final distinction; tests own falsifiers. Three existing instruction files repaired in place under retained-document Rule 8; base versions lack pending guidance, candidate structural instruction checks pass and native command execution verifies the described ordering. Condensed continuation repetition while preserving existing contract/mutation anchors; no historical/project-context artifact rewritten. No new product comment blocks; synthetic fixture labels remain to prevent accidental real-approval claims.
- Static accounting: actual assert_proportional_load initially rejected 40249/40000 bytes; in-scope prose condensation yields final maximum 39979/40000, recorded in implementation-budget.json. Tests exposed exact-text anchors during condensation; restored required phrases and full contract suite passes. Budget was not expanded.
- project_context: impact none; authority PRODUCT.md, ARCHITECTURE.md and CLAUDE.md; no stale/replacement/landed claim. Fresh native evidence preserves profile-native authority, outcome routing and native terminal gate; check-final adds no state or approval power. Independent validation remains pending.
- Optional RoboRev observation: UNAVAILABLE(reason: unavailable), observe/Pilot, CLI v0.62.0 plus review/list/show help checked. No committed candidate/config object can be bound because product commit is not authorized; old HEAD was not reviewed, identity/config/job/member result unknown, request_count 0, confirmation_count 0. No install/start/setup/provider query/model run; local worker/parent cost coverage unknown. See implementation-checks.json.
- Exact base: c2c62bf9dff5c3af1e27eb643a15eadf9023485f; branch spacedock-ensign/poc-close-measurement-order. Patch SHA-256: 8269d36074756c06edfd66a60b4569342692f0e6886a64c6db930100b0bdfc18. Five files, 198 added + 48 deleted = 246 changed lines; guard 26 added + 6 deleted = 32, under 360/110 limits. git diff --check passes; product index stays empty.
- File SHA-256 kc-dev-flow/references/profiles/poc-exploration/build.md: 736ea46354d5813d98cd9c5a35e7c3ae716df95f2e1efd48de615589edffe15e.
- File SHA-256 kc-dev-flow/references/profiles/poc-exploration/prove.md: c2a996268d2e35f8386de1244ec073fdbaadc3908d488dab93a9b0fbda01cbab.
- File SHA-256 kc-dev-flow/scripts/poc-close-guard.py: 56606dfcd8b1d475df71a8e264e4b155a225f4c2dc45d8b4263b76d6c84b5a8b.
- File SHA-256 kc-dev-flow/scripts/poc-close-guard.test.py: a8d4e5fdaf7240d059098a0d19440baff001d5962625effb859b90505bfa74f2.
- File SHA-256 kc-dev-flow/skills/continue-dev-flow/SKILL.md: 5db194ead89a44abc234ed261f5af8bb367eece385698ca91a17330629a94f83.

State-only report/evidence commit through registered native state commit is authorized; product patch remains uncommitted for independent verification and Kent confirmation. No CI changes; measured cost per PR is unavailable/not applicable.


## Stage Report: validation

- DONE: Independently attack the exact patch against AC-1 through AC-5: manual approval/freshness, final truthful measurements, read-only completeness, compatibility, interruption recovery and original blocked snapshot.
  PASSED for the uncommitted patch below. Independent native refusal cases and publication-interruption recovery pass; producer snapshot/regression evidence supplies AC-4/AC-5 without claiming independent cloud verification.
- DONE: Verify producer-owned native proof and required regression results; run only missing or newly justified adversarial cases, and inspect instruction claims and minimal necessity against the exact five-file diff.
  Inspected required four-suite exit-0 evidence, native fixture assertions and original-failure reproducer; added only the missing actual publication failure/retry and full-fixture byte-preservation checks in validation-probe.py.
- DONE: Record PASSED or REJECTED with precise findings, patch hashes, AC evidence and delivery limitations; leave product files unchanged and uncommitted.
  PASSED; no material findings. Product branch remains spacedock-ensign/poc-close-measurement-order at c2c62bf9dff5c3af1e27eb643a15eadf9023485f with empty index and the same five modified files.
- SKIPPED: Repeat already-green suites, optional provider review, product delivery and original experiment close.
  No new falsifier justified full-suite repetition; optional RoboRev remains UNAVAILABLE, no provider request. Product commit requires Kent's exact-file approval; no PR, merge, install, cloud rerun or real POC outcome approval is implied.

### Summary

The exact candidate satisfies the bounded close-order repair: pending observations survive the manual gate, native terminalization consumes the approval, and final reporting refuses incomplete cleanup. The independent additional falsifier rejected a real local-remote publication attempt after the final archived-body commit; retry then published those same bytes without another approval, and a fresh clone passed the read-only final check. Goal sufficiency is established for this repair, not delivery or acceptance of the original cloud experiment.

### Evidence

- AC-1/AC-2: pending direct review/prepare passed; prepare reported open; unapproved consume exited 1 with unchanged task bytes; canonical Briefing tamper exited 1 on frozen-digest mismatch. Producer pending fresh-route proof and malformed/missing/duplicate controls were inspected, not rerun.
- AC-3: source measurement commit preserved the frozen Briefing; consume returned approved-awaiting-merge with consumed=false; native merge guard recorded done, PASSED and application consumed. Historical archived frontmatter and Briefing bytes survived final observation commit/publication; repeated archived consumption refused (native archive resolution, not a new guard-owned authority).
- AC-3 recovery refusal control: local bare-remote pre-receive rejection made native state commit exit 1 and retain recoverable local commit 893f6dc8985b74c726cad4e51e9143d701155ec2; removing the synthetic interruption and retrying published that exact commit. A second clone received identical archive bytes; only one synthetic gate record, zero cloud runs.
- AC-3 final truth/read-only control: nonterminal, pending, failed and negative-duration cases exited 2; completed terminal record exited 0. SHA-256 maps of every fixture file, including Git/state/remote files, stayed identical before/after each final-check call; returning success for a refusal case or writing any fixture byte fails the probe.
- AC-4: implementation-checks.json records exit 0 for poc-close-guard.test.py, profile-contract-loader.test.py, profile-spacedock-route.test.py and scripts/kc-dev-flow-contract-test.py. Inspected completed/not-applicable, proceed/stop/change, direct/fresh selected reports and malformed/uncovered/unknown-criterion assertions; no migration, schema, manifest or version edit.
- AC-5: inspected implementation-probe.py and native command evidence: full blocked snapshot retains source body/evidence with test-only native bindings removed and pending YAML supplied; baseline refuses non-integer wait, candidate completes synthetic lifecycle. Rehashed untouched original source as 7d918157b36f8ee0b3fa087ffb1671c969cc8bafcaabea5fe38e4828e616900d; original remains implementation. Original three cloud cases remain owner-reported.
- Reproduce independent gap: rtk proxy python3 /Users/kent/conductor/workspaces/kc-claude-plugins/kinshasa/.context/routine-coordinator/docs/dev/.spacedock-state/poc-close-measurement-order/validation-probe.py /Users/kent/conductor/workspaces/kc-claude-plugins/kinshasa/.context/routine-coordinator/.worktrees/spacedock-ensign-poc-close-measurement-order /Users/kent/conductor/workspaces/kc-claude-plugins/kinshasa/.context/routine-coordinator/docs/dev/.spacedock-state/poc-close-measurement-order/validation-evidence.json ; exact subprocess arguments/results are retained in validation-evidence.json.
- Contract: installed 4.3.0 profile-contract-loader.py --work-item <task>/index.md --local-profile <workflow>/README.md --stage-pin <task>/validation-stage-pin.json --stage-attempt validation/1 --format json exited 0, digest 8cd3a8c40ab258ebb2541b9b0346e56686f9d90d9e400ef4e575526fc0e3df5e; committed pin bytes unchanged, no repin.
- Retained-document policy: three existing instruction files repaired in place (Rule 8), no addition/deletion or diagram. Native prepare/consume/check-final and actual failed/resumed state publication exercise the changed claims; retaining pre-change eager measurements makes the original accepted journey fail. Tests map falsifiers; each instruction file supplies its direct/fresh or reporting-owner obligation. Condensation preserves authority/observation boundaries; no unmapped retained surface found.
- project_context: impact none; authority PRODUCT.md, ARCHITECTURE.md, CLAUDE.md; claim_locator ARCHITECTURE.md v3 outcome/direct terminal gate and PRODUCT.md profile-native authority; stale_claim/approved_change/landed_change none. validation_evidence: fresh native pending/open/consumed/archive behavior, refusal controls and read-only check preserve named owner/gate boundaries; exact diff adds no downstream work or profile/delivery authority, so accepted classification remains valid.
- Scope/budget: five files, +198/-48 = 246 changed lines (limit 360); guard +26/-6 = 32 (limit 110). Inspected unchanged static-budget accounting and exact producer result 39979/40000 BYTES; no ceiling expansion. git diff --check passes. No CI change; cost per PR not measured/not applicable.
- Patch SHA-256: 8269d36074756c06edfd66a60b4569342692f0e6886a64c6db930100b0bdfc18 (git diff bytes, not unchanged HEAD).
- File SHA-256 kc-dev-flow/references/profiles/poc-exploration/build.md: 736ea46354d5813d98cd9c5a35e7c3ae716df95f2e1efd48de615589edffe15e.
- File SHA-256 kc-dev-flow/references/profiles/poc-exploration/prove.md: c2a996268d2e35f8386de1244ec073fdbaadc3908d488dab93a9b0fbda01cbab.
- File SHA-256 kc-dev-flow/scripts/poc-close-guard.py: 56606dfcd8b1d475df71a8e264e4b155a225f4c2dc45d8b4263b76d6c84b5a8b.
- File SHA-256 kc-dev-flow/scripts/poc-close-guard.test.py: a8d4e5fdaf7240d059098a0d19440baff001d5962625effb859b90505bfa74f2.
- File SHA-256 kc-dev-flow/skills/continue-dev-flow/SKILL.md: 5db194ead89a44abc234ed261f5af8bb367eece385698ca91a17330629a94f83.

Checklist total: 4 items (3 DONE, 1 SKIPPED, 0 FAILED). Product changes remain uncommitted; state report publication is separate from product delivery or original experiment acceptance.
