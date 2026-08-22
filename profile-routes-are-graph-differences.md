---
id: 8x38b1qryjrmy5w4ffk1egy1
title: Profile routes are expressed as graph differences, so a POC or Pilot item cannot reach done
status: validation
source: hit in production 2026-08-20 by declared-receipts-need-a-reader (k69wjs5ttme3z11hph3sy45d), the first Pilot item this workflow has run; the Captain ruled that asking Spacedock to skip stages is the wrong ask
product: kc-dev-flow
sprint:
started: 2026-08-21T08:46:56Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-profile-routes-are-graph-differences
issue:
pr:
mod-block:
gates:
    version: 1
    records:
        - id: gate:8x38b1qryjrmy5w4ffk1egy1:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:8x38b1qryjrmy5w4ffk1egy1-backlog-1
              briefing:
                id: briefing:8x38b1qryjrmy5w4ffk1egy1:backlog:attempt-1:revision-1
                digest: sha256:2a61477e12e737f5b82ec15c384a84b1aab3d3bf5859c30a879f9659d7ddc1d1
                request-digest: sha256:daee347373ac8139866e8c03b4eca2c5e4f0a1a3cf0eabb58e58f4abe3e7f2e1
                room-ref: ./profile-routes-are-graph-differences/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:8x38b1qryjrmy5w4ffk1egy1:backlog:1
                briefing: briefing:8x38b1qryjrmy5w4ffk1egy1:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-08-21T08:46:04.874207Z"
                decision: approve
                reason: 'Captain approved scheduling with the Production work profile, calling this an evident defect. It is an observed failure: the first Pilot item this workflow ran could not reach done and needed a recorded no-op transition to terminalize. Production because any fix touches the ROUTES table or the profile contracts, which external adopters consume at a pinned tag and which carry compatibility obligations. The Captain accepted that the accepted outcome may be a design decision rather than a diff, and had already ruled out asking Spacedock for a skip-stage capability.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:8x38b1qryjrmy5w4ffk1egy1:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:8x38b1qryjrmy5w4ffk1egy1-ideation-1
              briefing:
                id: briefing:8x38b1qryjrmy5w4ffk1egy1:ideation:attempt-1:revision-1
                digest: sha256:7a04bf343bec13c50b9054e8109ce64bfd84696657049d70407e4920a421b1dd
                request-digest: sha256:3808eb2e350c12f10715bf47683125d67a0b6a6e6765a71e1e2a1b9d75ad377c
                room-ref: ./profile-routes-are-graph-differences/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:8x38b1qryjrmy5w4ffk1egy1:ideation:1
                briefing: briefing:8x38b1qryjrmy5w4ffk1egy1:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-08-21T09:34:07.272997Z"
                decision: approve
                reason: 'Captain approved Direction 1. The shape drove the real 0.27.0-pre8 CLI rather than reading docs: Fixture A reproduces the production failure red on demand through the full gate lifecycle with no forced status writes, and Fixture B shows a terminal-target approval leaves status put while merge guard terminalizes, so the fix asks nothing new of the runtime — a claim the FO independently corroborated against its own first-hand observations of #262 and #264 today. Direction 2 was rejected by citing the receipt''s own architecture obligation. Every changed file is named and the adopter migration is concrete. Approved with the FO residual carried forward as something implementation must answer with a mechanism: after the demotion, Production''s release authorization rests only on a prose obligation binding whoever types merge guard --verdict, which would collapse the two rulings the receipt''s architecture obligation requires be kept separate.'
              application:
                target-stage: implementation
                state: consumed
        - id: gate:8x38b1qryjrmy5w4ffk1egy1:validation
          stage: validation
          attempts:
            - id: gate-attempt:8x38b1qryjrmy5w4ffk1egy1-validation-1
              briefing:
                id: briefing:8x38b1qryjrmy5w4ffk1egy1:validation:attempt-1:revision-1
                digest: sha256:f9ff09956c625a7b414885ee67a650a86a505647ee0d2fb0f4fc3c734f161f32
                request-digest: sha256:3c4589787b233af4ff8e13494065147bafee1ef2219c569b65368d240c1ef461
                room-ref: ./profile-routes-are-graph-differences/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:8x38b1qryjrmy5w4ffk1egy1:validation:1
                briefing: briefing:8x38b1qryjrmy5w4ffk1egy1:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-08-21T15:15:13.086512Z"
                decision: approve
                reason: 'Captain approved validation at 3ad3725a. All four items were independently reproduced rather than read from the implementer''s transcript: the RED was recreated with a standalone script against the pre-fix loader, all six route-string copies were mutation-tested one at a time with each guarding check seen to fail on its own distinct message (6/6, none unverified), the release-authorization limits were re-probed against a fresh fixture and match the entity''s claims exactly, and the contract test''s sole failure is the pre-existing sibling casing bug reproducing identically on the merge base. The lost second review ceremony is accepted as a named residual, not a closed item. FO observation carried forward: the six new enforcement points are reachable in CI, where the sibling test skips for want of a spacedock binary, but are blocked locally by that test''s fail-fast failure — which promotes spacedock-route-test-passes-nowhere from an incidental find to a blocker on half this work''s local effect.'
              application:
                target-stage: release
                state: consumed
            - id: gate-attempt:8x38b1qryjrmy5w4ffk1egy1-validation-2
              briefing:
                id: briefing:8x38b1qryjrmy5w4ffk1egy1:validation:attempt-2:revision-1
                digest: sha256:ba8541dbe8a50b7c90568696f16c16680524de43e32545cdefbc655c77f28cef
                request-digest: sha256:bb9979e54d0a305ce22fdbb0138a2cc9c4a9923f4af41be53075be37e2ccefaf
                room-ref: ./profile-routes-are-graph-differences/review/validation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:8x38b1qryjrmy5w4ffk1egy1:validation:2
                briefing: briefing:8x38b1qryjrmy5w4ffk1egy1:validation:attempt-2:revision-1
                by: person:captain
                at: "2026-08-22T08:06:07.432186Z"
                decision: approve
                reason: 'Captain approved validation at d775a02f after correction round 1. The claim a cross-model interviewer falsified — that all six route-string copies had a check seen to fail — is closed and re-verified by that exact mutation: corrupting both kernel copies identically now fails with ''kernel route table omits the current Production route'', where the prior round''s one-copy mutation had only broken byte-parity. POC now terminalizes through merge guard with its live output captured. The branch/stack file intersection was recomputed independently with comm -12 and comes to the same three files, whose merged regions preserve the newly-landed backlog-exit-bar and profile-selection semantics intact and uncontradicted. The three recorded-not-fixed residuals stay named: release authorization as unenforced prose, the skip caveat as unmachine-checkable, and this fix''s own proof not running in CI.'
              application:
                target-stage: release
                state: pending
        - id: gate:8x38b1qryjrmy5w4ffk1egy1:release
          stage: release
          attempts:
            - id: gate-attempt:8x38b1qryjrmy5w4ffk1egy1-release-1
              briefing:
                id: briefing:8x38b1qryjrmy5w4ffk1egy1:release:attempt-1:revision-1
                digest: sha256:a888c5a62d2512316dc544cb0607ac6eb173b8baccad439d122ddb195575baff
                request-digest: sha256:c33d3e99e49705f28ae42ab8cd96c92f2e823e38dff8cf553dd1f278fd246e16
                room-ref: ./profile-routes-are-graph-differences/review/release/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:8x38b1qryjrmy5w4ffk1egy1:release:1
                briefing: briefing:8x38b1qryjrmy5w4ffk1egy1:release:attempt-1:revision-1
                by: person:captain
                at: "2026-08-22T01:24:26.984763Z"
                decision: approve
                reason: 'Captain approved release readiness at delivery revision b3b0e2ed and ruled the base stays main. The single commit was rebased with --onto after confirming the branch carried exactly one commit, and both suites were re-run on the rebased revision; the contract test''s sole failure remains the pre-existing sibling casing bug, with nothing hidden behind it. On the base question, delivery-branch-base.md''s trunk clause literally requires ''no shared file'' and this candidate does share kernel.md and choose-work-profile/SKILL.md with the open stack #267 -> #271 -> #272 -> #275. The FO compared the actual hunks: both sides insert near the same line of kernel.md but on unrelated subjects — this candidate bounds the runtime skip clause and rewrites the Production route table, while the stack inserts a backlog exit bar. Neither builds on, depends on, nor re-delivers the other, so the overlap is textual adjacency and the cost of trunk is a keep-both conflict for whoever merges second, against making an independent fix hostage to a four-deep stack. PR #276 is Draft, targets main, MERGEABLE/CLEAN with checks green. Mark-ready and merge remain the Captain''s actions.'
              application:
                target-stage: done
                state: superseded
            - id: gate-attempt:8x38b1qryjrmy5w4ffk1egy1-release-2
              briefing:
                id: briefing:8x38b1qryjrmy5w4ffk1egy1:release:attempt-2:revision-1
                digest: sha256:222aa5ccc90eaa983580b740d1d1ca9f49a517a6a98fbe346345fa0c62d0ae14
                request-digest: sha256:50819da469e4a0cfe734365042587d5ae2e5a70e4ce9ce60e450b0447b9de728
                room-ref: ./profile-routes-are-graph-differences/review/release/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:8x38b1qryjrmy5w4ffk1egy1:release:2
                briefing: briefing:8x38b1qryjrmy5w4ffk1egy1:release:attempt-2:revision-1
                by: person:captain
                at: "2026-08-22T07:05:50.083694Z"
                decision: approve
                reason: 'Captain re-approved release readiness at the rebased delivery revision 7bbae216, superseding the attempt-1 approval that cited b3b0e2ed, a revision no longer on the branch. The branch was rebased a second time onto origin/main at ef808a91 after the four-deep stack #267/#268/#269/#271/#272 landed, carrying exactly one commit before each rebase and using the explicit --onto form both times. Both suites were re-run on the rebased revision and the result improved: kc-dev-flow-contract-test.py now passes outright because #268''s casing fix reached main, so this work''s six route-parity checks are reachable and green locally as well as in CI, with no other check disabled to reach them. The PR body''s two statements that the contract test''s sole failure was the casing bug and that the six checks were locally blocked have been corrected to the current outputs. The lost second review ceremony remains a named residual, not a closed item.'
              application:
                target-stage: done
                state: superseded
