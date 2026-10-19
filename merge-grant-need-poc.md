---
title: POC — is a per-class merge grant needed, or does the Captain's pre-authorized merge already cover it
variant: kc-dev-flow-2
profile: poc
merge: pr
status: implementation
gates:
    version: 1
    records:
        - id: gate:merge-grant-need-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:merge-grant-need-poc-backlog-1
              briefing:
                id: briefing:merge-grant-need-poc:backlog:attempt-1:revision-1
                digest: sha256:9a1b96a876658a8f30b711a7c16f30d7f42081b6f5a0605e7f40695f64d3fb44
                room-ref: ./merge-grant-need-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:merge-grant-need-poc:backlog:1
                briefing: briefing:merge-grant-need-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-18T16:57:09.496498Z"
                decision: approve
                reason: Captain approved in chat (「批准這些作為第三批」) the five batch-3 backlog gates presented together, accepting profile poc and that FO proposes a bar at implementation for him to rule before any run
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-18T16:58:24Z
worktree: .worktrees/spacedock-ensign-merge-grant-need-poc
---

Filed on the Captain's 「同意」 (chat, 2026-10-18) to FO's proposal to narrow merge-gatekeeper (PR #666) and turn the grant half into a measure-first POC: 「授權那半不要開成「之後重做」，改開一個 POC 待辦，先量兩件事：adopter 裡有多少 PR 可以被授權；「預先授權合併」是不是已經涵蓋了你要的效果。量完確定有需要，才把程式碼從分支拿回來。」

## Scope

- Measure 1: in subspace-relay, subspace-web and qnow, how many merged PRs over a stated window would class as grant-eligible (not `never`) under the never list #666 ships; read-only `gh`.
- Measure 2: how often the Captain already uses a pre-authorized merge at a delivery gate (「預先授權」, 「批准並合併」 and similar) and how many of his turns per delivered PR remain, from the dev2 ledgers and state of this repository and the adopters.
- Parked code: the grant, merge-line and calibrate code, its tests, ADR 0023 and the AC-5 real-repository run are on branch spacedock-ensign/merge-gatekeeper at 3fd841789db9c76d863ae4f723184c790471a7da; two Codex P1 on that code are open (review:5562139252: grants read from the working tree, not the fetched trunk; an unreadable PR state counted as pending).
- Bar: set by the Captain at the backlog gate; the code returns only if the POC passes it.
- Retrieval (FO, 2026-10-19): the PR branch was deleted on merge; 3fd841789db9c76d863ae4f723184c790471a7da stays reachable from GitHub's refs/pull/666/head (head a05b18a0): `git fetch origin refs/pull/666/head`.

## Pre-registration (phase 1, for the Captain to rule before any measurement)

Nothing below has been measured. The only repository access so far: `gh auth status`, and `gh pr list --state merged --limit 1` on spacedock-dev/subspace-relay, spacedock-dev/subspace-web and iamcxa/qnow, each of which returned a PR. No PR count, file list or class was read.

**Question.** Does the parked per-class grant earn its return, or does the Captain's pre-authorized merge already give the effect (fewer of his turns per delivered PR)? The code returns only if both measures below pass the bar the Captain rules.

**Window.** Per repository, every PR with `mergedAt` from 2026-09-19T00:00Z up to but excluding 2026-10-19T00:00Z (30 days, fixed so a rerun lists the same PRs), listed by `gh pr list --state merged --search "merged:2026-09-19..2026-10-18" --limit 1000`. Drafts and bot PRs are included (release-please PRs class `never`); nothing is sampled out. If the listing returns exactly the limit, the window is cut shorter and said so.

**Classing (Measure 1).** Pin: `kc-dev-flow-2/scripts/delivery_gate.py` at origin/main c60e89e1 (blob 6cba92cc7a6e). The worker copies that blob to a scratch directory and imports `never_paths` and `classify`; it does not run `check`, which needs a task and a validation record.
- Paths: `filename` and `previous_filename` from `gh api --paginate repos/<R>/pulls/<N>/files`. If the count differs from `changedFiles`, the PR is `unclassifiable` (reported, never counted eligible).
- `never_paths` inputs: `migrations-path` and `adr-path` from that adopter's workflow README frontmatter at its trunk, and the README's own path.
- `never` also when `headRefName` starts `release-please--` (as `check` does). Task-level triggers (`profile: prod`, `Surfaces:` with `db`) apply only to a PR that maps to a task through its `pr:` field in the adopter's state checkout; for an unmapped PR they cannot be known.
- Output per PR: class `never`, `docs-only`, `script-with-test` or `other`. Grant-eligible = not `never`. Two counts are reported, never merged into one: path-level (every PR, an upper bound) and task-level (mapped PRs only, with how many are unmapped).
- Class counts are reported per repository, because `merge-grants:` lives in each repository's README and ADR 0023 (parked) needs 59 clean records per class.

**Recognizing a pre-authorized merge (Measure 2).** A task is mapped to its PR by `pr:` in the state checkout; the state branch name per adopter is discovered with a read-only branch listing at phase 2 (unknown now). For a mapped PR, read the gate records of the stage before delivery: `resolution.decision`, `resolution.reason`, the briefing at `room-ref`, and `merge:`/`pr:` timing. Recognition rules, fixed before reading any record:
- `covered`: the approval reason or the gate question contains 「預先授權」, 「批准並合併」, "approve and merge", or "approval also covers the merge", AND the PR merged with no later `person:captain` resolution or chat-quoted turn about it.
- `separate-turn`: a later Captain turn asking or approving the merge is recorded (a `--conn-quote` naming merge, or a second delivery-gate resolution).
- `unrecognizable`: PR unmapped, state branch unreadable, or records silent on merge.
Known limits: chat turns outside gate records are not in any ledger, so "turns per PR" is a lower bound from ledgers; the Captain and FO may merge under one GitHub account, so `mergedBy` is not used to tell who merged. Before rates are trusted, 10 PRs (or all, if fewer) are hand-checked against the recognizer, and the disagreement count is reported.

**Proposed pass bar (the Captain rules or replaces it).** Bring the parked code back only if ALL hold:
1. M1: in at least one repository, one non-`never` class (`docs-only` or `script-with-test`) has at least 20 merged PRs in the window (59 records in about 90 days at that pace; below it a class reaches its ADR 0023 bar slower than a quarter, and `other` is excluded because that ADR says it may never qualify).
2. M2: among non-`never` PRs that are recognized, fewer than half are `covered`, and the median count of Captain turns after the validation approval for the `separate-turn` ones is at least 1.
3. Reliability: `unrecognizable` is under 25% of non-`never` PRs and the hand-check disagrees on at most 1 of 10; otherwise the result is `inconclusive`, which does not bring the code back.
Result `retire`: M1 fails or M2 shows most eligible PRs already `covered`; the parked branch stays as is and the two Codex P1 on it are not worked. Result `inconclusive` returns to the Captain with what was unreadable.
What a pass would not prove: that a grant is safe (that needs the 59 clean records), or that the remaining turns are the ones he wants removed.

**Cost.** No model call and no code or adopter file change; the worker runs a throwaway script from a scratch directory and commits only the result table to this file. GitHub REST calls are 1 listing per repository plus about 2 per PR (files, view) plus a few README and state-branch reads; the PR count is not yet known, so the call count is not stated (the authenticated limit is 5000 requests per hour; the script stops and reports if it would exceed 1000 calls). Wall-clock was not measured; one worker session, stopping at the result table. All gh calls are GET or `gh pr list/view`; no comment, no `git config` write, no PR opened.

**Ask.** Rule: (1) the window, (2) the three recognition phrases and the `covered`/`separate-turn` split, (3) the bar in the three numbered conditions, or replace its numbers (20, one half, 25%, 1 of 10).

## Stage Report: implementation

- DONE: Phase 1 only: write and commit to the task file a pre-registration for the Captain to rule before any measurement: the window of merged PRs per repository (subspace-relay, subspace-web, qnow), how each PR is classed under the never list #666 shipped (kc-dev-flow-2/scripts/delivery_gate.py classify at origin/main), how a pre-authorized merge is recognized in gate records and briefings, the proposed pass bar (what result would justify bringing the parked grant code back), and the cost; then stop and report; run nothing against the repositories beyond listing that the read-only gh calls work
  Section `## Pre-registration (phase 1 ...)` above; read-only `gh pr list --limit 1` returned a PR for all three repositories; classifier pinned to origin/main c60e89e1, blob 6cba92cc7a6e.

### Summary

The pre-registration fixes the window (30 days to 2026-10-18), the pinned classifier use, the recognition rules and a three-part proposed bar, all awaiting the Captain's ruling. Nothing was measured; no package or adopter file changed and no PR opened. Unknowns left for phase 2: the PR counts and each adopter's state branch name.

comment_ratio and number_guards: not run, no code or migration added (this task adds no code bytes; the only change is this task file).
- ADR number (FO, 2026-10-19): ADR 0023 is no longer held for this POC. merge-gatekeeper never landed it and number_guards.py reserve does not read archived tasks, so it was reserved again for captain-question-load (batch 3), matching fo-write-checks D2 (a reserved number is landed or released). If this POC's result brings the grant ADR back, reserve a fresh number at that dispatch; the parked draft at 3fd84178 is titled 0023 and must be renumbered.

## Captain bar ruling

Captain: 「照建議」 (chat, 2026-10-19), to FO's question 「這 4 件照建議批准，POC 照建議的標準開跑嗎？」 whose POC part stated the pre-registration's window (30 days of merged PRs in relay, web and qnow) and its three pass conditions as written under `## Pre-registration (phase 1 ...)`. The bar is that text, unchanged.
