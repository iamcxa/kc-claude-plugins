---
id: g0nx8a1ht539e12e9jm54fbw
title: Extract the journey map into its own publishable plugin
status: implementation
source: captain
product: kc-journey-map
planning-window:
planning-outcome:
sprint: journey-map-poc
sprint-readiness: ready
started: 2026-09-10T04:38:38Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-extract-the-journey-map-plugin
issue:
pr:
mod-block:
gates:
    version: 1
    records:
        - id: gate:g0nx8a1ht539e12e9jm54fbw:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:g0nx8a1ht539e12e9jm54fbw-backlog-1
              briefing:
                id: briefing:g0nx8a1ht539e12e9jm54fbw:backlog:attempt-1:revision-1
                digest: sha256:b47e20f4f1ad241b14c1e741691b9ca7f7b5316f787e7182b0a0c2b03fe18c1d
                room-ref: ./extract-the-journey-map-plugin/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:g0nx8a1ht539e12e9jm54fbw:backlog:1
                briefing: briefing:g0nx8a1ht539e12e9jm54fbw:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-10T04:38:14.224865Z"
                decision: approve
                reason: 'Captain: 開切票,然後切成新的 plugin — and named it kc-journey-map after being told the -flow suffix is reserved for staged workflows. He also ruled the plan line is out of scope for now: focus on finishing journey-map well, integrate with plan later.'
              application:
                target-stage: ideation
                state: consumed
---

## The problem

The journey map lives inside kc-team-ops, which is a team-operations plugin: EM triage,
project pulse, Linear management, cross-model review. Anybody who installs those inherits a
canvas server, a browser client and a node dependency tree they did not ask for. Anybody who
wants only the journey map cannot have it without the rest.

The separation is already clean. Thirty-six files under `lib/`, `server/` and
`skills/kc-journey-map/`, and the only thing in kc-team-ops referencing them is the
`package.json` that exists solely to serve the canvas — which moves too. No other skill in
that plugin touches them.

## Work profile receipt

**Profile:** POC — bounded exploration.

**Next decision:** whether the journey map stands alone as a publishable unit before any
plan-flow integration is attempted.

**Cheapest credible falsifier:** run the repository's own marketplace install test against a
clean HOME. If the new plugin does not resolve and install, it is not publishable.

**Budget:** one worker dispatch. No browser.

**Observable stop point:** both repository gates green — version parity and marketplace
verify — with the new plugin registered and kc-team-ops no longer claiming the journey map.

## Accepted outcome

`kc-journey-map` is a plugin of its own, registered everywhere the repository requires, at
the version policy this repository sets for a new component.

## Non-goals

- No behaviour change. Not one line of rendering, linting or read-back logic changes meaning.
  A move that also fixes something is a move nobody can review.
- No plan-flow integration, no dev task field, no cross-repository evidence. Later items.
- Do not rename the skill. It is `kc-journey-map` inside a plugin of the same name, which
  this repository already does elsewhere.

## Acceptance evidence

**AC-1** `lib/`, `server/`, `skills/kc-journey-map/` and the canvas `package.json` live under
a new top-level `kc-journey-map/`, and nothing under `kc-team-ops/` references them.

**AC-2** The new plugin is registered in every place this repository requires a component:
its own plugin manifest, the marketplace entry, the release-please package config and the
release manifest at this repository's declared initial version. Read the repository's own
CLAUDE.md for the list rather than copying another plugin blindly.

**AC-3** `scripts/version-parity-check.sh` passes. It fails closed on an unregistered plugin
directory, so a half-registered move cannot pass this criterion.

**AC-4** `scripts/marketplace-verify.sh` passes, including the install test from a clean
HOME. This is the criterion that proves publishable rather than merely moved.

**AC-5** kc-team-ops no longer advertises the journey map: its description and keywords drop
the journey, user-journey and figjam terms, and its CHANGELOG is left alone.

**AC-6** The canvas CI workflow's path filters point at the new location, so the tests and
the boot smoke still run when the moved code changes. A workflow whose filter no longer
matches is silently dead, which is worse than a deleted one.

