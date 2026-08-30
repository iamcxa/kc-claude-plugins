---
title: "Add a workspace-bound Linear reader and admission guard"
status: validation
source: "https://linear.app/duckbase-co/issue/DEV-12/add-a-workspace-bound-linear-reader-and-admission-guard"
product: kc-dev-flow
planning-window: "Linear Cycle b788c52d-8370-475f-be4f-8fcd88dd03d6 2026-08-27T16:00:00.000Z/2026-09-10T16:00:00.000Z"
planning-outcome: "Linear Project 535b8bd1-2d97-4d57-9161-1051574af0d5 Repeatable Linear admission under 1 minute sha256:74d2f2065da858dfe47fe3c04f6b32f0cddb9418d477de18b766dc5089254854"
sprint: repeatable-linear-admission-under-one-minute
sprint-readiness: ready
started: 2026-08-30T10:11:04Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-repeatable-linear-admission-under-one-minute
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
            - id: gate-attempt:np4b5ef99wf5tns6r7aqs10p-ideation-2
              briefing:
                id: briefing:np4b5ef99wf5tns6r7aqs10p:ideation:attempt-2:revision-1
                digest: sha256:ae20440e2a9d139ab996caed53186c10e658ee16ccb129c0ca0f2e32c48dabac
                request-digest: sha256:5f5a3a3f4def9c771659a3e9aad04aeec3e70b90697676e78f077d7ed3aa499b
                room-ref: ./review/ideation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:np4b5ef99wf5tns6r7aqs10p:ideation:2
                briefing: briefing:np4b5ef99wf5tns6r7aqs10p:ideation:attempt-2:revision-1
                by: person:captain
                at: "2026-08-30T10:55:29.840978Z"
                decision: approve
                reason: Captain replied ok to the presented DEV-12 ideation gate, approving the shaped admission command, canonical AC contract, bounded fourteen-file implementation, and declared stop numbers.
              application:
                target-stage: implementation
                state: consumed
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

## Acceptance criteria

- **AC-1** One live workspace-bound Linear read resolves DEV-12, its Project, Cycle 1, and the complete admitted set into the existing five-field snapshot.
- **AC-2** Missing or invalid authentication stops before task creation, state mutation, or dispatch without altering the real credential.
- **AC-3** Pilot and Production admission rejects a missing or invalid Development Brief and a partial Planning Receipt before task creation or dispatch.
- **AC-4** Todo to In Progress remains clean; a changed Cycle, Project package, goal, non-goal, or admitted membership stops with a classified delta.
- **AC-5** A fresh exact-revision measurement emits a valid dispatch envelope within 60 seconds of Todo-plus-Cycle update readback with no additional Captain intervention.
- **AC-6** Removing any retained reader, loader guard, snapshot binding, comparator behavior, or dispatch stop breaks a named accepted property.

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
retained components, the acceptance criterion broken by removing each
component, and cleanup status.

## Pilot shape

### Delta versus the delivery base

The delivery base is fetched `origin/main` at
`7256e02dbbc5340e4328bfeeb016448e4033fde5`. The approved canonical acceptance
contract keeps the proposed route at fourteen files but reduces the estimate
from about 1,600 to about 1,350 changed lines after the minimum-stack
correction. The added surface over cycle 2 remains the shared kernel and adopted
mirror, profile-selection instruction, rationale, and their admission-boundary
coverage; no new runtime authority is added. Keep one integrated Draft PR with
three reviewable commits: canonical admission guard, repository-local Linear
adapter, then retained-document alignment. Splitting the PR would expose a new
internal brief contract without its first admitted consumer or duplicate the
same parity and ablation edits; reaching a stop number below still returns the
item to shape before implementation continues.

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
   loader's explicit admission-validation mode before provider access or any
   dispatch-envelope emission. That
   mode accepts a new Pilot or Production admission only when the Development
   Brief has exactly one non-placeholder problem, accepted outcome, non-goal
   list, `## Acceptance criteria`, and route-back section, and when the
   Planning Receipt tuple is complete or absent. Every acceptance bullet starts
   with one unique, ascending `**AC-N**` identifier and a non-placeholder
   observable condition. A new admission containing both
   `## Acceptance criteria` and `## Acceptance evidence` is invalid.
