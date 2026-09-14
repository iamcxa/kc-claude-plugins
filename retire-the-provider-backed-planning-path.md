---
title: "Retire the provider-backed planning path, so dev-flow's only intake is a committed brief"
status: implementation
source: Captain ruling 2026-09-14 in FO session
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: kc-dev-flow/S10
sprint-readiness: ready
started: 2026-09-14T08:25:39Z
completed:
verdict:
worktree:
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
