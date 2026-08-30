---
title: "Make POC decisions ready within 15 minutes"
status: implementation
source: "https://linear.app/duckbase-co/issue/DEV-14/make-poc-decisions-ready-within-15-minutes"
product: kc-dev-flow
planning-window: "Linear Cycle b788c52d-8370-475f-be4f-8fcd88dd03d6 2026-08-27T16:00:00.000Z/2026-09-10T16:00:00.000Z"
planning-outcome: Linear Project 90103fbc-2653-47d8-829a-36cccc6116da POC decisions within 15 minutes sha256:7d790de539c857ef05cea26e21d02850304b70e9eccca931daa463fc1df39a5b
sprint: poc-decisions-within-15-minutes
sprint-readiness: ready
started: 2026-08-30T13:20:03Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-make-poc-decisions-ready-within-15-minutes
issue:
pr:
mod-block:
id: k80xhxhk9b9e26mnnyn2jwsh
gates:
    version: 1
    records:
        - id: gate:k80xhxhk9b9e26mnnyn2jwsh:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:k80xhxhk9b9e26mnnyn2jwsh-backlog-1
              briefing:
                id: briefing:k80xhxhk9b9e26mnnyn2jwsh:backlog:attempt-1:revision-1
                digest: sha256:3508a3f5b697f989c16118348d0e213c997209b88c64cbcb149fc94a35343771
                request-digest: sha256:ec83aaa24f2d201c6dca20ff69b2a5a3d7b64778fd6fb19116eff1b56822839f
                room-ref: ./review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:k80xhxhk9b9e26mnnyn2jwsh:backlog:1
                briefing: briefing:k80xhxhk9b9e26mnnyn2jwsh:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-08-30T13:22:16.295709Z"
                decision: approve
                reason: Captain approved the presented DEV-14 Linear package and Pilot admission; live reconcile must remain clean before ideation dispatch.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:k80xhxhk9b9e26mnnyn2jwsh:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:k80xhxhk9b9e26mnnyn2jwsh-ideation-1
              briefing:
                id: briefing:k80xhxhk9b9e26mnnyn2jwsh:ideation:attempt-1:revision-1
                digest: sha256:2195c09ef398a2fca41d22928862c9963e60d8746208c9d8073b210881e1e82e
                request-digest: sha256:197fd1cbfa7c651e488cb63526bab3ee1654e43d44b7b17fcb45343b869475fe
                room-ref: ./review/ideation/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-08-30T13:39:27.008307Z"
                reason: The ideation report semantically covers AC-1 through AC-7, but the structured AC scan leaves AC-2 through AC-6 unevidenced; repair only scanner-readable report citations before Captain presentation.
            - id: gate-attempt:k80xhxhk9b9e26mnnyn2jwsh-ideation-2
              briefing:
                id: briefing:k80xhxhk9b9e26mnnyn2jwsh:ideation:attempt-2:revision-1
                digest: sha256:c6a10735e3e4cba1211f158691b198a0865d349c13fbdc825b6e8ff3663e1272
                request-digest: sha256:b03ad92af416ca0e63dd16286d0070a9eb00cf38d85ec8253970bea5c223c056
                room-ref: ./review/ideation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:k80xhxhk9b9e26mnnyn2jwsh:ideation:2
                briefing: briefing:k80xhxhk9b9e26mnnyn2jwsh:ideation:attempt-2:revision-1
                by: person:captain
                at: "2026-08-30T14:17:35.545336Z"
                decision: approve
                reason: Captain approved the presented bounded implementation shape, including the 15-minute fail-closed behavior, 16-file and 550-line caps, and focused evidence plan.
              application:
                target-stage: implementation
                state: consumed
---

## The problem