---

## Problem

`kc-dev-flow` gives each work item its own route. The workflow runtime owns one
stage graph. Where the two disagree, nothing reconciles them, and a POC or Pilot
item cannot complete.

Observed, not hypothetical. `declared-receipts-need-a-reader` is a
`pilot-product-slice` item. Its validation gate was approved; `gate consume`
advanced it to `release`; and it is now stranded:

```
status: release
loader: workflow stage 'release' is outside pilot-product-slice;
        expected: ideation, implementation, validation
status --next: dispatchable [] / ready_gates []
```

The loader had already computed the correct answer. For that same item at
`validation` it emits `next_workflow_stage: done`. `gate consume` never asks it;
it advances to the next stage in the declared graph.

`next_workflow_stage` is produced by the loader, asserted by the loader's own
tests, and mentioned in two prose files (`continue-dev-flow/SKILL.md`,
`docs/dev/README.md`). Nothing that executes reads it. That is the same shape as
the defect `#256` reported about `receipt`, one layer up: the right answer is
emitted into a field with no consumer.

`kernel.md` anticipates the need and assigns it to nobody in particular:

> A workflow runtime **may** expose the union of stage names and skip stages
> outside the selected route. Skipping an inactive stage requires no synthetic
> review or receipt.

Permission language, no named implementer, no requirement, and no fallback for a
runtime that cannot skip. Spacedock did not break a promise — it only ever
offered one graph per workflow. The routes are this package's invention, and
this package owns route *validation* (the loader fails closed on an out-of-route
stage, which is what caught this) while owning no part of route *traversal*.

## The two skip points are not equally dangerous

`ROUTES` in `profile-contract-loader.py` against the adopter graph
`backlog -> ideation -> implementation -> validation -> release -> done`:

| Skip | Who | Severity |
|---|---|---|
| `ideation` | POC | Harmless. Non-terminal, so an FO `status --set` moves past it. |
| `release` | POC and Pilot | Blocking. The terminal transition is owned by the merge ceremony and needs a pending approval whose target is `done`; the validation approval gets spent on `release` instead, so that approval never exists. |

Any fix that only addresses `release` still leaves POC items needing a manual
nudge past `ideation`; any fix that only addresses traversal still has to
explain where the terminal approval comes from.

## Ruled out before shaping starts

Asking Spacedock for a skip-stage capability. The Captain ruled this the wrong
ask on 2026-08-20: making traversal depend on data inside an entity body turns a
graph the runtime can reason about into one it cannot, and gates, invariants and
mod-blocks all key off stages. It would also be a large new surface for one
adopter's need.

## Candidate directions, not a decision

1. **Demote `release` from a state to a gate.** `ideation`, `implementation` and
   `validation` are all "work happens here"; `release` for Production is mainly
   an authorization checkpoint, which is the shape of a gate, not a state. Model
   it as a Production-only gate after `validation` and delete the state. All
   three profiles then share one graph, the difference lives in which gates
   fire, and nothing needs to skip. **Cost:** Production loses release authority
   as a separately-rendered decision — "the code is verified" and "this may be
   released" are two rulings, and collapsing the states risks collapsing the
   rulings. The gate design has to carry that weight back.
2. **One workflow per profile.** Three exact linear graphs, zero new mechanism,
   already supported. **Cost:** entities split across three state trees,
   promotion becomes a cross-workflow move, and a single-view status query over
   all work stops working.

Direction 1 is the FO's recommendation; it is recorded here as a starting point
for shape, not as a selection.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v2
  selected: production
  recommended: production
  basis: "Any fix touches the ROUTES table or the profile stage contracts, which external repositories consume at a pinned release tag. Changing which stages a profile has is a compatibility event for every adopter whose workflow graph mirrors the current routes, so it carries migration, rollback and announcement obligations."
  route: [shape, build, verify]
  obligations:
    architecture:
      - "Do not require the workflow runtime to skip a stage. The Captain ruled that the wrong ask: traversal that depends on data inside an entity body stops being a graph the runtime can reason about, and gates, invariants and mod-blocks all key off stages."
      - "Stop expressing profile differences as graph differences, rather than reconciling two graphs at runtime. If a difference must survive, it belongs in what happens inside a stage or in which gates fire, not in which states exist."
      - "Preserve Production's release authorization as a decision rendered separately from verification. Collapsing the states must not collapse the two rulings."
    implementation:
      - "A POC item and a Pilot item must each reach `done` without any recorded no-op transition through a stage their route excludes."
      - "Name the migration for adopters whose committed workflow graph already contains the stages this changes, including what an in-flight item at an affected stage does."
    testing:
      - "A check that FAILS today: drive a POC item and a Pilot item to their terminal state and assert no gate record exists at a stage outside their route. The current tree must go red on it before the fix, or the check is not measuring the defect."
      - "A check that fails when the loader's `next_workflow_stage` disagrees with the stage the runtime would advance to, so the two can never silently diverge again."
  scope_boundary: "Excludes a Spacedock skip-stage capability, excludes any FO-side manual nudge that leaves the graph and the routes disagreeing, and excludes broadening or narrowing what work each profile performs."
  promote_when:
    - "Already Production; no higher profile exists. Stop and obtain a new Captain choice if the accepted scope grows to changing which work a profile performs rather than which states it occupies."
  decision:
    authority: person:captain
    at: 2026-08-21T08:46:29Z
```

## Accepted outcome and non-goals

**Selected: Direction 1 — demote `release` from a graph state to a
terminal-approval boundary. Direction 2 (one workflow per profile) is
rejected.**

### Why Direction 2 is rejected

The Captain-accepted work-profile receipt already forecloses it. The
architecture obligation reads: *"Stop expressing profile differences as graph
differences ... If a difference must survive, it belongs in what happens
inside a stage or in which gates fire, not in which states exist."* Direction
2 is the maximal case of expressing a profile difference as a graph
difference — three separate graphs instead of one. It also costs a
single-view status query across all work (`spacedock status --boot` and
`--where` currently span one workflow) and turns promotion into a
cross-workflow move, neither of which the Captain's obligation or this
task's scope accepts paying for.

### Mechanism (empirically verified against Spacedock 0.27.0-pre8, not assumed)

Direction 1's original framing said "model release as a Production-only gate."
Concretely: Spacedock already has the mechanism this needs, so nothing new is
asked of the runtime — the same boundary the Captain already ruled out asking
for (skip-stage) is not needed.

`spacedock gate --help` documents that an approval whose **target stage is
terminal** is not spent by `consume`: it stays `pending`, reports
`route=approved-awaiting-merge`, and `spacedock merge guard <slug> --verdict
passed|rejected` is "the sole terminal consumer." I built two throwaway
fixtures under `/tmp` (not committed — code is not this stage's deliverable)
mirroring `docs/dev/README.md`'s state graph and drove entities through the
real CLI (`gate prepare` / `gate record --consume` / `status --set` /
`merge guard`), not by inspecting docs:

- **Fixture A — today's 6-state graph** (`backlog, ideation, implementation,
  validation, release, done`): a `pilot-product-slice` entity approved and
  consumed at `validation` lands at `status: release` — reproduced, see
  Acceptance evidence. This is the observed production failure, now shown red
  on demand instead of only inferred from one incident.
- **Fixture B — candidate 5-state graph** (`release` removed, `done`
  terminal): a `production` entity's validation-gate approval now targets
  `done`, which is terminal, so `gate record --consume` reports
  `application=advance/pending ... consumed=false target-stage=done
  route=approved-awaiting-merge` and **status stays `validation`** — it does
  not silently land anywhere. A separate, later `spacedock merge guard
  prod-item --verdict passed` is the action that terminalizes it, writes
  `verdict: PASSED`, and archives it. Full transcript in Acceptance evidence.

This gives two distinct, separately timestamped rulings on the same entity
without a dedicated `release` state: the validation gate's `resolution.decision:
approve` (**"the code is verified"**, Captain-recorded at validation-approval
time) and the `merge guard --verdict` write (**"this may be released"**,
recorded later, by whoever is authorized to run that command). Nothing about
this ruling separation depends on being Production-only — POC and Pilot
already deliver through the same PR/merge-guard path per this workflow's Local
Profile table, so `merge guard` firing for them too is not new exposure; what
changes is only what content a human must have satisfied *before* they are
willing to type `--verdict passed` for a Production item.

### Release-authorization residual: what is and isn't a mechanism

The FO's residual asked for a mechanism, not a sentence in a contract, and
named the specific risk: carrying `release.md`'s bullets into `verify.md`'s
prose could be the same no-enforcement-point shape this task exists to
remove. I probed `spacedock gate record --actor` directly (not from docs)
against a throwaway fixture, deliberately trying `person:kent`,
`team:release-owner`, `release-owner`, `agent:captain`, `captain` — every one
is refused with `unsupported chat decision actor "<value>"`; only
`person:captain` is accepted. `merge guard` itself takes no `--actor` flag at
all (confirmed via `--help`), and no gate command validates `--artifact` file
*content* against a stage's `## Required output` list — only that a
`.md`/`.markdown` file exists (confirmed: no such check string exists in the
binary). These are all pre-existing 0.27.0-pre8 constraints, unchanged by
this task in either direction:

