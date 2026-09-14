---
title: "Retire the provider-backed planning path, so dev-flow's only intake is a committed brief"
status: validation
source: Captain ruling 2026-09-14 in FO session
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: kc-dev-flow/S10
sprint-readiness: ready
started: 2026-09-14T08:25:39Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-retire-the-provider-backed-planning-path
issue:
pr:
mod-block:
id: f0m9yytzq7sczkam7rrq9ym3
gates:
    version: 1
    records:
        - id: gate:f0m9yytzq7sczkam7rrq9ym3:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:f0m9yytzq7sczkam7rrq9ym3-backlog-1
              briefing:
                id: briefing:f0m9yytzq7sczkam7rrq9ym3:backlog:attempt-1:revision-1
                digest: sha256:928bbdba36ae552ea731cc789b8ee494aca34d2538d925fb82d9fa56ecfdcf06
                room-ref: ./retire-the-provider-backed-planning-path/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:f0m9yytzq7sczkam7rrq9ym3:backlog:1
                briefing: briefing:f0m9yytzq7sczkam7rrq9ym3:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-14T08:24:57.489062Z"
                decision: approve
                reason: Captain said 開工 for this entity in the session, after selecting Pilot and the S10 grouping; the seed carries the Development Brief, AC-1..AC-5 and the v3 Pilot receipt.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:f0m9yytzq7sczkam7rrq9ym3:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:f0m9yytzq7sczkam7rrq9ym3-ideation-1
              briefing:
                id: briefing:f0m9yytzq7sczkam7rrq9ym3:ideation:attempt-1:revision-1
                digest: sha256:fabab197a41ee5c162c1e6f7ad6bb1d400dfad638abb94afb525bcc6dcf97ee5
                room-ref: ./retire-the-provider-backed-planning-path/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:f0m9yytzq7sczkam7rrq9ym3:ideation:1
                briefing: briefing:f0m9yytzq7sczkam7rrq9ym3:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-14T08:37:55.194949Z"
                decision: approve
                reason: 'Captain approved the ideation shape and took the recommended disposition of both residuals. Residual 1: move live_item and delivery_binding into docs/plan-flow before deleting linear-admission.py, so plan-lint.py''s L4 rule carries its own logic instead of reaching back into kc-dev-flow; AC-2 is read with that move as its precondition, not as a carve-out. Residual 2: the leave-delivery-untouched non-goal wins — the provider-backed delivery clauses in pr-delivery.md and pr-merge-extension.md stay, and AC-3 is read as scoped to intake, not delivery.'
              application:
                target-stage: implementation
                state: consumed
        - id: gate:f0m9yytzq7sczkam7rrq9ym3:validation
          stage: validation
          attempts:
            - id: gate-attempt:f0m9yytzq7sczkam7rrq9ym3-validation-1
              briefing:
                id: briefing:f0m9yytzq7sczkam7rrq9ym3:validation:attempt-1:revision-1
                digest: sha256:f260af715e173c411d22838065a2ed55a88fa63fb214ab0643e72cd76413ad73
                room-ref: ./retire-the-provider-backed-planning-path/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:f0m9yytzq7sczkam7rrq9ym3:validation:1
                briefing: briefing:f0m9yytzq7sczkam7rrq9ym3:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-14T10:06:03.347894Z"
                decision: approve
                reason: 'Captain approved at the validation gate. A fresh reviewer re-ran all five suites at candidate 95b19de0 in an independently resolved checkout, both ideation-gate dispositions were verified with direct evidence, and AC-1/AC-5 were re-proven against dev-52''s real committed bytes. AC-2 and AC-4 carry implementation-stage evidence plus an FO direct read. Disclosed limit: the branch is a single squashed commit, so the L4-never-raised claim holds at the two real git endpoints only.'
              application:
                target-stage: done
                state: superseded
---

## The problem

kc-dev-flow carries two intake paths. A standalone item runs on a Captain-approved committed
brief. A provider-backed item additionally records a complete Planning Receipt
(`source`, `planning-window`, `planning-outcome`), and dev-flow then owns machinery to keep that
receipt honest: `linear-admission.py`, `engage-reconcile.py`, the engage-reconcile comparison at
every provider-backed engage, and the partial-tuple refusal. Both scripts are declared resources
in `contract-manifest.json`.

The second path is almost entirely unused. In this repository's own execution state, one active
work item of 89 carries a complete Planning Receipt — `dev-52-inventory-kc-dev-flow-removal-candidates`,
still in `backlog`, never started. Eight items including archived ones ever carried a
`planning-window`. Every other item uses `source` as free-text provenance: `captain`,
`GitHub issue`, `EM validation gate`. Of the three adopter repositories checked on 2026-09-14
(`subspace-relay`, `carlove-v1`, `subspace-v0`), none binds the reader or the comparator in its
Local Profile; `subspace-relay` records Linear as a future binding that never landed. The
manifest's `required_bindings` list contains no planning row at all, so no adopter's
`kc-dev-flow-local-profile/v1` check depends on these resources.

