---
id:
title: release-please excludes workflow-state paths for every plugin
status: ideation
variant: kc-dev-flow-2
profile: prod
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:release-please-exclude-paths:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:release-please-exclude-paths-backlog-1
              briefing:
                id: briefing:release-please-exclude-paths:backlog:attempt-1:revision-1
                digest: sha256:cc5651b4964772c44a55ddeff8de95f71f5c450536eb581f23499da2b9174b2c
                room-ref: ./release-please-exclude-paths/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:release-please-exclude-paths:backlog:1
                briefing: briefing:release-please-exclude-paths:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-16T06:57:25.493101Z"
                decision: approve
                reason: Captain approved profile prod and the admission record's outcome, scope and exclusions.
              application:
                target-stage: ideation
                state: consumed
---

A single empty commit to `main` once bumped all seven plugins minor with the same
changelog line, because release-please's manifest mode attributes a path-less commit
to every package. The repository's own `CLAUDE.md` records the fix and its unfinished
half: every plugin except `kc-dev-flow` carries `exclude-paths`, and `kc-dev-flow`
was to receive it "after `kc-dev-flow-v4.2.0` is tagged". Tags now stand at
`kc-dev-flow-v4.6.0`, so the documented follow-up is overdue and `kc-dev-flow`
remains the one package a path-less commit can still bump.

Adopting this workflow adds a second workflow-state path, `docs/dev2`, of the same
class as the already-excluded `docs/dev`. Whether a `docs/dev2`-only commit actually
reaches release-please attribution is unverified; the adoption PR that introduces
`docs/dev2` is the first observation of it.

## Scope

In scope: `release-please-config.json` only — give `kc-dev-flow` the `exclude-paths`
every sibling package already carries, and extend the excluded set to the second
workflow-state path where evidence shows it is attributed.

Non-goals: no version or manifest edits, no marketplace changes, no new CI job, no
change to any plugin's source, no retirement of the `kc-dev-flow` plugin.

Stop condition: if the evidence shows a `docs/dev2` exclusion is unnecessary, land the
`kc-dev-flow` half alone and record the measurement rather than adding config that
nothing needs.

## Acceptance criteria

**AC-1**: `release-please-config.json` gives the `kc-dev-flow` package a non-empty
`exclude-paths`, and no package that had one loses it.
Verified by: `scripts/version-parity-check.sh` exits 0 on the candidate revision, and
`python3 -c` over the config prints an `exclude-paths` value for every package key.
It would fail if the key were added to the wrong package or a sibling's value dropped.

**AC-2**: The excluded set is decided by measurement, not assumption: the record names
whether a commit touching only a workflow-state path is attributed to a package, and the
config matches that finding.
Verified by: the pinned release-please fixture inside `scripts/version-parity-check.sh`
run against a commit that touches only a workflow-state path, with its resolved package
list captured in the stage report. A config entry with no supporting fixture output fails
this criterion.
