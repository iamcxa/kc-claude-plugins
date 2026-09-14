---
title: "Admission asks who was bitten and who will run it: a brief carries `bite:` and `consumer:` lines, and a fixture that copies an existing file is refused"
status: validation
source: "Captain 2026-09-15 「目前 dev flow 合約 or kernel 是否沒有 yagni 原則？為何會做出用不到的測試？」 then 「立這張 r4 票」"
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper-r4
sprint-readiness: ready
started: 2026-09-14T22:53:10Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-admission-asks-who-was-bitten-and-who-will-run-it
issue:
pr: 457
mod-block:
id: gzrgwdxkh6zkenkswkhasmjc
gates:
    version: 1
    records:
        - id: gate:gzrgwdxkh6zkenkswkhasmjc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:gzrgwdxkh6zkenkswkhasmjc-backlog-1
              briefing:
                id: briefing:gzrgwdxkh6zkenkswkhasmjc:backlog:attempt-1:revision-1
                digest: sha256:b52c60eac0ce49a09a95c4f58679f4e081cfc0f3d3f60cad211deb21d63275e7
                room-ref: ./admission-asks-who-was-bitten-and-who-will-run-it/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:gzrgwdxkh6zkenkswkhasmjc:backlog:1
                briefing: briefing:gzrgwdxkh6zkenkswkhasmjc:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-14T22:29:57.599568Z"
                decision: approve
                reason: 'backlog admission on the batch conn: brief carries bite, consumer, AC-1..4, non-goals, route-back. Enter ideation.'
                conn:
                    quote: r4 現在開
                    source: Captain chat 2026-09-15, opening the ship-cloud-wrapper-r4 batch of three (pilot profile)
              application:
                target-stage: ideation
                state: consumed
        - id: gate:gzrgwdxkh6zkenkswkhasmjc:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:gzrgwdxkh6zkenkswkhasmjc-ideation-1
              briefing:
                id: briefing:gzrgwdxkh6zkenkswkhasmjc:ideation:attempt-1:revision-1
                digest: sha256:defc1ab41d223924840192dd54badb4776694b473431fbb675f9ad6df9bcc034
                room-ref: ./admission-asks-who-was-bitten-and-who-will-run-it/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:gzrgwdxkh6zkenkswkhasmjc:ideation:1
                briefing: briefing:gzrgwdxkh6zkenkswkhasmjc:ideation:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-14T23:01:56.46505Z"
                decision: approve
                reason: 'ideation read by the ship FO: AC-1 correctly re-targeted from plan-lint.py to profile-contract-loader.py validate_admission_brief() per the brief''s own route-back clause (#444 landed first); AC-2 at surface-map-check.py; AC-3 as a small sibling script beside e2e-gate.py under run-batch step 3. Pilot receipt recorded. Enter implementation.'
                conn:
                    quote: r4 現在開
                    source: Captain chat 2026-09-15, opening the ship-cloud-wrapper-r4 batch of three (pilot profile)
              application:
                target-stage: implementation
                state: consumed
        - id: gate:gzrgwdxkh6zkenkswkhasmjc:validation
          stage: validation
          attempts:
            - id: gate-attempt:gzrgwdxkh6zkenkswkhasmjc-validation-1
              briefing:
                id: briefing:gzrgwdxkh6zkenkswkhasmjc:validation:attempt-1:revision-1
                digest: sha256:efd40f70c6971a300a6cd74a83fe3f075d2ab8ba106d02777ceeed33944cab88
                room-ref: ./admission-asks-who-was-bitten-and-who-will-run-it/review/validation/briefing-1
---

