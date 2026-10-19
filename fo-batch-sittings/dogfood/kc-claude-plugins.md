Observer dogfood sweep, 2026-10-20, repository kc-claude-plugins (read-only, kc-dev-flow-2:observer sonnet).

**Scope and method.** State checkout `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state` at `b2e7b938` (branch `spacedock-state/dev2`), working tree clean. Package: `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0`. Both `decision_ledger.py` and `role_triggers.py` ran on this state. Gate times below are UTC from the gate records. Commit times are +08:00.

- 34 Captain gate resolutions across 13 tasks fall in the window (gates recorded from 2026-10-17). All 34 are `approve`.
- There are 0 `Override:` rows in the ledger, and the whole 143-row ledger has 0.
- One correction to my own work: my first ledger read was overwritten by another session in shared `/tmp`. I discarded it and re-ran in a private directory.
- Figures labelled "FO's own" come from `captain-question-load.md` § Measured. They are the FO's transcript classification, and the transcript is machine-local, not in state.

## Q1 Batch dogfood

### Q1a Batches identified

| Batch / stage | Tasks | Gate rows (UTC) | Captain quote and reason | Commits |
|---|---|---|---|---|
| B2 backlog | workflow-budget-ratchet, special-role-triggers, worker-loads-declared-package, prod-security-validation-gate, ui-design-review-in-ideation, merge-gatekeeper | 6 rows, 10-17 06:10:07 to 06:10:37 | 「准」: "the six batch-2 backlog gates presented together in one message" | 080fadd3 to f40506fa |
| B2 ideation | the same six | 6 rows, 07:30:16 to 07:30:44 | 「那就照建議」, "after asking FO to restate the merge-gatekeeper D1 reasoning" | 5905c398 to dc73540e |
| B2 delivery, joint | special-role-triggers #664, ui-design-review-in-ideation #663 | 2 rows, 10-18 03:03:15 and 03:03:18 | 「批准並合併」: "the #664 and #663 delivery gates presented together" | becde7a3, 97ddcb90 |
| B2 delivery, single | ratchet #658, prod-security-validation-gate #659, worker-loads #661, merge-gatekeeper #666 | 13:48, 14:06, 14:31 on 10-17; 16:06 on 10-18 | one quote each | 44e3bdcb, dc4bd39e, bbbcc856, cf528f4a |
| B3 backlog | fo-write-checks, chat-only-evidence-observer-blind, captain-question-load, number-guards-readme-shrink | 4 rows, 10-18 16:56:47 to 16:57:03 | 「批准這些作為第三批」: "the five batch-3 backlog gates presented together" | 02288769, a22114f1, 85ccea50, 660ddbdf |
| B3 ideation | the same four | 4 rows, 10-19 00:43:52 to 00:44:09 | 「照建議」: "four batch-3 ideation gates presented together" | b29dbd6e, 6e62b135, 7b75cf34, dcdfaed1 |
| B3 delivery | number-guards-readme-shrink #670 (04:37:32), fo-write-checks #671 (08:09:20), captain-question-load #675 (14:21:21) | 3 single rows | 「准」 each | a18013f1, b1fe6a4b, e18c41bb |
| B3 delivery, chat-only | chat-only-evidence-observer-blind #679 | no gate record yet; task is at `validation` | n/a | n/a |
| Not in a batch | extension-instruction-reaches-dispatch (10-17 02:15), prod-security-review-gates (ideation-2 03:03, validation 04:32), delivery-gate-settles-skipped-checks (10-19 15:33 and 16:03) | 5 single rows | see Q1d | 2732fed1, 946aaa7c, 130416ce, 8074250b, 16758ef8 |

Outside state:
- The fifth B3 backlog gate (`merge-grant-need-poc`) is not in this workflow.
- The "merge-grant-need-poc closing gate", joint with #670's gate (reason text of a18013f1), is also not in this workflow. It sits in the `dev2-poc` workflow.
- Chat messages themselves are outside state. "Joint" is inferred from the shared quote and reason text plus timestamps 5 to 6 seconds apart, because Spacedock records one gate per task.

### Q1b Per task

