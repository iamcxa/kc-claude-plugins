---
id: w8z5xrcexs9k1qq7xrwzx5bk
title: Add a manual Cycle-Release admission path
status: implementation
source: https://github.com/iamcxa/kc-claude-plugins/issues/305
product: kc-dev-flow
planning-window: Iteration 2
planning-outcome: kc-dev-flow Cycle-Release Admission Pilot
sprint: S6
sprint-readiness: ready
started: 2026-08-28T00:05:28Z
completed:
verdict:
worktree:
issue: "#305"
pr:
mod-block:
gates:
    version: 1
    records:
        - id: gate:w8z5xrcexs9k1qq7xrwzx5bk:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:w8z5xrcexs9k1qq7xrwzx5bk-backlog-1
              briefing:
                id: briefing:w8z5xrcexs9k1qq7xrwzx5bk:backlog:attempt-1:revision-1
                digest: sha256:090dcffcf46754187a66e77c0d0b88390545c113bbb5e5522feb26d87a9e6fca
                request-digest: sha256:9ed5cf164977e3553f12d76b4bc304e7d22083ab853405caff94b34c1a0a550e
                room-ref: ./manual-cycle-release-admission-path/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:w8z5xrcexs9k1qq7xrwzx5bk:backlog:1
                briefing: briefing:w8z5xrcexs9k1qq7xrwzx5bk:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-08-28T00:04:38.624069Z"
                decision: approve
                reason: Captain approved the admitted direction and instructed future issues to omit the redundant Human-readable release brief wrapper, start directly with The problem, and retain the agent execution contract.
              application:
                target-stage: ideation
                state: consumed
        - id: gate:w8z5xrcexs9k1qq7xrwzx5bk:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:w8z5xrcexs9k1qq7xrwzx5bk-ideation-1
              briefing:
                id: briefing:w8z5xrcexs9k1qq7xrwzx5bk:ideation:attempt-1:revision-1
                digest: sha256:2115bf236c6997cb43ce868d765bca267845fb8e6805953f00f5e822117abded
                request-digest: sha256:2efac7a3f2ef2390158d775dded2eabe4dff041ec995cdd39840df7c9e392209
                room-ref: ./manual-cycle-release-admission-path/review/ideation/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-08-28T00:24:23.244715Z"
                reason: The prepared ideation briefing cannot be presented because ac-scan found no required Acceptance criteria section; preserve the six shaped checks and repair only their scanner-readable heading and AC labels.
            - id: gate-attempt:w8z5xrcexs9k1qq7xrwzx5bk-ideation-2
              briefing:
                id: briefing:w8z5xrcexs9k1qq7xrwzx5bk:ideation:attempt-2:revision-1
                digest: sha256:944c9e9743399a545d3aefd074a2d9032e65acf9be94ed65cae117cce50a96ae
                request-digest: sha256:fd8584a5796c7d41bf89decdfb66f7206b52f47bac6097c1a9ffcc57eaa74229
                room-ref: ./manual-cycle-release-admission-path/review/ideation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:w8z5xrcexs9k1qq7xrwzx5bk:ideation:2
                briefing: briefing:w8z5xrcexs9k1qq7xrwzx5bk:ideation:attempt-2:revision-1
                by: person:captain
                at: "2026-08-28T00:29:36.288342Z"
                decision: approve
                reason: 'Captain approved the shaped Pilot slice: one manual admission journey, six falsifiable acceptance criteria, seven existing touch files, and the recorded stop numbers.'
              application:
                target-stage: implementation
                state: consumed
---

## Problem

kc-dev-flow separates planning authority from execution authority in its kernel, but the everyday handoff still depends on a long interactive session. Product shaping, profile selection, implementation, and verification can happen together, making progress difficult to read and forcing repeated Captain steering after execution starts.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: "One maintainer-visible repository change creates persistent process value for limited real use. It changes kc-dev-flow documentation and contracts but adds no production credentials, data migration, unattended operation, consumer-action compatibility break, SLO, or release and rollback ownership."
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - "Keep GitHub as the replaceable planning authority and Spacedock as the execution authority."
      - "Preserve one Issue to one Spacedock task to one isolated workspace or worktree."
    implementation:
      - "Change only existing kc-dev-flow product documentation, contracts, and deterministic coverage required for manual admission and route-back."
      - "Do not add automatic dispatch, a new stored schema, status synchronization, a new Spacedock stage, or a sprint-field rename."
    testing:
      - "Keep the kc-dev-flow contract, profile-route, comparator, and minimal-stack ablation suites green at the exact candidate revision."
      - "Add targeted negative coverage that rejects hidden one-to-many task execution or silent execution-time goal reshaping."
  scope_boundary: "One manual GitHub admission and fresh-context dogfood run only; excludes automatic Conductor Cloud dispatch, multi-Issue or multi-agent packages, new stored planning state, provider writes, stage changes, and release automation."
  promote_when:
    - "An accepted scope adds unattended dispatch, multi-Issue integration, provider writes, a consumer-action compatibility migration, SLO duty, or release and rollback ownership."
  decision:
    authority: "Captain via GitHub Issue #305 admission"
    at: "2026-08-27T23:48:54Z"