The Captain ruled on 2026-09-14 that work reaches dev-flow either from his own dictation or by
expanding a plan, and that the flow no longer takes over the Linear route. A user may still start
in Linear; dev-flow simply stops reading it. The Captain defined the plan in that ruling as what a
user journey map converts into dev-flow input, and that producer already exists and is already
aligned: `kc-journey-map`'s `plan-release` mode loads the five-section admission format from
`kc-dev-flow:adopt-dev-flow` and emits a reviewed Development Brief. Both intake paths therefore
produce the same artifact and differ only in who authored it, so no new input format is owed.

## Accepted outcome

Dev-flow has one intake: a committed Development Brief or Exploration Brief. Who authored that
brief — the Captain dictating, or `kc-journey-map`'s `plan-release` converting a journey map — is
outside dev-flow's contract, and dev-flow gains no reader for either.
`source` survives as free-text provenance and may hold a Linear URL. The Planning Receipt tuple,
its partial-tuple refusal, the engage-reconcile step, and both provider scripts leave the package
and this repository's Local Profile.

## Non-goals

- Stopping anyone from starting work in Linear, or removing Linear from the Captain's own habits.
- The `Fixes DEV-N` close line and anything else `pr-merge` or `kc-ship-flow` owns at delivery.
- Changing `kc-journey-map`, or building any second producer of a Development Brief.
- Renaming the `standalone` term once it is the only intake.
- Editing any other adopter's records.
- Reviving the retired local Linear reader that 4.3.0 already removed.

## Acceptance criteria

- **AC-1** An item whose frontmatter carries a `source` string and empty `planning-window` and
  `planning-outcome` loads through `profile-contract-loader.py` at every working stage, and an item
  that still carries all three loads the same way with no provider invocation.
- **AC-2** `scripts/linear-admission.py` and `scripts/engage-reconcile.py`, their tests, and their
  `contract-manifest.json` entries are absent, and `kc-dev-flow-contract-test.py` exits 0.
- **AC-3** No shipped skill or reference states a provider-backed route, an engage reconcile, a
  Planning Receipt, or a partial-tuple refusal as a requirement.
- **AC-4** This repository's `docs/dev/README.md` Local Profile no longer binds a planning reader
  or comparator and no longer carries an Engage reconcile section, and the loader runs clean
  against an existing committed work item after that edit.
- **AC-5** `dev-52-inventory-kc-dev-flow-removal-candidates` keeps its Linear URL in `source`,
  carries no `planning-window` or `planning-outcome`, and loads without refusal.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names
the changed premise, affected acceptance evidence, and recommended change or stop.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: >-
    Kent selected Pilot on 2026-09-14. Removing an intake path is a permanent
    contract change, not a disposable experiment. No consumer must act to take
    the new version: measured on 2026-09-14, none of the three adopter
    repositories binds the reader or comparator in its Local Profile, and the
    manifest's required_bindings carries no planning row. The one bound
    consumer is this repository, and AC-4 carries that edit.
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - Keep `source` as free-text provenance that may hold a Linear URL, and remove only the tuple that turned it into planning evidence.
      - Name where the removed engage-reconcile duty goes, or state that it goes nowhere because nothing consumed it.
      - Leave delivery untouched; the close line belongs to pr-merge and kc-ship-flow.
    implementation:
      - Remove both scripts, their tests, and their manifest entries in one change.
      - Strip the provider-backed route, engage reconcile, and partial-tuple refusal from shipped skills and references.
      - Edit this repository's Local Profile and `dev-52-inventory-kc-dev-flow-removal-candidates` in the same delivery.
    testing:
      - Cover the two frontmatter cases in AC-1 in the existing loader tests.
      - Run the package contract test and the existing loader and route suites; add no standing CI lane.
  scope_boundary: >-
    The accepted outcome and complete non-goal list in this task remain unchanged.
    Excludes delivery close lines, any change to kc-journey-map, other adopters'
    records, and renaming the standalone term.
  semantics_unchanged: false
  promote_when:
    - An adopter is found binding the reader or comparator and must edit owned records to upgrade.
    - Delivery close lines or another plugin's contract enters scope.
  decision:
    authority: Kent (Captain)
    at: 2026-09-14T00:00:00Z
