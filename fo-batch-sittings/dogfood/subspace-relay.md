Observer dogfood sweep, 2026-10-20, repository subspace-relay (read-only, kc-dev-flow-2:observer sonnet).

# Dogfood evidence: fo-batch-sittings and special-role calls

Read-only. Source: state branch `spacedock-state/dev2`, HEAD `628334a4`. Package 0.25.0; README marker 0.25.0.

`decision_ledger.py` ran on this state. It returned 201 rows in total, 29 of them dated 2026-10-17 or later. `role_triggers.py` ran for every window task.

Ledger times are UTC. Commit times are +0800 and name the same instants.

Window tasks (gate recorded on or after 10-17): identity-cannot-be-borrowed, revoke-ends-access, storage-stops-growing, frame-and-content-headers, owner-feedback-pages, junk-share-edge-cost, account-publish-ceiling, others-highlights-in-author-colour, own-comments-follow-account, entry-without-name-field, spacedock-install-beta.

## Q1. Batch dogfood

### (a) Batches identified

| Batch | Stage and time (UTC) | Tasks | Evidence |
|---|---|---|---|
| B0, before the window, for context | backlog, 10-16 15:30:47 to 15:32:09 | the same seven tasks as B1 | Reason: "one answer to batch 1 presented together (7 tasks…)". Quote 「准」. |
| B1 | ideation, 10-17 02:08:58 to 02:10:11 | identity-cannot-be-borrowed, revoke-ends-access, storage-stops-growing, frame-and-content-headers, owner-feedback-pages, junk-share-edge-cost, account-publish-ceiling | Quote 「照這樣」. Reason: "one answer to batch 1 ideation presented together". Question: "Batch 1 ideation, 7 designs presented together…". Commits `54e75195`, `5fd983fb`, `73ca6c1b`, `057db2da`, `e63278c3`, `e2d74fac`, `0d83bbd9`. Six approvals and one revise. |
| B2 | validation (junk-share-edge-cost) plus ideation 2 (account-publish-ceiling), 10-17 03:27:41 and 03:27:47 | junk-share-edge-cost, account-publish-ceiling | Quote 「就照這樣」. Question: "Batch 1, presented with account-publish-ceiling's ideation gate…". Commits `7257a48d`, `9a74a54d`. |
| B3, probable | validation (revoke-ends-access) plus ideation 3 (account-publish-ceiling), 10-19 09:05:21 and 09:05:28 | revoke-ends-access, account-publish-ceiling | Same quote 「對，都准」, 7 seconds apart. Commits `477774bf`, `b9942445`. Neither reason names joint presentation, and the briefings are separate. I infer "joint" from the quote and timing only. |

**Batch-1 validation gates were not joint.** All five tasks entered validation together on 10-17 11:37 to 11:38 (`ecce69eb`, `3e6a2cf4`, `633178c3`, `6d02d7a4`, `c9c3b1d9`). Each gate was presented as its own one-item brief:

| Task | Gate (UTC) | Commit |
|---|---|---|
| frame-and-content-headers | 10-17 04:41 | `3a38fc12` |
| identity-cannot-be-borrowed | 10-19 08:21 | `672ef6ae` |
| revoke-ends-access | 10-19 09:05 | `477774bf` |
| storage-stops-growing | 10-19 10:55 | `464f4c24` |
| owner-feedback-pages | 10-19 14:47 | `316cde7a` |

The briefing question for frame-and-content-headers says "first in batch 1's merge order". The later ones name a head already merged with main, for example "validated 97be0134 merged with main".

Adjacent but not joint, because the quotes differ: 14:46:55 entry-without-name-field 「補」 and 14:47:31 owner-feedback-pages 「准」, 36 seconds apart.

### (b) Counts per task

Counts cover gate resolutions in the window. The pre-window gates are in the "Pre-window gates" column. The ledger counts only gate resolutions and withdrawals, so the other-rulings column comes from the task bodies.

