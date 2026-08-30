---
title: "Add a workspace-bound Linear reader and admission guard"
status: ideation
source: "https://linear.app/duckbase-co/issue/DEV-12/add-a-workspace-bound-linear-reader-and-admission-guard"
product: kc-dev-flow
planning-window: "Linear Cycle b788c52d-8370-475f-be4f-8fcd88dd03d6 2026-08-27T16:00:00.000Z/2026-09-10T16:00:00.000Z"
planning-outcome: "Linear Project 535b8bd1-2d97-4d57-9161-1051574af0d5 Repeatable Linear admission under 1 minute sha256:74d2f2065da858dfe47fe3c04f6b32f0cddb9418d477de18b766dc5089254854"
sprint: repeatable-linear-admission-under-one-minute
sprint-readiness: ready
started: 2026-08-30T10:11:04Z
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: np4b5ef99wf5tns6r7aqs10p
gates:
    version: 1
    records:
        - id: gate:np4b5ef99wf5tns6r7aqs10p:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:np4b5ef99wf5tns6r7aqs10p-backlog-1
              briefing:
                id: briefing:np4b5ef99wf5tns6r7aqs10p:backlog:attempt-1:revision-1
                digest: sha256:d957aa962460d82265eb1b209882c1fb94a5f9f730bad3285ea9790107fd1fa0
                request-digest: sha256:d389c270362b520d29fb75b44a2009188fee723770ce1223a38ebd69df97677c
                room-ref: ./review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:np4b5ef99wf5tns6r7aqs10p:backlog:1
                briefing: briefing:np4b5ef99wf5tns6r7aqs10p:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-08-30T10:09:33.703034Z"
                decision: approve
                reason: Captain approved the DEV-12 Pilot and the one-time manual workspace Linear MCP bootstrap for initial admission only; validation must use the durable reader and retain no exception.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:np4b5ef99wf5tns6r7aqs10p:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:np4b5ef99wf5tns6r7aqs10p-ideation-1
              briefing:
                id: briefing:np4b5ef99wf5tns6r7aqs10p:ideation:attempt-1:revision-1
                digest: sha256:e362aa8d68d66fbc893646535091801441fd33ad5f190e2adccfab0516839533
                request-digest: sha256:a71cab564b59dd27a70565bf670fb3b84ca0e9e2dfbb66993a7a010bd94f4c2f
                room-ref: ./review/ideation/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-08-30T10:35:35.951128Z"
                reason: Captain approved replacing the internal Acceptance evidence list with the single Spacedock-native Acceptance criteria plus AC-N contract; the prepared ideation snapshot is stale.
---

## The problem

DEV-11 proved that Linear planning can enter the existing provider-neutral kc-dev-flow contract, but the path still depends on manual MCP reads and hand-built normalization. There is no persistent workspace-bound reader, and the loader does not enforce the Development Brief plus complete-or-absent Planning Receipt for Pilot or Production admission. The measured admission-to-verdict interval was 41m43s.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: >-
    One maintainer will repeatedly use a persistent repository-local admission
    path that reads the current workspace's Linear account and creates durable
    execution state only after a clean reconcile. This is limited real use with
    likely iteration, but it accepts no production data, unattended operation,
    compatibility migration, automatic launch, SLO, or release duty.
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - Preserve the existing five-field provider-neutral Planning Receipt; Linear remains the planning authority and Spacedock remains the execution authority.
      - Bind authentication to the current workspace and fail closed before execution-state mutation.
    implementation:
      - Retain only a workspace-bound Linear reader, loader admission guard, exact snapshot binding, comparator stop, and dispatch-envelope path required by the accepted journey.
      - Create no mirror, synchronization, polling, webhook, automatic launch, paid Linear Agent delegation, or second planning authority.
    testing:
      - Measure no more than 60 seconds from successful Todo-plus-Cycle update readback to a valid dispatch envelope, excluding prior human review and later worker startup.
      - Prove authentication refusal, invalid Development Brief refusal, partial Planning Receipt refusal, clean status progress, classified planning drift, and without-it failure for each retained component.
  scope_boundary: >-
    One repository, one workspace-bound Linear account, one Project, one Cycle,
    one issue, one Spacedock task, and one execution worktree. No multi-issue
    package, Initiative, Milestone, automatic launch, migration of prior work,
    POC-profile redesign, production operation, or broader provider framework.
  promote_when:
    - Unattended operation, production credentials or data, cross-repository reuse, compatibility migration, automatic launch, or an SLO becomes accepted scope.
  decision:
    authority: Kent Chen (Captain)
    at: 2026-08-30T09:59:53Z