```

## Stage Report: ideation

- DONE: The removed surface is enumerated exactly: every shipped skill, reference, script, test, and contract-manifest entry that states the provider-backed route, the Planning Receipt tuple, the engage reconcile, or the partial-tuple refusal, named by greppable symbol, with the loader's two frontmatter reads separated from the prose that merely describes them.
  See "### Removed-surface enumeration" below.

- DONE: Where the engage-reconcile duty goes is settled: either a named successor owner, or the evidence that nothing consumed it, carrying two search strategies and the boundary at which they stopped.
  See "### `engage-reconcile.py` consumer trace" below — no successor; nothing outside the provider-backed branch invokes it.

- DONE: The surviving `source` boundary is proven, not asserted: what the loader must still accept once the tuple leaves, exercised against a real committed work item that carries a Linear URL in `source`.
  See "### `source`-boundary proof" below — exercised against `dev-52-inventory-kc-dev-flow-removal-candidates`'s real content via `validate_admission_brief`.

### Removed-surface enumeration

Scope: `kc-dev-flow/` shipped package content only. Excludes `.worktrees/`, `.context/` (historical snapshots, not live), and `kc-ship-flow/scripts/fixtures/**/DEV-*.md` (already-empty `planning-window`/`planning-outcome` frontmatter keys, no assertion of the provider route — no action).

**Skills (prose to strip of the provider-backed route, engage reconcile, Planning Receipt tuple, partial-tuple refusal):**
- `kc-dev-flow/skills/adopt-dev-flow/SKILL.md` — provider-backed classification, `linear-admission.py` binding instructions, engage-reconcile invocation steps, the removal-candidate table row for a repository-local Linear reader.
- `kc-dev-flow/skills/choose-work-profile/SKILL.md` — "a partial tuple" / provider-backed-path selection language.
- `kc-dev-flow/skills/continue-dev-flow/SKILL.md` — step 4 (classify Planning Receipt), step 5 (`linear-admission.py` invocation), step 7 (engage-reconcile invocation with `--expected-window`/`--expected-outcome`).

**References:**
- `kc-dev-flow/references/kernel.md` — "one planning-window authority, one planning-outcome authority" line; Planning Receipt complete-or-absent rule.
- `kc-dev-flow/references/pr-delivery.md` — provider-backed delivery branch/close-line clauses. **Flagged, not removed — see residual 2 below** (collides with non-goal "leave delivery untouched").
- `kc-dev-flow/references/pr-merge-extension.md` — same provider-backed delivery clause, duplicated. Same residual.

**Top-level package docs (shipped, not skill/reference, still in scope for AC-3):**
- `kc-dev-flow/README.md` — Planning Receipt definition, provider-backed comparator/reader description.
- `kc-dev-flow/MIGRATION.md` — historical provider-backed migration steps referencing `linear-admission.py`/`engage-reconcile.py`.
- `kc-dev-flow/RATIONALE.md` — Planning Receipt rationale, provider-backed engage description.

**Scripts (definitions — removed whole per AC-2):**
- `kc-dev-flow/scripts/linear-admission.py` (whole file, including `delivery_binding()` — see residual 2).
- `kc-dev-flow/scripts/engage-reconcile.py` (whole file).

**Tests (removed or edited per AC-2):**
- `kc-dev-flow/scripts/engage-reconcile.test.py` — removed whole (tests a file being removed).
- No standalone `linear-admission.test.py` exists; its coverage lives in `scripts/kc-dev-flow-contract-test.py` (repo-level, not shipped) and must be edited there.
- `kc-dev-flow/scripts/profile-contract-loader.test.py` — edited, not removed: presence-mask tests (`Planning Receipt presence mask …`) and the partial-tuple-rejection test exercise the exact code path AC-1 changes.

**`contract-manifest.json`:**
- `kc-dev-flow/contract-manifest.json` lines declaring `"scripts/engage-reconcile.py"` and `"scripts/linear-admission.py"` as resources — both entries removed.

**The loader's two frontmatter reads (code, not prose) — `kc-dev-flow/scripts/profile-contract-loader.py::validate_admission_brief`:**
Only one function in the shipped loader reads `source`/`planning-window`/`planning-outcome`, and only for `profile in {"pilot-product-slice", "production"}` (POC skips it entirely — matches the ideation stage-def's "POC moves directly from backlog to implementation"). Two `raise ContractError("Planning Receipt must be complete or absent")` sites inside it, corresponding to AC-1's two shapes:
1. `declared_receipt_fields` check (`any(...) and not all(...)`) — fires when a field key is entirely absent from frontmatter.
2. `present` check (`any(present) and not all(present)`, `present = [not is_placeholder_scalar(value) ...]`) — fires when a key is declared but its value is empty/placeholder. **This is the site the `source`-boundary proof below exercises.**

**Repo-level test scripts (not shipped, but AC-2 requires them to exit 0 / stay accurate):**
- `scripts/kc-dev-flow-contract-test.py` — extensive literal-string assertions on the prose being removed (lines matching the enumerated skill/reference text above) plus a full `linear-admission.py` compile/contract test block. All of this must be edited alongside the package, or `kc-dev-flow-contract-test.py` will fail against its own fixtures once the prose it asserts on is gone.
  - Distinguish: `docs/dev/_mods/engage-reconcile.py`, `scripts/kc-dev-flow/engage-reconcile.py`, `scripts/kc-dev-flow/linear-admission.py` referenced in this file are **absence assertions** (proving the 4.3.0-retired local reader stays retired) — these stay, they assert nothing exists at those paths.
- `scripts/kc-dev-flow-minimal-stack-ablation.test.py` — same class of literal-string prose assertions plus direct `Path(...)` references to both scripts.

**Local Profile (this repository, AC-4 — separate from the shipped package):**
- `docs/dev/README.md` lines 50, 54, 59-60, 65, 68-69, 86, 195, 212, 223, 245, 247, 297 — planning-provider binding table rows, Engage reconcile section, provider-backed base-policy clause.
- `ARCHITECTURE.md`, `docs/dev/ROADMAP.md` — one-line mentions, prose-only, no enforcement.

**Out of scope, flagged as stale prose (not touched, not this task's non-goal list, but will drift):**
- `kc-journey-map/skills/kc-journey-map/references/map-from-conversation.md:144` — one mention of "provider Planning Receipt" in a sibling plugin. Non-goal excludes changing `kc-journey-map`; this line goes stale and is not this task's responsibility to fix.

### `engage-reconcile.py` consumer trace

Two search strategies, both stopped at the same boundary:
1. **Path-string grep** — `grep -rn "engage-reconcile.py" --include="*.py" --include="*.md" --include="*.json" .` (excluding `.worktrees/`, `.context/`) surfaces exactly: its own definition, its own test, the `contract-manifest.json` declaration, `linear-admission.py:298` (`comparator = profile_loader.parent / "engage-reconcile.py"`, invoked as a subprocess at line ~406), `continue-dev-flow/SKILL.md` step 7 (same subprocess invocation, documented), and prose in `README.md`/`MIGRATION.md`/`docs/dev/README.md` describing it. No other call site.
2. **Symbol grep** — `grep -rn "reconcile(" --include="*.py" .` for its defined names (`ReconcileError`, `valid_text`, `reject_duplicate_fields`, `by_source`, `comparable`) across the whole tree (including `docs/plan-flow`, `kc-ship-flow`) returns zero hits outside `engage-reconcile.py`/`engage-reconcile.test.py` itself — ruling out a dynamic `importlib` consumer the path-grep could miss (the pattern that caught the `linear-admission.py` finding below).

Both searches stop at "invoked only from inside the provider-backed branch of `linear-admission.py` and `continue-dev-flow`." No successor owner exists or is needed — the whole duty leaves with the branch that invokes it.

**Residual 1 (does not block this stage, needs Captain disposition before/with build):** `docs/plan-flow/plan-lint.py` — a *different* script in this repo, not `kc-dev-flow`'s package — does `importlib.util.spec_from_file_location` on `kc-dev-flow/scripts/linear-admission.py` (not `engage-reconcile.py`) and calls `la.live_item(i)` / `la.delivery_binding(i, ...)` for its own "L4 admission" lint rule. This is live, not stale: `kc-ship-flow/scripts/fixtures/real-AC367-r2.md` pins a real commit SHA and a `WITHOUT_IT_COMMAND` exercising `plan-lint.py`'s L4 output, and `kc-ship-flow/scripts/contract-test.py` asserts a `"kc-plan-lint/v1"` schema pass. Deleting `linear-admission.py` per AC-2 breaks `plan-lint.py`'s L4 rule at runtime (`ImportError`/`AttributeError` on the missing file/attribute). This is not a route-back — the accepted outcome and non-goals name only dev-flow's package and this repo's Local Profile, and `plan-flow` is neither — but AC-2 as written ("absent," no carve-out) collides with a live consumer AC-2 didn't anticipate. Two options, not chosen here: (a) move `live_item`/`delivery_binding` into `docs/plan-flow` before deleting `linear-admission.py`, or (b) retire `plan-lint.py`'s L4 rule. Memory notes `plan-flow` is a layer Kent owns directly (plan-flow decides WHEN/HOW TO PLAN, dev-flow decides HOW TO BUILD) — this ensign does not rule on which option.

**Residual 2 (same class, smaller):** `linear-admission.py::delivery_binding()` (line ~166, called at line ~357) is the sole producer of the `branch`/`close_line` pair that `kc-dev-flow/references/pr-delivery.md`, `pr-merge-extension.md`, and `docs/dev/_mods/pr-merge.md` describe as `delivery.branch`/`delivery.close_line` for "provider-backed" delivery. The non-goal list says "Leave delivery untouched; the close line belongs to `pr-merge` and `kc-ship-flow`." AC-3 says no shipped reference may state a provider-backed route as a requirement. Once `linear-admission.py` is gone, the provider-backed delivery clause in `pr-delivery.md`/`pr-merge-extension.md` has no producer and can never fire (dead conditional, not broken), but it still *states* a provider-backed route — a literal AC-3 hit that the non-goal appears to carve out. Flagging the tension; not resolving it here.

### `source`-boundary proof

Exercised `kc-dev-flow/scripts/profile-contract-loader.py::validate_admission_brief` directly (via `importlib`) against the real committed content of `docs/dev/.spacedock-state/dev-52-inventory-kc-dev-flow-removal-candidates.md` (the AC-5 target, `source: https://linear.app/duckbase-co/issue/DEV-52/...`):

