---
title: Decouple the measurement ledger from delivery terminalization
status: validation
source: captain direction 2026-07-31 after EM merge-readiness closeout
product: repo-platform
sprint:
started: 2026-07-31T10:22:20Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-decouple-ledger-from-terminalization
issue:
pr:
ledger_pr:
pr_artifact_v1:
ledger_artifact_v1:
mod-block:
design: required
lane: main
id: 7rgdvsjypgmzk8wh03h3vst9
---

The current PR lifecycle makes a completed product change wait for a second ledger-only PR and an
escaped-defect placeholder before the task can become done. Recover the existing measurement seams
into a non-blocking feedback loop: task state remains the delivery authority, completion never waits
for ledger maintenance, and process observations may later propose one narrow improvement task.
Preserve existing ledger history and read compatibility. Do not add a daemon, automatic process
mutation, or universally mandatory token/coverage metrics.

## Captain-authored scope

The dispatch already answers the ideation scope questions: the bad outcome is a delivered product
change remaining live and non-terminal for bookkeeping; the invariant to keep is authoritative task
state backed by an authenticated product merge; the happy exclusions are a second completion PR, a
seven-day done gate, a daemon, automatic task creation, generic analytics, and universal token or
diff-coverage requirements. The captain also chose the framing: the ledger is an observational
feedback instrument, not workflow state or merge/done authority. That complete, narrow direction is
the stated reason for not asking a second questionnaire and risking a scope rewrite.

Sprint remains blank. This is a repo-platform lifecycle correction, and the design found no reason
to claim a product-local ROADMAP allocation before the captain schedules it.

## Problem

The dev-flow contract currently treats a merged product PR as necessary but insufficient for
delivery completion. Accepted validation first has to write a sentinel-bearing ledger row into the
product branch. After product merge, the lifecycle opens a second, ledger-only PR, waits for it to
merge, verifies the seven-day observation placeholder, and only then writes `status: done` and
archives the entity.

That makes an observational record a second state machine. A GitHub outage, approval pause, stale
pending date, malformed historical row, or ledger-only merge conflict can hold a delivered task in
validation indefinitely. It also makes absence of optional token or diff-coverage evidence look like
a delivery defect even though neither metric establishes that the product change shipped correctly.

The latest completed example makes the coupling concrete. Product PR `#118` merged at
`2026-07-31T09:50:02Z`; ledger-only PR `#119` merged at `10:05:09Z`; the state entity was archived at
`10:12:02Z`. The product was delivered for about twenty-two minutes before workflow state was allowed
to say so. The new contract must make that exact symptom impossible without weakening product-merge,
state-durability, or archive recovery evidence.

## Appetite and stop condition

- **Ideation-declared estimate:** at most 90 minutes for one implementation worker to revise the two
  lifecycle documents and add/run the focused contract fixture.
- **Declared tolerance:** 30 additional minutes. At 120 minutes, stop with a clean, re-enterable
  branch and return to the captain for a re-cut; do not silently extend the budget or remove proof.
- **Smallest cut:** change the authority edge, preserve the current archive and CSV shapes, and reuse
  archived task evidence. No new persistence, scheduler, service, CI job, or task type.

## Reverse-recovery audit

Audit base: freshly fetched `origin/main` at
`1d6d0d02d4b0d6c84eac0813e6962c6774e652b7` on 2026-07-31.

