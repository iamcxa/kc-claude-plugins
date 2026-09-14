---
title: "kc-journey-map's typecheck has been red since #417 and nothing reports it"
status: implementation
source:
product: kc-journey-map
planning-window:
planning-outcome:
sprint: journey-map-typecheck-red
sprint-readiness: ready
started: 2026-09-14T09:15:57Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-kc-journey-map-typecheck-red-since-417
issue:
pr:
mod-block:
id: fafrpfqmdc3zqhq8asfbt83r
gates:
    version: 1
    records:
        - id: gate:fafrpfqmdc3zqhq8asfbt83r:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:fafrpfqmdc3zqhq8asfbt83r-backlog-1
              briefing:
                id: briefing:fafrpfqmdc3zqhq8asfbt83r:backlog:attempt-1:revision-1
                digest: sha256:4d7dbe4d4448b4714b1f61fdec26054a509f5d16013d1a34935f518003637811
                room-ref: ./kc-journey-map-typecheck-red-since-417/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:fafrpfqmdc3zqhq8asfbt83r:backlog:1
                briefing: briefing:fafrpfqmdc3zqhq8asfbt83r:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-14T09:15:17.246135Z"
                decision: approve
                reason: Captain approved in chat 2026-09-14 with 「可以」 to the FO's Pilot recommendation, after 「型別檢查修復」 in the same conversation. Pilot rather than POC because AC-3 requires a reverted fix to redden a real pull-request check, which is an evidence round rather than a one-shot exploration; the CI step is justified by a defect that already bit — the typecheck has been red since 3fd2fc59 (#417) and no check reported it.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:fafrpfqmdc3zqhq8asfbt83r:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:fafrpfqmdc3zqhq8asfbt83r-ideation-1
              briefing:
                id: briefing:fafrpfqmdc3zqhq8asfbt83r:ideation:attempt-1:revision-1
                digest: sha256:92c9240fd715c0724aa64abdbfbd7a46bd6a6db4632285100ee3115eaecb7df5
                room-ref: ./kc-journey-map-typecheck-red-since-417/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:fafrpfqmdc3zqhq8asfbt83r:ideation:1
                briefing: briefing:fafrpfqmdc3zqhq8asfbt83r:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-14T09:20:51.682381Z"
                decision: approve
                reason: 'Captain approved the shaping in chat 2026-09-14 with 「一起做」, ruling that the two scope additions the ensign found are in: pin typescript as a devDependency so the CI step runs an installed compiler rather than an unpinned registry fetch, and add kc-journey-map/tsconfig.json to the workflow''s pull_request and push paths filters. The FO''s stated basis was that an unpinned compiler makes the typecheck step itself unreliable. The chosen fix form is lib/records.d.mts; the .d.mts extension was verified empirically against records.d.ts, which left tsc red.'
              application:
                target-stage: implementation
                state: consumed
---