- **Real, verified mechanism:** `merge guard --verdict passed|rejected` is
  refused with no pending terminal-target approval (RED-demo below: `entity
  carries no binding pending terminal-target approval`). This did not exist
  as a concept before `release`'s removal turned `validation`'s approval into
  the terminal-target approval; it is genuinely new leverage this task's
  mechanism provides, not carried over from `release.md`.
- **Unchanged, not weakened:** "Captain or declared release owner" was never
  actor-enforced by the tool — before this task, `release`'s own gate
  ceremony was equally restricted to `--actor person:captain` (the tool
  recognizes no other decision actor), so a distinct named release owner was
  already unenforceable at the CLI level. This task does not remove a
  capability the tool ever had.
- **Unchanged, not weakened:** artifact *content* (rollout/rollback,
  operational owner, authorization language) was never CLI-validated for
  `release.md` either — an agent or human is trusted to write it, then and
  now.
- **Genuine residual, correctly scoped as a residual, not silently closed:**
  before this task there were two separate `gate prepare`/`gate record`
  ceremonies before terminal (validation's, and release's), each with its own
  `--artifact`/`--summary`/`--question` and its own resolution timestamp —
  two independently reviewable records even though both were restricted to
  the same actor. After this task there is one gate ceremony (validation)
  plus a bare `merge guard --verdict` write with no artifact or reasoning
  field of its own. The temporal separation and the refusal-without-approval
  property both survive and are verified; the second ceremony's *own* review
  artifact does not. Closing this fully would mean asking Spacedock for a
  second content-validated ceremony or a `merge guard --actor` field — new
  CLI capability, out of this task's scope (`architecture` obligation:
  "excludes broadening... what a Spacedock skip-stage capability" and this
  task's non-goals already draw the line at not asking for new runtime
  capability at all). The available, in-scope answer is procedural: `verify.
  md`'s `## Required output` now names the release-readiness bullets as
  content of *the one artifact that still exists* (validation's), so a human
  preparing that gate has a named place to put release-readiness content
  before approving — weaker than a second ceremony, but not weaker than what
  `release.md` ever enforced at the tool level, and it is the FO's decision
  whether that residual is acceptable or worth a follow-up item asking
  Spacedock for `merge guard --actor`.

**Landed change, concretely.** The Production route string `shape -> build ->
verify[ -> release]` (or its runtime-stage-name equivalent) is duplicated in
at least six places. All six are changed in this task, not the two originally
named:

1. `kc-dev-flow/references/kernel.md` and its `docs/dev/_mods/kernel.md`
   vendored copy — the `## Select before routing` route table's `production`
   row drops ` -> release`. Kept byte-identical (verified: `diff` reports no
   difference; `scripts/kc-dev-flow-contract-test.py` also enforces this by
   byte-comparing the two files, not by trusting the author) and, since
   correction round 1 (Finding A), additionally content-checked: a `require()`
   reads the route row's exact text and fails independently of the
   byte-parity check — see "Does anything check that the six agree?" below for
   why byte-parity alone was insufficient and how the gap was closed.
2. `kc-dev-flow/README.md` — the routes-table row and the profile mermaid
   diagram (`R4["Verify..." ] --> D`, `R5["Release..."]` node and edge
   deleted).
3. `kc-dev-flow/skills/choose-work-profile/SKILL.md` — the profile-selection
   route table row.
4. `kc-dev-flow/skills/continue-dev-flow/SKILL.md` — the superset-graph route
   table row.
5. `kc-dev-flow/scripts/profile-contract-loader.py` `ROUTES["production"]` —
   drops the `"release"` key; `"validation"` now maps to `("verify", "done")`.
   `pilot-product-slice` and `poc-exploration` entries are unaffected (they
   never had a `release` key). Its `docs/dev/_mods/profile-contract-loader.py`
   vendored copy is the same file (byte-parity enforced the same way as #1).
6. `docs/dev/README.md` `stages.states` block and its prose route table —
   drops the `release` state entry; `validation` keeps `gate: true`.

Plus the profile-stage content itself: `profiles/production/verify.md`'s
`## Required output` gains `release.md`'s four bullets (rollout/rollback
readiness, operational owner and monitoring handoff, explicit
Captain-or-release-owner authorization — "do not merge, publish, migrate, or
mutate production without the named authority" carries over verbatim as the
gate on invoking `merge guard`); `profiles/production/release.md` is deleted,
in both `kc-dev-flow/references/` and its `docs/dev/_mods/` vendored copy.
`kc-dev-flow/scripts/profile-contract-loader.test.py` and
`scripts/kc-dev-flow-contract-test.py` (`profile_files["production"]`,
formerly `("base.md", "shape.md", "build.md", "verify.md", "release.md")`)
lose the `release.md` member and any release-route assertion.

**Does anything check that the six agree? Corrected in correction round 1
(Finding A).** The claim below was false as first written: it asserted a
content check (one that fails when the route *string itself* drifts, as
opposed to the two copies merely drifting from each other) existed for the
kernel.md pair. It did not. Byte-parity between `kc-dev-flow/references/kernel.md`
and `docs/dev/_mods/kernel.md` only proves the two copies agree with *each
other*; the validation round's mutation-testing changed one copy at a time,
so it could never have exercised the case where both are edited identically —
which is exactly what the FO's reproduction did, leaving
`scripts/kc-dev-flow-contract-test.py` green on a corrupted Production route
row. Two of the six copies shared a single guard that any consistent
corruption passed.

As of this correction, all 6 of 6 named copies carry a content check — one
that reads the route string itself and fails on the exact wording, not merely
on cross-copy disagreement. Two (`kc-dev-flow/README.md`,
`continue-dev-flow/SKILL.md`) had no enforcement point at all before this
task and were fixed by hand; both now carry a `require()` in
`scripts/kc-dev-flow-contract-test.py` (a positive phrase check for the
current route, a negative check that the removed `release` element is gone).
`choose-work-profile/SKILL.md` and `docs/dev/README.md` each already carried
an existing positive/negative phrase pair. `profile-contract-loader.py`'s
`ROUTES` table already carried a content check — structural equality against
a hardcoded `expected_routes` dict, plus, live, agreement with the real
loader's `next_workflow_stage` output — so it was never the byte-parity-only
gap Finding A named; its `docs/dev/_mods/` twin is additionally
byte-parity-checked, giving it both. `kernel.md`'s pair is the one that
changed this round: it kept its pre-existing byte-parity check (still
structurally one source, not two data points to keep in sync) and gained a
new, separate content check —
`require("| \`production\` | \`shape -> build -> verify\` |" in kernel, ...)`
in `scripts/kc-dev-flow-contract-test.py` — proven by reproducing the FO's
exact mutation (both copies edited identically to
`` | `production` | `shape -> build -> verify -> deploy` | ``) and observing
`kc-dev-flow contract: kernel route table omits the current Production route`,
exit 1, then reverting to a clean `git status --porcelain`. Every one of the
six now rests on a content check seen to fail on its own mutation; none rests
on byte-parity alone. `kc-dev-flow/MIGRATION.md`'s new changelog entry is
prose documentation of a change, not a copy of the route string in the sense
above, and carries no separate enforcement point — a stale migration note is
a documentation-quality residual, not a routing defect this task's mechanism
depends on.

### The remaining skip clause: bounded, not removed

`kernel.md`'s `## Select before routing` carries: *"A workflow runtime may
expose the union of stage names and skip stages outside the selected route.
Skipping an inactive stage requires no synthetic review or receipt."* Before
this task there were two skip points it covered — `ideation` for POC
(harmless, non-terminal) and `release` for POC and Pilot (blocking, because it
sat in front of the terminal transition). This task removes `release` as a
runtime state entirely, so it stops being a skip candidate at all — there is
no longer a `release` stage to skip. POC's `ideation` skip is unchanged and
still governed by this clause (confirmed: `ROUTES["poc-exploration"]` has no
`ideation` key, so the loader never expects that stage; the FO jumps `status`
directly from `backlog` to `implementation`, and no gate record is ever
created at `ideation` for a POC item).

Decision: the clause **stays, bounded**, not removed. It cannot be removed —
POC's `ideation` skip is a real, Captain-accepted design (severity table in
`## The two skip points are not equally dangerous` above), not a leftover, and
still needs a runtime affordance. But leaving it exactly as-is is the same
"permission language, no named implementer" shape the Problem section
diagnosed: nothing in the clause said *which* skips are safe, and that missing
boundary is what let a dangerous skip (`release`, gating a terminal
transition) go unnoticed next to a harmless one (`ideation`, not gating
anything) for as long as it did. `kernel.md` now states the invariant this
incident surfaced: a skip is safe only when the skipped stage carries no
authorization checkpoint a later stage does not also carry; a stage whose skip
would remove the route's sole terminal-authorization checkpoint is not a
candidate for the clause and must fold that checkpoint into an adjacent
working stage's contract instead — cross-referencing `production`'s own route
row above as the worked example. This does not add a new mechanism; it names,
in the shared core, the boundary this task's fix already draws in practice.
Both `kernel.md` copies carry the addition, verified byte-identical the same
way as the route-table edit.

### Non-goals

- No Spacedock skip-stage capability — the mechanism above is existing,
  documented 0.27.0-pre8 behavior (terminal-approval + `merge guard`), not a
  new runtime ask.
- No change to what work each profile performs, only which graph states its
  route occupies (kernel.md's `poc-exploration` / `pilot-product-slice` /
  `production` route table entries for `shape`/`build`/`verify(-deliver)` are
  unchanged; only `production`'s trailing `release` route element and its
  runtime `release` stage are removed).
- POC's existing `ideation` skip (harmless per the severity table — no gate
  record is ever created there because the FO jumps `status` directly from
  `backlog` to `implementation`) is unchanged by this task. It remains a
  correctly-functioning manual nudge, not a defect this task closes; closing
  it would need its own graph change and is out of scope here.
- Does not touch `poc-exploration` or `pilot-product-slice` ROUTES entries,
  which already exclude `release` and are not the broken leg.

