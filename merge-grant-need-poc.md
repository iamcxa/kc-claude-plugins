---
title: POC — is a per-class merge grant needed, or does the Captain's pre-authorized merge already cover it
variant: kc-dev-flow-2
profile: poc
merge: pr
status: validation
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
        - id: gate:merge-grant-need-poc:validation
          stage: validation
          attempts:
            - id: gate-attempt:merge-grant-need-poc-validation-1
              briefing:
                id: briefing:merge-grant-need-poc:validation:attempt-1:revision-1
                digest: sha256:48f39df1ca10e5f45634972d9b54afe77ad9ac9f1c9fb242423a3fc9b2642b23
                room-ref: ./merge-grant-need-poc/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:merge-grant-need-poc:validation:1
                briefing: briefing:merge-grant-need-poc:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-19T04:37:35.961272Z"
                decision: approve
                reason: 'Captain approved in chat (「准」) the merge-grant-need-poc closing gate, presented together with the #670 delivery gate: retire the per-class merge grant, keep the parked code parked, leave its two Codex P1 unworked'
              application:
                target-stage: done
                state: pending
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

## Results (phase 2)

Run 2026-10-19 exactly as pre-registered; scratch scripts and per-PR JSON are in /tmp/mgn (not committed, throwaway as registered). Classifier: `delivery_gate.py` blob 6cba92cc7a6e (verified by `git hash-object` of the scratch copy), `never_paths` + `classify` called directly. Window 2026-09-19..2026-10-18: no listing reached the 1000 limit; every file list matched `changedFiles` (0 unclassifiable). gh calls: 309 file lists + 3 PR listings + about 20 discovery and probe calls not individually counted, well under the 1000 cap. State read by `git clone --bare --filter=blob:none` of spacedock-state/dev and /dev2 for each adopter (no gh call). Classifier README inputs: `docs/dev2/README.md` scalars per adopter at its trunk (qnow trunk `next`, `migrations-path: apps/qnow-api/netlify/database/migrations`; relay and web declare none), placed in a scratch repo root so the README-path rule resolves.

### Measure 1: counts per repository (30-day window)

| repo | merged PRs | never | docs-only | script-with-test | other | mapped to a task | task-level never added (prod/db) |
|---|---|---|---|---|---|---|---|
| subspace-relay | 143 | 95 | 2 | 2 | 44 | 38 | 1 |
| subspace-web | 70 | 63 | 0 | 0 | 7 | 21 | 0 |
| qnow | 96 | 71 | 1 | 0 | 24 | 45 | 0 |

Path-level counts above are the upper bound; the one task-level change is a relay PR whose task is `prod` or `db`. Why never: release-please branches (relay 37, web 22), `docs/adr|dev*` paths (relay 41, web 36, qnow 57), `scripts/`/`.github` (relay 30), migrations (qnow 21 under `migrations-path`), and the other NEVER_PATH rules; every never PR names at least one rule. Largest non-`other` class in any repository: 2 PRs (bar needs 20).

### Measure 2: recognition over non-never PRs (79: relay 47, web 7, qnow 25)

| repo | covered | separate-turn | unrecognizable | of which unmapped |
|---|---|---|---|---|
| subspace-relay | 0 | 0 | 47 | 38 |
| subspace-web | 0 | 0 | 7 | 6 |
| qnow | 0 | 2 | 23 | 16 |

Unrecognizable is 77 of 79 (97%). Across all 166 Captain validation approvals in every task that maps to a PR in these three state branches (213 PRs, not limited to the window), none contains 「預先授權」, 「批准並合併」, "approve and merge" or "approval also covers the merge"; 25 mention merge or 合併 and 6 of those say merging stays with the Captain. The Captain's merge is not in the gate records, so the ledgers cannot show a pre-authorized merge or the turn after approval.

### Hand-check of 10 PRs (the recognizer against my reading of the full approval reasons, briefing questions and the later resolutions)

Chosen before reading the labels: both `separate-turn` PRs plus eight mapped non-never PRs spread over the three repositories.

