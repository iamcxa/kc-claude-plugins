---
id: 6zjg1gnq3dmtk2dsny8k4m3s
title: Make CI actually run the tests this monorepo already has
status: backlog
source: captain directive, 2026-07-26, after discovering during 3t's validation that `npm test` runs nowhere in CI
started:
completed:
verdict:
worktree:
issue:
pr:
design:
gates:
    version: 1
    records:
        - id: gate:6zjg1gnq3dmtk2dsny8k4m3s:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:6zjg1gnq3dmtk2dsny8k4m3s-backlog-1
              briefing:
                id: briefing:6zjg1gnq3dmtk2dsny8k4m3s:backlog:attempt-1:revision-1
                digest: sha256:eff8e8fbbb89753e7a6949b3eafe2a0b027761b595346e51a763cf906eb088a1
                request-digest: sha256:095de7b96f5a07ccf7a6fbbd3ac0314be51f543ea3bccb69aabc8ed2e47d93d2
                room-ref: ./monorepo-ci-test-strength/review/backlog/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-08-23T04:20:09.11807Z"
                reason: The presented recommendation rested on kc-nightwatch's 49 unrunnable test files being the residual work. The Captain states kc-nightwatch is deprecated, which removes that residual and leaves a materially smaller question, so the open attempt is stale before decision and a successor will be prepared at the re-scoped shape.
---

## Problem

The repo has 71 test files. **61 of them (86%) belong to two plugins that no workflow mentions
at all.** Measured against `origin/main` @ `ccaf028`:

| plugin | test files | workflows naming it |
|---|---|---|
| kc-nightwatch | 49 | **0** |
| e2e-pipeline | 12 | **0** |
| kc-pr-flow | 7 | 3 |
| kc-hyperfocus | 3 | 1 |
| kc-plugin-forge | 0 | 0 |
| kc-team-ops | 0 | 0 |

`grep -rn 'npm test' .github/workflows/` returns nothing. The six workflows are
`cross-model-tests`, `kc-hyperfocus-install`, `marketplace-parity`, `release-please`,
`review-architecture-diagrams-tests` and `review-runtime-tests`; between them they run three
`kc-pr-flow` shell suites plus repo-wide schema and version-parity checks. Plugin *behavior* is
otherwise unverified in CI.

The two required checks — version parity and skill-frontmatter lint — verify manifests, not
behavior. So "CI is green" on this repo means "the manifests agree", and a reviewer who reads it
as "the tests passed" is wrong.

## How this surfaced, because the mechanism matters more than the count

`e2e-pipeline`'s 659-test suite passed on the author's MacBook and failed 654/659 on the mac
mini during a validation leg. The cause was `compiler/test/integration.test.js` hardcoding
`/Users/kent/Project/carlove/...`, a path that exists on exactly one machine — filed separately
as [[tracked-tests-hardcode-another-repo]].

That defect had been sitting in a *tracked* test file. Nothing caught it because nothing ran it.
It only appeared when work moved to a second machine. A suite that runs in one place and nowhere
else decays into a suite that only passes in one place, and there is no signal in between.

## What ideation must decide

1. **Which suites are safe to run in CI today.** `kc-nightwatch`'s 49 files and
   `e2e-pipeline`'s 12 have never run on a clean runner; some will fail for environment reasons
   rather than real defects. Expect a triage pass before any gate can be required.
2. **Required versus advisory.** A red check nobody can make green gets routed around within a
   week. Landing these as non-blocking first, then promoting once green, is likely the honest
   sequence — but that is a decision, not a default.
3. **Whether a runner exists per plugin.** `e2e-pipeline` has `package.json` with `npm test`;
   `kc-nightwatch` appears to have neither a package manifest nor a script entry point, so its
   49 files need an invocation path before CI can have one.
4. **Path filtering.** Six plugins in one repo: running everything on every PR wastes minutes,
   but path filters are how a required check silently stops running. `marketplace-parity.yml`
   deliberately has no path filter for exactly that reason; decide consciously either way.

## Value AC candidate, so this does not become ceremony

Not "a workflow exists". Something like: reintroduce a known-good defect (for example, restore
the hardcoded corpus path) on a branch and show CI goes red. A CI lane that cannot be shown to
fail is the same tautology this workflow's proof policy already refuses elsewhere.