`kc-journey-map/server/client/App.tsx` imports `storyBorder` from `../../lib/records.mjs`, and
nothing under `kc-journey-map/lib` ships a declaration file, so `npx tsc` exits 2 with
`TS7016: Could not find a declaration file for module '../../lib/records.mjs'`. Both the import
line and the missing declaration are present on `origin/main`; `lib/records.mjs` was last touched
by `3fd2fc59` (#417). The POC on PR #440 measured this at `cfb804d` on 2026-09-14
(`mermaid-sequence-companion-has-no-repeatable-check`, receipt AC-1).

Nothing reported it because nothing runs it. `package.json` has no `typecheck` or `build` script,
and `.github/workflows/kc-journey-map-tests.yml` runs only `node --test lib/*.test.mjs` and
`scripts/canvas-smoke.sh`, both server- and model-side. The client has never been compiled in CI.
This is the defect that justifies the check: the typecheck went red in an earlier merge and stayed
red across every PR since, unseen.

## Accepted outcome

`npx tsc` exits 0 on `kc-journey-map`, and a named npm script running it is a step in
`kc-journey-map-tests.yml`, so the next regression fails a PR instead of sitting unread. The fix is
whichever of a hand-written `lib/records.d.ts`, JSDoc types on `records.mjs`, or `allowJs` the
maintainer judges smallest; the declaration is chosen for the module's real exported shape, not to
silence the error.

## Non-goals

* Converting `kc-journey-map/lib` to TypeScript.
* Adding a production bundle step or a browser job to CI.
* Any change to PR #440 or to the Mermaid sequence companion.

## Acceptance criteria

* **AC-1** `npx tsc` in `kc-journey-map` exits 0 on the branch head, with no `skipLibCheck`
  loosening, no `// @ts-ignore`, and no `any` on `storyBorder`'s signature.
* **AC-2** The declared type of `storyBorder` matches what `lib/records.mjs` actually exports;
  a call that violates it fails `tsc`.
* **AC-3** A named npm script runs the typecheck, and a step in `kc-journey-map-tests.yml` runs
  that script. Reverting the declaration fix makes that CI step red in a pull request.
* **AC-4** The added CI cost is stated as a measured number from the job's own timing, not an
  estimate.
* **AC-5** `node --test lib/*.test.mjs` and `bash scripts/canvas-smoke.sh` still pass.
* **AC-6** `typescript` is a `devDependencies` entry in `kc-journey-map/package.json` and is
  present in `package-lock.json`, so the CI typecheck runs an installed compiler. `npx tsc
  --version` after a clean `npm ci`, with the network unavailable to fetch a package, still
  reports a version. Added on the Captain's 「一起做」 ruling, 2026-09-14.
* **AC-7** `kc-journey-map/tsconfig.json` is in both the `pull_request` and `push` `paths` lists of
  `.github/workflows/kc-journey-map-tests.yml`, and a tsconfig-only commit retriggers the job.
  Added on the Captain's 「一起做」 ruling, 2026-09-14.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: >-
    The typecheck has been red since #417 and no check reported it, so the
    repair is small but its guard must be proven by a real pull-request check
    turning red on a reverted fix. That is an evidence round, not a one-shot
    exploration. Scope stays inside kc-journey-map's own build tooling; no
    consumer migrates and no production surface changes.
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - Type lib/records.mjs at its real exported shape; do not loosen tsconfig to pass.
      - Keep lib as JavaScript; a declaration or JSDoc, not a TypeScript conversion.
    implementation:
      - npx tsc exits 0 on kc-journey-map.
      - A named npm script runs the typecheck.
      - kc-journey-map-tests.yml runs that script as a step.
    testing:
      - A call violating storyBorder's declared type fails tsc.
      - Reverting the declaration fix reddens the CI step in a pull request.
      - Existing model tests and canvas-smoke.sh still pass.
      - The added CI cost is a measured number from the job's own timing.
  scope_boundary: >-
    kc-journey-map declaration typing and its typecheck CI step only. Excludes a
    TypeScript conversion of lib, a production bundle step, a browser job, and
    any change to PR #440 or the Mermaid sequence companion.
  semantics_unchanged: true
  promote_when:
    - The fix requires consumers to change configuration or migrate records.
    - The CI step is extended to gate anything beyond this package's typecheck.
```

## Stage Report: ideation

- DONE: Reproduce the defect first.
  `npm ci && npx tsc` at `origin/main` (e3cca913), run from a scratch worktree, exits 2:
  `server/client/App.tsx(6,29): error TS7016: Could not find a declaration file for module
  '../../lib/records.mjs'. ... implicitly has an 'any' type.`
- DONE: Read what lib/records.mjs actually exports.
  13 exports: `richText`, `note`, `releaseLine`, `label`, `pageLink`, `fitHeight`, `indexes`,
  `page`, `STORY_STATUS_COLORS`, `storyBorder`, `storyProgress`, `releaseProgressText`,
  `withStoryStatus`. Only `storyBorder` is imported today (App.tsx:6), called at App.tsx:39 with
  a `TLShape` argument (App.tsx already imports `TLShape` from `tldraw` for sibling code at
  line 35-36).
- DONE: Choose the declaration form.
  Hand-written `lib/records.d.mts` — note the `.d.mts` extension, not `.d.ts`. Empirically
  verified: a `lib/records.d.ts` with the identical content left `tsc` still red with the same
  TS7016 (bundler resolution maps a `.mjs` import to `.d.mts` first); renaming the same content to
  `lib/records.d.mts` made `tsc` exit 0. This is the load-bearing fact that rules out the naming
  a "chosen but standard" .d.ts would silently get wrong.
  JSDoc types on records.mjs: rejected — requires editing the 13-export file being typed, higher
  blast radius than an additive declaration file for one consumed export.
  tsconfig `allowJs`: rejected — pulls all of `lib/*.mjs` (13 modules) into strict-mode checking
  at once, an uncontrolled scope expansion versus typing one call site.
- DONE: Check for the same class of defect elsewhere.
  `grep -rnE "from ['\"].*\.mjs['\"]" server lib --include='*.ts' --include='*.tsx'` returns only
  App.tsx:6. No other class-open import.
- DONE: Name the npm script and CI step.
  Script: add `"typecheck": "tsc"` to `package.json` `scripts`. Precondition found during
  reproduction: `typescript` is not in `package.json`/`package-lock.json` at all — `npx tsc`
  silently network-fetched TypeScript 5.9.3 from the registry rather than running an installed
  binary. Add `"typescript": "^5.9.3"` to `devDependencies` (matching this package's existing
  caret-range convention) so `npm ci` installs it and the CI step runs an installed `tsc`, not an
  uncached `npx` fetch. Workflow step: a new `Typecheck` step in `kc-journey-map-tests.yml`,
  placed after `Preflight` and before `Model tests` (fail fast on a type error before the slower
  model-test suite runs). `paths:` filter gap found: today's filter (`lib/**`, `server/**`,
  `canvas-smoke.sh`, `package.json`, `package-lock.json`, the workflow file itself) omits
  `kc-journey-map/tsconfig.json` — an edit to tsconfig alone would not retrigger the job. Add
  `kc-journey-map/tsconfig.json` to both the `pull_request` and `push` filter lists.
- DONE: State how AC-3's falsifier will be demonstrated.
  On the branch carrying the fix, delete or revert `lib/records.d.mts` (or rename it back to
  `records.d.ts`) and open a PR. Demonstrated concretely in this stage with the reproduction
  worktree: reverting to no declaration file reproduces the original `TS7016` exit-2 failure above;
  reverting to the wrong extension (`records.d.ts`) reproduces the same TS7016 failure. Either
  revert makes the new `Typecheck` CI step fail with that TS7016 line in its log output.
- DONE: Write the shaping report into the entity's ideation room.
  This report. No file under `lib/`, `server/`, `package.json`, `tsconfig.json`, or
  `.github/workflows/` was modified in this repo checkout — all reproduction and falsifier
  commands ran in a disposable `git worktree` at `/tmp/kcjm-typecheck-check` (removed after use),
  never in this workflow's own worktree or the montpellier-v1 checkout.

### Summary

Reproduced TS7016 at `origin/main` (exit 2) and confirmed the fix shape empirically, not just by
reading docs: `lib/records.d.mts` (the `.mjs`-matching extension) with `storyBorder(story: TLShape):
TLShape | null` makes `tsc` exit 0, and a call-site type violation (`storyBorder(42)`) fails `tsc`
with TS2345 — both AC-1 and AC-2's falsifier are demonstrated, not asserted. One class-defining fact
surfaced that the known-facts list didn't have: `typescript` isn't a project dependency at all today,
so an un-pinned `npx tsc` in CI would silently fetch from the registry each run; the build stage
should add it to `devDependencies` alongside the new script and CI step. The `paths:` filter is also
missing `tsconfig.json`.

## Stage Report: implementation

- DONE: AC-1/AC-2 — add `kc-journey-map/lib/records.d.mts` declaring `storyBorder(story: TLShape): TLShape | null`.
  `npx tsc` exits 0 at commit `fb84f89a`; violating probe `storyBorder(42)` failed `TS2345: Argument
  of type 'number' is not assignable to parameter of type 'TLShape'`, then removed (not in diff).
  No `@ts-ignore`, no `any`, `strict`/`skipLibCheck` unchanged.
- DONE: AC-6 — `typescript: ^5.9.3` added to `devDependencies`; range resolves (`npm view
  typescript@5.9.3 version` → `5.9.3`). `npm install` recorded it in `package-lock.json` (15-line
  diff). After `rm -rf node_modules && npm ci`, `npx --offline tsc --version` → `Version 5.9.3`
  with no registry fetch.
- DONE: AC-3 — `typecheck` npm script (`tsc`) added; `Typecheck` CI step added to
  `kc-journey-map-tests.yml` between `Preflight` and `Install pinned Spacedock` (before `Model
  tests`). Local revert of `lib/records.d.mts` reproduces the original TS7016 exit 2. Live CI-red
  demonstration on the pull request is deferred to verify-deliver — pushing a revert/re-add to
  this PR's head was judged out of scope for the implementation checklist per advisor review.
- DONE: AC-7 — `kc-journey-map/tsconfig.json` added to both `pull_request` and `push` `paths`
  lists in `.github/workflows/kc-journey-map-tests.yml`.
- DONE: AC-5 — `node --test lib/*.test.mjs`: 72/72 pass, exit 0. `bash scripts/canvas-smoke.sh`:
  exit 0 (`ok 262 shapes across 5 pages`, `ok round trip clean`).
- DONE: Commit on a feature branch with a Conventional Commit subject scoped to this plugin.
  `fb84f89a` on `spacedock-ensign/kc-journey-map-typecheck-red-since-417`, staged the 4 in-scope
  files only (`lib/records.d.mts`, `package.json`, `package-lock.json`,
  `.github/workflows/kc-journey-map-tests.yml`); no version field touched.
- DONE: Push the branch and open a DRAFT pull request whose body carries the reproduction, the
  `.d.mts` finding, and the AC evidence.
  PR #441 (draft): https://github.com/iamcxa/kc-claude-plugins/pull/441. Not marked ready, not
  merged.
- DONE: AC-4 — CI's measured `Typecheck` step duration, via `gh api
  repos/iamcxa/kc-claude-plugins/actions/jobs/{id}` step timestamps on PR #441: 3s on node 22.13.0
  (job 103924029150, `09:25:36Z`→`09:25:39Z`), 2s on node 24 (job 103924029553,
  `09:25:35Z`→`09:25:37Z`). PR body updated with these numbers via `gh pr edit 441`.
- DONE: Write the implementation receipt with every command, its exit code, and its output
  excerpt.
  `npx tsc` exit 0; probe `storyBorder(42)` exit 2 (TS2345), reverted; `npm install` exit 0;
  `npm run typecheck` exit 0; `node --test lib/*.test.mjs` exit 0 (72 pass); `bash
  scripts/canvas-smoke.sh` exit 0; `rm -rf node_modules && npm ci` exit 0; `npx --offline tsc
  --version` exit 0 (`5.9.3`); `git commit` exit 0 (`fb84f89a`); `git push` exit 0; `gh pr create`
  exit 0 (PR #441).

### Summary

Added `lib/records.d.mts` (the `.mjs`-matching extension, load-bearing per the ideation finding),
pinned `typescript` as a devDependency, added a `typecheck` script and CI step, and added
`tsconfig.json` to the workflow's `paths` filters. All local AC checks (1, 2, 5, 6, 7) pass with
exit-code evidence; AC-4 is a measured CI number from PR #441's own job timing (3s / 2s), not an
estimate. AC-3's local-revert reproduction is demonstrated; its live-CI-red demonstration on a real
pull request is left to verify-deliver rather than pushed to this branch, per advisor review — the
obligation lives in `work_profile.obligations.testing`, not this stage's checklist.