| Slug | Gate rows (joint / single) | Other Captain rulings in state (commit) | Override | Own followups task |
|---|---|---|---|---|
| extension-instruction-reaches-dispatch | 1 / 1 (validation-2, 2732fed1; 3 earlier rows on 10-16 are outside the window) | Amendment 1 「修改 AC-6，讓 #652 一併把 README 傳給 laws_check」 (9e98e7c7). The Cycle 3 entry (03b30ad6) shows FO holding the PR and asking him. | 0 | extension-instruction-followups, created 10-16 16:00 |
| prod-security-review-gates | 0 / 2 (ideation-2, validation) | Amendment 1 「就按照新的建議」 (470199a8), Amendment 2 「照這樣做」 (dff76c9a), both 10-16 | 0 | prod-security-check-round3-followups |
| workflow-budget-ratchet | 2 / 1 | none as an amendment. The gate reason carries 「合併且開任務，先走poc證明真的比較好再繼續」 after he asked how the change protects attention. | 0 | workflow-budget-ratchet-followups |
| special-role-triggers | 3 / 0 | Amendment 1 「第四題同意」 (4c1b7183, after validation-1) | 0 | special-role-triggers-followups |
| worker-loads-declared-package | 2 / 1 | none. The gate reason carries 「批准，也預先授權你合併」. | 0 | worker-loads-declared-package-followups |
| prod-security-validation-gate | 2 / 1 | none | 0 | prod-security-validation-gate-followups |
| ui-design-review-in-ideation | 3 / 0 | none (preview comments in the file are replay findings, not rulings) | 0 | ui-design-review-round3-followups |
| merge-gatekeeper | 2 / 1 | Cycle 2 ruling 「同意」 on a compromise instead of a waiver (3e2b7490). Amendment 1 「同意」 narrowing the PR (c99159cf). | 0 | merge-gatekeeper-followups |
| fo-write-checks | 2 / 1 | none | 0 | fo-write-checks-followups |
| chat-only-evidence-observer-blind | 2 / 0 (delivery gate not recorded) | none | 0 | chat-only-evidence-observer-blind-followups, created 10-19 23:59 |
| captain-question-load | 2 / 1 | Amendment 1 (9b7cac15, re-authorization after a refused edit). Amendment 2 「…為何你沒有自動找 CE 來問？此外改下你自己的 paseo 內的名字」 (4028338c). He asked for the CE call with 「對」 (35bdf5ef). | 0 | none (declines went to fo-write-checks-followups) |
| number-guards-readme-shrink | 2 / 1 (the validation row was presented jointly with a gate outside this state) | none | 0 | number-guards-readme-shrink-followups |
| delivery-gate-settles-skipped-checks | 0 / 2 | The backlog gate "binds that question and answer after the fact" (8074250b). The ideation reason says "after the re-briefing" (16758ef8). | 0 | not yet (task is at `implementation`) |

Totals:
- 34 rows: 22 joint (6+6+2+4+4) and 12 single.
- By my count, 17 Captain messages produced those 34 rows.
- Batch 2 is 18 rows in 7 messages (backlog 1, ideation 1, delivery 5), matching FO's own count in `captain-question-load.md` § Measured. Batch 3 in state is 11 rows in 5 messages, plus the outside-state gates.
- FO's own batch-2 figures: 22 Captain answers (7 gate, 6 needs-decision or amendment, 5 merge ask, 4 procedural) and 63 asks over six tasks. One task, merge-gatekeeper, drew 7 of the 22.
- The batch-3 recount (AC-5) is not in state. It is marked SKIPPED in the captain-question-load stage report, and `fo-batch-sittings.md` lists it as the baseline.

### Q1c Interim rules in state

| Rule | Shows in state? | Evidence |
|---|---|---|
| Gates per task, one stage per message, reason names joint presentation | Yes for backlog and ideation in both batches. Delivery is mostly single. | Reason strings in the Q1a table. Each task keeps its own gate record. |
| `### Batch overlap` in every ideation | Yes, 13 of 13 tasks | Each task file has the section. Caveat: batch-2 designs were read against siblings' backlog stubs, and number-guards-readme-shrink says "Not read yet: the three siblings' designs". |
| Numbers reserved before the batch's first dispatch | Partly | First ideation dispatches: B2 10-17 14:11 and B3 10-19 00:57. ADR lines were added at B2 15:31 (040e1068, 03d11e6e, cdf3f576, 1bd8448c) and B3 08:44 (e2e9c881, f66e4922). Both are before the first implementation dispatch (B2 15:31:48, B3 08:45:25), but after the first dispatch of any kind. So "before the first implementation dispatch" holds, and "before the batch's first dispatch" does not. |
| Number reservation exceptions | Yes | fo-write-checks ADR 0025 was added at 12:38 (b7220eab), after implementation-1 (08:45) and validation-1 (09:02). prod-security-review-gates ADR 0018 was added 2 minutes after implementation-1 and re-reserved as 0019 after a collision (77ebe044, 53b877b9). |
| Package rule conflict | Yes | The captain-question-load observer, line 3: reserving 7.5 hours before the implementation dispatch is a violation of "when the implementation dispatch is built and not earlier". |
| Number line missing from dispatch scope notes | 4 of the 6 batch-2 observers (ratchet, prod-security-validation-gate, ui, prod-security-review-gates). FO's own count in fo-write-checks is 3 of 6. | The four observer reports. |
| One followups task per delivered task | 10 of 11 delivered tasks | The one miss is captain-question-load, which declined into `fo-write-checks-followups`. Each followups file's creation commit is earlier than its gate (compared after time-zone conversion). |
| Repeated finding class calls the chief-engineer | Partly | Calls exist for 4 tasks. See Q2. |
| Repairs and review rounds between sittings | Not separable in state | The Feedback Cycle commits fall between gate commits. Chat timing is outside state. |