4. **OBSERVED/DESIGNED:** Normal profile loading remains the existing path and
   does not inspect, revalidate, normalize, or rewrite acceptance headings.
   Active `manual-cycle-release-admission-path` is work-profile v3 at validation
   and contains both headings; it must continue unchanged through normal
   loading. Canonical validation is therefore selected only by the admission
   guard for DEV-12 and future admissions, never inferred from status,
   timestamp, heading shape, or legacy content.
5. **DESIGNED:** For the complete Linear receipt, the command reads the key
   only from the current Conductor process environment, requires the current
   `CONDUCTOR_WORKSPACE_ID`, and checks that the authenticated Linear
   organization is `duckbase-co`. It follows the exact issue source, paginates
   the Project-plus-Cycle set whose state type is `unstarted` or `started`, and
   also re-reads still-active snapshot sources that moved outside that scope.
   Missing variables, an authentication or organization mismatch, malformed
   data, incomplete pagination, network failure, or timeout emits no envelope
   and exits before state access or mutation.
6. **DESIGNED:** The command derives the committed five-field snapshot from
   the immutable state revision for every ready execution item sharing the
   engaged `sprint`. It maps source, planning window, planning outcome,
   accepted outcome, and complete non-goals without writing an intermediate
   file; it rejects a dirty, changing, missing, duplicate, or mixed-scope
   snapshot.
7. **OBSERVED:** The unchanged `engage-reconcile.py` comparator at `7256e02`
   returned exit `0` with four empty delta arrays after DEV-11 moved from Todo
   to In Progress, and returned exit `1` with `moved` after intentional Project
   digest drift. The designed command accepts only exit `0` plus one parsed
   `status: clean` object; `added`, `removed`, `changed`, `moved`, invalid
   output, process death, or no answer emits no envelope.
8. **DESIGNED:** At process entry, the command records a diagnostic monotonic
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
9. **DESIGNED:** Every refusal is safe to retry after the credential, network,
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
- The profile loader's default invocation retains its current route, stage, and
  hash-binding behavior and does not validate acceptance headings. Its explicit
  admission-validation mode requires one canonical `## Acceptance criteria`
  section with stable `AC-N` identifiers and a complete-or-absent Planning
  Receipt; duplicate, missing, non-ascending, placeholder, evidence-only, or
  dual-section new admission fails closed before provider access.
- The admission-validation mode returns the validated Development Brief hash
  and no heading classification or rewritten content. Already-admitted items
  continue under default loading exactly as committed, even when their
  historical headings would fail new admission.
- The five-field snapshot and comparator exit/output schemas remain unchanged.
  Todo-to-In-Progress is execution progress, while Project, Cycle, accepted
  goal, non-goal, or membership differences remain planning drift.
- No stored schema, planning authority, execution authority, or delivery
  authority changes. The dispatch envelope is ephemeral input to the First
  Officer, not a second execution record.

### Persistence, recovery, and data safety

- For DEV-12 and future admissions, persistent inputs are only the committed
  Linear Planning Receipt, canonical Development Brief, admitted Spacedock
  snapshot, and selected profile receipt. Canonical `AC-N` identifiers remain
  stable within the hash-bound brief and are the references consumed by
  Spacedock `--ac-scan`.