Two PRs in the ship-cloud-wrapper-r3 batch passed every gate — backlog admission, ideation, the
implementation-exit `surface-map-check.py`, validation, and the ship first officer's verification at
the pinned SHA — and were closed unmerged by the Captain within one question each on 2026-09-15:
iamcxa/kc-claude-plugins#446 (2136 lines, 1946 of them three copies of a released `pr-merge.md`; the
0.27.0 pin row had no consumer once adopter-side checks were removed) and #450 (1117 lines, 618 a
byte-identical copy of `docs/dev/_mods/pr-merge.md`; its checks duplicated the installed loader and
#446, and the only measured bite was one sentence in `MIGRATION.md`). The kernel's Minimal necessity
(`references/kernel.md` § Completion invariant) grades every retained surface against the brief's
accepted outcome, so a surface the brief asked for is necessary by construction; nothing in the
kernel, `choose-work-profile`, or the pilot contract asks who was bitten before the brief was
written or who executes the change after merge (`grep -rn consumer` finds only the compatibility
definition). A one-word mutant that makes a test fail satisfies the without-it observation while
proving only that the test detects change, not that anyone needs the detection.

## Accepted outcome

Admission refuses a brief that cannot name its bite and its consumer, and the fixture copy escape
is closed, without touching the kernel's Minimal necessity text.

## Acceptance criteria