### Q1d Extra Captain turns visible in state

| Slug | Evidence (commit) |
|---|---|
| B2 ideation | He asked FO to restate the merge-gatekeeper D1 reasoning before 「那就照建議」 (5905c398 reason). |
| workflow-budget-ratchet | He asked how the change protects attention, then added a POC task to the approval (44e3bdcb). |
| special-role-triggers | The amendment asks "第 4 題", so FO put at least four questions in one message (4c1b7183). |
| merge-gatekeeper | A waiver recommendation became a compromise 「同意」 (3e2b7490). Cycle 3 ended in a narrowing amendment (c99159cf). FO's own count: 3 procedural asks (repository create, deletion handoff, push). `--require 0023` exit 1 was passed through (merge-gatekeeper observer, line 10). |
| captain-question-load | His merge edit was refused, so he gave a re-authorization quote (9b7cac15). He asked FO to restate the merge wording as 「合理嗎」. He asked why FO did not call the CE (4028338c). The "bypass" request is only in the observer text. |
| delivery-gate-settles-skipped-checks | The backlog gate was recorded after the chat answer (8074250b). The ideation needed a re-briefing (16758ef8). |
| fo-write-checks | 「after the Chinese gate briefing」 (b1fe6a4b reason). |
| extension-instruction-reaches-dispatch | FO held the PR at Cycle 3 and asked him whether to amend AC-6 (03b30ad6, 9e98e7c7). |
| Holds he overrode | None. There are 0 `hold` rows in the window. The only `hold` in the ledger is outside the window. |

## Q2 Special-role calls

### Q2a `role_triggers.py` owed-versus-made, per task

| Slug | Script result | Reviewer line made? |
|---|---|---|
| extension-instruction-reaches-dispatch | OWED: chief-engineer for Cycle 3, and engineering-reviewer for Amendment 1 | none |
| prod-security-review-gates | OWED: chief-engineer for Cycle 3, and engineering-reviewer for Amendments 1 and 2 | A CE line exists but sits under `### Feedback Cycles`, not `## FO alignment` (42946bb3). The script ignores it, and the observer flags it. No engineering-reviewer line. |
| special-role-triggers | OWED: engineering-reviewer for Amendment 1 | none |
| ui-design-review-in-ideation | OWED: chief-engineer for Cycle 3 | A CE line exists under `## FO alignment` (183a6338). Its question says "third repair cycle", not the token `Cycle 3`, so the script does not recognise it. Made but unrecognized. |
| merge-gatekeeper | OWED: chief-engineer for Cycle 3, and engineering-reviewer for Amendment 1 | A CE line exists (757e9c24), with the same wording problem ("third repair cycle"). No engineering-reviewer line. |
| workflow-budget-ratchet, worker-loads-declared-package, prod-security-validation-gate, fo-write-checks, chat-only-evidence-observer-blind, captain-question-load, number-guards-readme-shrink, delivery-gate-settles-skipped-checks | "0 event(s) read at HEAD", exit 0 | captain-question-load has a CE line (35bdf5ef) that the script does not count. |

`fo-batch-sittings` also reports 0 events.

### Q2b Calls that look owed by judgment but are not flagged by the script