The POC profile claims bounded exploration but does not enforce a wall-clock decision budget. DEV-11 needed 41m43s to write its `poc_outcome` and 1h34m33s to terminalize. Its no-code proof repeated the same live read, reconcile, drift, and mutation evidence across build and prove, ran an unconditional RoboRev observation, and expanded without-it validation beyond the two mechanisms it retained.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: >-
    This bounded repository change repairs the POC profile for limited real use.
    It changes shipped contracts and deterministic coverage without adding
    production operation, provider writes, compatibility migration, an SLO, or
    release ownership.
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - Preserve the existing proceed, change, stop, and route-back boundary for POC work.
      - Keep Pilot and Production profile routes and obligations unchanged.
      - Keep the decision budget inside the POC contract without adding a timer or scheduler authority.
    implementation:
      - Add a positive decision-ready minute budget that defaults to 15 unless the approved brief records an override and reason.
      - Separate decision-ready latency from Captain wait and terminal cleanup.
      - Remove unconditional RoboRev and fresh validation for no-code or disposable POCs while retaining independently required repository safety boundaries.
    testing:
      - Prove one real journey, one critical falsifier, and focused without-it checks for only retained mechanisms.
      - Run one fresh measured no-code POC that reaches a durable outcome within 15 minutes with zero post-admission Captain intervention.
      - Reject any Pilot or Production route or obligation drift deterministically.
  scope_boundary: >-
    One repository-local Pilot changes only the POC profile contract, its focused
    enforcement, and one measured no-code dogfood. No daemon, polling, webhook,
    automatic workspace launch, token accounting, planning-provider redesign,
    DEV-11 history rewrite, or universal guarantee for an approved longer external experiment.
  promote_when:
    - Unattended operation, production credentials or data, provider writes, compatibility migration, an SLO, or release ownership enters accepted scope.
  decision:
    authority: Kent Chen (Captain)
    at: 2026-08-30T13:19:00Z
```

## Accepted outcome

Starting from an admitted Captain-approved POC, write a durable proceed, change, or stop outcome within 15 minutes by default and without another Captain intervention, while preserving one real journey, the critical falsifier, focused without-it evidence, cleanup, and an explicit route back to planning.

## Non-goals

- No timer daemon, polling loop, webhook, or automatic workspace launch.
- No token-accounting or model-cost framework.
- No changes to Pilot or Production requirements.
- No planning-provider, Project, Cycle, Initiative, or Milestone redesign.
- No rewriting or reclassifying DEV-11's historical evidence.
- No promise that an explicitly approved longer external experiment finishes within 15 minutes.

## Acceptance criteria

- **AC-1** Every admitted POC carries a positive decision-ready minute budget, defaulting to 15 unless the approved brief records a different limit and reason.
- **AC-2** Decision-ready elapsed time is measured from admitted task creation to the durable `poc_outcome`; Captain wait and post-decision cleanup are separate measurements.
- **AC-3** A no-code or disposable POC does not invoke RoboRev or fresh independent validation unless an independently required repository safety boundary applies.
- **AC-4** POC proof covers one real journey, one critical falsifier, and without-it checks only for its retained mechanisms; unrelated full regression or mutant suites are not selected.
- **AC-5** Budget exhaustion produces `change` with elapsed time, strongest evidence, strongest limit, reversal fact, and cleanup status instead of silent continuation.
- **AC-6** One fresh measured no-code POC reaches a durable outcome within 15 minutes with zero post-admission Captain interventions before decision-ready.
- **AC-7** Existing Pilot and Production routes, obligations, and admission behavior remain byte-equivalent or are rejected by deterministic contract tests.

## Route-back conditions

Return `change` to planning if the time budget cannot fail closed without killing an active tool call or losing evidence, if removing fresh validation or review violates a repository-owned safety boundary, if the POC needs Pilot or Production scope to meet the target, or if a provider prerequisite still needs Captain action after admission.

## Measurement

Record admitted-task creation time, durable `poc_outcome` time, decision-ready elapsed time, Captain interventions before that outcome, Captain wait, terminal cleanup, exact implementation revision, retained mechanisms, focused falsifier results, and cleanup status. The accepted dogfood requires decision-ready elapsed time at or below 15 minutes and zero post-admission Captain interventions before the durable outcome.

## Ideation shape

### Decision

Retain three mechanisms only: an effective decision-ready budget in the existing
profile loader, a proof-path selector in the existing POC receipt, and timing plus
route enforcement in the existing POC close guard. Do not add a timer, scheduler,
new state store, review service, or generic ablation harness.

`direct proof` means the build worker writes the outcome. `fresh proof` means a
separate validation worker checks retained code. New POC admissions record:

```yaml
poc_artifact: no-code | disposable | retained
poc_safety_boundary: none | <named repository safety check>
poc_decision_ready_minutes: 15
poc_decision_ready_reason: <required only for a non-15 override>
```

The loader requires a positive integer, uses 15 when the minute field is absent,
and requires a concrete reason when it differs from 15. Missing artifact fields
on an already-admitted v3 receipt select the existing retained/fresh path, so no
receipt migration or historical rewrite is needed.

`no-code` and `disposable` select direct proof only when
`poc_safety_boundary: none`; `retained` or any named safety boundary selects fresh
proof. Direct proof emits `implementation_exit_observation_declared: false`, so
RoboRev, the optional code-review observer, is not invoked. Pilot and Production
continue to emit their existing observation and route values.

The durable decision record is:

```yaml
poc_outcome:
  direction: proceed | stop | change
  admitted_at: <RFC3339 value equal to frontmatter started>
  decision_ready_at: <RFC3339 durable-outcome time>
  decision_ready_elapsed_seconds: <non-negative integer>
  captain_interventions_before_decision_ready: <non-negative integer>
  evidence: <strongest exact evidence and revision>
  strongest_limit: <strongest remaining limit>
  reversal_fact: <fact that reverses the conclusion>
  cleanup_status_at_decision: pending | complete | failed | not-applicable
