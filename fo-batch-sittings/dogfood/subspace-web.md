Observer dogfood sweep, 2026-10-20, repository subspace-web (read-only, kc-dev-flow-2:observer sonnet).

**Scope.** State checkout `/Users/kent/conductor/workspaces/subspace-web/dev2-fo/docs/dev2/.spacedock-state`, reading committed state only. Package is kc-dev-flow-2 0.25.0. Five tasks have gate resolutions on or after 2026-10-17:
- `others-highlights-in-author-colour` (archived)
- `comment-links-open-with-confirm` (archived)
- `disclosure-chevrons-follow-state` (archived)
- `ac9-feedback-phone-revision-drawer-note-time` (archived)
- `web-render-rules` (live)

The ledger gives 13 rows in the window: 12 Captain resolutions and 1 FO withdrawal. `decision_ledger.py` ran clean, and every window row has `override: null`.

One correction: my first ledger run wrote to a shared `/tmp` filename that another process overwrote, so I discarded it. Everything below comes from a rerun in a private directory.

Times below are the state commits' local time (+0800).

## Q1 Batch dogfood

**(a) Batches in state**

| Batch | Slug / stage / decision | Evidence (quote, commit) | Counts |
|---|---|---|---|
| A, 10-17 10:09, 3 gates within 7 s | `others-highlights-in-author-colour` validation revise; `comment-links-open-with-confirm` validation revise; `disclosure-chevrons-follow-state` ideation approve | Each reason reads 「准」 "to the FO's package". Gate commits `da2167c`, `bb17e77`, `352db63`. All three amendments carry the same `Asked:` line: "approve the three web items … and fix H1+N2+N5, L1+L2, and N1 before launch?" | 3 Captain answers recorded, from 1 question. The stages are mixed (2 validation, 1 ideation), so this is not "all gates of one stage". |
| B, 10-17 11:11, 3 gates within 7 s | The same three tasks, all validation approve | Identical reason in all three: 「准」 "validation passed; deliver as a pull request (approval also covers later external-review rounds on the same PR)". Commits `fe153d1`, `0e4aa92`, `afe36a5` | 3 answers, all joint. No reason names "joint" or "package". |

- **Between A and B:** FO repairs and rechecks ran with no Captain turn, 10:42 to 11:04. Examples: `b9569e7`, `bf09765`, `37c062f`, `7a5efc0`.
- **Joint stated in a reason:** only batch A, as "package".
- **Before the window:** two earlier joint pairs. Backlog gates for `disclosure-chevrons-follow-state` and `comment-links-open-with-confirm` on 10-15 at 08:34:08 and 08:34:19, 「兩題都好」. Ideation gates for `others-highlights-in-author-colour` and `comment-links-open-with-confirm` on 10-16, 5 minutes apart.

**(b) Counts per task (window only)**

| Task | Captain gate resolutions | Joint | Single | Other recorded Captain rulings |
|---|---|---|---|---|
| `others-highlights-in-author-colour` | 2 (revise, approve) | 2 | 0 | Amendment 1 (supersedes AC-4 and AC-15), `5b7f98e`; N5 prompt quote 「咦，為何…後面有兩則沒有順序標記？」 |
| `comment-links-open-with-confirm` | 2 | 2 | 0 | Amendment 1 (supersedes AC-1), `f8232f2` |
| `disclosure-chevrons-follow-state` | 2 | 2 | 0 | Amendment 1, `Supersedes: none` (N1), `b1415f5` |
| `ac9-feedback-phone-revision-drawer-note-time` | 4 (backlog, ideation revise, ideation approve, validation approve) | 0 | 4 | Drawer choice 「Ｂ」 (in chat), recorded only as an FO withdrawal of ideation attempt 2 (`bbdb40d`). Backlog 「准」 was "answering this question as asked in chat". |
| `web-render-rules` | 2 (revise, approve) | 0 | 2 | None in the window. A 10-10 amendment also exists. The dispatch record holds the 「Ａ」 timing choice (merge after 10/22). |
| Total | 12 | 6 | 6 | 3 amendments, 0 Override lines, 0 waivers |

Checks behind those totals:
- `git grep Override:` over the window tasks matches design prose only (the ac9 design says "No gate record carries an Override: line").
- `grep -i 'waive|not run:'` finds no waiver of any role call. The matches are "Not run:" validation limits.

**(c) Interim rules in state**