| Layer / authority seam | Classification | Evidence and disproof hook |
|---|---|---|
| Product delivery identity | `WORKING` | `docs/dev/_mods/pr-merge.md:386-395` authenticates the numbered product PR and observes `MERGED`; live `gh pr view 118` returned `MERGED`, exact head `be450e4...`, base `main`, and `mergedAt=2026-07-31T09:50:02Z`. Disproved by the same live query no longer matching the archived artifact. |
| Delivery-to-task authority edge | `EXISTS_BROKEN` | `docs/dev/README.md:1106-1114` says a product merge is insufficient and leaves the entity live on a missing, sentinel, or incomplete ledger row. `docs/dev/_mods/pr-merge.md:393-415,474-580` implements the second ledger-PR state machine. Disproved by a disposable merged-product fixture reaching `done` and archive with no ledger row or ledger ref. |
| Task terminal mutation and durable archive | `WORKING` | `docs/dev/_mods/pr-merge.md:581-614` already has the compound clear-block/terminal state commit, and `:1914-1979` has durable live-root and archive recovery. The fault is its ledger precondition, not the state/archive mechanism. Disproved by a real Spacedock fixture failing to durably archive after all ledger predicates are removed. |
| Existing product-only precedent | `WORKING_UNIT_UNPROVEN` | The generic modifier already advances on product merge at `docs/ship-flow/_mods/pr-merge.md:51-59`; it proves the contract shape exists, but its simpler prose is not evidence for dev-flow's stronger artifact/recovery path. Disproved or promoted by exercising the dev-flow fixture against the recovered product-only decision. |
| Measurement source after archive | `WORKING` | `_archive/agy-first-whole-diff-review-seat.md:1-20,1347-1362,1574,1731` preserves timestamps, product identity, fourteen dispatch lines, rework records, and final coverage. A read-only spike derived `14,2,18.81,n/a,88.17,pending:2026-08-07`, exactly matching `docs/dev/ledger.csv:16`. Disproved by another archived v1 entity whose recorded row cannot be derived or honestly marked unknown from its archive plus product merge metadata. |
| Historical ledger persistence/readback | `WORKING_UNIT_UNPROVEN` | `docs/dev/ledger.csv:1-16` retains the canonical eight-column history; `docs/dev/README.md:1406-1416,1428-1456` defines terminal and read-only legacy modes; `:1353-1359` preserves bare pending and blank historical cells as unknown. The extracted existing ledger fixture ran fresh and exited 0 across exact/missing/duplicate/unknown/legacy/phase cases; archive-to-batch wiring remains unproven. Disproved by the focused compatibility suite rejecting a committed row or failing post-archive import. |
| Process-improvement authority | `EXISTS_BROKEN` | The ledger is described as an experiment and bookkeeping at `docs/dev/README.md:1678-1707`, but completion still consumes it as workflow authority at `:1108-1114`. Captain scope authority already exists at `:1179-1201`. Disproved by any post-change measurement path that creates or advances an entity without a new captain decision. |

This is recovery, not greenfield work. Product authentication, compound state mutation, archive
recovery, archived evidence, CSV preservation, and captain scope authority all exist. The one broken
seam is the ledger predicate between authenticated product merge and task terminalization.

## Approaches considered

### A. Archive first, observe later — recommended

On authenticated product merge, clear the product `mod-block`, set `completed` from product
`mergedAt`, set the passed verdict, durably commit terminal state, and archive through the existing
recovery transaction. Ledger fields and rows are not read by that decision. A later human-triggered
measurement pass derives or batches rows from archived entity evidence and product metadata.

This is the cheapest path that satisfies the acceptance criteria: it removes one authority edge and
reuses every durable surface already present. It also gives failures the right blast radius: archive
failure can still block archive truth, while ledger failure can only leave measurement debt.

### B. Keep the pre-merge row, but terminalize before the ledger-only PR

This requires fewer textual deletions, but it preserves a mandatory ledger mutation on every product
branch and continues to treat missing token/coverage data as a pre-PR delivery defect. It also keeps
one per-task bookkeeping PR alive after completion. That is not the captain's requested archive-first
feedback loop, so it is not selected.

### C. Emit events to a daemon or analytics store

This could automate observation, but introduces a new runtime, scheduler, persistence contract,
failure mode, and automatic mutation temptation. It is expressly out of scope and unnecessary while
the archive already retains the evidence.

**Taking the cheap path:** Approach A. The more thorough service/analytics approach is not needed to
prove the ledger can inform later proposals without controlling delivery.

## Proposed approach

### Authority contract

1. **Product delivery authority:** an authenticated product PR in `MERGED`, with accepted validation
   and the exact stored artifact/head evidence, authorizes the terminal state transaction.
2. **Task-state authority:** the entity's durable `status`, `completed`, `verdict`, and archive root
   say whether delivery is terminal. Archive recovery remains part of lifecycle correctness.
3. **Measurement authority:** `docs/dev/ledger.csv` says only what has been observed about completed
   work. Missing, stale, unknown, or pending measurement can produce a warning or later batch item;
   it cannot block product PR creation, terminal state, cleanup, or archive.