### Adopter migration

1. **Every committed Production v2 receipt goes stale the moment ROUTES
   changes — including this work item's own receipt.** The loader recomputes
   `expected_route = [logical for logical, _next in ROUTES[profile].values()]`;
   for `production` that becomes `[shape, build, verify]` once `release` is
   dropped, so any committed receipt still reading
   `route: [shape, build, verify, release]` throws `stale route for
   production: expected [...], got [...]` on next load — a fail-closed
   refusal, not a silent pass. Migration path: identical to the documented
   v1→v2 upgrade — `kc-dev-flow:choose-work-profile` re-records the receipt
   mechanically under the *same* Captain selection (no new Captain decision
   required, since the profile itself did not change, only its route
   representation). This item's own `route: [shape, build, verify, release]`
   above must be re-recorded in the same commit that lands the ROUTES change,
   or `implementation` cannot even load its own stage contract.
   `poc-exploration` and `pilot-product-slice` receipts carry no `release`
   entry today and are unaffected.
2. **An in-flight item sitting at `status: release` when the graph changes.**
   Verified empirically (Fixture A's entity, after editing its README to the
   5-state graph): `spacedock status --validate` still reports `VALID` — a
   status value with no matching declared state is **not flagged** — but
   `spacedock status --boot`'s dispatchable table silently excludes it (no row,
   no NEXT, no error); it remains reachable only via `--where status=release`
   /`--fields`, i.e. it goes quietly non-dispatchable rather than loudly
   broken. This is a materially different (worse, because silent) failure mode
   than today's loader `ContractError`. **Required migration step: before the
   README states-graph edit lands, drain every item with
   `status: release` to `done` under the *old* graph** (approve its pending
   release content, run `merge guard --verdict passed|rejected` under
   0.27.0-pre8's current release-state flow) **and confirm
   `spacedock status --where status=release` returns empty** as a preflight
   gate on the graph-edit commit. Do not land the states edit and the drain in
   the same commit if any item is mid-release; drain first, edit second.
3. **Pinned-tag adopters (repositories consuming a released `kc-dev-flow`
   tag whose committed workflow README already contains a `release` state).**
   This is a compatibility event, not an internal refactor: (a) the new
   `kc-dev-flow` tag's `MIGRATION.md` gets a dated entry naming the ROUTES and
   README-template change; (b) each adopter repo must edit its own vendored
   `docs/dev/README.md` `states:` block to drop `release`, re-vendor
   `profile-contract-loader.py`/`kernel.md` (the byte-parity contract test in
   `scripts/kc-dev-flow-contract-test.py` already fails closed on drift
   between `kc-dev-flow/scripts/*` and `docs/dev/_mods/*`, so a partial
   re-vendor is caught, not silently accepted); (c) re-record every committed
   Production receipt per migration step 1; (d) run migration step 2's
   preflight drain before touching its own README. An adopter that does *not*
   upgrade keeps working exactly as today (the old graph, the old ROUTES, the
   same stranding risk this task exists to close) — this is opt-in per
   adopter at their next `kc-dev-flow` tag bump, not a forced break.
4. **Sibling coupling.** `spacedock-route-test-passes-nowhere`
   (`2nwpze64kkr5qeg6d8tm4g4p`, still `backlog`) owns
   `kc-dev-flow/scripts/profile-spacedock-route.test.py`, whose fixture models
   the *old* 6-state graph and force-sets `status=done` directly (bypassing
   `gate consume` — it does not exercise this defect at all, see Acceptance
   evidence). That sibling item's fix and this task's `build` stage land the
   same file; whichever lands second must rewrite the fixture to the 5-state
   graph and replace the forced `--set status=done` with the real
   `gate prepare` / `gate record --consume` / `merge guard` sequence used to
   produce this task's RED evidence below — the sibling's own casing fix
   (`verdict: PASSED`, confirmed uppercase in the Fixture B transcript) is
   subsumed by that rewrite rather than done twice. Record which item actually
   lands it once scheduling is known; do not let both touch it independently.
5. **This item's own migration sequencing.** This item (`8x38b1qryjrmy5w4ffk1egy1`)
   itself sat at `status: release` during its release gate's attempt-1
   resolution (superseded, see gate history above) — the exact graph state
   this change removes from `docs/dev/README.md`. Landing this diff and
   terminalizing this item are not automatically ordered: if the merge of
   this branch's README/ROUTES edit reaches a checkout while this entity's own
   state checkout still reads `status: release` (e.g. a stale local
   `.spacedock-state` clone, or a re-run of a prior stage), that copy hits
   exactly migration step 2's silent-non-dispatchable failure — no row, no
   NEXT, no error, reachable only via `--where status=release`. Required
   order: this item must reach `done` via `merge guard --verdict` under the
   *pre-change* graph (as this correction round's Finding B proves the
   mechanism does, using `poc-item`) before any `.spacedock-state` checkout
   that has pulled this branch's `docs/dev/README.md` change is treated as
   authoritative. This is a one-time bootstrapping concern for this item
   alone, not a recurring rule — ordinary future items never sit at `release`
   under the new graph because the state no longer exists to sit at.

## Reverse-recovery audit (`brownfield_capability_change`)

This task proposes removing an existing capability (the `release` graph state
and its dedicated stage contract), so the trigger fires.

```yaml
reverse_recovery:
  trigger: "remove the `release` runtime state and `profiles/production/release.md` stage contract; replace with terminal-approval + merge-guard content on `validation`"
  boundary: "kc-dev-flow profile routing — docs/dev/README.md stages graph, kc-dev-flow/scripts/profile-contract-loader.py ROUTES, kc-dev-flow/references/profiles/production/{verify,release}.md and their docs/dev/_mods vendored copies"
  layers:
    - surface: "`release` entry in docs/dev/README.md `stages.states` (and the kc-dev-flow adopter template it is vendored from)"
      location: "docs/dev/README.md stages.states; kc-dev-flow README template"
      completeness: WORKING
      need: NO_OBSERVED_CONSUMER
      evidence: "Functions exactly as declared (Fixture A: validation-approval consume lands there), but no consumer requires the authorization ruling to be a distinct *graph node* — Fixture B shows the same ruling reachable via the existing terminal-approval+merge-guard path with the state removed. Searched: profile-contract-loader.py ROUTES (only production references it), docs/dev/README.md prose (describes it, does not require it structurally), kernel.md (requires 'release owner retains release authority' as a ruling, not as a graph state)."
      disproof_hook: "Fixture B transcript below: 5-state graph, no `release` state, terminal ruling still recorded via `merge guard --verdict`"
    - surface: "`profiles/production/release.md` required-output content (rollback/forward-recovery readiness, operational owner, explicit authorization)"
      location: "kc-dev-flow/references/profiles/production/release.md; docs/dev/_mods/profiles/production/release.md"
      completeness: WORKING
      need: REQUIRED
      evidence: "README Gate ownership table: 'Production release | Captain or declared release owner'; kernel.md: 'Captain or the declared release owner retains release authority.' The content is a live consumer requirement; only its packaging as a separate graph-node contract is being removed."
      disproof_hook: "grep -n 'release owner' docs/dev/README.md ARCHITECTURE.md kc-dev-flow/references/kernel.md — all three cite the ruling, none cites the state"
    - surface: "ROUTES['production']['release'] entry in profile-contract-loader.py"
      location: "kc-dev-flow/scripts/profile-contract-loader.py:26-27 (ROUTES table)"
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: "Present, loads correctly, but its computed next_workflow_stage is never read by Spacedock's own gate consume (confirmed: consume advances by the README's declared graph order, not by this table) — this is the exact seam failure the task exists to close, evidenced by the production incident and Fixture A."
      disproof_hook: "Fixture A transcript below"
  decision: redesign
```

Removal authority: Captain, already granted in this item's approved scope
(work-profile receipt architecture obligation explicitly names collapsing the
`release` state as the accepted shape of a fix).

## Project-context impact

```yaml
project_context:
  impact: none
  authority: ARCHITECTURE.md
  claim_locator: "## kc-dev-flow profile-native loading"
  surface: "\"One superset Spacedock graph serves all three routes\" and \"Backlog and done are state boundaries rather than worker stages\" — neither sentence names `release` or any specific state count."
  stale_claim: none
  approved_change: none
  landed_change: none
  planned_check: "After the states-graph edit lands, re-read ARCHITECTURE.md `## kc-dev-flow profile-native loading` and confirm it still describes one shared graph with backlog/done as boundaries — true whether the graph has 5 or 6 states, so the edit changes no described claim. planned_check: `grep -n 'superset\\|state boundaries' ARCHITECTURE.md` returns the same two sentences, unedited."
  validation_evidence: pending
```

## Acceptance evidence

Both transcripts below are from throwaway `/tmp` fixtures run today against
the installed `spacedock 0.27.0-pre8` binary (`/Users/kent/.local/bin/spacedock`),
mirroring `docs/dev/README.md`'s state graph exactly. Nothing durable was
written to the repo; the check's durable home is `build`, likely folded into
(or replacing the fixture in) `kc-dev-flow/scripts/profile-spacedock-route.test.py`
per the sibling-coupling note above.

**RED today — Fixture A, current 6-state graph, `pilot-product-slice` entity,
real gate lifecycle (`gate prepare` → `gate record --decision approve
--consume` at backlog, then ideation, then `validation`; no forced `--set
status=done` anywhere):**

```
$ spacedock gate record pilot-item --workflow-dir /tmp/sd-route-probe --decision approve --actor person:captain --consume
recorded gate=gate:...:validation ... decision=approve
gate=gate:...:validation application=advance/consumed condition=approved-pending eligible=true consumed=true target-stage=release
$ grep '^status:' pilot-item.md
status: release
```

`pilot-product-slice`'s declared route is `[ideation, implementation,
validation]` (no `release`) — the entity is now at a stage outside its route,
reached by the ordinary gate-consume path, exactly reproducing the
`declared-receipts-need-a-reader` incident. This is the check named in the
completion checklist ("drive a Pilot item ... assert no gate record exists at
a stage outside their route"), shown failing on the current tree before any
fix.

**Candidate mechanism confirmed — Fixture B, 5-state graph (`release`
removed), `production` entity, same real gate lifecycle to `validation`:**

```
$ spacedock gate record prod-item --workflow-dir /tmp/sd-route-probe-fixed --decision approve --actor person:captain --consume
gate=gate:...:validation application=advance/pending condition=approved-pending eligible=true consumed=false target-stage=done route=approved-awaiting-merge
$ grep '^status:' prod-item.md
status: validation
$ spacedock merge guard prod-item --workflow-dir /tmp/sd-route-probe-fixed --verdict passed
finalized: prod-item -> done (verdict passed), archived.
$ cat _archive/prod-item.md | grep -E '^(status|verdict|completed):'
status: done
verdict: PASSED
completed: 2026-08-21T08:56:09Z
```

No stranding: the entity never sits at an excluded stage, and the release
ruling (`merge guard --verdict`) is a distinct, separately timestamped
decision from the validation gate's `resolution.decision: approve`.

**Contamination avoided:** the existing
`kc-dev-flow/scripts/profile-spacedock-route.test.py` was not reused as
evidence — it forces `--set status=done` directly, which bypasses `gate
consume` entirely and asserts nothing about this defect, and it hardcodes
lowercase `verdict: passed`, which 0.27.0-pre8 does not write (confirmed
`PASSED` above, matching the sibling item's independent finding).

## Measurement

Two checks are owed at `build`, both named in the committed work-profile
receipt's `testing` obligations and neither written durably yet (ideation's
deliverable is the decision and its evidence, not the script):

1. The RED check above, rewritten as a durable script (see sibling-coupling
   migration note): drive a POC and a Pilot item through the real gate
   lifecycle to `done` against the *post-fix* graph and assert no gate record
   exists at a stage outside their declared route. Must flip from red (today,
   demonstrated above) to green once the README/ROUTES change lands.
2. A check that fails when `profile-contract-loader.py`'s computed
   `next_workflow_stage` disagrees with the stage Spacedock's `gate consume`
   actually advances to — so the two cannot silently diverge again the way
   they did here. Candidate shape: for each profile/stage pair in ROUTES,
   assert the loader's `next_workflow_stage` equals the runtime's
   `target-stage` from a real `gate record --consume` run in a matching
   fixture (the same fixtures built for this stage's evidence, retained as the
   starting point).

### Landed at `build`, both RED-then-GREEN

**Corrected in correction round 1 (Finding B, downgraded from Codex's
[P1]).** As first written this section proved POC only up to the gate
target: `poc_target_validation == "done"` confirmed the loader's computed
target, and `sd_status(...) == "validation"` confirmed the entity parked at
the terminal-target-approval status — the same shape as Pilot's
pre-merge-guard assertions. But Pilot's block goes one step further and
Pilot's did not: it calls `spacedock merge guard pilot-item --verdict passed`
and asserts the result actually reaches `done`. POC stopped one step short, so
"a POC item can now reach done" was proven up to the gate target and no
further. Closed this round: `kc-dev-flow/scripts/profile-contract-loader.test.py`
now runs the identical `merge guard poc-item --workflow-dir ... --verdict
passed` call immediately after the existing POC assertions, requires
`returncode == 0`, and requires `"done" in stdout and "verdict passed" in
stdout` — the same two assertions already used for pilot-item, applied to
poc-item. Ran with a one-line temporary `print` on the captured stdout (added
and reverted; `git diff` on the test file shows only the two new `require()`
calls, no residual print) to confirm the actual CLI output, not just the
require passing:
`finalized: poc-item -> done (verdict passed), archived. State durability:
pushed to the split-root origin.` The full suite still reports
`profile contract loader test: route mechanism PASS` / `PASS` with this block
included — the mechanism is exercised, not asserted from the print alone.

Both checks above are now durable in
`kc-dev-flow/scripts/profile-contract-loader.test.py`'s "Live Spacedock route
mechanism" section (a real split-root Spacedock fixture, real `gate
prepare`/`gate record --consume`/`status --set`/`merge guard`, no forced
status writes) — check 1 is the POC+Pilot route-mechanism block, check 2 is
its `pilot_target_ideation == pilot_route["ideation"][1]` /
`pilot_target_validation == pilot_route["validation"][1]` /
`prod_target_validation == prod_route["validation"][1]` loader-vs-runtime
agreement assertions.

**RED, demonstrated against the pre-fix tree, not merely inferred.** I
extracted the landed check's own POC+Pilot logic into a standalone script,
pointed it at `git show HEAD:kc-dev-flow/scripts/profile-contract-loader.py`
(pre-fix `ROUTES`, `release` still present) and a 6-state
`WORKFLOW_STATES_BLOCK` matching the pre-fix `docs/dev/README.md` (`release`
added back between `validation` and `done`), and ran it — same helper
functions, same real CLI calls, only the fixture's graph and loader module
differ:

```
RED-DEMO FAIL (expected on pre-fix tree): POC validation did not terminalize at done: runtime=release
RED-DEMO FAIL (expected on pre-fix tree): POC validation-approval-consume should stay pending at validation (terminal-target approved-awaiting-merge)
RED-DEMO FAIL (expected on pre-fix tree): loader/runtime disagree at pilot validation (the exact divergence that stranded declared-receipts-need-a-reader): loader=done runtime=release
RED-DEMO FAIL (expected on pre-fix tree): pilot landed outside its declared route ['ideation', 'implementation', 'validation'] after validation-approval-consume: status='release' (this is the incident this task closes)
RED-DEMO FAIL (expected on pre-fix tree): pilot merge guard finalize failed: Error: merge guard: refusing to finalize pilot-item: entity carries no binding pending terminal-target approval (condition "ineligible")
RED-DEMO: 6 assertion(s) failed on the pre-fix tree, as expected
```

Both POC and Pilot strand at `status: release` on the pre-fix graph, matching
the severity table's row for POC (previously only inferred, not run) as well
as Pilot's already-observed incident. `merge guard` also confirms the
terminal-approval mechanism itself did not exist pre-fix (`refusing to
finalize ... no binding pending terminal-target approval`) — the mechanism is
new leverage this task adds, not something silently already there.

**GREEN, the same landed script, run unmodified against the current
(post-fix) worktree:**

```
$ python3 kc-dev-flow/scripts/profile-contract-loader.test.py
profile contract loader test: route mechanism PASS
profile contract loader test: PASS
```

**Full contract-test regression.** `python3 scripts/kc-dev-flow-contract-test.py`
passes every check except the pre-existing `profile-spacedock-route.test.py`
failure, confirmed (by running the identical command against the unmodified
base commit with this task's changes stashed) to reproduce identically
before this task touched anything — owned by sibling item
`spacedock-route-test-passes-nowhere`, not fixed here per the sibling-coupling
migration note. Every other assertion, including the two new
`kc-dev-flow/README.md` / `continue-dev-flow/SKILL.md` route-string checks
added this stage, passes; each new check was mutation-tested by reverting its
one target file to pre-fix content in isolation and confirming it — and only
it — fails.

## Stage Report: ideation

- DONE: Select ONE direction and record why the other was rejected.
  Selected Direction 1 (demote `release` from a graph state to a
  terminal-approval boundary); Direction 2 rejected by citing the receipt's
  own architecture obligation, not just cost tradeoffs — see "Accepted
  outcome and non-goals".
- DONE: Acceptance evidence names a check RED on the current tree, shown failing today.
  Ran the real `spacedock gate prepare`/`gate record --consume` lifecycle
  (no forced `--set status=done`) against a `/tmp` fixture mirroring
  `docs/dev/README.md`'s graph; a `pilot-product-slice` entity's validation
  approval lands at `status: release`, outside its declared route — transcript
  in "Acceptance evidence". Also empirically confirmed the candidate
  mechanism (Fixture B: terminal-target approval + `merge guard --verdict`
  gives a second, separately timestamped ruling with no `release` state).
- DONE: Name the adopter migration concretely, including in-flight items and pinned-tag adopters.
  Four numbered steps in "Adopter migration": stale-receipt re-record (this
  item's own receipt included), in-flight `status: release` drain preflight
  (verified `--validate` does not flag it and `--boot` silently drops it from
  the dispatchable table — a worse, quieter failure than today's loader
  error), pinned-tag adopter upgrade path (opt-in per tag bump, byte-parity
  contract test catches partial re-vendor), and the sibling-item coupling
  disposition for `spacedock-route-test-passes-nowhere`.

### Summary

Selected Direction 1: drop `release` as a Spacedock graph state and fold its
required-output content into `verify.md` for Production only, relying on
Spacedock 0.27.0-pre8's existing terminal-approval + `merge guard` mechanism
(confirmed empirically, not assumed) to keep verification and release as two
separately rendered rulings. Direction 2 is rejected against the receipt's own
obligation. Reverse-recovery and project-context receipts recorded per shape
trigger; multi-slice guard does not fire (single decision, not two slices).

### Dispatch Retries

- Retry 1: implementation — agent-error (API ENOTFOUND, session terminated mid-run with no completion signal and no stage report); re-dispatched -retry. The prior worker's 15 uncommitted worktree changes were reviewed by the FO before the re-attempt and left in place: all fifteen are within the accepted outcome or a necessary consequence of it, including five route-table copies the accepted outcome's file list omitted. A patch backup is at `.context/recovery/8x38b1q-implementation-attempt1.patch`. Nothing in them is verified — the worker died before writing any report.

## Stage Report: implementation

- DONE: Verify every inherited hunk against the accepted outcome; reject or repair anything unjustified.
  Reviewed all 15 uncommitted hunks (`docs/dev/README.md`, `docs/dev/_mods/kernel.md`,
  `docs/dev/_mods/profile-contract-loader.py`, deleted `docs/dev/_mods/profiles/production/release.md`,
  `docs/dev/_mods/profiles/production/verify.md`, `kc-dev-flow/MIGRATION.md`, `kc-dev-flow/README.md`,
  `kc-dev-flow/references/kernel.md`, deleted `kc-dev-flow/references/profiles/production/release.md`,
  `kc-dev-flow/references/profiles/production/verify.md`,
  `kc-dev-flow/scripts/profile-contract-loader.py`, `kc-dev-flow/scripts/profile-contract-loader.test.py`,
  `kc-dev-flow/skills/choose-work-profile/SKILL.md`, `kc-dev-flow/skills/continue-dev-flow/SKILL.md`,
  `scripts/kc-dev-flow-contract-test.py`) one file at a time against `## Accepted outcome and
  non-goals`. All 15 accepted unmodified; each matches the mechanism (terminal-target approval +
  `merge guard`), the four-bullet content move into `verify.md`, or the route-table edit. No hunk
  rejected. Correctness confirmed empirically, not by re-reading: ran the already-landed
  `profile-contract-loader.test.py` (route-mechanism PASS, both loader copies byte-identical) and
  the full `scripts/kc-dev-flow-contract-test.py` (passes except the pre-existing sibling-owned
  failure, see below) before adding anything of my own. Commit 3ad3725a.
- DONE: Correct the accepted outcome's route-string copy count and name every copy actually changed; state whether anything checks the six agree.
  Rewrote `## Accepted outcome and non-goals`'s "Landed change, concretely" to enumerate all six
  (kernel.md pair, `kc-dev-flow/README.md`, `choose-work-profile/SKILL.md`, `continue-dev-flow/SKILL.md`,
  `ROUTES["production"]`, `docs/dev/README.md`'s stages block) instead of the two the prior draft
  named. Audited which have an enforcement point: four already did (kernel.md/loader byte-parity
  pairs, `choose-work-profile`/`docs/dev/README.md` phrase pairs); two did not
  (`kc-dev-flow/README.md`, `continue-dev-flow/SKILL.md`) and were fixed by hand with nothing to
  catch future drift. Added a positive+negative `require()` pair for each of those two to
  `scripts/kc-dev-flow-contract-test.py`, then mutation-tested each in isolation (reverted one file
  to pre-fix content, confirmed only that file's new check fails) — both fire correctly. Commit 3ad3725a.
- DONE: Answer the release-authorization residual with a mechanism or recorded gate content, not a sentence in a contract.
  Probed `spacedock gate record --actor` and `merge guard --help` directly (not from docs): only
  `person:captain` is an accepted decision actor (`unsupported chat decision actor` for every other
  value tried), `merge guard` takes no `--actor` at all, and no gate command validates `--artifact`
  content. These are pre-existing 0.27.0-pre8 constraints, unchanged in either direction by this
  task — "declared release owner" was never actor-enforced even at the old dedicated `release`
  stage. The real, verified mechanism is the refusal: `merge guard --verdict passed` is refused
  with no pending terminal-target approval (reproduced live, see RED-demo transcript below). Wrote
  a new "Release-authorization residual" subsection distinguishing what's genuinely new leverage
  (the refusal), what's unchanged strength (actor and content enforcement), and the one honest
  residual this collapse costs (a second ceremony's own dedicated review artifact no longer exists;
  `verify.md`'s Required output is the available, in-scope answer given the tool has no
  content-validated second ceremony) — not silently closed, flagged for the FO to accept or follow
  up on.
- DONE: Land the RED check durably; show it RED on the pre-fix tree and GREEN after, both outputs in the stage report.
  Durable script already landed in inherited work
  (`kc-dev-flow/scripts/profile-contract-loader.test.py`'s "Live Spacedock route mechanism"
  section, ~250 lines, real split-root fixture, real `gate prepare`/`gate record --consume`/
  `merge guard`, no forced status writes) — I verified rather than re-authored it. GREEN: `python3
  kc-dev-flow/scripts/profile-contract-loader.test.py` on the current worktree prints
  `profile contract loader test: route mechanism PASS` / `... PASS`. RED: extracted the same
  script's POC+Pilot logic standalone, pointed it at the pre-fix loader
  (`git show HEAD:kc-dev-flow/scripts/profile-contract-loader.py`, `release` present) and a 6-state
  `WORKFLOW_STATES_BLOCK` matching pre-fix `docs/dev/README.md`, ran it:
  `POC validation did not terminalize at done: runtime=release`,
  `pilot landed outside its declared route ['ideation','implementation','validation'] ... status='release'`,
  `merge guard: refusing to finalize pilot-item: entity carries no binding pending terminal-target
  approval` — 6 assertions fail, matching the severity table for both POC and Pilot (POC's failure
  was previously only inferred from the table, not run). Full transcripts in `## Measurement` ->
  "Landed at `build`, both RED-then-GREEN".
- DONE: Keep the two loader copies byte-identical.
  `diff kc-dev-flow/references/kernel.md docs/dev/_mods/kernel.md` and
  `diff kc-dev-flow/scripts/profile-contract-loader.py docs/dev/_mods/profile-contract-loader.py`
  both report no difference after my edits; `scripts/kc-dev-flow-contract-test.py` also
  byte-compares both pairs and passes.
- DONE: Decide deliberately whether kernel.md's runtime-may-skip clause stays, is bounded, or goes; record the reasoning.
  Decision: bounded, not removed or left untouched. POC's `ideation` skip (confirmed:
  `ROUTES["poc-exploration"]` has no `ideation` key) is the sole surviving referent and is a real,
  Captain-accepted design, so the clause cannot go. Added one sentence to both kernel.md copies
  naming the invariant this incident exposed: a skip is safe only when the skipped stage carries no
  authorization checkpoint a later stage does not also carry; a stage gating the route's sole
  terminal-authorization checkpoint is not a candidate for the clause and must fold into an adjacent
  stage's contract instead (cross-referencing Production's own route row as the worked example).
  Reasoning recorded in a new "The remaining skip clause: bounded, not removed" subsection. Commit 3ad3725a.

### Summary

Verified and committed all 15 inherited hunks (commit 3ad3725a) after confirming each against the
accepted outcome by running the tests, not re-reading notes. Closed three gaps the FO flagged as
unaddressed: named and enforced all six route-string copies (two previously had no check; both now
do, mutation-tested), answered the release-authorization residual with empirically-probed tool
constraints instead of assumption (found the real mechanism, and named the one genuine, unclosed
residual rather than papering over it), and bounded kernel.md's skip clause with the invariant this
incident exposed. RED reproduced live on the pre-fix tree using the landed check's own logic (both
POC and Pilot strand at `status: release`); GREEN confirmed on the post-fix tree unmodified. Full
contract test passes except the pre-existing, sibling-owned `profile-spacedock-route.test.py`
failure, confirmed to reproduce identically on the unmodified base commit — not this task's
regression, not fixed here.