| Rule | Shows? | Evidence |
|---|---|---|
| One answer, gates recorded per task | Yes, batches A and B | See (a) |
| Reason names the joint presentation | Partly | Batch A says "package". Batch B does not. |
| FO repairs and rechecks between sittings | Yes | See (a), repairs between A and B |
| `### Batch overlap` section | No | `grep -rniE 'batch overlap'` over the whole state returns nothing. The nearest thing is a sibling `git merge-tree` clean check inside the `others-highlights-in-author-colour` validation report. |
| Numbers reserved before the batch's first dispatch | No | Each task's `ADR:` line lands in the same minute as its own implementation dispatch. `others-highlights-in-author-colour` 0038 and 0039 at `bb4b5f8` 10-16 17:17, dispatch `b210e6c` 17:18. `comment-links-open-with-confirm` 0040 at `43750c0` 17:22, dispatch `0000d8b`. `disclosure-chevrons-follow-state` 0041 at `b1415f5` 10:09, dispatch `aba5b72` 10:10. `ac9-feedback-phone-revision-drawer-note-time` 0042 at `faa8f1e` 16:10, dispatch `14dfef1` 16:11. `web-render-rules` 0043 in the dispatch commit `97e10be`. The first two are consecutive and about 5 minutes apart, which is not proof of an up-front reservation. |
| One follow-up backlog task per delivered task | No | Backlog tasks added in the window: `number-tag-shows-send-time` (`8247bed`), `phone-stage-reserve-spec-waits` (`c59873c`), `author-handle-after-name` (`bc21e07`). `number-tag-shows-send-time` follows the Captain's deferral of ac9 item 4b. `phone-stage-reserve-spec-waits` was opened after a release-PR test failure, and cites the ac9 validation Polish P3 as the same lag. No follow-up exists in state for `others-highlights-in-author-colour`, `comment-links-open-with-confirm` or `disclosure-chevrons-follow-state`, though all three recorded Polish or Deferred items. |

Outside state: the chat presentation of batches A and B, and whether any follow-up lives in another repo or tracker.

**(d) Captain extra turns visible in state**

| Slug | Evidence |
|---|---|
| `others-highlights-in-author-colour` | Validation asked twice: revise, then approve. The task's `observer.md` marks as "can't tell" whether the 10:09 「准」 answered the probe-naming question or the batch question. "Which question he answered is in chat." |
| `comment-links-open-with-confirm` | Validation asked twice. |
| `ac9-feedback-phone-revision-drawer-note-time` | Ideation asked three times: revise, FO-withdrawn attempt 2 (because 「Ｂ」 arrived mid-ask), approve. Backlog 「准」 was given in chat. |
| `web-render-rules` | FO recommended revise for two Polish items, so the Captain answered 「照建議送回修那兩項」 and then 「准」 6 minutes later (`0b4b2dc`, `32093ad`). The validation report itself says "Two Polish items for FO to route". |
| `others-highlights-in-author-colour` | Dispatch Retries: "Retry 4 … nudged to resume … after the Captain switched accounts". |
| `others-highlights-in-author-colour`, `comment-links-open-with-confirm` | The Captain added scope at the gate (H1, N2, N5, L1, L2). |

- **Holds he overrode:** none in the window.
- **Procedural asks recorded:** the clause "Delivery approval also covers later external-review rounds on the same PR" is in every validation gate question from 10-17 onward. That is 8 gates; the ledger shows none earlier.

## Q2 Special-role calls

**Script result (`role_triggers.py`, HEAD)**

| Slug | Result |
|---|---|
| `others-highlights-in-author-colour` | exit 1, owed: engineering-reviewer for Amendment 1 |
| `comment-links-open-with-confirm` | exit 1, owed: engineering-reviewer for Amendment 1 |
| `disclosure-chevrons-follow-state` | 0 events (Amendment 1 says `Supersedes: none`, `Design: none`) |
| `ac9-feedback-phone-revision-drawer-note-time` | 0 events |
| `web-render-rules` | 0 events |
| `author-handle-after-name`, `number-tag-shows-send-time`, `phone-stage-reserve-spec-waits`, `web-draw-figures`, `webkit-on-release-pr` | 0 events |

- **Script blind spot:** Event A needs a `### Feedback Cycles` section with a `- Cycle N` line, and no window task has one. Cycle counts live only in Stage Report titles, so the script reads 0 events regardless.
- **Uncommitted change:** `web-render-rules.md` has a working-tree edit (`mod-block: merge:pr-merge`) that the script does not read.