```

## Admission snapshot: accepted outcome and non-goals (copied from `source`)

Accepted outcome: A maintainer can fully shape one bounded change in GitHub, admit it into a Cycle, and hand it to a fresh workspace that reaches a reviewable candidate or explicitly returns to planning without reopening product direction.

Non-goals:

- No automatic Conductor Cloud dispatch.
- No multi-Issue or multi-agent package.
- No new hand-maintained JSON manifest.
- No GitHub/Spacedock status synchronization.
- No new SD stage or serialized `sprint` field rename.
- No change to POC, Pilot, or Production lifecycle depth.
- Admission grants no commit, pull-request, merge, release, or publication authority.

## Acceptance evidence

- Existing kc-dev-flow contract, profile-route, comparator, and minimal-stack ablation suites pass at the exact candidate revision.
- Targeted negative coverage rejects hidden one-Issue-to-many-task execution or silent execution-time reshaping.
- One Spacedock task and one fresh workspace or worktree are recorded for Issue #305.
- The fresh executor receives no planning transcript.
- The executor produces one reviewable candidate or one structured planning delta within one working day.
- Closeout records elapsed span, Captain decision count, and `proceed`, `change`, or `stop` for a later multi-Issue pilot.

## Measurement

Record the admission time, workspace or worktree identity, exact candidate revision, Captain decisions after admission, route-back events, and final `proceed`, `change`, or `stop` result.

## Shape decision

Recover the existing planning/execution seams with one narrow contract change. Do not add a command, stage, stored schema, synchronizer, template, or retained release-brief document. Per the Captain's backlog decision, future planning Issues start with `## The problem` and retain `## Agent execution contract`; they omit the redundant `## Human-readable release brief` wrapper.

The accepted outcome and non-goals above remain unchanged. One integrated documentation-and-contract slice is sufficient; a changed accepted goal or non-goal returns to GitHub planning before further execution.

## Accepted manual-admission journey

1. **OBSERVED** — `gh issue view 305 --repo iamcxa/kc-claude-plugins` returned one open Issue in Project status `Ready`, Iteration 2, and milestone `kc-dev-flow Cycle-Release Admission Pilot`, with the accepted outcome, non-goals, evidence, and route-back conditions.
2. **OBSERVED** — the state checkout at admission commit `07929c0723b585829b15d6a21e659aa6879de535` contained one entity whose `source` and `issue` resolve to Issue #305. The repository-local profile loader accepted that exact entity as `pilot-product-slice`, selected `shape`, and hash-bound it as `ca070a029595ba91f44d49c1c9db31ae5666445f989029878ef32b749e3b6b0b`.
3. **OBSERVED** — the ideation worker started from the generated dispatch pointer, repository rules, and committed entity rather than the planning conversation. This proves the fresh-context handoff shape for ideation, not yet isolated implementation or delivery.
4. **DESIGNED** — before implementation dispatch, `continue-dev-flow` re-reads the Issue and the current Ready set, then compares source membership, planning window, outcome, accepted goal, and non-goals with the committed `sprint: S6` snapshot. Missing input reports `planning source unavailable` or `planning reconcile unavailable`; any added, removed, changed, or moved item produces a structured planning delta and stops before dispatch or state mutation.
5. **DESIGNED** — Spacedock dispatch creates one implementation worker for this one task in one isolated worktree and records its path in this entity. Dispatch failure, no answer, worker death, or timeout does not create a second task or execution lane; resume the same task/worktree when safe, otherwise record route-back.
6. **DESIGNED** — the implementation worker receives the Issue, repository context, exact committed entity, and selected contract, but no planning transcript. It may clarify implementation details; if an accepted goal, non-goal, profile premise, dependency boundary, or one-working-day limit must change, it stops with a structured planning delta naming the changed premise, affected acceptance evidence, and recommended `change` or `stop` choice.
7. **DESIGNED** — with unchanged premises, the worker produces one reviewable diff in that worktree, runs the declared exact-head checks, and records the base revision plus patch identity. A commit SHA, pull request, merge, release, or publication exists only after its separate authorization; without commit authority, the reviewable diff remains the candidate and is not promoted to a revision claim.
8. **DESIGNED** — validation either accepts the one candidate for the existing delivery ceremony or routes the structured delta back to GitHub planning. Closeout records elapsed span from `started`, Captain decisions after admission, route-back events, worktree identity, candidate identity when one exists, and one later-pilot result: `proceed`, `change`, or `stop`.