| PR | path class | recognizer | my reading | agree |
|---|---|---|---|---|
| qnow#1269 | other | separate-turn (2 later) | the 2 later resolutions are repair pushes to the same PR, not a merge ask | no |
| qnow#1231 | other | separate-turn (2 later) | the 2 later resolutions are redeliveries to the same PR | no |
| relay#368 | other | unrecognizable | no merge wording in reason or question | yes |
| relay#346 | other | unrecognizable | none | yes |
| relay#322 | other | unrecognizable | none | yes |
| relay#314 | other | unrecognizable | none | yes |
| relay#276 | script-with-test | unrecognizable | none | yes |
| web#96 | other | unrecognizable | says "merge stays with the Captain", not a pre-authorization | yes |
| qnow#1278 | other | unrecognizable | approval covers later Codex repair rounds only | yes |
| qnow#1238 | other | unrecognizable | none | yes |

Classification spot-check on the same PRs: relay#276 (`*.ts` files each with a `.test.ts` sibling) is `script-with-test`; relay#346 and web#96 change one spec file only, so `other`; relay#368 and relay#322 mix docs and code, so `other`; qnow#1278 and #1269 change journey YAML only, so `other`. Disagreements: 2 of 10.

### Against the bar (as ruled, unchanged)

1. M1: FAILS. The largest docs-only or script-with-test count in any repository is 2 (relay), against 20.
2. M2: not evaluable. Recognized non-never PRs are 2 (both `separate-turn` by the literal rule, 0 `covered`, so the stated thresholds read as met on n=2), and the hand-check shows both are false `separate-turn`.
3. Reliability: FAILS. Unrecognizable is 97% (limit 25%) and the hand-check disagrees on 2 of 10 (limit 1).

**Result: retire** (M1 fails; the pre-registration names that as sufficient). The parked branch spacedock-ensign/merge-gatekeeper at 3fd841789db9 stays as is and the two Codex P1 on it are not worked. Condition 3 also makes M2 `inconclusive`: the ledgers do not record the Captain's merge turn, so whether his pre-authorized merge covers the effect is not answered by this measurement.