- Existing admitted work remains persisted exactly as committed. Neither
  default loading nor continuation creates a canonical copy, chooses between
  historical headings, or writes a compatibility receipt.
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
| `AC-5` End-to-end under 60 seconds | On the exact candidate revision, an external harness captures monotonic `t0` at successful readback of the separately authorized DEV-12 Todo-plus-Cycle update, immediately invokes the command, captures `t1` after parsing one bound envelope, and asserts `t1 - t0 <= 60000` with zero later Captain prompts. It also records `command_elapsed_ms` only as a nested diagnostic and proves the full interval contains the command's fresh Linear request. | Manual JSON/MCP input, an interactive prompt, missing binding, invalid envelope, omitted provider-read interval, use of `command_elapsed_ms` as the acceptance result, or `t1 - t0` above 60 seconds. |
| `AC-2` Workspace-bound authentication | Run with the current workspace variables; then independently test missing key, missing Conductor identity, synthetic 401, and wrong Linear organization. Assert all refusals have empty stdout and unchanged state. | Any fallback credential, accepted mismatch, secret-bearing diagnostic, task creation, state write, or envelope. |
| `AC-3` Canonical admission brief | In admission-validation mode, mutate each required section to missing, duplicate, empty, or placeholder; mutate criteria to missing, duplicate, non-ascending, duplicate-ID, or placeholder `AC-N`; and supply evidence-only or both sections. Require every mutant to fail before provider access. | Any malformed new Pilot or Production admission loads, both acceptance sections coexist in a new admission, or criteria load without stable `AC-N` identifiers. |
| Existing continuation boundary | Run the default loader on the exact active `manual-cycle-release-admission-path` at validation and require the same selected route despite both historical headings; hash the file before/after. Run admission-validation mode on the same fixture and require refusal. | Normal continuation rejects or rewrites existing work, or new-admission validation accepts its dual-section shape. |
| `AC-3` Complete-or-absent Planning Receipt | In admission-validation mode, exercise all eight presence combinations for source, window, and outcome: zero or three may load, while the other six fail before provider access. | A partial tuple loads or an absent standalone tuple invokes Linear. |
| `AC-1` Live read and exact snapshot binding | Run the workspace read and assert DEV-12, Project `535b8bd1`, Cycle `b788c52d`, and the complete admitted set normalize to the five fields; then change work-item bytes, state revision, source, window, outcome, accepted goal, non-goal, or membership between reads. | The exact live set does not resolve, a stale or mixed snapshot produces an envelope, or no changed hash/delta identifies the premise. |
| `AC-4` Planning semantics | Live Todo-to-In-Progress stays clean; fixtures classify Cycle or Project as `moved`, goal or non-goal as `changed`, and membership as `added` or `removed`. | Status-only progress stops, or any planning change is clean/unclassified. |
| Acceptance coverage | Run Spacedock `--ac-scan` against the exact DEV-12 revision after the latest Stage Report and require `AC-1` through `AC-6` covered with no unknown identifier. | Any criterion is uncovered, renumbered, duplicated, or cited only outside the latest Stage Report evidence. |
| Read-only and cleanup | A fake GraphQL server rejects mutation text and captures requested fields; compare Linear fixtures, state HEAD/status, temp paths, and credential value before and after every outcome. | Provider/state bytes change, an intermediate survives, unnecessary fields are fetched, or the real credential changes. |
| Dispatch stop | Feed auth, brief, receipt, truncation, comparator, state-race, and timeout failures to the integration fixture and assert empty stdout; feed the clean case and assert one envelope. | Any failure produces dispatchable stdout or success produces more than one object. |
| `AC-6` Without-it proof | Mutate away each retained reader, admission-guard invocation, canonical/dual-section/`AC-N` check, default-loader no-revalidation boundary, Planning Receipt check, state/hash binding, comparator exit/payload check, and empty-stdout dispatch stop. | The contract and ablation suites do not reject every mutant. |

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
      evidence: The prose contract exists and the current loader parses only profile and scheduling fields; an active v3 validation item with both historical headings proves normal loading cannot adopt the new admission rule.
      disproof_hook: Exercise canonical and dual-section fixtures in admission mode, then load the exact active dual-section item in default mode without changing its bytes.
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
| `kc-dev-flow/scripts/profile-contract-loader.py` | 419 | 505 | Add explicit canonical admission validation while leaving default profile loading behavior unchanged. |
| `kc-dev-flow/scripts/profile-contract-loader.test.py` | 1,455 | 1,650 | Falsify every admission brief section, `AC-N` shape, dual-section case, receipt combination, guard invocation, and default-loader no-revalidation boundary. |
| `docs/dev/_mods/profile-contract-loader.py` | 419 | 505 | Preserve byte-identical adopted loader behavior used by this workflow. |
| `kc-dev-flow/references/kernel.md` | 249 | 265 | Make canonical `## Acceptance criteria` with stable `AC-N` identifiers an admission-only contract and preserve admitted work as committed. |
| `docs/dev/_mods/kernel.md` | 249 | 265 | Preserve byte-identical adopted core semantics. |
| `kc-dev-flow/skills/choose-work-profile/SKILL.md` | 122 | 133 | Capture canonical criteria at new admission and refuse a dual-section admission. |
| `kc-dev-flow/skills/continue-dev-flow/SKILL.md` | 228 | 255 | Preserve normal continuation, invoke canonical validation only through the bound admission guard, run `--ac-scan` for canonical work, and accept only one valid envelope. |
| `docs/dev/README.md` | 403 | 445 | Bind `duckbase-co`, the Conductor credential, local guard command, admission-only canonical brief template, and local `--ac-scan` proof without changing historical tasks. |
| `kc-dev-flow/README.md` | 192 | 218 | Document canonical admission criteria, unchanged continuation, strengthened admission guard, and optional adopter seam. |
| `kc-dev-flow/RATIONALE.md` | 176 | 188 | Keep the planning/execution rationale aligned with admission-time validation and no migration. |
| `scripts/kc-dev-flow-contract-test.py` | 1,182 | 1,500 | Exercise admission/default-mode separation and `--ac-scan` coverage plus fake Linear/state integration, full-boundary timing, envelope/auth/data safety, and package/adopter identity. |
| `scripts/kc-dev-flow-minimal-stack-ablation.test.py` | 487 | 575 | Reject removal of reader, admission invocation, canonical/dual-section/`AC-N` checks, default no-revalidation, receipt guard, snapshot binding, comparator validation, or dispatch stop. |
| `ARCHITECTURE.md` | 252 | 270 | Repair profile-loading and acceptance-authority claims to distinguish canonical admission validation from unchanged normal loading and the provider guard. |