### Observable semantics and boundaries

- The changed semantics are documentation-contract semantics: manual Ready admission is one planning Issue to one Spacedock task to one isolated execution context, and execution cannot silently reshape the accepted goal or non-goals.
- Command grammar, YAML frontmatter fields, profile routes, workflow stages, provider ownership, and delivery authority do not change. `sprint` remains an execution grouping.
- GitHub retains planning truth; the committed state-branch entity retains the admission snapshot and execution evidence; the isolated worktree retains candidate bytes. No new persistence, credentials, migration, automatic provider write, or destructive path is introduced.
- Existing retained files are repaired in place. The kernel is the explanatory home; adopter, continuation, and local-workflow text state their bounded action and point to that invariant. No new retained document or duplicate release brief is created.

## Reverse-recovery receipt

```yaml
reverse_recovery:
  trigger: "Add a manual one-to-one, fresh-context admission and route-back contract in an existing workflow."
  boundary: "Issue #305 Ready selection through the committed SD snapshot, selected Pilot route, and candidate-or-route-back result in this repository."
  layers:
    - surface: planning entry
      location: docs/dev/README.md:50
      completeness: WORKING
      need: REQUIRED
      evidence: "The live Issue is Ready and exactly one committed entity references Issue #305."
      disproof_hook: "Read Project #4 Ready items and count state entities with source Issue #305."
    - surface: portable admission contract
      location: kc-dev-flow/references/kernel.md:35
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: "Authority and reconcile exist, but exact-term search and structural reads found no explicit one-task/one-context, no-transcript, candidate-or-route-back journey."
      disproof_hook: "Show one current kernel/adopt/continue clause that binds all three missing semantics."
    - surface: execution entry
      location: kc-dev-flow/skills/continue-dev-flow/SKILL.md:10
      completeness: WORKING_UNIT_UNPROVEN
      need: REQUIRED
      evidence: "Authority resolution and hash-bound profile loading run; isolated implementation and its route-back have not yet been exercised for this Issue."
      disproof_hook: "Run the fresh implementation dispatch and observe either duplicate execution or silent premise replacement."
    - surface: persistence and readback
      location: docs/dev/.spacedock-state/manual-cycle-release-admission-path.md
      completeness: WORKING
      need: REQUIRED
      evidence: "The state branch preserves the source, window, outcome, sprint, receipt, gate decision, and admission body at one committed path."
      disproof_hook: "Read the committed entity and fail if any bound field or accepted snapshot is absent."
  decision: recover
```

Two searches support `EXISTS_BROKEN`: an exact repository search for Cycle-Release, manual admission, one-to-one, fresh executor, transcript, and planning delta found no shipped kc-dev-flow contract; a structural read of the kernel, adopter, continuation skill, and local workflow found working authority, reconcile, loader, and state seams but not the accepted end-to-end guarantee.

## Acceptance criteria

**AC-1 — Portable and self-adopted contracts agree on one-to-one admission, fresh context, route-back, and no wrapper.**
Verified by: `python3 scripts/kc-dev-flow-contract-test.py`
Falsified by: Any required clause disappears, packaged/adopted kernel bytes diverge, or the local workflow loses its binding.

**AC-2 — The new deterministic checks can speak.**
Verified by: `python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py`
Falsified by: A mutant permits one Issue to fan out, permits execution to replace accepted scope, or restores the release-brief wrapper without the contract test rejecting it for the named reason.