```

## Accepted outcome

Starting from successful readback of one Captain-approved Todo-plus-Cycle update, emit a valid kc-dev-flow dispatch envelope within 60 seconds and with no further Captain intervention, using the workspace's Linear connection, the existing five-field snapshot, read-only reconcile, and fail-closed loader validation.

## Non-goals

- No GitHub mirror, bidirectional synchronization, polling, or webhook.
- No automatic workspace launch.
- No paid Linear Agent coding delegation.
- No multi-issue package, Initiative, or Milestone.
- No POC-profile redesign.
- No migration of previously admitted work.

## Acceptance evidence

- One live workspace-bound Linear read resolves DEV-12, its Project, Cycle 1, and the complete admitted set into the existing five-field snapshot.
- Missing or invalid authentication stops before task creation, state mutation, or dispatch without altering the real credential.
- Pilot and Production admission rejects a missing or invalid Development Brief and a partial Planning Receipt before task creation or dispatch.
- Todo to In Progress remains clean; a changed Cycle, Project package, goal, non-goal, or admitted membership stops with a classified delta.
- A fresh exact-revision measurement emits a valid dispatch envelope within 60 seconds of Todo-plus-Cycle update readback with no additional Captain intervention.
- Removing any retained reader, loader guard, snapshot binding, comparator behavior, or dispatch stop breaks a named accepted property.

## Route-back conditions

Return to Linear Planning with `change` or `stop` if the 60-second target requires synchronization or automatic launch, workspace-bound authentication cannot fail closed, the five-field provider-neutral contract cannot express the planning object, or any accepted goal or non-goal changes.

## Measurement

An external validation harness captures monotonic `t0` when the authorized
Todo-plus-Cycle update readback succeeds, immediately invokes the admission
command, and captures `t1` only after it parses the emitted dispatch envelope.
The accepted wall-clock measurement is `t1 - t0`, so it includes command
startup, the command's fresh Linear read, normalization, snapshot binding,
reconcile, loader work, and envelope emission. The command may separately
report its process-local elapsed time for diagnosis, but that shorter interval
does not prove the 60-second journey. Record the exact candidate revision, both
intervals, Captain interventions after admission, clean and drift results,
retained components, the acceptance evidence broken by removing each
component, and cleanup status.

## Pilot shape

### Delta versus the delivery base

The delivery base is fetched `origin/main` at
`7256e02dbbc5340e4328bfeeb016448e4033fde5`. The proposed route changes ten
files and is expected to change about 1,050 lines: most of the size is the
provider fixture coverage, existing loader tests, package/adopter parity, and
ablation proof rather than new runtime behavior. It is the minimum one-PR
route because landing the loader alone leaves the manual Linear bootstrap,
while landing the reader alone admits invalid briefs and partial receipts; use
two reviewable commits in one Draft PR, generic admission enforcement followed
by the repository-local Linear adapter.

### Accepted journey

1. **OBSERVED:** Conductor exposes the current local workspace identity and a
   non-empty `LINEAR_API_KEY` to this session; the prior DEV-11 run observed
   Linear Project, Cycle, and issue readback and retained no credential or
   provider payload.
2. **DESIGNED:** An external validation harness observes the successful
   readback of the separately authorized Todo-plus-Cycle update, captures
   monotonic `t0`, and immediately starts the read-only admission command. The
   harness neither performs nor repeats the update; it only owns the full
   journey clock.
3. **DESIGNED:** `linear-admission.py` — one read-only admission command — pins
   the exact committed work item and state revision, then invokes the profile
   loader before provider access. The loader accepts Pilot or Production only
   when the Development Brief has exactly one non-placeholder problem,
   accepted outcome, non-goal list, acceptance-evidence list, and route-back
   section, and when the Planning Receipt tuple is complete or absent.
4. **DESIGNED:** For the complete Linear receipt, the command reads the key
   only from the current Conductor process environment, requires the current
   `CONDUCTOR_WORKSPACE_ID`, and checks that the authenticated Linear
   organization is `duckbase-co`. It follows the exact issue source, paginates
   the Project-plus-Cycle set whose state type is `unstarted` or `started`, and
   also re-reads still-active snapshot sources that moved outside that scope.
   Missing variables, an authentication or organization mismatch, malformed
   data, incomplete pagination, network failure, or timeout emits no envelope
   and exits before state access or mutation.
5. **DESIGNED:** The command derives the committed five-field snapshot from
   the immutable state revision for every ready execution item sharing the
   engaged `sprint`. It maps source, planning window, planning outcome,
   accepted outcome, and complete non-goals without writing an intermediate
   file; it rejects a dirty, changing, missing, duplicate, or mixed-scope
   snapshot.
6. **OBSERVED:** The unchanged `engage-reconcile.py` comparator at `7256e02`
   returned exit `0` with four empty delta arrays after DEV-11 moved from Todo
   to In Progress, and returned exit `1` with `moved` after intentional Project
   digest drift. The designed command accepts only exit `0` plus one parsed
   `status: clean` object; `added`, `removed`, `changed`, `moved`, invalid
   output, process death, or no answer emits no envelope.
7. **DESIGNED:** At process entry, the command records a diagnostic monotonic
   start, then binds the work-item hash, state revision, Linear
   organization, five-field snapshot hash, live-read hash, clean reconcile,
   and loaded profile-contract hashes into one
   `kc-dev-flow-dispatch-envelope/v1` JSON object. The envelope's
   `command_elapsed_ms` covers process entry through emission and is useful for
   diagnosis, but does not include the external readback-to-invocation gap and
   is not the accepted metric. After parsing the envelope, the harness captures
   `t1` and proves `journey_elapsed_ms = t1 - t0 <= 60000`; this full interval
   includes the command's fresh provider read. The First Officer may dispatch
   from that envelope; the command never creates a task, launches a workspace,
   or contacts a worker.
8. **DESIGNED:** Every refusal is safe to retry after the credential, network,
   state race, or Captain-approved snapshot is repaired. A crash, abandonment,
   timeout, or rerun leaves Linear and Spacedock unchanged and cannot reuse an
   earlier envelope because each envelope binds the current work-item and state
   revisions.

There is no manual MCP read, hand-written normalization, temporary snapshot,
or Captain prompt in the steady-state route. Provisioning the workspace
environment variable remains configuration outside the measured journey; the
reader has no OAuth, shared-account, or interactive fallback.

### Observable semantics

- New command: `python3 scripts/kc-dev-flow/linear-admission.py` takes the exact
  workflow directory, work item, contracts root, comparator, Linear workspace,
  and timeout; secrets are environment-only.
- Success stdout is one JSON dispatch envelope and exit `0`. Every refusal uses
  non-secret stderr, non-zero exit, and empty stdout, so envelope presence is
  the mechanical dispatch stop.
- The envelope's `command_elapsed_ms` is a diagnostic segment only. The
  external validation receipt owns `readback_t0`, `envelope_t1`, and
  `journey_elapsed_ms`; only that receipt can prove the accepted 60-second
  boundary.
- The profile loader newly rejects an invalid Development Brief or partial
  Planning Receipt and returns hashes for the validated brief and complete or
  absent receipt. Its selected route, stage loading, and hash binding remain
  unchanged.
- The five-field snapshot and comparator exit/output schemas remain unchanged.
  Todo-to-In-Progress is execution progress, while Project, Cycle, accepted
  goal, non-goal, or membership differences remain planning drift.
- No stored schema, planning authority, execution authority, or delivery
  authority changes. The dispatch envelope is ephemeral input to the First
  Officer, not a second execution record.

### Persistence, recovery, and data safety

- Persistent inputs are only the committed Linear Planning Receipt,
  Development Brief, admitted Spacedock snapshot, and selected profile receipt.
  Linear results, normalized current data, and the envelope stay in memory or
  stdout; later stage evidence may record hashes, revisions, the harness's
  `readback_t0`, `envelope_t1`, full `journey_elapsed_ms`, and diagnostic
  `command_elapsed_ms`, not the token or raw provider response.
- The reader uses GraphQL query operations only, requests only organization,
  issue, Project, Cycle, state, goal, and non-goal fields, follows pagination,
  and has no mutation, comment, webhook, poller, cache, mirror, or retry loop.
- The real credential is never accepted as an argument, written, echoed,
  hashed, mutated, or copied to a fixture. Authentication tests unset the real
  variable or use a fake local endpoint with synthetic keys.
- Recovery is operator repair plus a fresh rerun. Authentication and transient
  transport failures do not fall back; state-head races and timeouts do not
  reuse partial results; planning drift requires Captain admission and a newly
  committed snapshot before rerun.

### Falsifiable acceptance checks

| Property | Check that must pass | Change that makes it fail |
|---|---|---|
| End-to-end under 60 seconds | On the exact candidate revision, an external harness captures monotonic `t0` at successful readback of the separately authorized DEV-12 Todo-plus-Cycle update, immediately invokes the command, captures `t1` after parsing one bound envelope, and asserts `t1 - t0 <= 60000` with zero later Captain prompts. It also records `command_elapsed_ms` only as a nested diagnostic and proves the full interval contains the command's fresh Linear request. | Manual JSON/MCP input, an interactive prompt, missing binding, invalid envelope, omitted provider-read interval, use of `command_elapsed_ms` as the acceptance result, or `t1 - t0` above 60 seconds. |
| Workspace-bound authentication | Run with the current workspace variables; then independently test missing key, missing Conductor identity, synthetic 401, and wrong Linear organization. Assert all refusals have empty stdout and unchanged state. | Any fallback credential, accepted mismatch, secret-bearing diagnostic, task creation, state write, or envelope. |
| Development Brief | Mutate each required section to missing, duplicate, empty, or placeholder and run the loader before provider access. | Any malformed Pilot or Production brief loads a route. |
| Complete-or-absent Planning Receipt | Exercise all eight presence combinations for source, window, and outcome: zero or three may load, while the other six fail before provider access. | A partial tuple loads or an absent standalone tuple invokes Linear. |
| Exact snapshot binding | Change the work-item bytes, state revision, source, window, outcome, accepted goal, non-goal, or admitted membership between reads. | A stale or mixed snapshot produces an envelope, or no changed hash/delta identifies the premise. |
| Planning semantics | Live Todo-to-In-Progress stays clean; fixtures classify Cycle or Project as `moved`, goal or non-goal as `changed`, and membership as `added` or `removed`. | Status-only progress stops, or any planning change is clean/unclassified. |
| Read-only and cleanup | A fake GraphQL server rejects mutation text and captures requested fields; compare Linear fixtures, state HEAD/status, temp paths, and credential value before and after every outcome. | Provider/state bytes change, an intermediate survives, unnecessary fields are fetched, or the real credential changes. |
| Dispatch stop | Feed auth, brief, receipt, truncation, comparator, state-race, and timeout failures to the integration fixture and assert empty stdout; feed the clean case and assert one envelope. | Any failure produces dispatchable stdout or success produces more than one object. |
| Without-it proof | Mutate away each retained reader, loader check, state/hash binding, comparator exit/payload check, and empty-stdout dispatch stop. | The contract and ablation suites do not reject every mutant. |

### Reverse-recovery receipt

```yaml
reverse_recovery:
  trigger: persistent Linear reader plus missing Pilot and Production admission enforcement
  boundary: one repository, DEV-12, the adopted kc-dev-flow engage path, and dispatch-envelope emission
  layers:
    - surface: Local Profile entry and steady-state command
      location: docs/dev/README.md:44
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: Current binding names a GitHub reader; DEV-11 required manual Linear MCP and hand normalization.
      disproof_hook: Run the Local Profile command from a fresh Conductor workspace without manual provider input.
    - surface: Development Brief and Planning Receipt contract
      location: kc-dev-flow/references/kernel.md:35
      completeness: WORKING_UNIT_UNPROVEN
      need: REQUIRED
      evidence: The contract is explicit, but the current loader parses only profile and scheduling fields.
      disproof_hook: Pass a Pilot fixture with a missing brief and a partial receipt to the loader.
    - surface: Linear read and normalization handler
      location: MISSING
      completeness: MISSING
      need: REQUIRED
      evidence: Filename search and behavior search across tracked scripts found no Linear admission reader; the archived POC records no retained adapter.
      disproof_hook: Find a tracked command that authenticates, paginates, normalizes, and runs without manual JSON.
    - surface: Admitted snapshot persistence and binding
      location: docs/dev/.spacedock-state plus five-field work-item sections
      completeness: WORKING
      need: REQUIRED
      evidence: DEV-11 retained the exact tuple, goal, and non-goals and reconciled clean at a committed state revision.
      disproof_hook: Reconstruct the group from the pinned state revision and compare its canonical hash.
    - surface: Provider-neutral comparator
      location: kc-dev-flow/scripts/engage-reconcile.py:1
      completeness: WORKING
      need: REQUIRED
      evidence: Contract tests and live clean/drift runs passed at 7256e02.
      disproof_hook: Run engage-reconcile.test.py and the clean plus intentional-drift fixture.
    - surface: Dispatch stop and envelope
      location: kc-dev-flow/skills/continue-dev-flow/SKILL.md:23
      completeness: WORKING_UNIT_UNPROVEN
      need: REQUIRED
      evidence: Prose stops were manually exercised, but no machine-valid envelope binds the read, snapshot, comparator, and loader.
      disproof_hook: Cause each refusal and observe whether dispatchable stdout exists.
  decision: recover the existing route, add only the proven-missing local adapter, and reuse the comparator