4. **Scope authority:** a ledger review may output at most one narrow repo-platform improvement
   proposal. It does not create an entity. Turning the proposal into backlog/sprint work requires a
   new explicit captain approval under the existing Gate Authority rules.

### Terminal data flow

`validation PASSED -> product PR -> authenticated MERGED -> durable done state -> durable archive`

There is no ledger node on that path. The terminal transaction keeps the current product artifact,
exact `mergedAt`, product ref, clear-block setter, terminal setter, one state commit, and restart-safe
archive transaction. It drops the pre-merge `ledger_verify` gate, ledger-finalization branch/PR, and
ledger artifact requirement.

### Observational data flow

`archived entity + product mergedAt -> optional derive/preview -> batched ledger PR -> later human review`

The archive is the source for dispatch count, rework rounds, observed token figures, final validation
coverage when present, `started`, `completed`, slug, and task id. Product metadata supplies the
authenticated merge timestamp already copied into `completed`. Unknown token or diff-coverage data
is recorded as unknown, not reconstructed and not treated as a task defect. The seven-day escape
window can remain dated/pending in the ledger and be swept later; it never delays `done`.

The pass is explicitly invoked by a human, may combine multiple archived tasks in one protected-main
PR, and changes only observational docs. It is not a daemon, CI requirement, completion PR, or
per-task deadline. A failed import reports measurement debt and leaves the archived entity untouched.

### Backward-compatible migration

- Keep the eight-column `ledger.csv` schema and every existing row byte-for-byte. Blank, bare pending,
  dated pending, `n/a`, floors, and complete historical values keep their current read meanings.
- Keep `ledger_pr` and `ledger_artifact_v1` as optional legacy audit fields. New entities do not need
  them. Archived entities that already carry `ledger-merge:` remain readable without normalization.
- A live entity with draft, pending, open, merged, malformed, or empty ledger metadata terminalizes
  from its authenticated product merge. Preserve any existing ledger metadata in its archive for
  audit; never clear or rewrite it merely to fit the new form.
- Existing ledger PRs may still be reconciled as observational work, but their state cannot reopen,
  delay, or re-terminalize the product entity. No automatic close/merge/supersede action is added.
- Reframe `ledger_verify` and line-preserving `ledger_upsert` as batch/import checks. Their failures
  reject the measurement diff only. They never authorize task-state mutation.
- Archive recovery accepts both the new product-only terminal route and the historical product-plus-
  ledger route. Both continue to authenticate the product ref; the latter keeps ledger refs as audit
  evidence, not a prerequisite.

### Error handling

- Product identity mismatch, non-merged product state, failed validation, dirty/unattributable state,
  or archive comparator failure still blocks terminalization or archive exactly where it does now.
- Missing/unreadable ledger, incomplete metrics, overdue observation cells, ledger conflicts, or an
  unavailable measurement PR host produce an observation warning only.
- If archive evidence cannot supply a metric, write the existing unknown form where allowed or omit
  the observational update. Never invent `0`, a token total, diff coverage, or a clean escape count.
- A batch conflict is resolved as an append-preserving row union and retried without touching state.

## Design determination

`required` — this task changes the lifecycle contract, state-field meaning, recovery acceptance
forms, and the interface between archived task evidence and the CSV. The concrete before/after is:

- **Before:** `product MERGED -> ledger row/PR MERGED -> ledger verify -> done -> archive`.
- **After:** `product MERGED -> done -> archive`; separately,
  `archive -> optional measurement batch -> human proposal -> captain decision`.

No new schema field, UI, daemon API, CI job, or storage service is introduced.

## Acceptance criteria

**AC-1 — Product delivery terminalizes without ledger upkeep.**

Given an accepted entity with an authenticated merged product PR, the lifecycle reaches durable
`done` and archive when `ledger.csv` is absent/unwritable and both ledger fields are empty or malformed.
The current baseline is the opposite: `docs/dev/README.md:1108-1114` leaves it live.