**AC-7** The full test suite and the boot smoke pass from the new location.

## Route-back conditions

Return `poc_outcome` to planning. Publication itself stays release-please's, and the captain's.

## Measurement

Both repository gates, and whether the install test resolves the new plugin from a clean HOME.

## Stage Report: implementation

- DONE: Move the journey map's code, server, skill and canvas package into a new top-level kc-journey-map plugin, changing no behaviour.
  `git mv` for all 36 files (lib/, server/, skills/kc-journey-map/, package.json, package-lock.json, tsconfig.json, vite.config.mts, .gitignore, scripts/canvas-smoke.sh) — commit dc317b5e shows 100% renames with zero content diff on every moved file. `grep -rn 'kc-team-ops' kc-journey-map/` after the move finds only the private npm package name (`kc-team-ops-journey-canvas` in package.json/package-lock.json, unpublished, functionally inert) and one historical test comment in lint.test.mjs describing a past defect — both left as-is rather than silently fixed. Verified the .gitignore/package.json-exists-only-for-the-canvas claim: `grep -rlE 'lib/|server/' kc-team-ops` before the move matched only vite.config.mts, package.json, package-lock.json, canvas-smoke.sh, and the kc-journey-map skill files — claim holds.
- DONE: Register the new plugin everywhere this repository requires a component, and stop kc-team-ops advertising the journey map.
  Read this repo's CLAUDE.md's release-please section rather than copying blindly; used kc-ship-flow (the most recent addition) as the structural template. New `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` under kc-journey-map, a `release-please-config.json` package block with `exclude-paths: ["docs/dev"]` (the documented path-less-commit trap) and all three extra-files targets, `.release-please-manifest.json` entry at the repo's declared initial-version `0.1.0`, and a `marketplace.json` entry. kc-team-ops's `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` (including interface shortDescription/longDescription) and README.md no longer mention journey/user-journey/figjam; CHANGELOG.md untouched.
- DONE: Run both repository gates — version parity and marketplace verify with its clean-HOME install test — plus the full suite and the boot smoke from the new location.
  `./scripts/version-parity-check.sh` exit 0, kc-journey-map row `ok` across release/plugin.json/market/codex. `./scripts/marketplace-verify.sh` exit 0 — L0 parity, L1 schema, and L2 clean-`$TEMP_HOME` install all PASS for all 9 plugins including kc-journey-map. `node --test lib/*.test.mjs` from `kc-journey-map/`: 44/44 pass (assertions span function-map lane drawing, journey-lint's three evidence checks including the executable-vs-prose-only distinction, read-back conflict detection, and the >61-shape index-key regression) — a broken relative import after the move would fail every one of them. `bash scripts/canvas-smoke.sh` from the new location: server boots, renders 141 shapes across 5 pages, round-trip reports clean. `npm run doctor` reports the two canvas ports in use by a concurrent session on this host (unrelated to the move — canvas-smoke.sh picks its own port via `JOURNEY_API_PORT=0` and is unaffected, confirmed by its own pass above).

### Fetch commands used

    /Users/kent/.local/bin/spacedock dispatch show-stage-def --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/docs/dev --stage implementation

### Summary

Extracted kc-team-ops's journey map (lib/, server/, skills/kc-journey-map/, canvas package) into a new top-level `kc-journey-map` plugin via `git mv`, with no rendering/linting/read-back logic changed — verified by zero-diff renames and 44/44 passing tests plus a passing boot smoke from the new location. Registered kc-journey-map as a release-please component at the repo's 0.1.0 initial-version policy across both plugin manifests and marketplace.json, repointed and renamed the canvas CI workflow (`kc-journey-map-tests.yml`), and stopped kc-team-ops advertising the journey map in its manifests and README (CHANGELOG left alone). Both repository gates (version-parity-check.sh, marketplace-verify.sh) pass. One naming residual left unfixed and reported rather than silently changed: the canvas's private npm package name still reads `kc-team-ops-journey-canvas`.