The existing `kc-dev-flow/scripts/engage-reconcile.py` and adopted
`scripts/kc-dev-flow/engage-reconcile.py` remain byte-identical and unchanged;
their 168-line behavior is exercised, not redesigned.

### Retained mechanism map

| Retained mechanism | Goal or safety boundary | Without-it failure |
|---|---|---|
| Workspace Linear reader inside `linear-admission.py` | Replace manual MCP and normalization while failing closed on credential, organization, pagination, and timeout. | No repeatable live read, or a wrong/truncated workspace can be dispatched. |
| Admission-only Development Brief and receipt guard | When explicitly invoked by the Linear admission guard, require canonical `AC-N` criteria, reject evidence-only or dual-section new admission, and validate the Planning Receipt before provider or state read; default profile loading remains unchanged. | New admission bypasses canonical criteria, prior admitted work is revalidated or rewritten, or a provider path has incomplete identity. |
| State-revision and canonical snapshot binding | Make the compared five fields and execution group exact and replayable. | A clean result can describe different work-item or state bytes than the dispatch. |
| Existing comparator exit and payload behavior | Preserve clean progress and classify planning drift without writes. | Todo progress falsely blocks, or Project/Cycle/goal/non-goal/membership drift proceeds. |
| Success-only envelope and First Officer stop | Give dispatch one machine-checkable, current input without automatic launch. | A failure can be mistaken for approval, or an old receipt can authorize new work. |

### Stop numbers and scope guard