Verified by: `bash docs/dev/artifacts/decoupled-ledger-contract-test.sh terminal-without-ledger`
runs the marked terminal/archive transaction in a disposable split-root workflow, makes every ledger
access fail, and asserts exactly one archived entity with the product `mergedAt`.

Falsified by: any product-merged fixture remaining live, attempting a ledger PR, or requiring a
seven-day value.

**AC-2 — Legacy ledger and in-flight entities stay readable.**

All committed historical CSV rows and archived product-plus-ledger refs retain their meanings, while
active entities in each existing ledger phase become terminalizable from product evidence.

Verified by: `bash docs/dev/artifacts/decoupled-ledger-contract-test.sh compatibility` copies the
current `ledger.csv` and representative archived/live entity forms, runs the legacy/observer readers,
asserts byte-identical pre-existing rows, and covers empty, draft, pending, numbered, merged, and
malformed ledger refs without weakening product authentication.

Falsified by: a current row becoming unreadable, a historical ref being rewritten, or a ledger phase
changing the task-state verdict.

**AC-3 — Archive-first observation remains useful and non-authoritative.**

A post-archive pass can derive an honest row, batch it without changing the archived entity, and
produce only a proposal for later captain consideration.

Verified by: `bash docs/dev/artifacts/decoupled-ledger-contract-test.sh archive-derive` reproduces the
current `agy-first-whole-diff-review-seat` row from its archive as
`14,2,18.81,n/a,88.17,pending:2026-08-07`, upserts it into a copy, and asserts the archive tree hash is
unchanged; a negative case with unknown token/coverage evidence reports unknown rather than failing
task state.

Falsified by: measurement code calling a state setter/entity creator, inventing a metric, or treating
an importer failure as non-terminal delivery.

**AC-4 — The change stays inside the declared repo-platform boundary.**

The landed diff changes only the dev-flow lifecycle docs and focused local fixture; it adds no daemon,
CI/workflow trigger, generic analytics store, automatic task creation, or universal token/diff-coverage
gate.

Verified by: `git diff --name-only origin/main...HEAD` plus
`bash docs/dev/artifacts/decoupled-ledger-contract-test.sh scope` checks the allowed paths, scans for
lifecycle mutation and workflow/daemon additions, and exercises no-network/no-task-creation stubs.

Falsified by: any new runtime or automatic process mutation, or any wording that makes optional
metrics a delivery gate.

## Test plan

1. Add a focused shell contract fixture under `docs/dev/artifacts/` and keep it local/manual: no new
   GitHub Actions job. Extract or invoke marked lifecycle snippets so the test exercises the exact
   documented transaction rather than a second handwritten algorithm.
2. RED on current `origin/main`: product-merged + ledger unavailable remains live or the scan finds
   the ledger precondition. GREEN after the authority edge is removed: terminal commit and archive
   succeed with all ledger access forced to fail.
3. Run migration cases for empty/draft/pending/numbered/merged/malformed ledger refs and both flat and
   folder archive roots. Product authentication remains mandatory in every case.
4. Copy the live CSV and archived exemplar into the fixture. Assert byte-preserving historical reads,
   exact post-archive derivation, honest unknowns, and no archived-state mutation during upsert.
5. Run `spacedock status --workflow-dir docs/dev --read 7rgdvsjypgmzk8wh03h3vst9 --ac-scan`,
   `git diff --check`, the focused fixture, and the existing ledger verifier fixture.

E2E-first is satisfied at the relevant surface by the real Spacedock CLI over a disposable split-root
workflow. Browser/full-stack E2E is skipped because this is a docs/execution-contract change with no
application or user-visible runtime surface.

## Risk spike

The riskiest premise was whether measurement remains derivable once the live task is archived. A
read-only spike against `_archive/agy-first-whole-diff-review-seat.md` counted fourteen dispatch
lines, two rejected feedback cycles, calculated `18.81` hours from `started`/`completed`, read the
final `88.17%` coverage, retained `n/a` tokens, and derived the seven-day date `2026-08-07`. The tuple
matched `docs/dev/ledger.csv:16` exactly. Live GitHub reads independently confirmed product PR `#118`
and ledger PR `#119` merged at the stored heads/timestamps. Result: PASSED; no new measurement store
is needed.

## Implementation dispatch sizing