## Stage Report: validation

- DONE: Reproduce the RED-then-GREEN yourself rather than reading the implementer's report: run the durable check's logic against the pre-fix tree (merge-base b8ff74ec) and show BOTH a POC item and a Pilot item stranding outside their route, then show it green on HEAD.
  Wrote an independent standalone script (not copied from the implementer's transcript) importing `git show b8ff74ec:kc-dev-flow/scripts/profile-contract-loader.py` (pre-fix `ROUTES`, `release` present) against a 6-state `WORKFLOW_STATES_BLOCK`, and ran the same POC+Pilot gate-lifecycle logic the landed test uses. RED, independently reproduced: `POC validation did not terminalize at done: runtime=release`, `POC validation-approval-consume should stay pending...`, `loader/runtime disagree at pilot validation: loader=done runtime=release`, `pilot landed outside its declared route [...] status='release'`, `pilot merge guard finalize failed: ... no binding pending terminal-target approval` — 5 assertions failed, both POC and Pilot strand at `status: release`. GREEN, independently reproduced on HEAD: `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` → `profile contract loader test: route mechanism PASS` / `... PASS`. One discrepancy found: the implementer's own RED transcript in "Landed at `build`" prints 5 distinct FAIL lines but its own summary line claims `6 assertion(s) failed` — my independent script's failure count (5) matches the number of printed FAIL lines exactly; the implementer's `6` is an off-by-one in their own counting, not evidence of a missing assertion (the same 5 failure conditions are the ones that matter and both items strand, which is what the checklist asked to prove).
- DONE: Prove the new route-parity require() checks DISCRIMINATE: for each copy they guard, mutate that copy back to the old `-> release` string and show the specific check going red, then revert.
  Mutated each of the six copies named in "Landed change, concretely" one at a time (working-tree edit, ran `scripts/kc-dev-flow-contract-test.py`, confirmed the exact expected failure, reverted via backup, confirmed `git status --porcelain` clean before the next mutation): (1) `kc-dev-flow/references/kernel.md` → `self-adopted shared core differs from package source`; (2) `docs/dev/_mods/kernel.md` → same byte-parity message; (3) `kc-dev-flow/README.md` → `package README route table omits the current Production route`; (4) `kc-dev-flow/skills/choose-work-profile/SKILL.md` → `chooser is missing: ...The scope accepts a production boundary` (caught by the adjacent positive-phrase require, not the negative one — still red, still discriminates); (5) `kc-dev-flow/skills/continue-dev-flow/SKILL.md` → `continuation route table omits the current Production route`; (6) `docs/dev/README.md` states block → `workflow stage graph drifted: [..., 'release', 'done']`. `kc-dev-flow/scripts/profile-contract-loader.py`'s `ROUTES["production"]` was additionally mutated on its own (not counted as a 7th copy — it is the code half of copy pair 5's underlying mechanism, checked twice: by `profile-contract-loader.test.py`'s own `expected_routes` content check, `route topology drifted`, reached before the byte-parity check in file order; and its `docs/dev/_mods/` vendored twin independently, `self-adopted profile loader differs from package source`). Because the `profile-spacedock-route.test.py` casing bug fails first and aborts the fail-fast orchestrator before reaching later checks, most of these mutations required a temporary, fully-reverted comment-out of that one `run()` call to reach the check under test — reverted immediately after each mutation's read, confirmed via `git diff --stat` returning empty before moving on. All 6 of the 6 named copies have a check that was seen to fail on that exact mutation and pass again after revert; none is unverified.
- DONE: Confirm the release-authorization answer is honestly bounded, not overclaimed: verify the empirical findings behind it and confirm the entity states the loss of a dedicated second review ceremony as a live residual rather than as closed.
  Independently reproduced all three empirical claims against a fresh throwaway fixture (not reusing the implementer's fixture or trusting their transcript): `spacedock gate record --actor` refuses every value tried except `person:captain` — tested `person:kent`, `team:release-owner`, `release-owner`, `agent:captain`, `captain`, all five refused with `unsupported chat decision actor "<value>"`, `person:captain` alone succeeds; `spacedock merge guard --help` confirms no `--actor` flag exists at all (only `--verdict`, `--rework`, `--workflow-dir`, `--json`, `--quiet`); `gate prepare` accepts an artifact whose content is unrelated junk text (`"totally unrelated junk content, not a review at all..."`) as long as it is the exact committed `.md` file — no content validation against a stage's Required-output list. All three match the entity's claims exactly. Confirmed the entity's own "Release-authorization residual" subsection explicitly labels the lost second-ceremony artifact a "genuine residual, correctly scoped as a residual, not silently closed" and defers the acceptance decision to the FO/Captain rather than declaring it solved — the claim is bounded, not overclaimed.
- DONE: Confirm the contract test's ONLY failure is the pre-existing profile-spacedock-route casing bug and not a new route failure: its output must show the item reaching `status: done` with the assertion failing solely on `verdict: PASSED` vs lowercase, and the same failure must reproduce on the unmodified merge-base. Note that this branch is behind origin/main (534a148a); flag it for release, do not rebase here.
  Ran `python3 scripts/kc-dev-flow-contract-test.py` on HEAD: exit 1, single failure `poc-exploration did not terminalize directly`, entity body shows `status: done` / `verdict: PASSED` / `completed: ...` — the assertion (`kc-dev-flow/scripts/profile-spacedock-route.test.py` line 93, `"verdict: passed" in updated`) fails solely on casing against the actually-written uppercase `PASSED`. Confirmed identical on the unmodified merge-base: extracted `git show b8ff74ec:kc-dev-flow/scripts/profile-spacedock-route.test.py` and ran it standalone — same message, same `status: done` / `verdict: PASSED` shape, exit 1. Confirmed no OTHER failure is hiding behind this fail-fast script: temporarily commented out (then fully reverted) the one `run()` call for this sibling-owned check in `scripts/kc-dev-flow-contract-test.py` and re-ran the full suite — `kc-dev-flow contract: PASS`, exit 0, covering the remaining ~60% of the file (everything after line 269) that the fail-fast ordering otherwise hides. `git diff --stat` empty before and after. Branch state: `git rev-list --count HEAD..origin/main` = 1, `origin/main` at `534a148a`; `HEAD..origin/main` and `origin/main..HEAD` are each exactly 1 commit (this task's single commit `3ad3725a` sits directly on merge-base `b8ff74ec`). Not rebased, per instruction; flagged here for the FO to handle at release.

### Summary

Independently reproduced every piece of evidence the implementer claimed rather than trusting the transcript: RED (both POC and Pilot stranding at `status: release` on the pre-fix tree, from a self-written script against the pre-fix loader module) and GREEN (unmodified landed test, PASS) for the route mechanism; all 6 named route-string copies individually mutated and reverted, each showing its own check go red on exactly that mutation and clean afterward; the three release-authorization tool constraints re-probed from a fresh fixture, matching the entity's claims, with the entity's own "not silently closed" residual framing confirmed accurate rather than overclaimed; and the contract-test's sole failure isolated to the pre-existing `profile-spacedock-route.test.py` casing bug, reproduced identically on the unmodified merge-base, with the rest of the fail-fast suite exercised via a fully-reverted temporary skip to prove no other failure hides behind it. One minor, non-blocking finding: the implementer's own RED transcript undercounts its printed FAIL lines by one in its summary line (says 6, prints 5) — does not change which assertions fired or what they prove. Branch is 1 commit behind `origin/main` (`534a148a`); not rebased here, flagged for the FO to handle at release per instruction.

## Stage Report: release

- DONE: Rebase the single commit onto current origin/main with `git rebase --onto origin/main b8ff74ec`.
  Checked first: `git log --oneline origin/main..HEAD` showed exactly one commit (3ad3725a), so the plain form was safe; used the explicit `--onto` form as instructed. Rebase succeeded cleanly (no conflicts), producing `b3b0e2ed` on top of `origin/main` at `534a148a`. `git rev-list --count origin/main..HEAD` = 1 after rebase.
- DONE: Re-run `kc-dev-flow/scripts/profile-contract-loader.test.py` and `scripts/kc-dev-flow-contract-test.py` ON THE REBASED REVISION and paste both outcomes.
  On `b3b0e2ed`: `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` -> `profile contract loader test: route mechanism PASS` / `... PASS`, exit 0. `python3 scripts/kc-dev-flow-contract-test.py` -> exit 1, sole failure `poc-exploration did not terminalize directly` (the pre-existing `profile-spacedock-route.test.py` casing bug: asserts lowercase `verdict: passed`, tool writes uppercase `PASSED`). Confirmed nothing else hides behind the fail-fast ordering: temporarily disabled that one `run()` call (backed up, restored immediately after), re-ran -> `kc-dev-flow contract: PASS`, exit 0; `git status --porcelain` empty before and after the temporary edit.
- DONE: Record the delivery-base reason with the evidence you actually checked, per references/delivery-branch-base.md.
  Listed 10 open PRs (`gh pr list --state open`) and compared file lists against this commit's `git show --stat HEAD`. Found real file overlap: `kernel.md` (both copies) and `choose-work-profile/SKILL.md` are also touched by a 4-deep open stack (#267->#271->#272->#275), and `profile-spacedock-route.test.py` is touched by #268 and #272. Compared actual diff hunks (`gh pr diff <n>` vs `git show HEAD -- <file>`): overlap is textual adjacency (#267 inserts new content immediately after the sentence this commit rewrites) and disjoint-hunk sharing, not lineage — this commit was authored and both tests run against plain `origin/main` with zero content from any open PR, and re-delivers none of their diff. Applied the reference's actual test ("builds on, depends on, or would otherwise re-deliver") rather than the file-overlap heuristic alone; targeted `main`, not stacked, and named the finding plus the small mechanical-conflict consequence in the PR body rather than asserting unsupported independence. Consulted advisor before committing to this call given it was consequential and hard to reverse.
- DONE: Open a Draft PR to main whose body carries all required content.
  https://github.com/iamcxa/kc-claude-plugins/pull/276 (`gh pr view 276` confirms `isDraft: true`, `baseRefName: main`, `headRefName: spacedock-ensign/profile-routes-are-graph-differences`). Body carries: the six route-string copies with each check's mutation-fail message; the release-authorization residual as a live residual with the three probe results (actor refusal, no merge-guard --actor flag, no artifact-content validation); the adopter migration including the in-flight `status: release` check (only this task's own entity, confirmed via `grep -rn '^status:' docs/dev/.spacedock-state`); the CI-reachable/locally-blocked coupling tracked as `spacedock-route-test-passes-nowhere`; and the delivery-base record above. No version bump, no marketplace edit. Not marked ready.

### Summary

Rebased the single commit onto current origin/main (`b3b0e2ed`), re-verified both owed checks pass on the rebased revision with the pre-existing sibling casing failure isolated and confirmed non-hiding. Found genuine file overlap with a 4-deep open PR stack on `kernel.md`/`choose-work-profile/SKILL.md`, evaluated it against the delivery-base reference's actual lineage test rather than a bare shared-file check, and targeted `main` with the overlap and reasoning recorded in the PR body for the FO/Captain to confirm or override. Opened Draft PR #276 with all four required content elements plus the delivery-base record; left unready pending review.

## Stage Report: implementation (cycle 2)

- DONE: Finding A closed — the kernel route row gains a CONTENT check, proven by repeating the FO's exact mutation and reverting; entity's own six-copy claim corrected.
  Added `require("| \`production\` | \`shape -> build -> verify\` |" in kernel, "kernel route table omits the current Production route")` to `scripts/kc-dev-flow-contract-test.py`, right after the existing subtraction-rule loop that already reads the `kernel` variable. Reproduced the FO's exact mutation (edited both `kc-dev-flow/references/kernel.md` and `docs/dev/_mods/kernel.md` to `` | `production` | `shape -> build -> verify -> deploy` | ``, keeping the two byte-identical, confirmed via `diff`): `python3 scripts/kc-dev-flow-contract-test.py` -> `kc-dev-flow contract: kernel route table omits the current Production route`, exit 1. Reverted both files from backups, confirmed `git status --porcelain -- kc-dev-flow/references/kernel.md docs/dev/_mods/kernel.md` empty, re-ran -> `kc-dev-flow contract: PASS`, exit 0. Rewrote the entity's "Does anything check that the six agree?" paragraph and the kernel.md line of "Landed change, concretely" to state the corrected count: all 6 of 6 named copies now carry a content check seen to fail on its own mutation (`profile-contract-loader.py`'s already did, via `expected_routes` structural equality — not a byte-parity-only gap; kernel.md's pair is the one that changed, gaining a new check on top of its pre-existing byte-parity check); none rests on byte-parity alone.
- DONE: Finding B closed — `poc-item` driven to terminal through `merge guard --verdict passed` exactly as `pilot-item`, asserted to reach `done`.
  Added a `merge guard poc-item --workflow-dir ... --verdict passed` call to `kc-dev-flow/scripts/profile-contract-loader.test.py` immediately after POC's existing validation-target assertions, with the same two `require()`s already used for pilot-item (`returncode == 0`; `"done" in stdout and "verdict passed" in stdout`). `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` -> `profile contract loader test: route mechanism PASS` / `PASS`, exit 0 (not SKIP — the real `spacedock` binary ran). Captured the actual CLI output via a one-line temporary `print` (added, run once, reverted; `git diff` on the test file now shows only the two new `require()` calls): `finalized: poc-item -> done (verdict passed), archived. State durability: pushed to the split-root origin.` Corrected the "Landed at `build`, both RED-then-GREEN" section to record that POC previously stopped at the gate target and now terminalizes identically to Pilot.
- DONE: Finding C closed — for every file this branch and the landed stack both touched, read the merged result and confirm the stack's new backlog/ideation semantics survive intact.
  Computed the exact intersection mechanically rather than trusting memory: `comm -12 <(git diff --name-only ef808a91 7bbae216 | sort) <(git diff --name-only a15ab033^ ef808a91 | sort)` (`a15ab033^` is the parent of #267, the stack's first commit; `ef808a91` is #272, the stack's tip and this branch's own base) returned exactly three files, matching the entity's own prior claim with no additions: `docs/dev/_mods/kernel.md`, `kc-dev-flow/references/kernel.md`, `kc-dev-flow/skills/choose-work-profile/SKILL.md`. Compared each: (1) `kernel.md` (both copies, byte-identical) — read the merged region lines 38-100; the stack's `backlog` exit bar paragraph ("Queue state still has an exit bar...") and its `## Shared boundaries` additions (the size-threshold bullet from #272, the two scaffolding/removal-condition bullets from #271) are all present verbatim and immediately adjacent to this branch's edits (the route table row and the skip-clause caveat sentence); the two topics don't reference or contradict each other — the skip clause bounds which *stages* may be silently skipped, the exit bar governs leaving `backlog`, a queue state neither side's edit touches. (2) `choose-work-profile/SKILL.md` — read lines 18-55; the stack's new paragraph ("Check the shared core's `backlog` exit bar in the same read...") sits between this branch's corrected route table row (line 25, `shape -> build -> verify`, no longer `-> release`) and the pre-existing POC-downscope paragraph, reads coherently, and its "leave `backlog`" language is unaffected by whether Production's *working* route still has a `release` element. No third file in common; the stack's other touched files (`journey-slicing.md`, `pilot-product-slice/build.md`, `pilot-product-slice/shape.md`, `poc-exploration/base.md`, `production/build.md`, `production/shape.md`, `profile-spacedock-route.test.py`) are disjoint from this branch's diff.
- DONE: Record without fixing — CI-skip of this fix's own proof added as a second victim to `spacedock-route-test-passes-nowhere`'s body; migration sequencing note added to this entity.
  Appended a paragraph to `docs/dev/.spacedock-state/spacedock-route-test-passes-nowhere.md`'s Problem section naming `profile-contract-loader.test.py`'s "Live Spacedock route mechanism" section as a second victim of the same CI-skip (`shutil.which("spacedock")` finds nothing in `marketplace-parity.yml`) and the same local block (the fail-fast abort at the casing bug), now resolved locally by #268 but still CI-blind — did not touch that entity's frontmatter or otherwise change its `status: backlog`. Added an "Adopter migration" step 5 to this entity naming the sequencing hazard: this item itself sat at `status: release` during its own release-gate attempt-1 (superseded), the exact state this change removes, so a `.spacedock-state` checkout that has pulled this branch's README/ROUTES edit while still reading this entity at `status: release` hits migration step 2's silent-non-dispatchable failure; required order is this item reaching `done` via `merge guard` before such a checkout is treated as authoritative.
- SKIPPED: Reopening release-authorization prose or the unenforceable skip caveat.
  Both were explicitly named "closed — do not reopen" in the correction round instructions; left untouched.

### Summary

Closed Findings A, B, and C from correction round 1. A: added a content check on the kernel.md production route row (the entity's kernel.md pair previously rested on byte-parity alone, which cannot catch an identical corruption of both copies), reproduced the FO's exact both-copies mutation going red and reverting clean, and corrected the entity's overclaimed "all six agree" paragraph. B: drove `poc-item` through `merge guard --verdict passed` to `done` in the same landed test block that already does this for `pilot-item`, with the real CLI output captured as evidence. C: mechanically recomputed the file intersection between this branch and the #267/#268/#269/#271/#272 stack (three files, matching the entity's prior claim), and read each merged region to confirm the stack's backlog-exit-bar and shared-boundaries additions survive intact and don't contradict this branch's route-table and skip-clause wording. Recorded the CI-skip's second victim in the sibling entity and the one-time migration-sequencing hazard in this entity, without fixing either. Did not touch the standing constraints (`profile-contract-loader.py` byte-parity, no rebase, no version bump).

## Stage Report: validation (cycle 2)

- DONE: Independently reproduce the kernel-route content-check discrimination by mutating BOTH kernel copies to `shape -> build -> verify -> deploy` and showing the suite fail with the new kernel-route message; revert and confirm clean.
  `kc-dev-flow/references/kernel.md` and `docs/dev/_mods/kernel.md` edited identically via `sed`; `python3 scripts/kc-dev-flow-contract-test.py` → `kc-dev-flow contract: kernel route table omits the current Production route`, exit 1 (not the parity check — that check compares `profile-contract-loader.py`, a separate pair). `git checkout --` reverted both files; `git status --porcelain` empty; re-run → `PASS`, exit 0. This is the exact hole correction round 1 named: the prior validation round mutated one copy at a time and only ever exercised byte-parity, never this content check.
- DONE: Confirm `poc-item` actually terminalizes through `merge guard --verdict passed` in the live fixture, quoting the `finalized: poc-item -> done` line.
  Ran `kc-dev-flow/scripts/profile-contract-loader.test.py` live (real `spacedock` binary resolved, not SKIP) with a one-line temporary `print` on `poc_finalize.stdout` (added, run once, reverted; `git diff` empty after). Captured: `finalized: poc-item -> done (verdict passed), archived. State durability: pushed to the split-root origin.` Suite reports `route mechanism PASS` / `PASS`.
- DONE: Recompute the file intersection between this branch and the landed stack (#267/#268/#269/#271/#272) independently and confirm it matches the implementer's named set.
  `git diff --name-only ef808a91..HEAD` (this branch's own two commits, isolated by the rebase boundary) vs `git diff --name-only a15ab033^..ef808a91` (the full #267–#272 stack range), intersected with `comm -12`: exactly `docs/dev/_mods/kernel.md`, `kc-dev-flow/references/kernel.md`, `kc-dev-flow/skills/choose-work-profile/SKILL.md` — three files, matching the entity's claim, not larger.
- DONE: Read each merged region and confirm the stack's backlog-exit-bar and shape/journey additions survive intact and uncontradicted.
  `kernel.md`: stack's "Queue state still has an exit bar" block (What-it-is/Why-it's-worth-doing, Captain-checks-on-every-exit) and the size-threshold/scaffolding-removal-condition bullets read intact at their post-rebase location, directly following this branch's route-table edit and new skip-clause caveat — no truncation, no contradiction (caveat narrows when the skip clause applies; exit bar is untouched prose). `choose-work-profile/SKILL.md`: stack's "Check the shared core's `backlog` exit bar in the same read" paragraph and the `NEEDS_PROFILE_DECISION`-names-the-missing-fact sentence are present unchanged; this branch's own edit is a single route-table cell (`-> release` dropped), several lines away.
- DONE: Confirm the entity's own six-copy claim is corrected to state how many copies rest on a content check vs byte-parity alone.
  Entity body (§"Does anything check that the six agree?") now reads: "Every one of the six now rests on a content check seen to fail on its own mutation; none rests on byte-parity alone" — matches what this round independently reproduced for the kernel.md pair, the one copy that changed.
- DONE: Confirm the CI-skip second-victim note landed in `spacedock-route-test-passes-nowhere`'s body.
  Read `docs/dev/.spacedock-state/spacedock-route-test-passes-nowhere.md` directly: a "Second victim, added by `profile-routes-are-graph-differences`" paragraph is present under `## Problem`, naming the same `profile-contract-loader.test.py` live-mechanism section, the same CI skip, and the same now-locally-resolved casing block. `status: backlog` untouched.
- DONE: Confirm the migration-sequencing note landed in this entity.
  §"Adopter migration" step 5, "This item's own migration sequencing," present and states the required order: this item must reach `done` via `merge guard --verdict` under the pre-change graph before any checkout that pulled the README/ROUTES edit is treated as authoritative.
- DONE: Confirm both suites are green and the tree is clean on the final state.
  `git status --porcelain` empty; `python3 scripts/kc-dev-flow-contract-test.py` → `PASS`, exit 0; `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` → `route mechanism PASS` / `PASS`, exit 0. HEAD unchanged at `d775a02f`, base `origin/main@ef808a91`, PR #276 still open. Not rebased.

### Summary

Independently reproduced (not re-read) all three correction-round findings this cycle owed proof for: the kernel-route content-check catches the FO's exact both-copies-identical mutation and reverts clean; `poc-item` terminalizes through `merge guard` with the actual CLI line captured; and the branch/stack file intersection was recomputed from git history rather than trusted, landing on the same three files the entity claims, with each merged region read and confirmed uncontradicted. The entity's six-copy claim, the sibling's second-victim note, and this entity's own migration-sequencing note were all verified present and accurate, not just asserted. No code changes; validation only.