| Task | Captain resolutions (window) | Joint / single | Other recorded Captain rulings | Pre-window gates |
|---|---|---|---|---|
| identity-cannot-be-borrowed | 2 (ideation, validation) | 1 / 1 | none | 1 (backlog, joint) |
| revoke-ends-access | 2 | 2 / 0 | none | 1 (backlog, joint) |
| storage-stops-growing | 2 | 1 / 1 | none | 1 (backlog, joint) |
| frame-and-content-headers | 2 | 1 / 1 | none | 1 (backlog, joint) |
| owner-feedback-pages | 2 | 1 / 1 | none | 1 (backlog, joint) |
| junk-share-edge-cost | 2 | 2 / 0 | Amendment 1 「改成 pilot」 (poc to pilot, recorded late on the observer's finding, `071dafde`) | 1 (backlog, joint) |
| account-publish-ceiling | 3 (revise, revise, approve) | 3 / 0 | Amendment 1 (cap 500 to 1000, `9ec1f5da`); Amendment 2 (split, supersedes Option C, `b860ca83`); Grant 「准」 for the deploy run (`80d0b78c`); Ruling 「在 #400 修」 (`67b113e4`); Option C 「Ｃ」 (10-17, `4d01b524`); one `Override:` line, which the FO later corrected in the body as wrong | 1 (backlog, joint) |
| others-highlights-in-author-colour | 1 (validation) | 0 / 1 | none | 2 (backlog, ideation) |
| own-comments-follow-account | 5 (backlog, ideation, 3 validation) plus 1 FO withdrawal and 1 FO-authored revise | 0 / 5 | Result 「照建議」; 「開」 pulling it into the 10/22 launch; 「授權開 PR」 inside the ideation reason; standing 「准補」 | none |
| entry-without-name-field | 5 (backlog, ideation ×2, validation ×2) | 0 / 5 | 1 `Override:` (「越過」); the 「授權開 PR」 grant is quoted only in the dispatch record | none |
| spacedock-install-beta | 1 (hold) | 0 / 1 | Amendments 4 and 5 are in the window; 1 to 3 date from 10-14 | 6 more (10-14 to 10-15) |

Totals for the window: 27 Captain-authored rows and 2 FO-authored rows.

- The 27 Captain rows came from 19 Captain answers. Three joint answers covered 11 rows (B1 7, B2 2, B3 2). The other 16 rows each had their own answer.
- The 2 FO rows are the own-comments backlog withdrawal and own-comments validation-3.

### (c) Interim rules visible in state

| Rule | Shows in state | Does not show |
|---|---|---|
| `### Batch overlap` in every ideation | All 7 B1 tasks have the section. Six also carry a stage-report item "DONE: Batch overlap:…". The overlap notes did predict the ADR-index conflicts: identity says "the only conflict is one line in `docs/adr/README.md`", and owner-feedback-pages F3 says the same. | Absent in own-comments, entry-without-name-field, others-highlights and spacedock-install-beta. The first two are single-task ideations after B1. |
| Numbers reserved before the batch's first dispatch | ADR 0055 to 0058 were written under `## Number guards` on 10-17 10:11 (`76fcd3fc`, `7579cab1`, `f3c020ab`, `15704f64`). The first implementation dispatches were at 10:12 (`fba50dbd`, `d3dfdc03`, `3b970eea`). Also on time: 0060 (`e67911a9`, 17:06, before the 17:08 dispatch) and 0061 (`a6113328`, before `432e9c46`). | ADR 0059 was reserved at 16:03:22 (`71b6928d`), after its dispatch at 15:59:28 (`96a8f67c`). The observer flagged it. No `Migration:` line exists anywhere in state. |
| Joint gates, each recorded with the one answer, the reason naming joint presentation | B0, B1 and B2 reasons name it. | The B3 reasons do not. Validation was never batched. |
| FO-side repairs, rechecks and review rounds between sittings | owner-feedback-pages had implementation cycles 2 to 4 (merges of main). The reports are `40fae3a8` and `52f7bd19`, and validation cycle 3 is `eef2d001`. They ran after the 22:47 approval, within the "covers later external-review rounds" grant. own-comments cycle 3 was resolved by the FO under the Captain's earlier 「准補」 (`f2262241`). | The observer marks several of these "can't tell". Chat is outside state. |
| One follow-up backlog task per delivered task for declined findings | None of the 8 merged tasks has such a task. Declined findings exist: revoke-ends-access security findings 1 to 5, own-comments design findings 3 to 10, entry design findings 1 to 10. Only one pointer exists: account-publish-ceiling's security finding 1 names `capacity-raise-and-respond`. | The four backlog tasks created in the window came from Captain direction or an amendment, not from declined findings. They are `capacity-triage-prompt`, `relay-first-officer`, `author-handle` and `capacity-raise-and-respond`. |
| A repeated finding class calls the chief-engineer | The ADR-index conflict class: own-comments cycles 2 and 3 both hit `docs/adr/README.md`; entry cycle 2 and owner-feedback-pages cycle 3 hit it too; identity's validation noted it. | No call was made. The only `Reviewer:` line is a waiver written after the merge (see Q2). |

### (d) Extra Captain turns visible in state

| Task | Evidence |
|---|---|
| own-comments-follow-account | Four validation gates for one task. Cycle 1 (`df94f637`): rebase after #389 merged. Cycles 2 and 3: the same `docs/adr/README.md` conflict (`8bf1da3b`, `f2262241`). The backlog gate was withdrawn by the FO because scope gained a fact, then re-approved (10-19 03:17 and 03:37). |
| entry-without-name-field | Ideation sent back once (「按鈕怪怪的，Or 應該要保留…」, `c63cfec2`). Validation sent back once for the ADR-index conflict (`1e61d94e`). The Captain overrode a hold: "Override: recommended hold on delivery_gate exit 1; Captain chose 越過" (`8775f6ae`). |
| own-comments-follow-account | Validation-4 also asked for approval with "delivery_gate.py exit 1 shown (skipped and neutral checks only)" (`7e94a927`). |
| account-publish-ceiling | Ideation sent back twice (`0d83bbd9`, `9a74a54d`). The Captain then asked 「每天 1000 好了？」 inside the third gate, the FO restated, and he answered 「對，都准」. Two amendments followed within 59 minutes. A deploy-run grant and a ruling are recorded in the body. |
| account-publish-ceiling (ledger quirk) | The ideation-1 row carries an `Override:` clause. The task body says "Correction (FO, 2026-10-17): … it is wrong", but the ledger still counts it as an override. |
| spacedock-install-beta | Five amendments, each answering a chat "要你決定" (amendments 4 and 5 are in the window). Hold at `66a6afbb`. |
| Batch-1 validation | Five separate sittings between 10-17 and 10-19 (see (a)). |
| others-highlights-in-author-colour | The validation question says the FO shows the PR body "and, on your yes, pushes and opens it". That is a second ask, visible only in the question text. |

## Q2. Special-role calls

### Script results (`role_triggers.py`)

| Task | Exit | Result |
|---|---|---|
| identity-cannot-be-borrowed, revoke-ends-access, storage-stops-growing, frame-and-content-headers, owner-feedback-pages, others-highlights-in-author-colour, entry-without-name-field | 0 | 0 events read. Nothing owed. |
| own-comments-follow-account | 0 | 1 event (Cycle 3), cleared by a waiver. |
| junk-share-edge-cost | 1 | Owes engineering-reviewer for Amendment 1. |
| account-publish-ceiling | 1 | Owes engineering-reviewer for Amendments 1 and 2. |
| spacedock-install-beta | 1 | Owes engineering-reviewer for Amendments 1 to 5. |

Outside the window, no gate since 10-17: limit-telemetry-posthog exits 1 (owes Amendments 1 and 2). review-ui-room-asks-through-shell and signed-in-specs-run exit 0.

Owed against made: 8 owed and 0 made for engineering-reviewer; 1 owed for chief-engineer, waived after the merge.

### `Reviewer:` lines that exist

| Where | Line | What the role recommended |
|---|---|---|
| `_archive/own-comments-follow-account.md`, under `## FO alignment` | "Reviewer: kc-dev-flow-2:chief-engineer not run: cycles 2 and 3 were stale-base merges of main (#388, #390)… no product finding… #398 merged 2026-10-19 (05bb04f) Cycle 3" | Nothing. It is a waiver, not a call. |
| (history of that waiver) | Added at `af96a807` (22:12) under `## Acceptance criteria`, so `role_triggers.py` still exited 1. Moved under `## FO alignment` at `4f10767b` (22:18), alongside the observer report. | — |
| Outside the window: `_archive/front-door-hardening/reviews.md`, 10-15, not a `Reviewer:` line | Engineering-reviewer verdict: "open after fixing two things" (rate limits on read routes; an `/llms.txt` sentence). It also raised H2 (retention stall; Captain decision), M3 (account multiplication) and M4 (revoke does not stop reads). | Those findings are the stated origin of batch 1. |

Other seats exist in state. `kc-pr-flow:tob-security-reviewer` (sonnet) ran at ideation for revoke-ends-access (verdict "design must change"), identity-cannot-be-borrowed ("design must change") and account-publish-ceiling (three rounds). It also ran at validation for revoke-ends-access and account-publish-ceiling. The observer role has reports for at least six window tasks. None of these is a `Reviewer:` call.

### Cases that look owed by judgment with no call made

| Case | Evidence | `Reviewer:` line? |
|---|---|---|
| **Amendment reverses an earlier Captain ruling: account-publish-ceiling** | Decision 10 says "Option C chosen by the Captain (「Ｃ」, 2026-10-17)". It was approved at the 10-19 ideation gate (`b9942445`, 17:05). Amendment 2 at `b860ca83` (18:04) says "Supersedes: Decision 10 (the Option C route…)" and moves AC-9, 12, 16, 17, 19, 21, 22. Amendment 1 (`9ec1f5da`) moved the cap from 500 to 1000 at 17:05. | None. The script owes two calls. |
| **Several review rounds, new gaps on the same design** | Three ideation security reviews. Review 1 found HIGH: the ceiling does not bound a parallel burst. Review 3 found HIGH: AC-7 and AC-8 prescribe opposite outcomes. Review 4 found HIGH: the empty-token digest comparison, and "rotation and containment claim is wrong or unverified". Validation then found Material finding 1: the scripts "cannot reach the real store by their documented invocation… AC-25 passed only against the test double". Ideation took four cycles. | None. Security review is a different seat from the two roles. |
| **Amendments reverse earlier Captain-approved text: spacedock-install-beta** | Amendment 4 (`cdfeaefa`): "FO-added edge entries and `scripts/bump-edge-extensions.sh` are withdrawn". That script was added by Amendment 3 (Captain 「好」, 10-14, `fe5873b8`). Amendment 5 (`302b1401`) supersedes AC-1 and AC-3. The 10-19 hold also approves force-pushing `1384218da` onto #842 and `5ef903b23` onto #843. | None. The script owes five calls. |
| **Amendment replaces a Captain-approved profile: junk-share-edge-cost** | "Supersedes: the profile poc the Captain approved at the backlog gate… Recorded late (2026-10-17) on the observer's finding" (`071dafde`). | None. One call owed. Low stakes. |
| **Validation sent back two or more times on the same surface: own-comments-follow-account** | Feedback Cycles 2 and 3 are both "left #398 conflicting on docs/adr/README.md". The observer notes "validation sent back twice". | Waiver only, written after the merge and first filed under the wrong heading. |
| **Same finding class across tasks** | `docs/adr/README.md` conflicts: own-comments cycles 2 and 3, entry-without-name-field cycle 2, owner-feedback-pages cycle 3, plus identity's validation note and owner-feedback-pages F3. | None. |
| **Hard-to-reverse or authority change, borderline** | storage-stops-growing deletes dead records and amends ADR 34 and ADR 54; "ADR 57 states this [list time and delete throughput] unmeasured". own-comments records an account hash beside each Result, amends ADR 0051, and has a "Rollback, measured" section. own-comments validation-3 was resolved by `agent:first-officer` under a Captain 「准補」 given earlier for a future gate; the observer rated that "ok". | None. |

## Outside state (not evaluated)

- The text of Captain chat and whether a message was one joint presentation.
- PR comments and CI.
- Whether any seat ran off-record.
- Merge asks and merge times, apart from the archive commits.
- The `Override:` lines' underlying question and recommendation (the observer also marked these "can't tell").

Files: state `/Users/kent/conductor/workspaces/subspace-relay/beirut-dev2/docs/dev2/.spacedock-state`; ledger scratch output `/tmp/ledger_obs.jsonl`. I wrote no report file into the repository.