ONE worker session. The implementation has one behavior boundary: remove ledger authority while
preserving product terminal/archive and historical reads. It stays below 90 minutes and has fewer
than three independent behaviors, so another cold-start or parallel worktree lane does not buy useful
wall-clock. The worker should complete one RED-to-GREEN loop spanning docs plus the focused fixture.

## Pre-mortem

If this ships exactly per spec and still fails, the most likely cause is a **hidden assumption**:
some archived entities may not preserve enough optional measurement evidence to reconstruct a full
row. That must reduce measurement completeness to explicit unknowns, never pull ledger maintenance
back into the delivery authority path.

## Measurement

FO-owned. This ideation worker does not invent its own dispatch count or token figure.

## Doc diff

- `docs/dev/README.md:394-401,1095-1140`: change ledger fields from terminal prerequisites to optional
  legacy/observation metadata; replace the ledger-gated `done` definition with product-merge-driven
  terminal state plus durable archive.
- `docs/dev/README.md:220-240,287-293,336-375`: make dirty/outgoing terminalization replay consume
  only product fields and product host facts. Preserve ledger artifacts as unconsumed bytes so an
  empty, historical, or malformed ledger ref cannot veto a product-derived state transition.
- `docs/dev/README.md:1258-1750`: move collection to post-archive derive/batch semantics; retain CSV
  history/read modes and explicitly make unknown token/diff coverage non-blocking. Replace per-task
  finalization with a human-triggered batch and captain-approved proposal boundary.
- `docs/dev/_mods/pr-merge.md:143-220,393-620,1914-1985,2023-2036,2284-2297`: remove ledger artifact
  authentication from dirty/outgoing product terminalization and remove the second PR/ledger predicate
  from the normal merged-product path; retain exact product authentication, compound state commit,
  archive recovery, and legacy audit-ref reads.
- Add `docs/dev/artifacts/decoupled-ledger-contract-test.sh` as the focused executable proof. Do not
  add or modify CI.
- No `PRODUCT.md`, `ARCHITECTURE.md`, `ROADMAP.md`, or `ledger.csv` content change is required by the
  design. The README is the current published authority for this behavior, and sprint allocation
  remains a captain choice.

## Out of scope

- A second completion/finalization PR for each task.
- Any seven-day wait before `done` or archive.
- Daemons, schedulers, new CI, telemetry ingestion, generic analytics, or a new datastore.
- Automatic backlog/task creation, automatic process mutation, or ledger-owned task state.
- Universal token or diff-coverage requirements; unavailable observations remain unknown.
- Reinterpreting or normalizing historical rows and archived refs.
- Product/plugin behavior, release automation, or ROADMAP scheduling.

## Stage Report: ideation

- DONE: Recover current terminalization and measurement seams with file:line evidence and classify
  existing authority before proposing changes.
  The seven-row reverse-recovery table is pinned to fetched `origin/main` `1d6d0d0`; it separates
  working product/state/archive mechanisms from the one `EXISTS_BROKEN` ledger authority edge.
- DONE: Produce the smallest non-blocking ledger contract and backward-compatible migration.
  The selected archive-first approach reuses current product artifacts, state mutation, archive,
  archive evidence, CSV schema, and readers. It explicitly excludes a second completion PR, a
  seven-day done gate, a daemon, automatic process mutation, and mandatory token/coverage metrics.
- DONE: Define falsifiable acceptance checks for ledger-independent terminalization and useful
  historical observation.
  Four ACs name executable CLI/static proofs, RED baseline behavior, negative cases, and the exact
  archived row the post-archive derivation must reproduce.
- DONE: AC-1 has a runnable terminal-without-ledger end-state proof and a current negative baseline.
  Verified by: `docs/dev/README.md:1108-1114` names the blocking behavior today, while the planned
  `docs/dev/artifacts/decoupled-ledger-contract-test.sh terminal-without-ledger` forces every ledger
  access to fail and requires one durable archived product entity.
- DONE: AC-2 has a backward-compatibility matrix rather than a migration-by-assertion.
  Verified by: `docs/dev/README.md:1406-1416,1428-1456` and `docs/dev/ledger.csv:1-16` provide the
  existing reader/history fixtures that the planned `compatibility` case must preserve byte-for-byte;
  the extracted current fixture ran fresh and exited 0 for all expected result modes.