```

Two bounded searches support the `MISSING` classification: tracked filename
enumeration for Linear/admission/reader scripts, and content search for provider
read, dispatch-envelope, and comparator consumers across `kc-dev-flow/`,
`scripts/`, and `docs/dev/`. External hosted automation and unrelated plugins
were excluded; the prior live POC and archived work item were included.

### Where it touches

| Path | Lines now | Lines after | Journey obligation |
|---|---:|---:|---|
| `scripts/kc-dev-flow/linear-admission.py` | 0 | 280 | Workspace authentication, paginated read, five-field normalization, immutable state binding, comparator invocation, internal diagnostic timing, and success-only envelope. |
| `kc-dev-flow/scripts/profile-contract-loader.py` | 419 | 500 | Fail-closed Development Brief and complete-or-absent Planning Receipt validation before route load. |
| `kc-dev-flow/scripts/profile-contract-loader.test.py` | 1,455 | 1,640 | Falsify every brief section, receipt presence combination, duplicate, placeholder, and valid standalone/provider case. |
| `docs/dev/_mods/profile-contract-loader.py` | 419 | 500 | Preserve byte-identical adopted loader behavior used by this workflow. |
| `kc-dev-flow/skills/continue-dev-flow/SKILL.md` | 228 | 250 | Prefer the bound admission guard and treat one valid envelope as the only provider-backed dispatch input; retain manual fallback for adopters without a guard. |
| `docs/dev/README.md` | 403 | 435 | Bind `duckbase-co`, the Conductor environment credential, the local guard, and its exact command without changing authorities. |
| `kc-dev-flow/README.md` | 192 | 210 | Document the strengthened loader and optional adopter admission-guard seam. |
| `scripts/kc-dev-flow-contract-test.py` | 1,182 | 1,450 | Fake Linear/state integration, external full-boundary timing, envelope/auth/data-safety checks, and package/adopter binding. |
| `scripts/kc-dev-flow-minimal-stack-ablation.test.py` | 487 | 555 | Reject removal of reader, loader checks, snapshot binding, comparator validation, or dispatch stop. |
| `ARCHITECTURE.md` | 252 | 265 | Repair the profile-loading claim to include admission validation and the provider guard outside the provider-neutral loader. |

The existing `kc-dev-flow/scripts/engage-reconcile.py` and adopted
`scripts/kc-dev-flow/engage-reconcile.py` remain byte-identical and unchanged;
their 168-line behavior is exercised, not redesigned.

### Retained mechanism map

| Retained mechanism | Goal or safety boundary | Without-it failure |
|---|---|---|
| Workspace Linear reader inside `linear-admission.py` | Replace manual MCP and normalization while failing closed on credential, organization, pagination, and timeout. | No repeatable live read, or a wrong/truncated workspace can be dispatched. |
| Loader Development Brief and receipt guard | Reject invalid authority inputs before provider access or state read. | Pilot/Production admits missing scope or a provider path with no complete identity. |
| State-revision and canonical snapshot binding | Make the compared five fields and execution group exact and replayable. | A clean result can describe different work-item or state bytes than the dispatch. |
| Existing comparator exit and payload behavior | Preserve clean progress and classify planning drift without writes. | Todo progress falsely blocks, or Project/Cycle/goal/non-goal/membership drift proceeds. |
| Success-only envelope and First Officer stop | Give dispatch one machine-checkable, current input without automatic launch. | A failure can be mistaken for approval, or an old receipt can authorize new work. |

### Stop numbers and scope guard

Measure all thresholds as additions plus deletions from
`7256e02dbbc5340e4328bfeeb016448e4033fde5` using diff numstat. Stop and return
to shape when the diff reaches **11 changed files**, **1,201 changed lines**, or
**301 changed lines in `scripts/kc-dev-flow/linear-admission.py`**, the provider
read/normalization area most likely to grow. These are halt conditions: do not
trade test, parity, data-safety, or dispatch-stop coverage to remain below them.

No retained component may add a GitHub mirror, synchronization, polling,
webhook, automatic workspace launch, paid Linear Agent delegation, multi-issue
package, Initiative, Milestone, POC redesign, prior-work migration, provider
framework, or production operation. Needing any of them is a route-back event,
not justification to raise a stop number.

### Project-context receipt

```yaml
project_context:
  impact: update
  authority: ARCHITECTURE.md
  claim_locator: kc-dev-flow profile-native loading
  surface: exact-work-item profile loading and provider-backed admission
  stale_claim: The loader is described as binding only status and profile receipt before emitting three policy artifacts.
  approved_change: State that the loader also validates the Development Brief and complete-or-absent Planning Receipt, while a repository-local provider guard owns authentication, current read, snapshot reconcile, and dispatch-envelope emission.
  landed_change: pending
  planned_check: Run the loader and Linear admission contract fixtures, then compare the architecture claim with their observed success and refusal behavior.
  validation_evidence: pending