Measure all thresholds as additions plus deletions from
`7256e02dbbc5340e4328bfeeb016448e4033fde5` using diff numstat. Stop and return
to shape when the diff reaches **15 changed files**, **1,501 changed lines**, or
**121 changed lines in `kc-dev-flow/scripts/profile-contract-loader.py`**, the
admission/default-mode separation most likely to grow after this correction.
These are halt conditions: do not trade admission-only enforcement, unchanged
continuation, `AC-N` coverage, parity, data safety, or dispatch-stop coverage
to remain below them.

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
  approved_change: State that explicit admission mode validates one canonical AC-N Development Brief and the complete-or-absent Planning Receipt before provider access, while default profile loading leaves already-admitted headings unchanged and the repository-local provider guard owns authentication, current read, snapshot reconcile, and dispatch-envelope emission.
  landed_change: "ARCHITECTURE.md at candidate 90de4e35748893529161a84bb863210259d1de1d now distinguishes explicit admission validation, unchanged default loading, and provider-guard ownership."
  planned_check: Run canonical admission, evidence-only and dual-section refusal, exact active dual-section default-load, AC-scan, and Linear admission fixtures, then compare the architecture claim with observed success and refusal behavior.
  validation_evidence: pending
```

No retained document is added or removed. Update `ARCHITECTURE.md`, the shared
kernel and adopted mirror, both README files, `RATIONALE.md`, and the existing
selection/continuation instructions in place; keep task status, revision,
timing, live credential facts, and admission-boundary evidence in this work item
rather than the retained documents.

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

## Stage Report: ideation (cycle 3)

- DONE: Define one end-to-end Pilot journey from the workspace-bound Linear read through the existing five-field snapshot and clean reconcile to a valid dispatch envelope within 60 seconds; the one-time manual bootstrap must not exist in the steady-state route.
  `AC-1` binds the live DEV-12/Project/Cycle read to the five fields, `AC-4` keeps execution progress clean and planning drift classified, and `AC-5` measures the full external readback-to-envelope interval including the provider read.
- DONE: Define fail-closed authentication, Development Brief, complete-or-absent Planning Receipt, and planning-drift behavior with falsifiable acceptance checks, observable semantics, persistence, recovery, and data-safety boundaries.
  `AC-2` covers workspace authentication refusal; `AC-3` covers canonical `AC-N`, dual-section rejection, pre-cutoff legacy compatibility, and receipt completeness; `AC-4` covers clean progress and each drift class.
- DONE: Name the smallest file-level implementation surface and diff-based stop numbers, mapping every retained reader, loader guard, snapshot binding, comparator behavior, and dispatch stop to a goal, safety boundary, or without-it failure while preserving all declared non-goals.
  `AC-6` covers every retained-mechanism mutant; the honest surface is fourteen files and implementation halts at 15 files, 1,751 changed lines, or 161 loader lines without migrating prior work or adding another authority. A live Spacedock `--ac-scan` returned `unevidenced: false` for `AC-1`, `AC-2`, `AC-3`, `AC-4`, `AC-5`, and `AC-6`.

### Summary

DEV-12 now uses one canonical `## Acceptance criteria` section with stable `AC-1` through `AC-6`, and the latest checklist evidence cites all six for Spacedock coverage scanning. Legacy evidence remains readable only for post-backlog items started before DEV-12 through one explicit local cutoff; both sections are always invalid, so compatibility neither migrates work nor creates a second authority.

## Stage Report: ideation (cycle 4)

- DONE: Define one end-to-end Pilot journey from the workspace-bound Linear read through the existing five-field snapshot and clean reconcile to a valid dispatch envelope within 60 seconds; the one-time manual bootstrap must not exist in the steady-state route.
  `AC-1` keeps the live DEV-12/Project/Cycle read and exact five-field binding, `AC-4` retains clean progress plus classified drift, and `AC-5` preserves the full external readback-to-envelope measurement including the provider read.
- DONE: Define fail-closed authentication, Development Brief, complete-or-absent Planning Receipt, and planning-drift behavior with falsifiable acceptance checks, observable semantics, persistence, recovery, and data-safety boundaries.
  `AC-2` covers workspace authentication refusal; `AC-3` invokes canonical validation only from the new-admission guard before provider access or dispatch, while default loading sent active dual-heading item hash `1b8ccf65` through `verify-deliver -> done` with identical before/after bytes; `AC-4` covers every drift class.