**AC-3 — Existing route and exact-item selection remain intact.**
Verified by: `python3 kc-dev-flow/scripts/profile-contract-loader.test.py` and `python3 kc-dev-flow/scripts/profile-spacedock-route.test.py`
Falsified by: The item loads another profile/stage, an off-route state advances, or route concurrency regresses.

**AC-4 — Existing comparator remains green.**
Verified by: `python3 scripts/kc-dev-flow-loader-eval.test.py`
Falsified by: The bounded loader/comparator contract changes while adding admission semantics.

**AC-5 — Dogfood remains one-to-one and fresh.**
Verified by: Count committed entities with Issue #305 as `source`; require one non-empty recorded implementation worktree and inspect the generated worker input
Falsified by: More or fewer than one entity/worktree exists, or the execution prompt includes planning transcript content beyond Issue/repository/entity pointers.

**AC-6 — Dogfood terminates inside the accepted box.**
Verified by: Compare closeout time with `started: 2026-08-28T00:05:28Z` and inspect the final report
Falsified by: No reviewable candidate or structured planning delta exists within one working day, or closeout omits Captain decisions and `proceed`, `change`, or `stop`.

These checks prove the documented/manual path and this dogfood instance. They do not claim engine-level prevention of an operator manually creating another task or workspace.

## Where it touches

Delivery base for stop-number measurement: fetched `origin/main@d8092fa93eec70a0d5c64d663e6c156983a785cf`; implementation must re-fetch and replace this base if it moved before editing.

| Path | Lines now | Estimated lines after | Purpose |
|---|---:|---:|---|
| `kc-dev-flow/references/kernel.md` | 214 | 228 | Own the portable manual-admission and route-back invariant. |
| `docs/dev/_mods/kernel.md` | 214 | 228 | Keep the self-adopted kernel byte-identical. |
| `kc-dev-flow/skills/adopt-dev-flow/SKILL.md` | 188 | 200 | Bind one Ready planning item to one task and one execution context without automation. |
| `kc-dev-flow/skills/continue-dev-flow/SKILL.md` | 186 | 202 | Verify fresh inputs and emit candidate or structured planning delta. |
| `docs/dev/README.md` | 356 | 374 | Bind the repository's manual GitHub-to-Spacedock journey and omit the wrapper. |
| `scripts/kc-dev-flow-contract-test.py` | 1016 | 1052 | Check package/adopter/local clauses and their single explanatory home. |
| `scripts/kc-dev-flow-minimal-stack-ablation.test.py` | 337 | 373 | Mutate one-to-one, no-reshape, and no-wrapper clauses and require named rejection. |

The existing profile loader, route test, comparator, and workflow graph are exercised but unchanged; changing them would be an unplanned surface and returns to shape.

## Stop numbers

- Stop when the diff against the recorded delivery base exceeds **7 changed files**.
- Stop when additions plus deletions exceed **175 changed lines**.
- Likeliest runaway area: stop when deterministic contract coverage across `scripts/kc-dev-flow-contract-test.py` and `scripts/kc-dev-flow-minimal-stack-ablation.test.py` exceeds **90 changed lines**.
- A crossed number requires one Captain choice recorded here: reduce scope, reshape with replacement numbers, or promote the profile. Any required change to the accepted outcome or non-goals returns to GitHub planning instead of choosing among those implementation options.

## Stage Report: ideation

- DONE: Define one accepted manual-admission journey from a Ready Issue through an exact snapshot and isolated execution to either a reviewable candidate or structured route-back; mark every step OBSERVED or DESIGNED.
  Eight ordered steps cover the observed Issue/entity/loader handoff and designed reconcile, isolated execution, candidate, failure, timeout, and route-back behavior.
- DONE: Produce falsifiable acceptance checks and a file-level touch table for the smallest existing documentation, contract, and test surfaces; incorporate the Captain decision to omit the redundant Human-readable release brief wrapper.
  Six checks name their falsifiers; seven existing files cover portable/local contracts and mutations, with no new wrapper or retained document.
- DONE: Set stop numbers for changed files, changed lines, and the likeliest runaway area; return to planning if the accepted goal or non-goals must change.
  Stop at more than 7 files, 175 changed lines, or 90 deterministic-test lines; accepted-scope change routes to GitHub planning.

### Summary

The shape recovers existing GitHub, Spacedock, loader, and worktree seams rather than adding runtime or schema. It defines one manual, fresh-context path with explicit failure and route-back behavior, bounded to seven existing files and separately authorized delivery actions.