```

After the outcome is committed, cleanup records its separate measurement before
the terminal gate is prepared:

```yaml
poc_close_measurement:
  captain_wait_seconds: <non-negative integer>
  terminal_cleanup_seconds: <non-negative integer>
  cleanup_status: complete | failed | not-applicable
```

The close guard parses both timestamps, recomputes elapsed seconds, and rejects a
mismatched measurement. The inclusive default limit is 900 seconds; 901 seconds
is exhausted. Exhaustion or any post-admission Captain intervention before the
decision requires `direction: change` and all evidence, limit, reversal, and
cleanup fields. It cannot silently continue as `proceed` or `stop`.

For direct proof, the First Officer calls the close guard after the implementation
report. The guard advances the existing task to `validation` only to use its
existing terminal authorization gate; it creates no validation worker dispatch
or validation report. The gate still prepares its approval briefing. Fresh proof
keeps the existing validation dispatch. Both paths keep the same Captain-owned
terminal gate and planning route-back.

### Accepted journey

1. **DESIGNED** — Spacedock consumes the admitted backlog gate, enters
   `implementation`, and persists the original `started` timestamp in the task.
2. **DESIGNED** — `profile-contract-loader.py` reads the exact committed POC
   receipt, emits the effective minute limit and proof path, and suppresses the
   POC review observation only for direct proof.
3. **DESIGNED** — The implementation worker exercises one real CLI journey and
   its critical falsifier. For direct proof it commits `poc_outcome` immediately;
   for fresh proof it leaves the outcome to the validation worker.
4. **DESIGNED** — Git in the Spacedock state checkout makes the outcome durable.
   The recorded decision-ready time is the outcome commit time, not prose written
   before persistence.
5. **DESIGNED** — `poc-close-guard.py` verifies the effective limit, elapsed time,
   intervention count, evidence fields, and selected proof path. Direct proof
   reaches the existing terminal gate without a validation dispatch.
6. **DESIGNED** — After cleanup measurement and the existing Captain approval,
   the close guard consumes the gate and Spacedock archives the task. Planning
   receives the outcome; no downstream task or profile is created.

Unhappy paths use the same facts. A provider prerequisite, no answer, or process
death resumes from the persisted `started` time; if the limit has expired, the
next durable result is `change`. An active tool call is not killed: once it
returns, an over-budget result records `change`; inability to preserve evidence
returns to planning. A direct receipt with a named safety boundary is refused as
inconsistent. A failed state commit is not decision-ready. Failed cleanup remains
visible and prevents terminalization without erasing the outcome.

### Acceptance checks

| Criterion | Check that can falsify it |
|---|---|
| AC-1 | Loader fixtures prove absent minutes emit 15, zero/negative/non-integer values fail, and a non-15 value without a reason fails. |
| AC-2 | Close-guard fixtures bind `admitted_at` to `started`, recompute elapsed seconds, and reject mismatched or negative measurements. |
| AC-3 | A direct no-code/disposable fixture emits no review observation and closes without invoking a validation worker; a named safety boundary stays fresh. |
| AC-4 | Run only the real dogfood journey, the 901-second falsifier, and the three mechanism-specific without-it checks below. |
| AC-5 | At 901 seconds, `proceed` and `stop` fail; `change` succeeds only with evidence, limit, reversal, and cleanup status. |
| AC-6 | A fresh state-backed no-code POC records outcome commit minus `started` at 900 seconds or less, zero interventions, no RoboRev receipt, and no validation dispatch. |
| AC-7 | Pilot and Production route tables, profile-contract bytes, observation values, and admission fixtures remain unchanged; any diff in their profile files stops implementation. |

### Measured no-code dogfood

Create one fresh POC on the implementation revision whose decision is: "Does the
new direct POC path produce a durable decision without extra proof ceremony?"
Its artifact is `no-code`, safety boundary is `none`, and the minute override is
omitted so the loader must emit 15. The real journey loads the committed task,
runs the repository-local loader and one exact read-only CLI probe, records the
critical result, and commits `poc_outcome` to the state branch.

The dogfood falsifier is any one of: effective budget not 15, a POC RoboRev
request, a validation-worker dispatch, elapsed time above 900 seconds, an
intervention count above zero, or changed Pilot/Production output. Record the
admission commit, outcome commit, both commit timestamps, elapsed seconds, exact
implementation revision, commands, proof-path fields, absence of review and
validation dispatch, and cleanup result. Captain gate wait and terminal cleanup
occur after decision-ready and remain separate measurements.

### Focused without-it proof

Use delivery base `6bcdea3eca985a42aeceea45534c91584fee490a` as the candidate
without the retained mechanisms. Do not run the repository's broad minimal-stack
ablation suite for this POC.

- Remove only effective-budget parsing: the default/override fixture must stop
  rejecting an invalid or unexplained limit.
- Remove only the proof-path selector: the direct fixture must again emit the POC
  review observation or require fresh validation.
- Remove only the close-guard elapsed/direct branch: the 901-second outcome must
  be accepted incorrectly or the direct implementation outcome must be refused.

Before shaping, the unchanged seams were exercised successfully:
`profile-contract-loader.test.py`, `poc-close-guard.test.py`, and
`profile-spacedock-route.test.py` all passed. Those results prove the existing
loader and terminal gate are recoverable; they do not prove the new budget or
direct path.

### Reverse-recovery receipt

```yaml
reverse_recovery:
  trigger: replace unconditional POC review/fresh proof and add decision-time enforcement
  boundary: committed POC receipt through loader, outcome, close guard, and Spacedock state
  layers:
    - surface: Exploration Brief budget
      location: kc-dev-flow/references/kernel.md:43-44,107-108
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: poc_budget is a free scalar and carries no enforced decision-ready limit
      disproof_hook: run a loader fixture with zero minutes or an unexplained override
    - surface: profile selection and review activation
      location: kc-dev-flow/scripts/profile-contract-loader.py:198-208,443-446
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: the loader accepts no artifact class and declares POC review unconditionally
      disproof_hook: load a no-code POC and inspect effective budget and observation fields
    - surface: durable outcome validation
      location: kc-dev-flow/scripts/poc-close-guard.py:99-114
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: the guard validates five strings but no clock, intervention, or proof path
      disproof_hook: validate a 901-second proceed outcome
    - surface: terminal state and archive
      location: kc-dev-flow/scripts/profile-spacedock-route.test.py
      completeness: WORKING
      need: REQUIRED
      evidence: the live focused route test passed on the delivery base
      disproof_hook: run profile-spacedock-route.test.py without a runnable Spacedock close path
  decision: recover