**Reviewer: lines that exist**

| Slug | Line (commit) | What the role recommended |
|---|---|---|
| `others-highlights-in-author-colour` | `engineering-reviewer opus 2026-10-15`, on whether the frame bridge may carry peer-marks (`04b85ff`) | SAFE WITH CONDITIONS C1–C5, recommendation "adjust". The implementation report says all five were built. |
| `others-highlights-in-author-colour` | `engineering-reviewer opus 2026-10-16`, on `peer-marks:probe` (`ff3ce97`) | SAFE, proceed, with a stated disproof condition (`peerFresh` gate removal turns the navigation spec red). Validation cycle 2 ran that mutation and it went red. |

No other Reviewer line exists in the whole state (`grep -rnE '^(- )?Reviewer:'`). No `chief-engineer` call exists, and no "not run" waiver.

**Calls owed by judgment beyond the script**

| Slug | Case | State evidence | Reviewer line? |
|---|---|---|---|
| `others-highlights-in-author-colour` | Amendment 1 replaces approved AC-4 and AC-15 (a card without an anchor "draws exactly as 0.2.25") | Amendment 1, validation gate revise at 10:09. Amendment committed `5b7f98e` (10:52), after repair 2 reported (`bf09765`, 10:51). The `observer.md` flags that the repair-2 checklist names no amendment. | No line names Amendment 1, and no waiver. The script flags this too. |
| `comment-links-open-with-confirm` | Amendment 1 supersedes AC-1, the sentence "a link's text is exactly the address as sent" | `f8232f2` 10:42, then AC-9 replaces it (`a298bc6`). | None. The script flags this too. |
| `others-highlights-in-author-colour` | Validation sent back twice on the peer-marks surface. Cycle 1 recommended REJECTED (F1: matching cost 95.7 s; F2: a navigated frame is sent marks). Then Captain revise on H1/N2/N5. | Repair 1 (`dacb0c9`) added `peer-marks:probe` to the Captain-approved bridge table. Repair 2 (`6b21fd3`) changed `src/review-shell.js` again. | The probe has a line (above). The H1/N2/N5 round has none. The round count is 3 validations and 3 implementation passes. |
| `ac9-feedback-phone-revision-drawer-note-time` | Ideation reached cycle 3 (`0c62c45`, `371f074`). The Captain's 「Ｂ」 replaced the cycle-2 inset drawer. Item 5 amends ADR 0017. | Withdrawal `bbdb40d`. Reason: "Captain chose drawer variant B … while attempt 2 was open". | None. This is Captain-driven rather than FO reversing a ruling, and I found no repeated finding class. Cycle 3 is not under `### Feedback Cycles`, so the script does not count it. |
| `ac9-feedback-phone-revision-drawer-note-time` | Item 3 narrows the 10-17 dash rule from `others-highlights-in-author-colour` Amendment 1 (ADR 0039) | The design cites the Captain's 10-19 observation and records "No gate record carries an Override: line". | None. A later Captain observation, not an FO reversal. |
| `web-render-rules` | Cross-repo contract change (Review & Gate v1 §6). The task's own "Pilot boundary" says stored anchors containing `~~` or a CriticMarkup delimiter stop resolving, and "how many exist was not measured". | Validation "Does not cover … stored anchors that stop resolving". | None, though the task stays Pilot. |
| `comment-links-open-with-confirm` | New link-opening path from untrusted comment bodies | Validation attacked it itself (about 45 crafted bodies, 10 mutations). | None. This is a weak candidate. |
| `disclosure-chevrons-follow-state` | Validation sent back 0 times, no repeated finding. No call looks owed by judgment. | n/a | n/a |

I found no case in the window of two or more review rounds finding new gaps in the same sentence or file, other than the `src/review-shell.js` surface in `others-highlights-in-author-colour` above.

Not decidable from state: whether either owed engineering-reviewer call was made in chat. Anything held by the observer role is out of scope here.

Files are all under `/Users/kent/conductor/workspaces/subspace-web/dev2-fo/docs/dev2/.spacedock-state/`:
- `_archive/others-highlights-in-author-colour.md`
- `_archive/others-highlights-in-author-colour/observer.md`
- `_archive/others-highlights-in-author-colour/engineering-review-bridge.md`
- `_archive/comment-links-open-with-confirm.md`
- `_archive/disclosure-chevrons-follow-state.md`
- `_archive/ac9-feedback-phone-revision-drawer-note-time.md`
- `web-render-rules.md`