* **AC-1** A brief entering the backlog gate carries `bite:` (the command, date and cost of the failure it repairs, or the Captain's verbatim ask) and `consumer:` (the program, workflow step or person that executes the change after merge). `plan-lint.py` (or the backlog-gate check the package already runs) refuses a brief missing either, naming the line. Verified by: the two closed PRs' briefs, replayed, are refused; the merged #445/#448/#451 briefs pass once the two lines are added. Falsified by: any of the five r3 briefs passing unchanged.
* **AC-2** `surface-map-check.py` refuses a changed file whose bytes are identical to another file in the repository at the candidate, or to a file in the cached Spacedock plugin, unless the `SURFACE:` line names it as a generated copy with the generating command. Verified by: #446's and #450's diffs, replayed, are refused on the fixture paths. Falsified by: either diff passing.
* **AC-3** The ship first officer's verification step (kc-ship-flow `run-batch` skill, accept-by-evidence) adds one line: the consumer named in the brief is shown to exist at the candidate (a path or symbol that invokes it). Verified by: the r3 questions log's two closures reproduce as a refusal in the dry run.
* **AC-4** No new receipt, harness or LOC gate; the kernel's "LOC is diagnostic, never a gate" sentence stands.

## Non-goals

- No change to `references/kernel.md` Minimal necessity wording.
- No retroactive edit of merged r3 briefs beyond adding the two lines as the AC-1 fixture.

## Route-back conditions

- Back to backlog if `plan-lint.py` no longer owns admission after `retire-the-provider-backed-planning-path` (#444) lands its committed-brief intake — re-point AC-1 at that intake's check.

Profile recommendation: pilot.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: >
    Two admission/verification checks the package already runs
    (profile-contract-loader.py's brief admission, surface-map-check.py's
    obligation binding) gain new refusal classes every future Pilot/Production
    brief and every future surface-map-check invocation depends on — not a
    disposable experiment. The r3 incident (two Captain-question closures in
    one question each) is the measured repeat-incident class this fixes; no
    production credentials/data, destructive external mutation, irreversible
    migration, or consumer-facing compatibility break is in scope; no
    SLO/support/release-ownership duty attaches.
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - Confirm profile-contract-loader.py's validate_admission_brief() is
        still the sole in-repo brief-admission check post-#444 (plan-lint.py's
        L4/live_item operates only on Linear GraphQL snapshots and has no
        code path from docs/dev/.spacedock-state/*.md; AC-1's own parenthetical
        already names "the backlog-gate check the package already runs").
      - Confirm surface-map-check.py's per-file loop (`for path in checked`)
        and its SURFACE-line vocabulary (`target_problem`, `without_it_binds`,
        LITERAL_TARGETS) are the single place a byte-identity refusal and its
        SURFACE: escape hatch land.
      - Confirm kc-ship-flow run-batch's `verified` stage (SKILL.md step 3)
        is the one call site the consumer-exists check joins, and whether it
        belongs inside e2e-gate.py (batch/milestone-receipt scoped) or as a
        sibling per-task script the FO runs alongside it (open fork, see
        Ideation: shape below).
    implementation:
      - validate_admission_brief() (profile-contract-loader.py:491-567)
        requires a concrete `bite:` and `consumer:` line in the brief's
        preamble (the text between the frontmatter close and the first `##`
        heading), reusing is_placeholder_scalar for concreteness.
      - surface-map-check.py gains a byte-identity check per checked file
        (repo-wide via `git ls-tree -r <candidate>` blob-SHA collisions, and
        against a cached-plugin directory passed by flag, not hardcoded) and
        a `generated-copy` SURFACE target that requires the generating
        command and a proof the file exists at candidate.
      - A one-line consumer-exists check joins kc-ship-flow's `verified`
        stage: the brief's `consumer:` value (a path or symbol) is shown to
        exist at the candidate SHA.
    testing:
      - profile-contract-loader.test.py: the two closed PRs' briefs (#446,
        #450), replayed without bite:/consumer:, are refused; the merged
        #445/#448/#451 briefs pass once the two lines are added (AC-1).
      - surface-map-check fixtures reproduce #446's fixture copies
        (scripts/fixtures/pr-merge-released-body/adopter-0.27.0-pr-merge.md)
        and #450's (kc-dev-flow/scripts/fixtures/adopter-contract-test/
        conforming/docs/dev/_mods/pr-merge.md) as refused; a SURFACE
        generated-copy line naming the real `cp`/generation command passes
        (AC-2).
      - A dry-run fixture reproducing the r3 questions log's two closures
        (a candidate where the brief's consumer path/symbol is absent)
        reproduces as a refusal (AC-3).
  scope_boundary: >
    No change to references/kernel.md Minimal necessity wording (Non-goal);
    no retroactive edit of merged r3 briefs beyond the AC-1 fixture
    (Non-goal); no new receipt, harness, or LOC gate (AC-4) — the byte-identity
    and consumer-exists checks are refusal conditions inside the two existing
    scripts and the existing run-batch verification step, not new artifacts.
  semantics_unchanged: false
  observable_semantics_changed: >
    Brief admission additionally refuses a brief missing a concrete bite:/
    consumer: line (new refusal, AC-1). surface-map-check.py additionally
    refuses a changed file byte-identical to another repo file or a cached-
    plugin file without a generated-copy SURFACE declaration (new refusal
    and new SURFACE target vocabulary, AC-2). kc-ship-flow's verified stage
    additionally refuses when the brief's named consumer does not exist at
    the candidate (new refusal, AC-3). No existing passing brief, diff, or
    batch changes outcome unless it falls into one of these three new
    refusal conditions.
  decision:
    authority: "Captain batch approval, 2026-09-15, 「r4 現在開」 (conn recorded in this entity's backlog gate resolution; batch conn already accepts pilot, per dispatch instructions)"
    at: "2026-09-15T00:00:00Z"
```

## Ideation: shape

### AC-1 target correction (surfaced, resolved without route-back)

The brief names `plan-lint.py` first, with a parenthetical fallback: "(or the
backlog-gate check the package already runs)". `plan-lint.py`
(`docs/plan-flow/plan-lint.py`) and its `admission.py` (`la.live_item`,
`la.delivery_binding`, rule "L4 admission") operate exclusively on a Linear
Project GraphQL snapshot — there is no code path from
`docs/dev/.spacedock-state/*.md` into either file. `retire-the-provider-backed-
planning-path` (#444) already landed (`status: done`, completed
2026-09-14T15:42:21Z — seven hours before this brief was opened) and made
`docs/dev`'s only intake a committed brief; the actual "backlog-gate check the
package already runs" is `kc-dev-flow/scripts/profile-contract-loader.py`'s
`validate_admission_brief()` (line 491), documented in `docs/dev/README.md`'s
Local Profile block. Because the parenthetical already anticipates exactly
this substitution, this is read as AC-1's intended target, not a change of
scope needing the brief's own route-back clause (which covers a *future* move
away from `profile-contract-loader.py`, not the one that already happened
before the brief existed).

### AC-1 mechanism: profile-contract-loader.py

`validate_admission_brief(path, profile)` (`kc-dev-flow/scripts/profile-
contract-loader.py:491-567`) already requires exactly one concrete instance of
each `DEVELOPMENT_BRIEF_SECTIONS` heading (`Accepted outcome`, `Non-goals`,
`Acceptance criteria`) via a per-heading regex/placeholder check
(lines 527-540), reusing `is_placeholder_scalar` (line 467). The `bite:` and
`consumer:` lines are not headed sections — in both existing examples
(`boot-names-delivery-order-and-forbidden-actions.md:67,69`, `close-roster-is-
the-fence-and-captain-stopped-validates.md:77`) they are plain-text lines in
the preamble, the prose block between the frontmatter's closing `\n---\n`
(already located at line 501's `frontmatter_end`) and the first `## ` heading.
The new check is one added block in the same function, before the
`## Acceptance evidence` guard (line 523): compute the preamble span (from
`frontmatter_end + 5` to the first `^## ` match), then require a `^bite:`
line and a `^consumer:` line in that span, each non-placeholder via
`is_placeholder_scalar`, raising `ContractError` naming which line is missing
or placeholder. No new file, no new CLI flag — same function, same call site
(`--validate-admission`, already wired at lines 898-905/1010-1029).

### AC-2 mechanism: surface-map-check.py

`surface-map-check.py`'s per-file loop (`for path in checked:`, lines
240-258) already looks up each changed file's `SURFACE:` line
(`parse_surface_lines`, line 105; format `path -> target | without_it |
removed`) and validates the target against `target_problem()` (line 142) and
the without-it pair against `without_it_binds()` (line 154). The byte-identity
refusal is a new check added inside that same loop, after the existing
`entry = surface_map.get(path)` lookup (line 241): for each checked path,
resolve its blob at the candidate SHA and test for a collision two ways —
(a) repo-wide, via `git ls-tree -r <candidate_sha>` (the blob SHA in that
output *is* the git-blob-hash of the content, so a second path sharing the
same blob SHA is a byte-identical repo file, no per-file hashing needed);
(b) against a cached-plugin directory, by computing the git-blob-style hash
(`blob <len>\0<content>`, sha1) of each file under that directory and
comparing to the candidate blob's hash. #446's `scripts/fixtures/pr-merge-
released-body/adopter-0.27.0-pr-merge.md` and #450's `kc-dev-flow/scripts/
fixtures/adopter-contract-test/conforming/docs/dev/_mods/pr-merge.md` are the
two replay fixtures for (a) — both are claimed-byte-identical copies of
`docs/dev/_mods/pr-merge.md` at their respective candidates. The escape hatch
is a new SURFACE target literal, `generated-copy:<name>`, alongside the
existing `LITERAL_TARGETS` (line 49) and `LIFECYCLE_TARGET_RE` (line 48) in
`target_problem()`; a matched target of that shape is accepted only when the
existing `without_it` field carries the generating command (e.g. `cp docs/
dev/_mods/pr-merge.md scripts/fixtures/.../adopter-0.27.0-pr-merge.md`) —
overloading the existing three-field SURFACE grammar per-target the same way
`without_it_binds()` already special-cases the `removal` target (line 155),
rather than adding a fourth pipe-delimited field.

**Notable decision surfaced for build (open fork):** the cached-Spacedock-
plugin comparison needs a directory path, and the repo has no existing
convention for locating it from inside a script (grep across the repo for
`plugins/cache/spacedock` found nothing) — hardcoding `~/.claude/plugins/
cache/spacedock` would violate the "no hidden machine dependency" rule
(a Codex install or CI runner does not share that path). Recommend a required
`--plugin-cache-dir` flag with no default, so the caller (the FO or CI
recipe) supplies the actual install path explicitly rather than the script
guessing; build should confirm this against how `kc-plugin-forge`'s
sanitize-check or version-parity-check (if either already takes a similar
flag) resolves the analogous problem, to reuse a convention rather than
invent a second one.

### AC-3 mechanism: kc-ship-flow run-batch

`kc-ship-flow/skills/run-batch/SKILL.md` step 3 (`verified`) is the one call
site: it currently runs only `kc-ship-flow/scripts/e2e-gate.py --root <code
checkout> --flows docs/ship/flows <targets>`, which reads a `kc-plan-receipt`/
`kc-ship-close-receipt` pair scoped to the whole batch's milestone, not a
single task's committed brief — there is no per-brief `consumer:` field in
that receipt shape. `kc-ship-flow/scripts/` has no existing consumer-existence
check (`grep -rn "accept-by-evidence|consumer"` over the package found
nothing).

**Notable decision surfaced for build (open fork):** the one-line check
does not fit inside `e2e-gate.py`'s receipt-pair signature without changing
that signature, which the brief does not ask for. Recommend a small sibling
script (e.g. `kc-ship-flow/scripts/consumer-exists-check.py <brief.md>
<candidate-root-or-sha>`) that step 3 runs once per task in the batch,
alongside (not inside) `e2e-gate.py` — SKILL.md step 3 gains one added
sentence naming the new script and its per-task invocation. Falsifiable by
the r3 questions log's two closures: replaying #446's candidate (the
consumer named in its brief — one sentence in `MIGRATION.md` — is absent
because the check was removed with adopter-side checks) and #450's candidate
(its only measured bite/consumer overlap was similarly thin) as fixtures
should both refuse.

### Accepted journey (per mechanism)

1. **AC-1** — A worker or the backlog gate runs `profile-contract-loader.py
   --validate-admission` on a new Pilot/Production brief. DESIGNED: the
   preamble-scan addition refuses a brief whose `bite:` or `consumer:` line
   is absent or placeholder, naming which.
2. **AC-2** — `surface-map-check.py` runs in the implementation-exit gate on a
   candidate diff. DESIGNED: for each checked changed file, a blob-SHA
   collision against the repo tree at candidate, or against a supplied
   plugin-cache directory, refuses unless the file's SURFACE line uses the
   `generated-copy:<name>` target with the generating command in `without_it`.
3. **AC-3** — kc-ship-flow's `verified` stage runs `e2e-gate.py` and (new)
   the consumer-exists check per task. DESIGNED: a task whose brief names a
   consumer absent at the candidate SHA is refused with a one-line reason
   before the batch reaches the `uat` gate.
4. Unhappy paths already covered above per mechanism: missing/placeholder
   `bite:`/`consumer:` (AC-1); an unexcused byte-identical copy (AC-2); a
   named consumer that does not exist at candidate (AC-3).

Semantics changed: yes — see `observable_semantics_changed` in the Work
profile receipt above; each is a new refusal condition on an existing check,
not a new check surface.

### Explicit non-goals (carried from the brief)

- No change to `references/kernel.md` Minimal necessity wording.
- No retroactive edit of merged r3 briefs beyond adding the two lines as the
  AC-1 fixture.
- No new receipt, harness, or LOC gate (AC-4) — confirmed both mechanisms
  above are refusal additions inside existing scripts/steps, not new files
  that would themselves need a receipt.

### Stop numbers for this slice

- 1 function touched for AC-1 (`validate_admission_brief`), 1 file.
- 1 loop + 1 vocabulary table touched for AC-2 (`surface-map-check.py`'s
  per-file loop and `LITERAL_TARGETS`), 1 file, plus fixture additions.
- 1 new small script + 1 SKILL.md sentence for AC-3 (open fork: script name
  and whether it's invoked from SKILL.md or from `e2e-gate.py` itself is
  build's call, not a broad-scale redesign).
- Two open forks flagged above (plugin-cache-dir flag; consumer-exists script
  placement) are the two places implementation could run away past a single
  integrated slice; both are named, neither is designed for production scale.

### File-level "where it touches"

| File | Touches | Lines now | Lines after (est.) | Reconciled against journey |
|---|---|---|---|---|
| `kc-dev-flow/scripts/profile-contract-loader.py` | `validate_admission_brief()` (491-567) gains a preamble-scan block before the `## Acceptance evidence` guard (523). | 567 (full file, but function spans 491-567) | +10-15 | Step 1. |
| `kc-dev-flow/scripts/profile-contract-loader.test.py` | New assertions: #446/#450 briefs replayed without bite:/consumer: refused; #445/#448/#451 briefs pass once added. | (existing) | +15-25 | Proves step 1. |
| `kc-dev-flow/scripts/surface-map-check.py` | New byte-identity helper + call site inside `for path in checked:` (240-258); `LITERAL_TARGETS`/`target_problem()`/`without_it_binds()` gain the `generated-copy:<name>` case. | 279 | ~300-320 | Step 2. |
| New fixtures under `kc-dev-flow/scripts/fixtures/surface-map/` | Not copies of #446/#450's actual files — small hand-written fixtures reproducing the byte-identity shape (a tracked file whose blob matches another tracked file) without copying real repository content, per AC-4/`references/kernel.md`'s no-copy hygiene. | 0 | ~20-40 per fixture | Proves step 2 against the #446/#450 shape without a literal copy. |
| `kc-ship-flow/skills/run-batch/SKILL.md` | Step 3 (`verified`) gains one sentence naming the new consumer-exists check and its per-task invocation. | 55 | ~57-60 | Step 3. |
| New `kc-ship-flow/scripts/consumer-exists-check.py` (open fork, see above) | New file: reads a task's brief `consumer:` line, checks the named path/symbol exists at the candidate SHA. | 0 | ~40-60 | Step 3. |
| `kc-ship-flow/scripts/consumer-exists-check.test.py` (new) | Fixtures reproducing the r3 questions log's two closures (#446, #450) as refusals. | 0 | ~30-50 | Falsifies step 3. |

## Stage Report: ideation

- DONE: Work profile receipt recorded: `## Work profile receipt` with schema kc-dev-flow-work-profile/v3, selected pilot-product-slice, route [shape, build, verify-deliver], grounded in this brief's accepted outcome/ACs/non-goals.
  See "Work profile receipt" above; basis, obligations, scope_boundary, and observable_semantics_changed all cite AC-1/AC-2/AC-3/AC-4 and the Non-goals directly.
- DONE: AC-1/AC-2 mechanism shape: name exactly where plan-lint.py's brief-admission check gains the bite:/consumer: refusal, and where surface-map-check.py gains the cross-repo/cached-plugin byte-identity refusal (SURFACE: escape hatch), demonstrated as a concrete plan against #446/#450, before implementation.
  Corrected the target first: #444 (retire-the-provider-backed-planning-path) landed 2026-09-14T15:42:21Z, seven hours before this brief opened, so `plan-lint.py`/`admission.py` have no code path from `docs/dev/.spacedock-state/*.md` (confirmed by grep — their only reader is a Linear GraphQL snapshot). AC-1's own parenthetical ("the backlog-gate check the package already runs") already names the real target, `profile-contract-loader.py:validate_admission_brief()` (491-567); named the exact insertion point (preamble scan before line 523) and the two replay fixtures. AC-2's mechanism named as a new check inside `surface-map-check.py`'s existing per-file loop (240-258) plus a new `generated-copy:<name>` SURFACE target beside `LITERAL_TARGETS` (49); grounded against #446's `scripts/fixtures/pr-merge-released-body/adopter-0.27.0-pr-merge.md` and #450's `kc-dev-flow/scripts/fixtures/adopter-contract-test/conforming/docs/dev/_mods/pr-merge.md`, both confirmed present via `gh pr diff --name-only`. Surfaced one open fork for build: the cached-plugin comparison needs a `--plugin-cache-dir` flag, not a hardcoded path (no existing convention found in-repo).
- DONE: AC-3 shape: name where kc-ship-flow's run-batch verification step gains the one-line consumer-exists check.
  `kc-ship-flow/skills/run-batch/SKILL.md` step 3 (`verified`) is the call site; `e2e-gate.py`'s receipt-pair shape has no per-task consumer field, so recommended a small sibling script (`consumer-exists-check.py`) run alongside it per task rather than folded into `e2e-gate.py` — flagged as an open fork for build, not decided here.

### Summary

Ideation's main finding is that AC-1's named target (`plan-lint.py`) was already stale at brief-open time — #444 moved brief admission to `profile-contract-loader.py` seven hours earlier — but AC-1's own parenthetical anticipated exactly this, so no route-back was needed, just naming the real function and insertion point. AC-2 and AC-3 mechanisms are named with exact files/functions/line ranges and grounded against the two closed PRs' actual changed-file lists (via `gh pr diff`), each with one open fork surfaced for build to resolve (a plugin-cache-dir flag; a new sibling script vs. extending `e2e-gate.py`) rather than pre-deciding either.

## Stage Report: implementation

- DONE: AC-1 `profile-contract-loader.py:validate_admission_brief()` refuses a brief missing `bite:` or `consumer:`, naming the line.
  Preamble scan (`frontmatter_end+5` to first `^## `) added before the `## Acceptance evidence` guard; reuses `is_placeholder_scalar`. `kc-dev-flow/scripts/profile-contract-loader.py` commit 5537e44c.
- DONE: AC-1 fixtures replay #446/#450-shaped briefs (hand-authored preambles, not byte-copies) refused; same fixtures pass once `bite:`/`consumer:` lines are added; single-missing and placeholder cases refused naming the field.
  `kc-dev-flow/scripts/profile-contract-loader.test.py` new `write_admission_brief` helper + "admission bite/consumer preamble" block; `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` exits 0 (asserts a change reverting the preamble-scan block back out would make these refusals disappear — the fixtures have no other check that would otherwise reject a missing-bite/consumer brief).
- DONE: AC-2 `surface-map-check.py`'s per-file loop refuses a changed file byte-identical to another repo file or a cached-plugin file, unless SURFACE declares `generated-copy:<name>` with a non-empty generating command.
  New `git_blob_map()` (repo-wide `git ls-tree -r` blob-SHA collision) and `hash_plugin_cache_dir()` (git-blob-style sha1 over an optional `--plugin-cache-dir`, no hardcoded path); `GENERATED_COPY_TARGET_RE` wired into `target_problem()`. `kc-dev-flow/scripts/surface-map-check.py` commit 5537e44c.
- DONE: AC-2 replay fixtures for #446's and #450's diff shape (hand-written, not literal copies per kernel no-copy hygiene) refused; the same shape declared `generated-copy:` passes; a `--plugin-cache-dir` variant of both cases behaves the same.
  Four new fixtures under `kc-dev-flow/scripts/fixtures/surface-map/`; `scripts/kc-dev-flow-contract-test.py` extends the existing surface-map test block (repo-wide + plugin-cache scenarios); `python3 scripts/kc-dev-flow-contract-test.py` exits 0 (a fixture whose SURFACE target reverts from `generated-copy:` to a plain `AC-1` would flip the "declared" case from pass to refused, proving the escape hatch is load-bearing, not a tautology).
- DONE: AC-3 `kc-ship-flow/skills/run-batch/SKILL.md` step 3 (`verified`) gains one line showing the brief's named consumer exists at the candidate.
  One sentence appended after "The exact target arguments are a separate task's to fix." — narrowed to the dispatch checklist's actual scope (one line), not ideation's floated new `consumer-exists-check.py` sibling script, which would have been new-script scope beyond this task's checklist.
- DONE: AC-4 confirm no new receipt/harness/LOC gate was added.
  Re-read the full diff (`git show 5537e44c --stat`): two refusal-condition additions inside existing scripts' existing call sites, one added SKILL.md sentence, four small fixture files, and their test coverage — no new JSON/YAML receipt schema, no new CI workflow, no LOC-counting gate; `references/kernel.md` untouched (Non-goal).

### Summary

Implemented all three mechanisms exactly where ideation named them: a preamble bite:/consumer: scan in `validate_admission_brief()`, a byte-identity collision check (repo-wide and optional cached-plugin) in `surface-map-check.py`'s existing per-file loop with a new `generated-copy:<name>` SURFACE escape hatch, and one added sentence in kc-ship-flow's `run-batch` SKILL.md. AC-3 was implemented at the dispatch checklist's narrower scope (one line, no new script) rather than ideation's floated sibling-script option, since the dispatch's own AC-3 wording asked only for the SKILL.md line. Both `kc-dev-flow/scripts/profile-contract-loader.test.py` and `scripts/kc-dev-flow-contract-test.py` pass (exit 0) after the change, and `python3 -m py_compile` succeeds on both touched scripts. Work committed on `spacedock-ensign/admission-asks-who-was-bitten-and-who-will-run-it` at 5537e44c.

## Stage Report: validation

- DONE: Local verification: profile-contract-loader.test.py and kc-dev-flow-contract-test.py both exit 0 at the exact candidate revision; re-run them fresh (not reused from the implementation report) and cite pass/fail.
  Both re-run fresh at candidate `5537e44c9e80e364cd8a7d9e7cbeb2d71cb067a9` in the worktree: `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` → all 6 suites PASS, exit 0 (a reverted preamble-scan block would flip the "admission bite/consumer preamble" suite to FAIL). `python3 scripts/kc-dev-flow-contract-test.py` → PASS, exit 0 (a reverted byte-identity block would flip the surface-map fixture assertions).
- DONE: Draft PR via the pr-merge mod: push the branch to origin and open a Draft PR whose body has all four headings present with items or "none" (What changed / Evidence / Residuals / without-it unanswered), a `Candidate: <sha>` line, a split-root audit link to the spacedock-state/dev branch's committed entity file, and a line naming who runs the change after merge; set the entity's `pr:` field to the bare PR number and commit.
  Preflighted `git merge-tree --write-tree origin/main 5537e44c` clean (no conflict markers), pushed `5537e44c9e80e364cd8a7d9e7cbeb2d71cb067a9` to `refs/heads/spacedock-ensign/admission-asks-who-was-bitten-and-who-will-run-it`, then `gh pr create --draft` opened https://github.com/iamcxa/kc-claude-plugins/pull/457. Body carries all four headings (Residuals: none; without-it unanswered: none), `Candidate: 5537e44c9e80e364cd8a7d9e7cbeb2d71cb067a9`, audit link `[gzr](/iamcxa/kc-claude-plugins/blob/ce2fbe4bc5a26ed6c4680504b9c87256df8a0044/admission-asks-who-was-bitten-and-who-will-run-it.md)` (spacedock-state/dev HEAD at push time), and a "Runs after merge" line naming the next Development Brief's backlog admitter and the ship FO's run-batch verification. `pr` field set to `457` via `spacedock status --set`.
- DONE: Re-confirm AC-1..AC-4 hold at the candidate: no kernel/references/kernel.md edit; no new receipt/harness/LOC gate; the two new checks are refusal conditions inside existing scripts' existing call sites.
  `git diff main...5537e44c --stat` at candidate: 9 files changed (4 fixtures, `profile-contract-loader.py`/`.test.py`, `surface-map-check.py`, `kc-ship-flow/skills/run-batch/SKILL.md`, `scripts/kc-dev-flow-contract-test.py`) — `references/kernel.md` not present in the diff (AC-4 kernel clause holds). No new JSON/YAML receipt schema, CI workflow, or LOC-counting file appears in the diff; the two new refusal conditions (bite:/consumer: preamble scan, byte-identity collision) live inside `validate_admission_brief()`'s and `surface-map-check.py`'s existing per-file loop, and AC-3's line is one added SKILL.md sentence at the existing `verified` step — no new call site (AC-1/AC-2/AC-3/AC-4 all hold).

### Summary

Re-ran both test suites fresh at candidate 5537e44c and both exit 0. Pushed the candidate SHA to a new remote branch and opened Draft PR #457 with the required four-heading body, Candidate line, split-root audit link, and runs-after-merge line; set `pr: 457` on the entity. Confirmed the diff touches no kernel file and adds no new receipt/harness/LOC gate — both new checks are refusal additions inside the two existing scripts' existing call sites, consistent with AC-1..AC-4.