- DONE: Name the smallest file-level implementation surface and diff-based stop numbers, mapping every retained reader, loader guard, snapshot binding, comparator behavior, and dispatch stop to a goal, safety boundary, or without-it failure while preserving all declared non-goals.
  `AC-6` covers admission invocation, canonical and dual-section refusal, default no-revalidation, reader, snapshot, comparator, and dispatch mutants; the surface remains fourteen files and halts at 15 files, 1,501 changed lines, or 121 loader lines.

### Summary

The minimum stack no longer classifies or migrates legacy headings: normal profile loading remains unchanged for every already-admitted item, including the active v3 validation item with both historical sections. DEV-12 and future admissions alone take the explicit canonical `AC-N` validation path through the admission guard, and a dual-section new admission still fails before provider access or dispatch.

## RoboRev implementation observation claim

```yaml
review_convergence:
  capability: review_convergence
  mode: observe
  provider: roborev
  identity: sha256:5dc242d9095dd2448bd786caac2b009e21d359920c0757f44a9905f11494004a
  claimant: agent:codex:01a05252-d05c-7ef2-ba41-b33fb04d87ed
  observed_state_revision: a022cac7b934734b7a96687d89d86208ddb39ef3
  base_sha: 7256e02dbbc5340e4328bfeeb016448e4033fde5
  tip_sha: 8675e8e46d865aba1428484002cee5cdbfd48b94
  config_sha256: ae3555f0b3fcf5b626c39c614e3b2058bd2e31fb5840ce864edfaeded34f07f1
  profile: pilot-product-slice
  agent: codex
  model: gpt-5.6-terra
  reasoning: medium
  minimum_severity: medium
  panel: none
  job_id: 290
  job_uuid: 1164593f-6e73-4b9a-a1bf-5dc08887da7f
  member_states: [codex:findings]
  outcome: FAIL
  reason: findings
  state: observed
```

## RoboRev implementation changed-tip confirmation claim

```yaml
review_convergence:
  capability: review_convergence
  mode: observe
  provider: roborev
  identity: sha256:41e6617b79eb0a764f04695d9fd274c0f8d0cc994b5355bcaa98f1ac08395526
  claimant: agent:codex:01a05252-d05c-7ef2-ba41-b33fb04d87ed
  observed_state_revision: d709d2f6211e9e2599cd8877997070d94747a550
  base_sha: 8675e8e46d865aba1428484002cee5cdbfd48b94
  tip_sha: 90de4e35748893529161a84bb863210259d1de1d
  config_sha256: ae3555f0b3fcf5b626c39c614e3b2058bd2e31fb5840ce864edfaeded34f07f1
  profile: pilot-product-slice
  agent: codex
  model: gpt-5.6-terra
  reasoning: medium
  minimum_severity: medium
  panel: none
  job_id: 291
  job_uuid: 04bc11c4-307b-4f61-a960-ec22ebe52b16
  member_states: [codex:passed]
  outcome: PASS
  reason: passed
  request_count: 1
  confirmation_count: 1
  cost_usd_approximate: 0.0684288
  cost_jobs_with_cost: 2
  cost_jobs_total: 2
  cost_complete: true
  state: observed
```

## Stage Report: implementation

- DONE: Implement the runnable read-only Linear admission command and explicit admission-only canonical Development Brief guard on the approved fourteen-file surface; stop before exceeding 15 files, 1,501 changed lines, or 121 loader lines, and preserve every declared non-goal.
  Evidence: `git diff --numstat 7256e02dbbc5340e4328bfeeb016448e4033fde5` at `90de4e35748893529161a84bb863210259d1de1d` reports 14 files and 1,284 additions-plus-deletions; the package loader reports 98 changed lines.
  Evidence: the candidate has the accepted three commits; `git diff --check` passes and package/adopter loader plus kernel bytes compare equal.
  Scope: no mirror, synchronization, polling, webhook, automatic launch, Linear Agent delegation, multi-issue package, Initiative, Milestone, POC redesign, migration, framework, or production operation was added.
  Failure boundary: 15 files, 1,501 lines, 121 loader lines, a byte mismatch, or any declared non-goal would have stopped implementation; none occurred.

