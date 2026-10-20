Observer dogfood sweep, 2026-10-20, repository qnow (read-only, kc-dev-flow-2:observer sonnet).

**Basis.** I read committed HEAD `8ce9bd767` of the qnow dev2 state branch (the State column notes where this differs for uncommitted tasks). The working tree has uncommitted edits to `check-database-version`, `move-to-singapore-region` and `product-analytics-posthog`, plus untracked `review/validation/` folders. I did not read these.

- **Ledger run:** `decision_ledger.py` reads the working tree, so I ran it on a `git archive HEAD` export, `/tmp/qs`. It ran fine.
- **Role-trigger run:** `role_triggers.py` ran on the real state path. It reads committed bytes itself.
- **Time bases:** Gate `at` values are UTC. Commit times are local (+08).
- **Window:** tasks with gates recorded on or after 2026-10-17 (UTC), live and archived.
- **Boundary task:** `owner-sms-notices` has four validation gates at 10-16T15:37, 16:07, 16:41 and 17:13 UTC. That is 10-16 23:37 to 10-17 01:13 local. I list it as a boundary task only, not as a window task.
- **Outside state:** the Captain's chat messages and the actual presentation of questions are not in state. I only see the quotes FO recorded.

## Q1 Batch dogfood

**(a) Batches identified**

| Batch | Stage | Tasks | Captain quote and time | Reason names joint presentation? |
|---|---|---|---|---|
| A | ideation | `cash-at-pickup`, `production-go-live` | 「我會再去買，你可繼續。核准 R11+R12」, 10-17 03:04:52 and 03:05:02 (commits `8c2a2bcfb`, `b0f788cb4`) | Yes: "one answer to the R11 and R12 ideation gates the FO presented together in one sitting (batch trial)". Questions say "Presented together". |
| A' | backlog | `go-live-consent`, `check-database-version`, `product-analytics-posthog`, `production-operations` | 「核准 R11+R12」 plus 「可以」, resolutions 03:22:19, :40, :57 and 03:23:28 (`fdab31dc4`, `ba1454e2b`, `66ac42a2c`, `8b01f18b8`) | Not in those words. Reasons cite batch A's quote: "production-go-live's gate stated approval files its parts as separate tasks". These four were recorded from the earlier answer. I see no new Captain message for them. |
| B | validation | `cash-at-pickup`, `go-live-consent`, `production-operations` | 「三個都准」, 10-18 04:55:19, :23, :27 (`f0557bd6d`, `c4c02ad62`, `6380a0301`) | Quote says "three". Reasons say "accepts the validated candidate and the recommendations stated in the gate question". The word "joint" does not appear. Questions order the merges: first, second, third. |
| Post-review | none (no gate) | `production-go-live`, `cash-at-pickup` bodies | 「可以」 to five items "the FO presented together after the r11 and r12 release reviews (batch trial)" (`b791600d5`, `5abf50f19`, 10-17 11:21) | Yes, in the body text. No gate record. |

**(b) Counts**

