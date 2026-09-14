---
title: "kc-journey-map's typecheck has been red since #417 and nothing reports it"
status: ideation
source:
product: kc-journey-map
planning-window:
planning-outcome:
sprint: journey-map-typecheck-red
sprint-readiness: ready
started: 2026-09-14T09:15:57Z
completed:
verdict:
worktree:
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