```

No retained document is added or removed. Update `ARCHITECTURE.md`, both README
sections, and the existing continuation instructions in place; keep task status,
revision, timing, and live credential facts in this work item rather than the
retained documents.

## Stage Report: ideation

- DONE: Define one end-to-end Pilot journey from the workspace-bound Linear read through the existing five-field snapshot and clean reconcile to a valid dispatch envelope within 60 seconds; the one-time manual bootstrap must not exist in the steady-state route.
  `Accepted journey` defines one non-interactive command from Conductor-bound authentication through immutable snapshot, observed comparator behavior, measured success-only envelope, and safe retry.
- DONE: Define fail-closed authentication, Development Brief, complete-or-absent Planning Receipt, and planning-drift behavior with falsifiable acceptance checks, observable semantics, persistence, recovery, and data-safety boundaries.
  `Observable semantics`, `Persistence, recovery, and data safety`, and nine falsifiable checks name every refusal, authority, mutation boundary, and recovery path.
- DONE: Name the smallest file-level implementation surface and diff-based stop numbers, mapping every retained reader, loader guard, snapshot binding, comparator behavior, and dispatch stop to a goal, safety boundary, or without-it failure while preserving all declared non-goals.
  Ten files are mapped from base `7256e02`; implementation halts at 11 files, 1,201 changed lines, or 301 adapter lines, and the retained-mechanism table plus scope guard covers every component and non-goal.

### Summary

The shaped Pilot is one fail-closed, read-only command that replaces DEV-11's manual MCP and normalization steps without changing the five-field contract or automatically launching work. The route recovers the loader and dispatch wiring, adds only the missing workspace Linear adapter, preserves the proven comparator, and keeps every output bound to current committed inputs.

## Stage Report: ideation (cycle 2)

- DONE: Define one end-to-end Pilot journey from the workspace-bound Linear read through the existing five-field snapshot and clean reconcile to a valid dispatch envelope within 60 seconds; the one-time manual bootstrap must not exist in the steady-state route.
  The repaired journey starts at external monotonic `t0` on successful Todo-plus-Cycle update readback and ends at `t1` after envelope parsing, explicitly including command startup and the command's fresh Linear read; `command_elapsed_ms` is diagnostic only.
- DONE: Define fail-closed authentication, Development Brief, complete-or-absent Planning Receipt, and planning-drift behavior with falsifiable acceptance checks, observable semantics, persistence, recovery, and data-safety boundaries.
  The unchanged refusal, persistence, recovery, and read-only boundaries now store the external full-journey timestamps separately from the shorter internal timing, so timing cannot weaken any stop.
- DONE: Name the smallest file-level implementation surface and diff-based stop numbers, mapping every retained reader, loader guard, snapshot binding, comparator behavior, and dispatch stop to a goal, safety boundary, or without-it failure while preserving all declared non-goals.
  The ten-file surface and all stop numbers remain unchanged; only the adapter's internal timing and the contract harness's authoritative external measurement responsibilities were clarified.

### Summary

The accepted 60-second proof now spans the full update-readback-to-envelope boundary and includes the provider read. The admission command remains read-only and may report its own shorter duration, but only the external harness interval can satisfy the Pilot metric.