There are 16 Captain gate resolutions in the window. Nine came from three joint answers (A 2, A' 4, B 3). Seven are single.

Override lines: none. Ledger `override` is null on all rows, and no `Override:` line exists in state. Withdrawals in window: none. FO-delegated gates in window: none. The only three are in the boundary task `owner-sms-notices`.

| Task | Captain gate resolutions (joint / single) | Other recorded Captain rulings | Amendments | Where the ruling is recorded |
|---|---|---|---|---|
| `cash-at-pickup` | 3 (A, B joint; backlog 「要」 single, chat) | Post-review 「可以」, 5 items (joint). D1-D10 recommendations adopted in A. Two without-it rulings accepted in B. | 0 | gate frontmatter + body |
| `production-go-live` | 2 (A joint; backlog 「可以，同意」 single, chat) | Post-review 5 items (joint). D1-D8 + B1-B6 adopted in A. | 0 | same |
| `go-live-consent` | 2 (A' and B joint) | 「准」 force-push, 10-18 (single, chat). Combined notice wording approved inside the B question. | 0 | `## Captain rulings during delivery` |
| `production-operations` | 3 (A' and B joint; validation-2 「核准 1287」 10-19 single) | 「准」 force-push (same quote as above). 「拆出去可以」 restore split out (single, undated in state, first committed `e4462daa3` 10-19 15:27). Security finding 1 recommendation accepted in validation-2. | 0 | `## Captain rulings during delivery` and stage report |
| `check-database-version` | 1 (A' joint) | none | 0 | |
| `product-analytics-posthog` | 1 (A' joint) | Post-review item (1) created it. A "Needs decision" on raw path fields is open in the validation report. | 0 | |
| `move-to-singapore-region` | 1 single (10-19 08:22, cites the 10-17 quote and 「我們今天目標是完成 R12」) | none | 0 | |
| `production-incident-agent` | 3 single (backlog from chat 10-18; ideation `revise` 10-19 04:34, `939da7855`; ideation `hold` 10-19 07:39, `bebb0ab85`) | Codex co-design instruction, inside the revise reason | 0 | |
| `owner-sms-notices` (boundary) | 1 Captain, 3 FO-delegated "standing approval" | 「准，冒號保留」, 「准」 on fallback wording | | |

**(c) Interim rules visible in state**

| Rule | Shows | Does not show |
|---|---|---|
| `### Batch overlap` in every ideation | `production-go-live` (`76660c15f`) and `cash-at-pickup` (`3ea75184b`), both committed before the ideation gate | `production-incident-agent` has two ideation cycles and no such section (0 matches). The other four parts are "Needed at ideation: no". |
| Numbers reserved before first dispatch | `cash-at-pickup`, `go-live-consent`, `production-operations` reserved at `cd62a6496`, `f76c1d423`, `4610aaa2e` (11:24). The first dispatch is `3b4f6497b`, same minute, after them. `move-to-singapore-region` reserved `27d59aa8b`, before dispatch `76b7cdd80`. | `product-analytics-posthog` was dispatched `d86752e28` (10-19 16:17). Its reservation is `00fe64c9e` (22:39), and its text says "after implementation". It has a later `Renumber:` line. `check-database-version` has no Number guards section. |
| One follow-up backlog task per delivered task | Follow-ups exist. | They are one per declined finding class, not one per task. `cash-at-pickup`: `owner-payment-view-recovers-from-failed-poll`, `signature-path-requires-a-line`, `demo-shop-migration-test-under-load`, `signature-accessible-alternative`. `void-paid-record` came from a post-review ruling, not a decline. `go-live-consent`: `first-consent-time-kept`, `consent-return-keeps-shop-code-native`. `production-operations`: `staff-booking-rechecks-closed-entry`, `operator-secret-hardening`, `production-database-restore`. |
| Repeated finding class calls chief-engineer | none (see Q2) | |

**(d) Captain extra turns visible in state**

| Slug | Evidence | Count |
|---|---|---|
| `production-operations` | Two validation approvals. The first was 10-18 `6380a0301`, candidate `737f64a4f`. The second was 10-19 `e7176deb4` (validation-2), candidate `c81f47629`, after implementation cycles 5-11, Codex rounds 1-6 and the restore split. | 1 re-ask |
| `production-incident-agent` | Gate `revise` then `hold`. The design was redirected to an MCP server for ChatGPT Dot, then paused: 「我覺得這件事先 hold 暫時不繼續，先完成其他故事」. | 2 gate turns, 0 holds overridden |
| `cash-at-pickup`, `production-go-live`, `production-incident-agent` | Admission asked in chat before the gate was prepared, then recorded at the gate. | 3 chat asks |
| `go-live-consent`, `production-operations` | The force-push ask 「准」 is a procedural ask. It is recorded in both bodies. | 1 turn |
| `production-operations` | 「拆出去可以」 came out of Codex rounds 4-5 on PR #1287. | 1 turn |
| `move-to-singapore-region` | Admitted alone on 10-19, two days after its siblings. | 1 turn |
| FO errors | None cost a Captain turn. `production-go-live` was filed with `profile: production` and corrected to `prod` at the worker's question (`befc4c07b`). Three split tasks omitted their ACs, repaired later (`116574769`). `production-incident-agent` alignment was recorded after dispatch. | 0 |

## Q2 Special-role calls

**Script result.** `role_triggers.py` returned "0 event(s) read at HEAD, each with a call or a waiver" for all 15 slugs. The slugs were the nine window tasks plus `operator-secret-hardening`, `production-database-restore`, `qnow-release-migration`, `production-on-qnow-tw-clerk-live`, `signature-accessible-alternative` and `void-paid-record`.

I did not capture the exit code. The wrapper printed it empty, so the exit code is unconfirmed.

Zero events were read, so the script saw nothing to judge. Event A needs a `- Cycle N` line under `### Feedback Cycles`. Event B needs a `## Captain amendments` section.

These tasks track cycles as `## Stage Report: implementation (cycle N)` headings. `owner-sms-notices` has `## Feedback Cycles` at level 2 and its lines are `- PR #1284 …`, not `- Cycle N`. `## Captain amendments` appears in no window task. The older `office-follows-antd-pro`, `accept-branch-invitation` and `vehicle-based-pricing` do have it.

**Reviewer: lines.** `grep -rIn 'Reviewer:'` over the whole state returns nothing. `git log -S'Reviewer:'` since 10-10 returns nothing. The only mention of chief-engineer or engineering-reviewer is in `_archive/staging-separate-project.md`, outside the window. There is therefore no role recommendation to report.

**Calls that look owed by judgment, none made**

| Slug | Trigger | State evidence (quote + commit) | Reviewer: line |
|---|---|---|---|
| `production-operations` | 2+ review rounds finding new gaps in the same file | ADR 0040 records "seven review rounds on a filter over error text each found a new leak" (`804e97d1b`). Stage report: "The scrubber was rewritten three times under security review" (`1cfe66113`). Roborev 816/817/819/820/821/839/848/849 and Codex rounds 1-6 on PR #1287 hit the same runbook and close-entry race. Round 4 reopened a decline: "Codex round 4 … rates it P1" (`95a8221b3`). 10 validation cycles, all PASSED, 11 implementation cycles. | none |
| `production-operations` | Scope cut of accepted work with no amendment entry | 「拆出去可以」: "the Captain approved splitting the database restore out of this PR … into task `production-database-restore`" (`e4462daa3`). Restore was in the task Scope ("restore the database"). | none, and no `## Captain amendments` |
| `cash-at-pickup` | 2+ rounds finding new gaps in the same class or file | Codex round 1 finding 1 puts the branch lock in `payment-store.ts` `signAsOwner`. Round 2 finding 1 is "Branch lock before booking state: `payment-store.ts` `open(…, lock)`" (`80502288e`). Round 3 P1 is the role check on `payment-routes.ts` (`27bee7ce0`). Round 4 P1 is the `PickupPayments.tsx` poll (`179ebbaba`). Roborev 822/825/828/834 repeat the polling and recovery findings (`8a4708e60`). 7 implementation cycles; 1 REJECTED + 5 PASSED validations. | none |
| `production-go-live` | Hard-to-reverse and approval/authority rule change | D2 "lock auto-publishing on `qnow-site` … this crosses that task's boundary". D5 amends ADR 0025 (operator secret on production). D6 "reopens ADR 0019 ruling 5". D1 amends ADR 0001 decision 18. Seven-row "Hard to reverse" table. All adopted by one joint approval (`b0f788cb4`, D-list `76660c15f`). The task also records `qnow-release-migration`'s open D4 as "Superseded in part" (`a82f53a8d`). That was an open decision, not a Captain ruling. | none |
| `production-incident-agent` | Design reversal; new authority surface | Cycle 2 replaces cycle 1 after the Captain's `revise` (`939da7855`). A machine account opens draft PRs, with a forbidden-path list (D7). A Netlify machine member is raised and left open. A Codex pass exists as `## Codex co-design (cycle 2)` (`60b6bf510`). It was the Captain's instruction and is not a role call. Gate then `hold`. | none |
| `owner-sms-notices` (boundary, pre-window) | Validation sent back 2+ times, same surface | Validation REJECTED twice on `plain-text.ts`: cycle 1 "link filter" (`b32ecc960`, 10-16 16:54), cycle 2 "two Material findings in `plain-text.ts`" (`6482bd1fa`, 10-16 23:02). Cycle 4 then changes the colon rule in the same file. | none |

**Cases checked, no trigger**
- **`go-live-consent`:** three validations, all PASSED. The notice wording changed once, in cycle 2. No repeated gap.
- **Validation sent back 2+ times, in window:** none.
- **Amendment that reverses an accepted ruling in window:** none recorded as an amendment.
  - The restore split and the go-live D1/D2/D5/D6 rulings above are the nearest cases.

Nothing was edited, committed or messaged. Scratch export: `/tmp/qs`; ledger: `/tmp/ledger.jsonl`.