Not proved: that `other` PRs could not be granted under a different class design (44 relay and 24 qnow `other` PRs exist, which the registered bar excludes by ADR 0023's rule); that the merge turn count is low (chat turns are not ledgered); anything beyond 2026-09-19..2026-10-18.

Cleanup: scratch directory /tmp/mgn only; no package, adopter or parked-branch file changed, no PR opened, no comment made.

### Non-never PRs (path class, task class where mapped, recognizer label)

- qnow#1198: other, task other, unrecognizable
- qnow#1199: other, task other, unrecognizable
- qnow#1201: other, task unmapped, unrecognizable
- qnow#1202: other, task unmapped, unrecognizable
- qnow#1206: other, task unmapped, unrecognizable
- qnow#1210: other, task unmapped, unrecognizable
- qnow#1211: other, task unmapped, unrecognizable
- qnow#1212: other, task unmapped, unrecognizable
- qnow#1213: other, task unmapped, unrecognizable
- qnow#1216: other, task other, unrecognizable
- qnow#1222: other, task unmapped, unrecognizable
- qnow#1224: other, task unmapped, unrecognizable
- qnow#1228: other, task unmapped, unrecognizable
- qnow#1230: other, task unmapped, unrecognizable
- qnow#1231: other, task other, separate-turn
- qnow#1232: other, task unmapped, unrecognizable
- qnow#1234: other, task other, unrecognizable
- qnow#1238: other, task other, unrecognizable
- qnow#1242: other, task other, unrecognizable
- qnow#1247: other, task unmapped, unrecognizable
- qnow#1257: other, task unmapped, unrecognizable
- qnow#1263: other, task unmapped, unrecognizable
- qnow#1269: other, task other, separate-turn
- qnow#1271: docs-only, task unmapped, unrecognizable
- qnow#1278: other, task other, unrecognizable
- subspace-relay#236: other, task unmapped, unrecognizable
- subspace-relay#240: script-with-test, task unmapped, unrecognizable
- subspace-relay#243: other, task unmapped, unrecognizable
- subspace-relay#244: other, task unmapped, unrecognizable
- subspace-relay#246: other, task unmapped, unrecognizable
- subspace-relay#253: other, task unmapped, unrecognizable
- subspace-relay#257: other, task unmapped, unrecognizable
- subspace-relay#263: other, task other, unrecognizable
- subspace-relay#264: other, task unmapped, unrecognizable
- subspace-relay#265: docs-only, task unmapped, unrecognizable
- subspace-relay#268: other, task unmapped, unrecognizable
- subspace-relay#273: other, task unmapped, unrecognizable
- subspace-relay#274: other, task unmapped, unrecognizable
- subspace-relay#276: script-with-test, task script-with-test, unrecognizable
- subspace-relay#278: other, task other, unrecognizable
- subspace-relay#292: other, task unmapped, unrecognizable
- subspace-relay#300: other, task unmapped, unrecognizable
- subspace-relay#301: other, task unmapped, unrecognizable
- subspace-relay#304: other, task unmapped, unrecognizable
- subspace-relay#305: docs-only, task unmapped, unrecognizable
- subspace-relay#307: other, task unmapped, unrecognizable
- subspace-relay#310: other, task unmapped, unrecognizable
- subspace-relay#314: other, task other, unrecognizable
- subspace-relay#315: other, task unmapped, unrecognizable
- subspace-relay#316: other, task unmapped, unrecognizable
- subspace-relay#318: other, task unmapped, unrecognizable
- subspace-relay#321: other, task other, unrecognizable
- subspace-relay#322: other, task other, unrecognizable
- subspace-relay#324: other, task unmapped, unrecognizable
- subspace-relay#329: other, task unmapped, unrecognizable
- subspace-relay#330: other, task unmapped, unrecognizable
- subspace-relay#333: other, task unmapped, unrecognizable
- subspace-relay#339: other, task other, unrecognizable
- subspace-relay#346: other, task other, unrecognizable
- subspace-relay#352: other, task unmapped, unrecognizable
- subspace-relay#357: other, task unmapped, unrecognizable
- subspace-relay#358: other, task unmapped, unrecognizable
- subspace-relay#368: other, task other, unrecognizable
- subspace-relay#369: other, task unmapped, unrecognizable
- subspace-relay#371: other, task unmapped, unrecognizable
- subspace-relay#372: other, task unmapped, unrecognizable
- subspace-relay#373: other, task unmapped, unrecognizable
- subspace-relay#374: other, task unmapped, unrecognizable
- subspace-relay#375: other, task unmapped, unrecognizable
- subspace-relay#376: other, task unmapped, unrecognizable
- subspace-relay#379: other, task unmapped, unrecognizable
- subspace-relay#386: other, task unmapped, unrecognizable
- subspace-web#78: other, task unmapped, unrecognizable
- subspace-web#80: other, task unmapped, unrecognizable
- subspace-web#86: other, task unmapped, unrecognizable
- subspace-web#90: other, task unmapped, unrecognizable
- subspace-web#91: other, task unmapped, unrecognizable
- subspace-web#96: other, task other, unrecognizable
- subspace-web#101: other, task unmapped, unrecognizable

## Stage Report: implementation (phase 2)

- DONE: Run the measurement exactly as pre-registered, with the bar as the Captain ruled it (## Captain bar ruling); commit the result table, the hand-check of 10 PRs and the counts per repository to the task file; report pass, fail or inconclusive against the bar without moving it; stop at the 1000-call cap if reached and report that
  `## Results (phase 2)` above; the cap was not reached (309 file lists + 3 listings + about 20 probes); the bar fails on M1 and on the reliability condition, result `retire`.

### Summary

Of 309 merged PRs in the window, the largest non-`other` class in any repository has 2 PRs, so the registered 20-PR bar fails and the result is retire. The ledgers hold no pre-authorized-merge phrase and do not record the Captain's merge turn, so M2 cannot be read from them (97% unrecognizable, hand-check 2 of 10 wrong). No code or migration was added, so `comment_ratio` and `number_guards` were not run.


## Stage Report: validation

- DONE: Confirm from state history that the pre-registration and the Captain's bar ruling were committed before the measurement ran, and that the bar text is unchanged
  Pre-registration ba904924 (2026-10-19 01:00:45 +0800), bar ruling cf25e19e (08:45:05), results a8229b8c (08:53:07); scratch files in /tmp/mgn start 08:45:24, after the ruling. The `## Pre-registration` section hashes identically at all three commits, and `git diff ba904924 a8229b8c` deletes 0 lines.
- DONE: Re-derive M1 independently on a sample: for each repository, list the merged PRs in the window with read-only gh, re-class at least 15 PRs per repository with kc-dev-flow-2/scripts/delivery_gate.py classify at origin/main, and compare with the committed table; confirm the largest docs-only or script-with-test count
  Beyond the sample I re-listed and re-classed all 309 PRs with my own script in /tmp/mgv, classifier blob 6cba92cc7a6e taken from `git show c60e89e1`: listings 143/70/96, and relay 95/2/2/44, web 63/0/0/7, qnow 71/1/0/24 (never/docs-only/script-with-test/other) match the committed table; 0 per-PR class disagreements out of 309; largest docs-only or script-with-test count is 2 (relay), bar needs 20. Adopter README scalars re-read at trunk (qnow `migrations-path` only).
- DONE: Re-check M2's recognizer on the 10 hand-checked PRs and on 5 more of your choosing; state whether the 'unrecognizable' rate and the hand-check disagreement hold
  I read the full gate resolutions of all 10 from the state branches (bare clones, `git show`): qnow#1269 and #1231 are false `separate-turn` (the later resolutions are push/redeliver approvals to the same PR), the other 8 agree, so disagreement 2 of 10 holds. 5 more (relay#263, relay#339, qnow#1199, #1234, #1242) all have no merge wording and are `unrecognizable`, agreeing. The 97% unrecognizable rate holds as computed (77 of 79; 60 of them unmapped to any task).
- DONE: Verdict against the Captain's bar as registered (PASSED meaning the code returns, or REJECTED meaning retire, or inconclusive), and what the POC does not show
  REJECTED (retire): M1 fails, 2 against 20, and the pre-registration names that as sufficient; reliability also fails (97% unrecognizable over 25%, hand-check 2 of 10 over 1), so M2 is inconclusive and not what decides this. Not shown: see Summary.

### Summary

Verdict REJECTED: the parked grant code does not return, because no repository has more than 2 PRs in a non-`other` class over the 30-day window against the registered 20. I reproduced the M1 table PR by PR and the hand-check count; the implementation worker's numbers stand.

Not shown: whether a pre-authorized merge covers the effect (M2 is unreadable from ledgers). One counter-example the recognizer could not have caught: qnow PR #1184 (merged 2026-09-13, before the window, old `dev` workflow) carries the Captain's 「都處理完就幫我合併」 as a conn-quote and "approve and merge delegated to the FO" in a validation review file, neither in an approval reason and neither a registered phrase, so pre-authorized merges exist but are phrased outside the registered list. Also not shown: `other` PRs under a different class design (44 relay, 24 qnow), and anything outside 2026-09-19..2026-10-18. The two qnow product strings containing 「預先授權」 (staff phone pre-authorization) are not merge grants.

Boundary: no `boundary-crossed:` found; read-only gh and git, no model run, no package, adopter or parked-branch change, no PR or comment. The candidate is this task file at a8229b8c.

Checks run, with exit codes: `adr_lint.py docs/adr --since c60e89e1` exit 0 (22 files, none added); `doc_impact.py c60e89e1 c60e89e1` exit 0 (no documents). comment_ratio and number_guards not run (no code or migration added). Returned to FO, not verdict-bearing: `dispatch_records.py` exit 1 (implementation-1.md lacks the roborev line or a `roborev not run:` line; no code was written), and `design_surfaces.py check` exit 1 (no FO alignment or acceptance criteria sections; the POC route skips ideation).

### Minimal acceptance script

1. Run `for r in spacedock-dev/subspace-relay spacedock-dev/subspace-web iamcxa/qnow; do gh pr list -R $r --state merged --search "merged:2026-09-19..2026-10-18" --limit 1000 --json number --jq length; done`. Expect 143, 70, 96 (309 PRs, none at the 1000 limit).
2. Run `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo show c60e89e1:kc-dev-flow-2/scripts/delivery_gate.py | git hash-object --stdin`. Expect 6cba92cc7a6edcf6aeb119ad4e99439fcffcca67, the classifier the table used.
3. Run `gh api --paginate repos/spacedock-dev/subspace-relay/pulls/276/files --jq '.[].filename'`. Expect 5 files: room-feedback.ts, room-view.ts, each with a `.test.ts` beside it, and one browser spec; all code with own tests, so `script-with-test`. This is one of the only 2 such PRs in relay.
4. Run `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/docs/dev2-poc/.spacedock-state diff ba904924 a8229b8c -- merge-grant-need-poc.md | grep -c '^-[^-]'`. Expect 0 (no registered line was removed or edited between pre-registration and results; grep exits 1 on a zero count).
5. Run `grep -cE '^- (subspace-relay|subspace-web|qnow)#[0-9]+: (docs-only|script-with-test)' merge-grant-need-poc.md` in the state checkout above. Expect 5 (relay#240, #265, #276, #305 and qnow#1271); relay has 4 of them, so the largest class count is 2 per class.

Does not cover: the 30 days outside the window, the Captain's chat turns (not in any ledger), `other` PRs, or whether a grant would be safe.