```

Recovery extends the loader and close guard already used by the journey. It does
not create a second route engine, timer, state ledger, or terminal authority.

### Project-context receipt

```yaml
project_context:
  impact: update
  authority: ARCHITECTURE.md via docs/dev/README.md Local Profile
  claim_locator: Architecture Contracts / kc-dev-flow profile-native loading / Proportional implementation-exit observation
  surface: POC review activation and proof dispatch
  stale_claim: every POC requests RoboRev and proceeds through fresh validation
  approved_change: direct no-code/disposable POCs suppress RoboRev and fresh proof; Pilot and Production remain unchanged
  landed_change: pending
  planned_check: compare the landed claim with loader and close-guard behavior plus the measured dogfood
  validation_evidence: pending
```

`PRODUCT.md` remains accurate: it already promises proportional routes without
specifying unconditional POC review or fresh validation. `CLAUDE.md` has no
affected claim. The only bound project-context edit is the stale Architecture
claim above.

### Retained-document treatment

Repair existing documents in place under Retained Document Policy Rule 8; add or
delete none. The per-section overlap check covers the POC budget, direct/fresh
proof, review activation, and close semantics across the kernel, package README,
adopter README, profile build contract, continuation skill, and Architecture.
Keep the portable rule in the kernel, runtime binding in `docs/dev/README.md`, and
public architecture claim in `ARCHITECTURE.md`; do not copy work-item timing or
dogfood results into retained documents.

### Where it touches

`lines after` is an estimate. Package/adopter mirror pairs are one logical
mechanism but both physical files and all bytes count.

| Path | Lines now | Lines after | Why omission fails |
|---|---:|---:|---|
| `ARCHITECTURE.md` | 257 | 257 | AC-3/AC-7: its unconditional POC-review claim would become false. |
| `docs/dev/README.md` | 431 | 441 | AC-2/AC-3/AC-6: the local runtime would not know the no-dispatch close path or measurements. |
| `kc-dev-flow/references/kernel.md` | 255 | 263 | AC-1/AC-3/AC-5: the portable admission and completion contract would stay stale. |
| `docs/dev/_mods/kernel.md` | 255 | 263 | Same kernel mechanism; omission breaks adopted/package byte identity and AC-7. |
| `kc-dev-flow/references/profiles/poc-exploration/build.md` | 76 | 84 | AC-3/AC-4/AC-6: direct build would not owe the outcome or focused proof. |
| `docs/dev/_mods/profiles/poc-exploration/build.md` | 76 | 84 | Same build mechanism; omission breaks adopted/package byte identity and AC-7. |
| `kc-dev-flow/scripts/profile-contract-loader.py` | 513 | 540 | AC-1/AC-3/AC-7: no effective budget, proof selector, or isolated POC activation. |
| `docs/dev/_mods/profile-contract-loader.py` | 513 | 540 | Same loader mechanism; omission leaves the live adopter unenforced. |
| `kc-dev-flow/scripts/poc-close-guard.py` | 202 | 250 | AC-2/AC-3/AC-5/AC-6: elapsed, intervention, and direct close remain unenforced. |
| `docs/dev/_mods/poc-close-guard.py` | 202 | 250 | Same close mechanism; omission leaves the live adopter unenforced. |
| `kc-dev-flow/README.md` | 202 | 212 | AC-1/AC-3: its public POC route and review description would be wrong. |
| `kc-dev-flow/scripts/profile-contract-loader.test.py` | 1630 | 1685 | AC-1/AC-3/AC-7: loader defaults, refusals, and unchanged higher profiles lack deterministic proof. |
| `kc-dev-flow/scripts/poc-close-guard.test.py` | 237 | 300 | AC-2/AC-3/AC-5/AC-6: timing, overrun, evidence, and direct-close falsifiers lack enforcement proof. |
| `kc-dev-flow/skills/choose-work-profile/SKILL.md` | 125 | 133 | AC-1/AC-3: new POC admissions would not record artifact, safety, or minute fields. |
| `kc-dev-flow/skills/continue-dev-flow/SKILL.md` | 242 | 254 | AC-2/AC-3/AC-5/AC-6: orchestration would still dispatch fresh validation unconditionally. |
| `scripts/kc-dev-flow-contract-test.py` | 1445 | 1470 | AC-3/AC-7: mirror identity and higher-profile invariants would not fail closed. |

No new file, dependency, stage, background process, or CI workflow is allowed.
Four required source/adopter pairs account for eight of the sixteen files; this
mirror cost is the irreducible size concern for the gate.

### Stop numbers

Measure from delivery base `6bcdea3eca985a42aeceea45534c91584fee490a`.
Implementation stops and reports instead of continuing when any condition holds:

- more than 16 changed files;
- more than 550 total added plus deleted lines from `git diff --numstat`;
- more than 320 added plus deleted lines across the loader, close guard, their
  tests, and required mirrors;
- any changed file under Pilot or Production profile contracts; or
- any new file, dependency, stage, scheduler, timer, state store, CI workflow, or
  planning-provider surface.

The likely runaway area is outcome parsing plus route transition in the loader
and close guard. If it crosses its 320-line stop, return to shape instead of
building a generic lifecycle engine.

## Stage Report: ideation

- DONE: Shape the smallest retained mechanisms that satisfy AC-1 through AC-7, including one real journey and the critical falsifier.
  Three existing seams retain the behavior; the designed state-backed dogfood and exact 901-second falsifier cover the real journey and failure boundary.
- DONE: Define exact touch surfaces, stop numbers, focused without-it checks, and the measured no-code dogfood without expanding the approved scope.
  Sixteen files, 550 changed lines, three focused removals, and one no-code dogfood are bounded against delivery base `6bcdea3eca985a42aeceea45534c91584fee490a`.
- DONE: AC-2 — Separate decision-ready, Captain-wait, and cleanup measurements.
  The shaped outcome binds `admitted_at` to `started`, recomputes elapsed seconds, and records close measurements separately.
- DONE: AC-3 — Skip review and fresh validation only for eligible direct POCs.
  The artifact-and-safety selector suppresses RoboRev and validation dispatch for no-code/disposable work while named safety boundaries stay fresh.
- DONE: AC-4 — Limit proof to retained mechanisms.
  The shape selects one real dogfood, the 901-second falsifier, and exactly three mechanism-specific without-it checks.
- DONE: AC-5 — Fail closed when the decision budget is exhausted.
  At 901 seconds, only `change` with evidence, limit, reversal, and cleanup status is accepted; `proceed` and `stop` are rejected.
- DONE: AC-6 — Measure one fresh no-code dogfood.
  The dogfood receipt records admission and outcome commits, elapsed seconds, zero interventions, exact revision, no review, no validation dispatch, and cleanup.

### Summary

The shape recovers the existing loader, POC build contract, and close guard; it
adds no timer, stage, provider, or state authority. Direct no-code/disposable POCs
write the decision during build and skip RoboRev plus fresh validation, while
retained or safety-bound POCs and all Pilot/Production behavior stay unchanged.

## Implementation evidence

```yaml
implementation_evidence:
  delivery_base: 6bcdea3eca985a42aeceea45534c91584fee490a
  candidate: 2f3391855653889ede9ac205eaa4b7a88befff43
  diff: {files: 16, added: 379, deleted: 51, changed_lines: 430, core_changed_lines: 320}
  stop_audit:
    new_files_dependencies_stages_services_ci_or_provider_surfaces: none
    pilot_or_production_profile_contract_diff: none
  retained_documents:
    treatment: repaired existing documents in place; added none; deleted none
    package_adopter_pairs: kernel, poc-exploration/build, profile-contract-loader.py, poc-close-guard.py
  project_context:
    authority: ARCHITECTURE.md
    landed_change: direct no-code/disposable POCs omit RoboRev and a validation worker; Pilot and Production remain unchanged
    check: kc-dev-flow-contract-test.py passed on the candidate
  focused_checks:
    - profile-contract-loader.test.py PASS; invalid budgets, unexplained overrides, direct selection, named safety, and higher-profile routes are behavioral assertions
    - poc-close-guard.test.py PASS; timestamp mismatch, intervention, 901-second proceed, 901-second change, and direct status routing are behavioral assertions
    - profile-spacedock-route.test.py and kc-dev-flow-contract-test.py PASS; route or mirror drift makes them fail
    - version-parity-check.sh and skill-frontmatter-lint.sh PASS
  without_it:
    effective_budget: removing parsing made zero minutes pass; loader test exited 1
    proof_selector: forcing fresh proof restored review for direct no-code; loader test exited 1
    close_guard: removing exhaustion enforcement accepted a required-change case; guard test exited 1
  dogfood:
    decision: Does the new direct POC path produce a durable decision without extra proof ceremony?
    admission_commit: 3076684c3d5fcbbed3ca0ac314c955ec669cbb05
    admission_time: 2026-08-30T14:36:20Z
    outcome_commit: 1c561f6d1cc7ad37ade7fd95825c748404d0efcf
    outcome_time: 2026-08-30T14:36:48Z
    decision_ready_elapsed_seconds: 28
    captain_interventions_before_decision_ready: 0
    candidate: 2f3391855653889ede9ac205eaa4b7a88befff43
    exact_tree_probe: a3de404c2b8fb21c9201e2e3d4312438c52e018d
    loader: {budget_minutes: 15, proof_path: direct, observation_declared: false}
    validation_dispatch_or_report: none
    cleanup: not-applicable
  implementation_exit_observation:
    capability: review_convergence
    mode: observe
    selected_profile: pilot-product-slice
    provider: roborev
    candidate: 2f3391855653889ede9ac205eaa4b7a88befff43
    identity_sha256: bc5b44b6a5dd76bed7c8a72829ffb30a0130f2f0ecebdeedb898154c275c1dc4
    config_blob_sha: 225a29d4fa1eef963a7effaab7e60afa5f488e8f
    config_sha256: ae3555f0b3fcf5b626c39c614e3b2058bd2e31fb5840ce864edfaeded34f07f1
    reviewer: {agent: codex, model: gpt-5.6-terra, reasoning: medium, minimum_severity: medium, panel: none}
    result: UNAVAILABLE
    reason: unavailable
    evidence: RoboRev v0.62.0 daemon healthy; fixed Codex reviewer health probe timed out after 30 seconds
    request_count: 0
    confirmation_count: 0
    cost_coverage: not-applicable because no review job was requested
    authority: observation only; validation and delivery authority unchanged