| Slug | Trigger by judgment | State lines and commits | Reviewer line? |
|---|---|---|---|
| special-role-triggers | Two review rounds each found new gaps in `role_triggers.py`, and validation passed three times. | The task has no `### Feedback Cycles` heading. Its two `- Cycle N` lines (f4bb51b3) sit inside the Design section, so the script reads 0 cycles. Cycle 1 is P2 on the date rule and section scope (review:5558171225). Cycle 2 is P2 on heading forms (review:5558381167). The task that shipped the trigger script had no CE call. | none |
| fo-write-checks | Two review rounds found new gaps in the same two files. | Cycle 1 (ff1dcd89) is two P2: a short declined item passes, and an unanchored reserved-line search in `delivery_gate.py` and `dispatch_records.py`. Cycle 2 (46f47970) is two P2: nested parentheses, and an Oxford-comma amendment list, in the same functions. Only 2 `- Cycle` lines exist, so the script's threshold of 3 is not reached. | none |
| extension-instruction-reaches-dispatch | Two rounds on the same match. | Cycle 1 (d9442617) is a missing trailing boundary on the script path. Cycle 2 (76bc42e3) is the same boundary letting `/` follow. | none (waiver or call owed by the script as well) |
| chat-only-evidence-observer-blind | A finding class repeated across tasks. | Its single P1 is "not line-anchored" search in `delivery_gate.py` `clause()` (f487d235). fo-write-checks cycle 1 has "unanchored" in `dispatch_records.py`. extension-instruction has the path boundary. ui-design and prod-security-review-gates have parser and fence variants. This is my reading of the class, not a state label. | none |
| merge-gatekeeper | Amendment reverses an approved design. | The ideation gate (dc73540e) accepted the per-class grant design. Amendment 1 (c99159cf) supersedes AC-3, 4, 5, 7, 8, 11 and 12 and parks the grant half. The ADR draft would supersede a sentence of ADR 0011 (merge never delegated). | CE yes (757e9c24). Engineering-reviewer none. |
| captain-question-load | Change to the merge/approval rule, plus 3 review rounds on the merge wording. | Amendment 1 (9b7cac15) changes the Delivery authority wording so an approved validation question can carry the merge. The amendment says `Supersedes: none`, so the script does not fire. Rounds: Codex P1 (6cf44a91), Codex P1 and P2 (6badfc24), and roborev High. | CE came only after his 「對」 (35bdf5ef). Engineering-reviewer none. |
| delivery-gate-settles-skipped-checks | Design reverses an earlier ruling. | Its gate reason says D1 "reverses the SKIPPED or NEUTRAL clause of merge-gatekeeper AC-1" (16758ef8). He approved it after a re-briefing. | none |
| prod-security-review-gates | Amendments 1 and 2 reversed prior approvals. | Amendment 2 (dff76c9a) supersedes AC-1, 2, 4, 5, 6 and 7 (AC-7 was itself the product of Amendment 1) and redoes the whole Design. | none (CE line present but misfiled) |
| ui-design-review-in-ideation | Repair cycles in the same file. | Cycles 1 to 3 (2e845bd9, c72fb569, e7e80f36) all hit `design_surfaces.py`, followed by a roborev 830 repair. | CE yes (183a6338) |

For the other three tasks (workflow-budget-ratchet, worker-loads-declared-package, prod-security-validation-gate) I found no judgment-owed case. number-guards-readme-shrink also has none, with no cycle or amendment.

### Q2c `Reviewer:` lines that exist and what the role recommended

| Slug | Line (commit) | Recommendation recorded |
|---|---|---|
| prod-security-review-gates | CE opus 2026-10-17, "patch the hand YAML parser again, or change the contract…?" (42946bb3) | Option (c): stop teaching the parser more shapes and accept only the reviewer's documented shape. Measured on 15 saved reports with 0 false holds. No Captain amendment needed. |
| ui-design-review-in-ideation | CE opus 2026-10-17, "repair the fence class once, decline to backlog, or narrow the PR?" (183a6338) | Narrowed third repair: read FO alignment from unfenced text. Compare main and candidate over four corpora. Decline the Codex round-3 P2 to `ui-design-review-round3-followups`. |
| merge-gatekeeper | CE opus 2026-10-18, "repair again, or narrow the PR…?" (757e9c24) | Counted 13 P1/High findings: 9 in grant, merge-line and calibrate code; 4 in the never-list and profile reading; 0 in holds, points and record. Ship about 244 code lines now and move the grant half out. The Captain approved this as Amendment 1, and the grant half became the POC task `merge-grant-need-poc`. |
| captain-question-load | CE opus 2026-10-19, "what is the smallest next step…?", asked by the Captain (35bdf5ef) | The advice text is not in the task file. Amendment 2's "Asked" quotes FO's follow-up question: waive the Codex P2 and roborev High into `fo-write-checks-followups` with ADR 0023's reopen condition. |
| Not role calls | prod-security-review-gates line 280, "Reviewer: one run per design…", and ui-design-review-in-ideation line 83, "Reviewer: open. Installed `design:design-critique`…" | These are a cost bullet and a scope bullet. |

No `engineering-reviewer` call or waiver exists anywhere in the window.

```
剩餘:   none; read-only collection complete (no edits, commits or messages sent)
下一步: 回收者 (the caller) to merge this with the relay, web and qnow observer reports
可收線: 是
```