- DONE: Prove AC-1 through AC-6 with focused deterministic checks: workspace authentication refusal, canonical and dual-section admission behavior, unchanged default loading for already-admitted work, five-field binding, clean progress and classified drift, the full external 60-second boundary, and without-it mutants for every retained mechanism.
  `AC-1` and `AC-2`: `python3 scripts/kc-dev-flow-contract-test.py` passes live-shape fixtures for the five fields, missing key/workspace, synthetic 401, wrong organization, truncation, timeout, read-only queries, and state/work-item races.
  `AC-3`: `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` passes required-section, duplicate, empty, placeholder, ordered unique `AC-N`, evidence-only, dual-section, all eight receipt masks, and unchanged historical default-load cases.
  `AC-4`: the contract test keeps started progress clean and classifies Project/Cycle as `moved`, goal/non-goal as `changed`, and membership as `added` or `removed`.
  `AC-5`: the exact candidate and state `7dc36f1d709c25ea228079f41640afedc965d7ad` read back DEV-12 `unstarted`, Cycle `b788c52d`, and Project `535b8bd1`, then emitted a clean envelope in 3,507 ms externally and 3,438 ms internally with zero Captain interventions; envelope SHA-256 is `35bdaa502e455825c13afc1ac9488b009d99d88e70b14ce920e518711b74e99b`.
  `AC-6`: focused without-it runs rejected 10 of 10 retained contract/runtime mutants; after the ordering repair, all six reader/auth/loader/state/comparator/envelope runtime mutants reran and were rejected at the final tip.
  Diagnostic: the broad historical mutant runner had already rejected 18 mechanisms before an unrelated baseline diagnostic and then disk pressure, so it was not rerun or treated as the acceptance authority; focused checks had no survivor and 14 GB was free afterward.
  Failure boundary: any refusal stdout, provider/state mutation, unclassified drift, elapsed time above 60 seconds, unchanged mutant, or non-clean reconcile would fail this item; none remained.

- DONE: Keep package/adopter bytes and retained claims aligned, record the project-context landed change, compare the exact implementation diff against the accepted journey, and take at most the declared single RoboRev observation plus one changed-tip confirmation without treating it as validation authority.
  Parity: `cmp` passes for package/adopter loaders and kernels; retained documentation names only admission-mode canonical validation and unchanged default continuation.
  Project context: `ARCHITECTURE.md` at the final candidate contains the approved loader/provider-guard ownership change; fresh validation evidence remains `pending` for the next stage.
  RoboRev observation: job 290 reviewed exact base-to-tip `7256e02..8675e8e` with Codex, `gpt-5.6-terra`, medium reasoning/severity, and no panel; it returned `FAIL(reason: findings)` for non-canonical multi-item ordering.
  Repair: both normalized lists now sort by source, and the integration fixture presents two clean items in reverse provider order while requiring equal snapshot/live hashes.
  RoboRev confirmation: the sole allowed changed-tip job 291 reviewed `8675e8e..90de4e3` with the same configuration and returned `PASS(reason: passed)` with no issues; request count is one and confirmation count is one.
  Cost coverage: `roborev cost --json` reports approximate total USD 0.0684288, `jobs_with_cost: 2`, `jobs_total: 2`, and `complete: true`.
  AC coverage: installed Spacedock 0.27.0 `status --read repeatable-linear-admission-under-one-minute --stage implementation --ac-scan --json` returns exactly `AC-1` through `AC-6`, each with `unevidenced: false`, and no unknown identifier.
  Failure boundary: parity drift, a missing landed claim, stale RoboRev correlation, a second request/confirmation, or treating reviewer output as validation would fail this item; none occurred.

### Summary

Candidate `90de4e35748893529161a84bb863210259d1de1d` implements the accepted read-only admission journey in three commits below every stop number. Deterministic contracts, exact live measurement, without-it evidence, and the bounded reviewer observation support implementation handoff; fresh validation remains the next-stage authority.