- DONE: AC-3's archive-first derivation premise was spiked against real completed evidence.
  Verified by: `_archive/agy-first-whole-diff-review-seat.md:1-20,1347-1362,1574,1731` reproduced the
  exact committed tuple in `docs/dev/ledger.csv:16`; the planned `archive-derive` case makes that
  comparison repeatable and asserts the archived root is unchanged.
- DONE: AC-4 has an exact diff boundary and negative scans.
  Verified by: `git diff --name-only origin/main...HEAD` plus the planned `scope` fixture permits only
  the two lifecycle docs and focused local test and rejects workflow, daemon, state-mutation, or
  automatic task-creation additions.
- DONE: Complete ideation discipline.
  Captain-authored scope and skip reason, 90-minute appetite plus 30-minute tolerance, fastest and
  smallest cut, rejected alternatives, required design decision, doc diff, risk spike, one-worker
  sizing, E2E surface, and one-sentence pre-mortem are recorded. Sprint remains blank.

### Summary

Recovered the current flow as a working delivery/archive mechanism with one policy defect: ledger
finalization sits between authenticated product merge and authoritative task state. The recommended
contract removes only that edge. Product merge terminalizes and archives immediately; archived
evidence can later populate the unchanged CSV in a human-triggered batch; any process-improvement
task still requires captain approval. A read-only spike reproduced the newest committed row exactly
from archived evidence, so the design preserves measurement value without a new service or second
completion PR.

## Stage Report: implementation

- DONE: AC-1 — Prove RED then GREEN for product-merged terminalization while every ledger access fails,
  keeping authenticated product evidence and durable archive fail-closed.
  RED `terminal-without-ledger` and `compatibility` on `origin/main@1d6d0d0` both exited 1 with
  `FAIL:RED: authenticated product MERGED still enters ledger finalization before terminal state`.
  The archive-derivation arrangement was intentionally green in RED: it is a precondition proving
  the historical archive contains the claimed observation, not a claim about terminalization.
  GREEN: `bash docs/dev/artifacts/decoupled-ledger-contract-test.sh terminal-without-ledger` passes
  against the marked product-only transaction. It would fail for any ledger access, unauthenticated
  product acceptance, dirty-root archive mutation, or missing flat/folder archive result.
- DONE: AC-2 / AC-3 — Preserve existing eight-column CSV rows and historical ledger refs, and prove archive-first
  derivation reports unknown instead of inventing optional metrics.
  GREEN: the `compatibility` case preserves the copied CSV hash, reads the historical
  `ledger-merge:` ref, and terminalizes empty, draft, pending, numbered, merged, and malformed ledger
  phases from authenticated product evidence. The `archive-derive` case reproduces
  `14,2,18.81,n/a,88.17,pending:2026-08-07`, keeps the archive tree hash unchanged, and requires
  unavailable token/coverage evidence to remain unknown. Either case fails if a row/ref is rewritten,
  a ledger phase vetoes delivery, a metric is invented, or the exact tuple differs.
- DONE: AC-4 — Keep the product diff to `docs/dev/README.md`, `docs/dev/_mods/pr-merge.md`, and
  `docs/dev/artifacts/decoupled-ledger-contract-test.sh` only; add no daemon, scheduler, CI trigger,
  automatic task creation, ROADMAP edit, or ledger data change.
  GREEN: `scope` permits exactly those three paths and rejects network, automatic process mutation,
  workflow/daemon additions, and mandatory optional-metric gates. `git diff --check`, `bash -n`,
  ShellCheck 0.11.0, even Markdown-fence counts, the extracted historical ledger verifier, and the
  Spacedock stage-definition parser all pass.