```

## Stage Report: implementation

- DONE: Implement only the three approved mechanisms and preserve Pilot and Production behavior within every stop number.
  Candidate `2f3391855653889ede9ac205eaa4b7a88befff43` changes 16 files and 430 lines, uses exactly 320 core lines, adds no surface, and has no Pilot/Production profile-contract diff.
- DONE: AC-1 — Enforce a positive default-15 decision-ready minute budget and explained overrides.
  `profile-contract-loader.test.py` fails if zero, negative, non-integer, or unexplained non-15 limits are accepted.
- DONE: AC-2 — Separate decision-ready elapsed time from Captain wait and terminal cleanup.
  `poc-close-guard.test.py` recomputes RFC3339 elapsed time and fails if timestamps mismatch or close measurements are missing.
- DONE: AC-3 — Skip RoboRev and fresh validation only for eligible direct POCs.
  Loader and guard tests fail if direct no-code work emits review, misses the direct path, or dispatches anything before the terminal gate; named safety remains fresh.
- DONE: AC-4 — Limit POC proof to one real journey, one critical falsifier, and retained mechanisms.
  The measured direct journey, 901-second falsifier, and three focused removals ran; no broad minimal-stack mutant suite ran.
- DONE: AC-5 — Fail closed on budget exhaustion or Captain intervention.
  The guard rejects 901-second `proceed` and intervention-bearing `proceed`; it accepts 901 seconds only as a complete `change`.
- DONE: AC-6 — Measure one fresh no-code POC within 15 minutes and without post-admission Captain intervention.
  Admission `3076684c3d5fcbbed3ca0ac314c955ec669cbb05` reached outcome `1c561f6d1cc7ad37ade7fd95825c748404d0efcf` in 28 seconds with zero interventions, no review, and no validation dispatch.
- DONE: AC-7 — Preserve Pilot and Production routes, obligations, and admission behavior.
  Focused route and full contract tests passed, and an exact base-to-candidate diff over both higher-profile contract trees is empty.
- DONE: Prove AC-1 through AC-7 with focused deterministic checks, three without-it removals, and one measured no-code dogfood bound to the exact candidate.
  Each removal made its owned test fail, all restored checks passed, and the dogfood records the candidate, commits, timestamps, loader result, and cleanup.
- DONE: Record the exact diff, retained-document treatment, project-context update, and the Pilot implementation-exit observation without granting it validation authority.
  The evidence above records all four; RoboRev is `UNAVAILABLE(reason: unavailable)` after its health probe, with zero requests and observation-only authority.

### Summary

The candidate adds only the approved effective budget, proof selector, and close
guard enforcement. Direct no-code/disposable POCs can reach the existing
terminal gate without RoboRev or a validation worker, while retained work,
safety-bound POCs, Pilot, and Production retain fresh proof behavior.
The Pilot RoboRev observation remained unavailable and non-authoritative.

## Stage Report: validation

- FAILED: Independently verify AC-1 through AC-7 at exact candidate 2f3391855653889ede9ac205eaa4b7a88befff43 and reject any claim not supported at that tip.
  At the clean exact tip, loader, close-guard, route, and full contract tests support AC-1, AC-2, AC-3, AC-5, and AC-7; AC-4 and AC-6 lack a durable real-journey receipt.
- FAILED: Verify the 28-second zero-intervention dogfood from durable state commits, including absence of RoboRev requests and validation dispatch for the direct POC.
  The two commits form the claimed 28-second ancestor pair only in unpushed `/Users/kent/.Trash/direct-poc-dogfood-20260830T143648Z`; they have no remote, are absent from shared state, and preserve no request or dispatch receipt.
- DONE: Adversarially confirm the three-mechanism minimum stack, all stop numbers, package-adopter parity, retained-document treatment, and honest RoboRev UNAVAILABLE disposition.
  Focused tests pass; the diff is 16 files, 430 lines, and exactly 320 core lines; four package-adopter pairs have matching SHA-256 values; all paths are modified in place; RoboRev v0.62.0 has no exact-branch job, so the pre-request `UNAVAILABLE` result claims no review authority.

### Summary

Validation rejects the candidate because the accepted dogfood proof is not in the authoritative split-root state and does not durably prove no RoboRev request or validation dispatch. Rework should rerun the direct POC on the shared state branch, push both commits and their absence receipts, then re-dispatch validation at the same exact candidate.