- Unmodified (full tuple: `source` + non-empty `planning-window` + `planning-outcome`) → **accepted**, returns a sha256 digest. This is today's already-passing case; AC-1's second clause ("an item that still carries all three loads the same way with no provider invocation") only requires removing the provider invocation elsewhere — the loader already accepts this shape.
- `planning-window`/`planning-outcome` values stripped to empty, `source` left as the Linear URL (the shape AC-1's first clause and AC-5 require) → **rejected today**: `ContractError: Planning Receipt must be complete or absent`, raised by the `present` check (case 2 in the enumeration above — keys declared, values empty).

This is the exact, and only, code change `validate_admission_brief` needs for AC-1: `source` must stop being counted as a Planning-Receipt-tuple member in both the `declared_receipt_fields` and `present` checks, leaving only `planning-window`+`planning-outcome` subject to the complete-or-absent rule. Proven against real content, not asserted.

**Search boundary (adopter checkouts on disk, 2026-09-14):** extended the entity's own two-adopter-repo check with a direct grep for `linear-admission|engage-reconcile` across `/Users/kent/conductor/workspaces/subspace-v0/quebec-v1`, `/Users/kent/conductor/workspaces/carlove-v1/kyoto`, `/Users/kent/Project/carlove` (excluding `node_modules`, `.git/`, `/plugins/cache/`). Only hit: a stale `.context/` snapshot in `quebec-v1`, not live. Not searched: adopter repositories not present on this machine.

### Summary

Enumerated the shipped provider-backed surface by greppable symbol, traced `engage-reconcile.py` to zero consumers outside the branch being removed (two independent search strategies), and proved empirically — against `dev-52`'s real committed content — the exact loader check AC-1 must change. Surfaced two residuals for Captain disposition before or during build: `docs/plan-flow/plan-lint.py` has a live, tested `importlib` dependency on `linear-admission.py` that AC-2 doesn't carve out, and the provider-backed delivery clauses in `pr-delivery.md`/`pr-merge-extension.md` lose their sole producer while a non-goal says leave delivery untouched. Neither blocks ideation completion; both are findings this stage exists to surface, not defects in this stage's own work.

## Stage Report: implementation

- DONE: The plan-flow move lands before the deletion — `live_item` and `delivery_binding` live in `docs/plan-flow/admission.py`, `plan-lint.py`'s L4 rule imports that local module instead of reaching into `kc-dev-flow`, and only then was `kc-dev-flow/scripts/linear-admission.py` removed.
  Proof, in order: (1) baseline `python3 scripts/kc-dev-flow-contract-test.py` → PASS with `linear-admission.py` still present; (2) created `docs/plan-flow/admission.py` (copy of `live_item`/`delivery_binding`/`issue_identifier`/`section`/`AdmissionError` from `linear-admission.py`), rewired `docs/plan-flow/plan-lint.py` to `import admission as la` via `sys.path.insert` instead of `importlib.util.spec_from_file_location` on the `kc-dev-flow` path; (3) re-ran `python3 scripts/kc-dev-flow-contract-test.py` → still PASS (L4 green off the new module, `linear-admission.py` untouched); (4) only then `git rm kc-dev-flow/scripts/linear-admission.py kc-dev-flow/scripts/engage-reconcile.py kc-dev-flow/scripts/engage-reconcile.test.py` and removed their `contract-manifest.json` entries. The repository was never in a state where L4 raised. Direct check kept: `python3 docs/plan-flow/plan-lint.py lint scripts/fixtures/plan-flow/admitted-only-rough-backlog.snapshot.json | grep 'PASS L4'` → `PASS L4 admission DEV-913: 2 non-goals`.

- DONE (AC-1): `kc-dev-flow/scripts/profile-contract-loader.py::validate_admission_brief` no longer counts `source` in the Planning-Receipt-tuple check — only `("planning-window", "planning-outcome")` are subject to the complete-or-absent rule.
  Two shapes exercised directly against real content in `kc-dev-flow/scripts/profile-contract-loader.test.py` (edited, not added): a `source` string with empty `planning-window`/`planning-outcome` now accepts (new `standalone-source-empty-window-outcome` case), and the full-tuple shape still accepts unchanged. `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` → PASS.

- DONE (AC-2): `scripts/linear-admission.py`, `scripts/engage-reconcile.py`, `scripts/engage-reconcile.test.py` and their `contract-manifest.json` resource entries are absent, and the exit-0 chain proves nothing in the repo still depends on them.
  `git rm`, confirmed no `retired`-list violation in `kc-dev-flow-contract-test.py`. `python3 scripts/kc-dev-flow-contract-test.py` → PASS (exit 0). `python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py` (the full mutation suite, ~55 mutants) → PASS, every mutant correctly REJECTED including the ones that used to target `linear-admission.py`/`engage-reconcile.py` directly (those mutant definitions were removed along with their targets, not left dangling). `python3 kc-ship-flow/scripts/contract-test.py` → PASS (unaffected, confirms the plan-lint move didn't regress `kc-ship-flow`'s own suite).

- DONE (AC-3): Every shipped skill/reference in the entity's own removed-surface enumeration was edited to remove the provider-backed route, Planning Receipt, engage reconcile, and partial-tuple refusal.
  `adopt-dev-flow/SKILL.md` (Planning Receipt/provider-backed prose and the retired-local-Linear-reader table row removed, steps renumbered 1-9), `choose-work-profile/SKILL.md` (partial-tuple/provider-backed language removed), `continue-dev-flow/SKILL.md` (old steps 4-7 — classify receipt, provider read, ready-set compare, engage-reconcile invocation, and the delivery-binding paragraph derived from that read — removed; steps renumbered 4-6), `kernel.md` (planning-window/planning-outcome authority line and Planning Receipt complete-or-absent rule removed), `README.md`/`MIGRATION.md`/`RATIONALE.md` (Planning Receipt definition and provider-backed comparator/reader description removed; `MIGRATION.md`'s historical 3.x-to-4.x and 2.x sections left as dated history, with a new 2026-09-14 entry at the top of the dated log explaining the retirement and pointing at the historical sections). `ARCHITECTURE.md` and `docs/dev/README.md` (this repository's own Local Profile) were also edited — flagged in ideation as "one-line mentions, prose-only, no enforcement" but still in AC-3's scope. `grep -rn "Planning Receipt\|planning-window\|planning-outcome\|linear-admission\|engage-reconcile\|provider-backed"` across the edited files returns nothing outside: `pr-delivery.md`/`pr-merge-extension.md` (residual 2, see below), `MIGRATION.md`'s historical dated sections, and `kc-journey-map/.../map-from-conversation.md` (out of scope, sibling plugin, entity's own non-goal).

- DONE (AC-4): `docs/dev/README.md`'s Local Profile no longer binds a planning reader or comparator, and no longer carries an Engage reconcile section.
  The table no longer carries "Planning reader and admission guard" / "Planning comparator" rows, its `### Engage reconcile` section is removed outright, and the provider-backed base-policy clause in the `## Local Profile` prose is replaced with the free-text-provenance statement. `validate_admission_brief` exercised directly against `dev-52-inventory-kc-dev-flow-removal-candidates.md`'s real committed bytes for `profile in {"poc-exploration"}` (its actual profile) returns `None` (skip, correct — matches the entity's own note that POC skips the check); the loader's complete-or-absent logic itself is proven by the `profile-contract-loader.test.py` cases above, which is where the enforcement actually lives.

- DONE (AC-5): `dev-52-inventory-kc-dev-flow-removal-candidates.md` keeps its Linear URL in `source`, carries no `planning-window`/`planning-outcome`, and loads without refusal.
  Frontmatter edited in the state checkout — `planning-window`/`planning-outcome` cleared to empty, `source: https://linear.app/duckbase-co/issue/DEV-52/...` untouched. `grep -n "planning-window\|planning-outcome\|Linear Cycle\|Linear Project" dev-52-inventory-kc-dev-flow-removal-candidates.md` → only the two now-empty frontmatter keys, no stray body references. Loads without refusal (see AC-1 proof above; this file's exact shape — non-empty `source`, empty window/outcome — is the literal case both new tests exercise).

- DONE: The delivery clauses survive untouched, per the Captain's ruling that the non-goal wins over a literal AC-3 reading.
  `git diff --stat kc-dev-flow/references/pr-delivery.md kc-dev-flow/references/pr-merge-extension.md` → empty (no diff, confirmed before commit). `kc-dev-flow-contract-test.py`'s existing assertions on `pr-delivery.md`'s provider-linkage phrases (`delivery.branch`, `delivery.close_line`, etc.) still pass unchanged. The Captain's AC-3-is-scoped-to-intake reading is stated at MIGRATION.md's new 2026-09-14 entry, which a later reader hits before the historical migration sections: "Delivery ... is untouched; those clauses describe a producer that no longer exists and so can never fire, which is accepted, not a defect."

- DONE: A real (not incidental) defect was caught and fixed mid-build, not merely disclosed.
  `docs/plan-flow/admission.py` was created untracked, and `scripts/kc-dev-flow-minimal-stack-ablation.test.py`'s fixture copier (`copy_repository_fixture`) builds its fixtures from `git ls-files`, so the new module was silently missing from every mutation-test fixture until `git add`ed — surfaced as an unrelated mutant (`rendered-kernel-and-base-omitted`) failing for the wrong reason. Fixed by staging the file before the final ablation run; re-run confirmed PASS.

### Full test evidence (final state, in order)

- `python3 scripts/kc-dev-flow-contract-test.py` → `kc-dev-flow contract: PASS` (exit 0)
- `python3 scripts/kc-dev-flow-contract-test.py --ablation-check` → `kc-dev-flow contract: PASS` (exit 0)
- `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` → PASS
- `python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py` → `kc-dev-flow minimal-stack ablation: PASS` (~55 mutants, all REJECTED as expected; none of the removed `linear-admission.py`/`engage-reconcile.py`-specific mutants left dangling)
- `python3 kc-ship-flow/scripts/contract-test.py` → `kc-ship-flow contract: PASS`

### Known residual

None outstanding against this stage's scope. The two residuals the ideation stage surfaced (plan-lint's dependency, and the delivery clauses losing their producer) were both Captain-dispositioned at the ideation gate and executed exactly as ruled — they are not open items here.

### Summary

Retired the provider-backed planning path: `linear-admission.py` and `engage-reconcile.py` (plus tests and manifest entries) are gone; `plan-lint.py`'s L4 rule carries its own admission logic in `docs/plan-flow/admission.py` instead of reaching into `kc-dev-flow`, proven green before the deletion; `source` is pure free-text provenance everywhere, with only `planning-window`/`planning-outcome` subject to the complete-or-absent rule; every shipped skill/reference and this repository's own Local Profile were stripped of the provider-backed route, Planning Receipt tuple, and engage-reconcile description; `dev-52` keeps its Linear URL in `source` with both planning fields empty; delivery (`pr-delivery.md`/`pr-merge-extension.md`) is byte-for-byte untouched per the Captain's ruling. All five ACs carry direct evidence, four test suites pass (contract test in both modes, the full ~55-mutant ablation suite, the loader's own test, and `kc-ship-flow`'s contract test).

## Stage Report: validation

- DONE: Re-run rather than re-read — the five suites the implementation report names, at the exact candidate commit `95b19de0` (`fix(kc-dev-flow): retire the provider-backed planning path`), in a fresh isolated checkout resolved independently (`git worktree add --detach /tmp/validation-checkout-95b19de0 95b19de0`), not the implementation worktree.
  `python3 scripts/kc-dev-flow-contract-test.py` → PASS (exit 0); `--ablation-check` → PASS (exit 0); `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` → PASS, including the new `standalone-source-empty-window-outcome` case (not vacuous: asserts `returncode == 0` on a real subprocess admission run); `python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py` → PASS, 59 named mutants all REJECTED; `python3 kc-ship-flow/scripts/contract-test.py` → PASS, `dispatch.test: 10 passed, 0 failed` / `watch.test: 11 passed, 0 failed`.

- DONE: Falsify the ordering claim, not trust it.
  The branch carries exactly one commit (`95b19de0`, parent `7b103a10`) — the implementation report's multi-step narrative (create `admission.py`, rewire `plan-lint.py`, test, only then `git rm`) happened inside one uncommitted session and was squashed before commit, so it has no git-level intermediate state to inspect. What is falsifiable is the two real endpoints: checked out parent `7b103a10` (pre-change) and candidate `95b19de0` (post-change) independently and ran `plan-lint.py lint scripts/fixtures/plan-flow/admitted-only-rough-backlog.snapshot.json` against both — `PASS L4 admission DEV-913: 2 non-goals` at both. Confirmed the ordering precondition directly on the candidate tree: `docs/plan-flow/admission.py` imports only `hashlib`, `os`, `re`, `subprocess` (stdlib, nothing from `kc-dev-flow`), `plan-lint.py` imports it as `import admission as la` (local module, not `importlib.util.spec_from_file_location` into `kc-dev-flow`), and `kc-dev-flow/scripts/linear-admission.py` / `engage-reconcile.py` are absent from the tree. This proves L4 is green at both ends and the dependency direction is correct at the end state — it does NOT prove the repository was never broken mid-session, because no commit exists at that granularity to check. Flagging this as the honest bound of what git history can prove here, not as a defect: the implementation ensign's own report already states this qualification implicitly by narrating steps that were never individually committed.

- DONE: The Captain's two ideation-gate dispositions held.
  Residual 1 (plan-lint move before deletion): confirmed above — `admission.py` carries the logic locally, imports nothing from `kc-dev-flow`, L4 passes. Residual 2 (delivery untouched): `git diff --stat 7b103a10 95b19de0 -- kc-dev-flow/references/pr-delivery.md kc-dev-flow/references/pr-merge-extension.md` → empty, confirming byte-for-byte no change. A repo-wide AC-3 scan (`grep -rln "Planning Receipt\|planning-window\|planning-outcome\|linear-admission\|engage-reconcile\|provider-backed" --include="*.md" kc-dev-flow/ kc-journey-map/`) returns exactly the disclosed set: `pr-delivery.md`, `pr-merge-extension.md` (residual 2, ruled to stay), `MIGRATION.md` (dated historical log), and `kc-journey-map/.../map-from-conversation.md` (out-of-scope sibling plugin, entity's own non-goal) — no undisclosed hit.

- DONE: AC-1 and AC-5 exercised against `dev-52-inventory-kc-dev-flow-removal-candidates`'s real committed content, not a fixture.
  Read the file's real committed frontmatter directly from the state checkout (`git log` shows it last touched by `684a5617`): `source: https://linear.app/duckbase-co/issue/DEV-52/...` populated, `planning-window:`/`planning-outcome:` both empty. Called `kc-dev-flow/scripts/profile-contract-loader.py::validate_admission_brief` at the candidate commit directly against that file's real `Path` (not a copied/edited string) for all three profiles: `pilot-product-slice` → accepted (digest returned), `production` → accepted (digest returned), `poc-exploration` (the file's actual profile) → `None` (correctly skipped, matching the entity's own note that POC skips the check). This is AC-5's exact shape and AC-1's first clause, proven live rather than re-read from the report's prose.

### Summary

Re-ran all five named suites green at an independently-resolved checkout of candidate commit `95b19de0`. Both Captain-dispositioned residuals hold with direct diff/grep evidence. AC-1/AC-5 re-proven against `dev-52`'s real committed bytes via a fresh direct call. One honest limit surfaced: the branch is a single squashed commit, so the implementation report's step-ordering narrative (never leaving L4 broken mid-session) is provable only at the two real git endpoints (parent, candidate) — both pass — not at any finer commit-by-commit granularity, because no finer granularity was committed. This is a gap in the evidence trail, not a found defect; no AC fails and no residual is newly outstanding.

## Stage Report: implementation (cycle 2)

- DONE: The branch rebases cleanly onto `origin/main` and the three conflicts are resolved on their meaning.
  `git rebase origin/main` conflicted in `kc-dev-flow/MIGRATION.md`, `kc-dev-flow/contract-manifest.json`, and `scripts/kc-dev-flow-contract-test.py` — the exact three files named in the rework spec, against the same two merged pull requests (`58748d73` #433, `da3f287f` #435). Resolved and continued; `git status` is clean, `git log --oneline -1` shows the rebased tip `5de5778a` (parent `e3cca913`, current `origin/main`). No fourth conflict appeared.
- DONE: `MIGRATION.md` keeps both dated entries.
  The 2026-09-14 retirement entry (this branch) now sits above the 2026-09-13 pull-request-title-refusal entry (`main`, #433) in the dated log, newest-first, matching the file's existing convention; neither entry's body text was altered, only reordered with a restored blank line between them.
- DONE: `contract-manifest.json` keeps every resource `main` added and loses every one this branch removed.
  `scripts/check-pr-title.py` and `scripts/fixtures/pr-title/release-please-verdicts.tsv` (added by #435/#433) stay in the `resources` array; `scripts/engage-reconcile.py` and `scripts/linear-admission.py` (removed by this branch) are absent. `python3 -c "import json; json.load(open('kc-dev-flow/contract-manifest.json'))"` confirms valid JSON post-edit.
- DONE: `scripts/kc-dev-flow-contract-test.py` keeps every title-refusal assertion `main` added, and it passes.
  Same conflict shape and same resolution as the manifest (`expected_manifest_resources` set) — `check-pr-title.py`/its fixture kept, `engage-reconcile.py`/`linear-admission.py` dropped. The surrounding required-file list, script-role classification, and retired-control assertions that `git` auto-merged cleanly (no conflict markers there) were left untouched. Verified by running the suite itself (below), not by re-reading the diff.
- DONE: All five suites re-run at the rebased commit `5de5778a`, all PASS.
  Listed with output in "Full test evidence" below.
- DONE: The two ideation-gate dispositions hold after the rebase.
  `docs/plan-flow/admission.py`'s imports at the rebased tip: `hashlib`, `os`, `re`, `subprocess`, `__future__.annotations` — stdlib only, nothing from `kc-dev-flow` (checked via `ast.parse` + `ast.walk`, not string grep). `git diff --stat origin/main -- kc-dev-flow/references/pr-delivery.md kc-dev-flow/references/pr-merge-extension.md` → empty output, confirming byte-for-byte no diff against the current `origin/main` tip (`e3cca913`), not the stale base the prior validation ran against.

### Full test evidence (rebased commit `5de5778a`, in order)

- `python3 scripts/kc-dev-flow-contract-test.py` → `kc-dev-flow contract: PASS` (exit 0)
- `python3 scripts/kc-dev-flow-contract-test.py --ablation-check` → `kc-dev-flow contract: PASS` (exit 0)
- `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` → all four named sub-suites PASS, overall `profile contract loader test: PASS`
- `python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py` → `kc-dev-flow minimal-stack ablation: PASS`, 61 named mutants all REJECTED, baseline PASS, exit 0
- `python3 kc-ship-flow/scripts/contract-test.py` → `kc-ship-flow contract: PASS`; `dispatch.test: 10 passed, 0 failed`; `watch.test: 11 passed, 0 failed`

### Known residual

None outstanding against this rework's scope. The mutant count (61) differs from the prior report's "~55"/"59" figures because `origin/main`'s two intervening pull requests added mutants of their own (e.g. the pull-request-title-refusal coverage); this is the rebased suite's real, current count, not a discrepancy to explain away.

### Summary

Rebased `spacedock-ensign/retire-the-provider-backed-planning-path` onto `origin/main` (tip `e3cca913`), resolving the three predicted conflicts on their meaning — both `MIGRATION.md` dated entries kept, `contract-manifest.json` and `kc-dev-flow-contract-test.py` keep `main`'s title-refusal additions and lose this branch's `linear-admission.py`/`engage-reconcile.py` removals. New candidate SHA `5de5778a`. All five suites re-run green at that commit. Both Captain-dispositioned residuals re-verified directly against the rebased tree: `admission.py` imports nothing from `kc-dev-flow`, and `pr-delivery.md`/`pr-merge-extension.md` show zero diff against current `origin/main`.