- DONE: Run scoped tests in the loop and a fresh full-suite/ripple exit on the committed code.
  `bash docs/dev/artifacts/decoupled-ledger-contract-test.sh all` passes all four cases.
  Repository exits pass: `scripts/dev-flow-work-context-check.test.sh` 23/23,
  `scripts/release-metadata.test.sh` 22/22, and `scripts/skill-frontmatter-lint.test.sh` 12/12.
  The fixture remains manual and adds no CI job, so it changes no CI job runtime margin; no
  OS/libc/locale/clock-dependent behavior or CI-pinned governed file was introduced.
  `spacedock status --read 7rgdvsjypgmzk8wh03h3vst9 --ac-scan` resolves AC-1 through AC-4 at
  lines 196, 209, 222, and 236. It also emits `unevidenced=true citations=0` for each despite their
  `Verified by:` commands, matching the known counter hazard recorded in `docs/dev/ROADMAP.md`.

### Summary

Commit `2d3985fc92523e49b6b513300811509043114406` removes ledger authority from product delivery while
preserving exact product authentication and fail-closed terminal/archive durability. The unchanged
eight-column ledger remains a backward-compatible, human-triggered observation surface whose
unknown values and failures cannot alter task state. The isolated worker branch and worktree remain
intact for First Officer integration; no worker-branch PR or cleanup was performed.

## Stage Report: validation

- FAILED: Independently reproduce every AC and the RED-to-GREEN contract at exact product head
  `2d3985fc92523e49b6b513300811509043114406`; do not rely on the implementation report.
  RED at `origin/main@1d6d0d0` failed both ledger-gated modes as expected; GREEN modes passed, but
  AC-1, AC-2, and AC-4 lack the independent proof their end-state claims require.
- DONE: Adversarially attack backward compatibility, empty/draft/pending/numbered/merged/malformed
  ledger refs, flat and folder archives, ledger inaccessibility, authenticated product fail-closed
  behavior, and honest unknown metrics.
  Auth removal, ledger re-coupling, and `unknown -> 0` all reddened; an automatic-task mutation did not.
- FAILED: Verify the exact three-path scope, diff/test evidence, required validation lenses,
  cross-model review, and material findings; report only and do not edit product files.
  Scope is exactly three paths and product stayed clean, but four material proof defects reject the gate.
- FAILED: AC-1 — Product delivery terminalizes without ledger upkeep.
  Real Spacedock 0.26 reached local `done` and flat/folder archive, but lines 77-124 and 222-243 use a
  no-origin fixture and handwritten archive path, not the documented remote-observed transaction.
- FAILED: AC-2 — Legacy ledger and in-flight entities stay readable.
  Six ledger phases and the historical v1 ref passed, but the changed direct-commit route at
  `docs/dev/_mods/pr-merge.md:1743` is never exercised by the v1-only fixture at lines 140-162.
- DONE: AC-3 — Archive-first observation remains useful and non-authoritative.
  `archive-derive` reproduced `14,2,18.81,n/a,88.17,pending:2026-08-07`, preserved the state tree,
  and reddened when missing optional evidence was changed from `unknown` to invented `0`.
- FAILED: AC-4 — The change stays inside the declared repo-platform boundary.
  Adding `spacedock new` outside the marked snippet left both `scope` and `all` green; lines 449-470
  only allowlist paths and grep prose, contrary to Proof Policy 1 at `docs/dev/README.md:552`.

Lenses: workflow prose plus executable shell; correctness REJECT/3, security REJECT/1,
silent-failure REJECT/1, type-design REJECT/1, concurrency REJECT/1,
resource-lifecycle PASS/0, manifest/back-compat REJECT/1.
Diff coverage: **65.65%** (172/262 traceable Bash logical statements), below the 85% ratchet; no waiver.
Adversarial: three core mutations red; automatic task creation outside the marker stayed green — test hole.
Cross-model: preferred `agy` failed wrong-scratch materialization/timeout; Claude Sonnet REJECTED with
P1/P2/P3 findings, and its cited lines were checked against the exact files (two approximations corrected).
E2E: real Spacedock 0.26 split-root flow passed locally, but its explicit no-origin output leaves remote
terminal/archive durability unproved, so the end-to-end verdict is REJECT.

### Summary

Validation REJECTS exact product head `2d3985fc92523e49b6b513300811509043114406` and routes back to
implementation. The final regression exit still passed focused `all`, 23/23, 22/22, 12/12, ShellCheck,
and `git diff --check`; the rejection is for falsified proof coverage and unsupported guarantees, not a
generic suite failure. Product files, branch, and worktree were preserved unchanged.
