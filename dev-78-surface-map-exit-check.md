---
title: "kc-dev-flow reads the candidate diff: a surface-to-obligation check at implementation exit"
status: implementation
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: S9
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue: DEV-78
pr:
mod-block:
id: 1t3634tfkq3v9tr3r3gcbtw8
gates:
    version: 1
    records:
        - id: gate:1t3634tfkq3v9tr3r3gcbtw8:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:1t3634tfkq3v9tr3r3gcbtw8-backlog-1
              briefing:
                id: briefing:1t3634tfkq3v9tr3r3gcbtw8:backlog:attempt-1:revision-1
                digest: sha256:0aa69f172d444735b3b6298368ad389db6e61e73aeadb6427c496deaff973f02
                room-ref: ./dev-78-surface-map-exit-check/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:1t3634tfkq3v9tr3r3gcbtw8:backlog:1
                briefing: briefing:1t3634tfkq3v9tr3r3gcbtw8:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-03T03:22:42.790072Z"
                decision: approve
                reason: Captain admitted dev-78-surface-map-exit-check as a standalone item in sprint S9 and authorized its dispatch.
                conn:
                    quote: 現在派工，同意你的分工方式
                    source: Captain chat, this conversation, 2026-09-03, approving dispatch of DEV-78 to a cloud worker and DEV-79 to the local FO
              application:
                target-stage: ideation
                state: consumed
---

## The problem

kc-dev-flow's kernel requires minimal necessity: every retained surface maps to an accepted goal, a falsifier, a safety boundary, or a lifecycle obligation, and a check is evidence only once seen to fail. Nothing in kc-dev-flow reads the candidate diff, so this is enforced by worker self-report only. In the DEV-67 POC (2026-09-03) three cloud workers each reported the same self-check (`python3 scripts/kc-dev-flow-contract-test.py`) as TESTS and WITHOUT_IT_COMMAND, none mapped a new file to an AC, and a ship-side Codex review found a P1 in every candidate (a regex YAML parser skipping quoted values, prose pins covering half a change, credentials not stripped, a shared worktree leaking state, a fence regex missing evidence). The five scripts in `kc-dev-flow/scripts/` validate receipts, contracts, and planning snapshots; none reads `git diff`.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  route: [shape, build, verify-deliver]
  basis: One deterministic script plus contract sentences used by this repository's own First Officer at implementation exit; no adopter-visible release or rollback obligation.
  obligations:
    architecture: [Deterministic diff-to-Evidence comparison; no model call, no harness; profile depth read from the receipt]
    implementation: [Add kc-dev-flow/scripts/surface-map-check.py and name it in the Pilot and Production build contracts; pin the POC retained-only sentence]
    testing: [AC-1 seen to fail on DEV-66 round-0; AC-3 unknown-AC refusal; contract-test mutation runs for each naming sentence]
  scope_boundary: No execution of without-it commands, no kernel wording change, no enforcement on disposable POC surfaces.
  semantics_unchanged: true
```

## Accepted outcome

One script, `kc-dev-flow/scripts/surface-map-check.py <base-sha> <candidate-sha> <evidence-file>`, lists every file the candidate adds or changes (excluding tests and fixtures under a declared pattern) and requires the worker's Evidence block to carry one `SURFACE:` line per file naming the AC, falsifier, safety boundary, or lifecycle obligation it serves plus one without-it command and removed-variant pair for that surface; a surface with no line, or a line naming an AC that does not exist in the Brief, exits 1 naming the surface. Profile depth: POC checks only surfaces the receipt marks retained; Pilot checks every non-test surface; Production checks every changed file against the shape contract's changed-file-to-obligation mapping. The build contracts for Pilot and Production name this script as an implementation-exit check, and the check has been seen to fail on a DEV-67 candidate (DEV-66 at 4ce46967, whose PyYAML parser mapped to no AC).

## Non-goals

* Do not run the without-it commands; `scripts/ship-flow/without-it.sh` owns execution. This script checks that each surface declares one.
* Do not change the kernel wording; the kernel already states the obligation, this is its enforcement point.
* Do not add a generic harness, a code-review call, or a model call; deterministic file-list comparison only.
* Do not enforce on POC surfaces the receipt marks disposable.

## Acceptance evidence

* **AC-1 **`surface-map-check.py` exits 1 naming `scripts/ship-flow/parse-execute-external.py` when run on DEV-66's round-0 candidate 4ce46967651c25234f1ed01b18e95d1fdfad2ff5 against base bda45e6bb2716d9276d0542b7c11edd2014ab1be with that round's Evidence block; the run is recorded.
* **AC-2** The same script exits 0 on a candidate whose Evidence block carries a `SURFACE:` line for every non-test changed file; a fixture Evidence block and its run are recorded.
* **AC-3** A `SURFACE:` line naming `AC-9` on a Brief that has three ACs exits 1 with `unknown AC`; the run is recorded.
* **AC-4** Pilot and Production build contracts name the script at implementation exit, and the contract test reddens when either naming sentence is removed; the mutation runs are recorded.
* **AC-5** The POC build contract states that the check applies only to retained surfaces; the contract test pins that sentence.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

## Measurement

Not yet measured.
