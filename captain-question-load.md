---
title: The Captain answers fewer FO questions per delivered task, without losing a decision that is his
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: implementation
gates:
    version: 1
    records:
        - id: gate:captain-question-load:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:captain-question-load-backlog-1
              briefing:
                id: briefing:captain-question-load:backlog:attempt-1:revision-1
                digest: sha256:f5df5bbb224d836196b8fe7f7d580cb661bba02b1564603d5073b4fef3eb9bdc
                room-ref: ./captain-question-load/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:captain-question-load:backlog:1
                briefing: briefing:captain-question-load:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-18T16:56:58.283398Z"
                decision: approve
                reason: Captain approved in chat (「批准這些作為第三批」) the five batch-3 backlog gates presented together, accepting the recommended profiles and the stated grouping and order
              application:
                target-stage: ideation
                state: consumed
        - id: gate:captain-question-load:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:captain-question-load-ideation-1
              briefing:
                id: briefing:captain-question-load:ideation:attempt-1:revision-1
                digest: sha256:83a268738d4202cf24a5a7899dc0a2bb046c266513d09699286a8de7f8b738f7
                room-ref: ./captain-question-load/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:captain-question-load:ideation:1
                briefing: briefing:captain-question-load:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-19T00:44:03.5019Z"
                decision: approve
                reason: Captain approved in chat (「照建議」) the four batch-3 ideation gates presented together, accepting each task's stated decisions and FO's implementation order
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-18T16:57:42Z
worktree: .worktrees/spacedock-ensign-captain-question-load
---

Filed for batch 3 on the Captain's 「先走批次三規劃」 (chat, 2026-10-19), after FO reported that most of his turns in batch 2 were answering FO's questions rather than reviewing PRs. His goal for batching (chat, 2026-10-16): 「這樣我才可以從一直在追每個 FO 過程中解放出來」.

## Scope

- Measure first, from the batch-2 decision ledger rows and the gate briefings of this workflow (2026-10-17 to 10-19): every Captain decision per task, split into stage gates, Needs decisions, amendments, merge asks, and procedural asks (a push the permission check refused, a throwaway repository, a PR-body edit, a waiver), and how many he answered with a plain approval of FO's recommendation.
- Then find which kinds a written standing rule could settle without him (for example a delivery gate that carries the merge grant by default, or a repair inside an approved design), and which must stay his (ADR 0011: authority, approval, merge, outward-facing actions, irreversible changes and money).
- Existing pieces: batch sittings (memory note fo-batch-sittings-interim), pre-authorized merges at delivery gates, the qnow R11 batching numbers the qnow FO owes.
- Non-goals: to be set at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain approved planning batch 3.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none

## Design

Ruling in one paragraph. Of the 22 answers the Captain gave FO in batch 2, a written rule can settle at most 2 (one removal, one conditional); the other 20 stay his under ADR 0011, README step 4, ADR 0009, his own ruling or the permission check, or are too rare to justify a rule. 20 of the 22 accepted FO's recommendation as stated, but 8 came with a question or comment of his before or inside the message, so the acceptance rate is not evidence for delegating. The change is one README sentence at net zero words plus the text of one script line: a delivery gate question may carry the merge of the validated head and the removal of the task's clean worktree, so he says it once, in words the question printed, and `delivery_gate.py` stops telling FO to ask when the question already covered it. FO's 12:31Z statement on 2026-10-18 holds on the count (about 20) but not on the kind ("many of them procedural"): procedural answers are 4 of 22.

### Chain check (Spacedock, kc-dev-flow-2, adopters)

- **Spacedock 0.27.2** (`spacedock gate --help`): `gate record --actor agent:first-officer` already takes `--conn-quote` and `--conn-source`, so a decision under a quoted grant is recorded as FO's. There is no multi-gate batch, no count of asks and no merge grant primitive. Nothing to reuse beyond the quote flags the README's Delivery authority already cites.
- **kc-dev-flow-2 0.25.0** (read at `origin/main` c60e89e1): `decision_ledger.py` reads gate rows only (its docstring: "one JSON line per gate resolution or withdrawal"). README step "A Needs decision put to the Captain at a gate" already makes a plain approval accept a recommendation when the question says so (L1 of ADR 0011). ADR 0015 is the precedent for a grant carried by the gate question ("this approval is that grant for this task") and its rejected option names the cost: "one more message and approval from him per task". ADR 0009 keeps learning-PR merges his. ADR 0020 forbids a README rise without his quoted ruling. `delivery_gate.py check` already holds the merge on head, CI, draft, base and file list and prints `next: hold the ask until the required CI has finished green on this head.`
- **Adopters**: relay's `docs/dev2/README.md` carries the same "is not permission to push, create or merge" sentence (`git grep` on its HEAD, 2026-10-19). The qnow R11 batching numbers the qnow FO owes are not in `docs/dev2` of `origin/next` (`git grep` for `R11|batching`) nor in its four `spacedock-state/*` branches (`git grep` for `batching|decisions per|questions per|asks per`, 2026-10-19), so no sibling number exists to reuse. I ran `git fetch` once in the qnow clone (a ref update, no file change).
- **Past rulings**: `git -C <state> grep -n 'Override:'` hits only prose in archived designs and observer reports, none on a delivery or merge question; the ledger shows 0 `override` rows. So no past ruling went against a similar recommendation. The merge-gatekeeper amendment 1 (「同意」, 2026-10-18) removed FO's merging from `delivery_gate.py`; this design adds no merge logic: the one script change is the text of the `next:` line that check prints.

### Measured

Window 2026-10-17T05:56Z (「開始批次2規劃」) to 2026-10-18T16:24Z; the six batch-2 tasks (the six named in the batch-2 backlog question) plus what they spawned. Sources and how to reproduce:

1. `python3 -B -I <package>/scripts/decision_ledger.py <state>` printed 134 rows, 119 by the Captain over 2026-09-16 to 10-18: 113 approve, 5 revise, 1 hold. In the window it holds 18 rows for the six tasks (6 backlog, 6 ideation, 6 validation), all approve, 0 `override`. Backlog gates over the whole record: 43 of 43 approved.
2. The 18 rows were answered in 7 messages: backlog 1, ideation 1, delivery 5 (#658, #659, #661, #663 with #664, #666). Group by `task` and `at` in the output.
3. Everything else is chat. The FO session transcript (`~/.claude/projects/-Users-kent-conductor-workspaces-kc-claude-plugins-colombo/5c030106-8d82-4542-855e-1498b2563c69.jsonl`, machine-local) lists 33 Captain messages in the window with the script below; 11 are his own (3 session-limit nudges 「繼續」, 5 questions or comments, 2 format corrections 「中文簡報」 and 「中文討論，一題題來」, 1 command), 22 answer an FO ask. I classified the 22 by reading the FO message before each.

```
python3 -I - "$SESSION_JSONL" <<'PY'
import json, sys
for line in open(sys.argv[1]):
    try: d = json.loads(line)
    except ValueError: continue
    if d.get("type") != "user" or d.get("isSidechain"): continue
    c = d["message"]["content"]
    t = c if isinstance(c, str) else " ".join(x.get("text", "") for x in c if x.get("type") == "text")
    if t.strip() and not t.lstrip().startswith("<") and "Another Claude session" not in t:
        print(d["timestamp"][:16], t.replace("\n", " ")[:100])
PY
```

Blind spot: 15 of the 22 answers (68%) leave no gate row, so `decision_ledger.py` cannot see them; this is the gap `chat-only-evidence-observer-blind` is scoped on. Not measured: minutes per answer.

| Kind | Answers | Share | Plain approval of FO's recommendation |
|---|---|---|---|
| Stage gates (alone or with a merge grant) | 7 | 32% | 6 |
| Needs decision or amendment outside a gate | 6 | 27% | 6 |
| Merge asks outside a gate message | 5 | 23% | 5 |
| Procedural (throwaway repository ×2, refused push, worktree cleanup) | 4 | 18% | 3 |
| **Total** | **22** | | **20** |

The two that were not plain: 13:48 (accepted #658 but added "先走poc證明真的比較好再繼續", narrowing FO's index-first task into a POC) and 04:55 (FO recommended `gh auth refresh -s delete_repo`; he chose to delete the repository himself). 8 of the 22 came with a question or comment of his before or inside the message (06:42, 06:44, 07:30, 12:35, 13:48, 14:34, 16:06, 16:21), and four of those changed the outcome: 13:27 and 13:39 produced the README-index POC, 06:42 made FO withdraw its waiver recommendation for a compromise, 12:30 produced the narrowing of #666.

Asks per task, counting each decision FO put to him (63 in all; 17 ideation decisions D1.. and 6 "decline into followups" items were accepted inside a gate by the question's "Approving accepts" sentence):

| Task (PR) | Gates | In-gate items | Merge | Needs or amendment | Procedural | Asks |
|---|---|---|---|---|---|---|
| workflow-budget-ratchet (#658) | 3 | 6 (D1-D4, decline, PR-body replace) | 1 in gate | 0 | 0 | 10 |
| special-role-triggers (#664) | 3 | 4 | 1 in gate | 1 (AC-2 amendment) | 0 | 9 |
| worker-loads-declared-package (#661) | 3 | 2 | 1 in gate | 0 | 0 | 6 |
| prod-security-validation-gate (#659) | 3 | 5 | 1 alone | 0 | 0 | 9 |
| ui-design-review-in-ideation (#663) | 3 | 4 | 1 in gate | 0 | 0 | 8 |
| merge-gatekeeper (#666) | 3 | 3 | 1 in gate | 2 (waiver, narrowing amendment) | 3 (repository create, deletion handoff, push) | 12 |
| Not one task: learning PRs #662 #665 #667 and the Release PR; README-index POC open, standard and close; laws-check enable; worktree cleanup | 0 | 0 | 4 alone | 4 (POC ×3, laws-check) | 1 (worktree cleanup) | 9 |

The rows sum to 63 (54 on the six tasks, 9 not on one). One task, merge-gatekeeper, drew 7 of the 22 answer messages (01:53, 04:55, 06:42, 06:44, 08:30, 12:35, 16:06) beside its 2 shared gate messages, through four validation rounds before he narrowed it. The chief-engineer call owed at a third Feedback Cycle (special-role-triggers D1, released in 0.25.0) is the existing lever on that tail; this task adds none.

### PRFAQ

**Press release.** From batch 3, a delivery gate question says what his one approval covers: the later review rounds it already covered, the merge of the validated head after `delivery_gate.py check` exits 0, and removing the task's clean, pushed worktree. He says he merges himself to keep the merge. Every other ask stays where ADR 0011 puts it.

**FAQ**
- *Does FO now merge for him?* Only when he approved a question that said so, for the head the check passed; 5 of the 6 batch-2 delivery approvals already carried his typed 「授權合併」, and the batch-2 accident count for "FO merged without his merge word" is 0 (merge-gatekeeper `### The bite, counted`). The two merged-head accidents of 2026-10-13 led to `delivery_gate.py`, which this keeps in the path.
- *Why so little removed?* Gates, merges, waivers, amendments, acceptance standards and consents are on the never-delegated list or README step 4. Delegating backlog gates would save one message per batch (43 of 43 approved, but 8 of 22 answers came with a question or comment of his), so no ADR 0011 change is proposed.
- *Why not let learning-PR merges ride along with the next message?* Those merges stay his (ADR 0009) and he ruled against stacking asks (「一題題來」, 14:31); bundling removes no decision and no answer.
- *Why no rule for the throwaway repository, the POC close or the AC-2 repair?* Each occurred once in the archive (the other throwaway repositories in task files were local `/tmp` ones, which asked nothing), and the without-it test needs a bite.
- *What stays outside this task?* The refused push is the session's permission check, not a workflow rule; its lever is his permission settings, not designed here (effect unmeasured). The 3 session-limit nudges and the 2 language corrections are not asks.

### Flow

```mermaid
flowchart TD
  A[FO has a question for the Captain] --> Q{Did he ask a question first}
  Q -->|yes| QA[FO answers it before dispatching, the ask stays]
  Q -->|no| K{Kind}
  K -->|stage gate, amendment, waiver, acceptance standard, consent, outward action| S1[Stays his: ADR 0011 never-list and README step 4]
  K -->|learning PR or Release PR merge| S2[Stays his: ADR 0009, one ask each, no stacking]
  K -->|refused push| S3[Stays his: permission settings, not a workflow rule]
  K -->|merge of a task PR or its worktree removal| D{Did the approved delivery question name it}
  D -->|yes| R1[FO runs delivery_gate.py check on the head]
  R1 -->|exit 0, next line says merge| R2[FO merges that head, then removes its clean pushed worktree]
  R1 -->|exit 1 or 2| R3[FO holds and shows what it printed, the ask goes to him]
  D -->|he said he merges himself| R4[He merges, FO asks nothing more]
  D -->|no| S4[FO asks him, stays his]
```

### Replay of every batch-2 answer after the rule

UTC, 2026-10-17 unless dated. "Stays" names the clause that keeps it his.

| # | Time | Answer | Kind | After the rule |
|---|---|---|---|---|
| 1 | 06:09 | 「准」 six backlog gates | gate | stays: gate approval, ADR 0011 |
| 2 | 07:30 | 「那就照建議」 six ideation gates, 17 decisions | gate | stays |
| 3 | 13:48 | #658 gate, merge, open POC task | gate, merge | stays; merge words now printed in the question |
| 4 | 13:57 | POC standard | needs | stays: his acceptance standard |
| 5 | 14:06 | #659 delivery gate | gate | stays |
| 6 | 14:09 | #659 「我合併了」 | merge | removed only if he does not opt out; he merged it himself, so counted as not removed |
| 7 | 14:31 | #661 gate, 「預先授權你合併」 | gate, merge | stays; words printed in the question |
| 8 | 14:34 | POC close | needs | stays: one occurrence, poc.md returns the outcome for the next planning decision |
| 9 | 14:38 | #662 learning PR merge | merge | stays: ADR 0009 |
| 10 | 14:43 | #664 AC-2 amendment | amendment | stays: README step 4 |
| 11 | 16:10 | #665 learning PR merge | merge | stays: ADR 0009 |
| 12 | 10-18 01:53 | throwaway repository | procedural | stays: outward action, one occurrence |
| 13 | 03:03 | #663 and #664 gates, merge | gate, merge | stays; words printed |
| 14 | 04:55 | repository deletion himself | procedural | stays: his token |
| 15 | 06:42 | #667 merge, waiver question | merge, needs | stays |
| 16 | 06:44 | gatekeeper compromise check | needs | stays: README step 4, risk acceptance |
| 17 | 08:30 | 「推」 refused push | procedural | stays: permission settings |
| 18 | 12:35 | #666 narrowing | amendment | stays: README step 4, authority |
| 19 | 16:06 | #666 gate, merge, special-agent question | gate, merge | stays |
| 20 | 16:09 | Release PR 0.25.0 | merge | stays: merge and publication |
| 21 | 16:21 | clean up 10 worker worktrees | procedural | **removed**: the five delivery questions would have named it |
| 22 | 16:24 | enable the laws check here | consent | stays: package consent rule |

Expected after, same batch: 21 answers (3.5 per task, from 3.7), or 20 (3.3) if he never opts out. It is arithmetic on batch 2, not a forecast of batch 3: batch 3 has four Pilot tasks and a POC, and one task drove 7 of 22 here.

### Mechanism: the sentence and the line the implementation lands

Two edits. (1) In `kc-dev-flow-2/references/sd/workflow.md` `## Delivery authority`: after "FO's delivery gate question says that approval also covers later external-review rounds on the same PR" add ", merging the head `delivery_gate.py check` passes unless he says he merges, and removing its clean, pushed worktree afterwards"; change "A rejected repair, a Needs decision, a scope change and the merge still go to him." to "A rejected repair, a Needs decision and a scope change go to him."; cut "Required CI is green only when its test jobs have finished on the PR head." Drafted and counted on a `/tmp` copy of `origin/main` c60e89e1: README 5429 to 5429, `## Delivery authority` 447 to 447. The cut sentence defines "green" for "request ready only after the required CI is green"; `pr_watch.py` `checks()` returns `green` only when no check is failing, pending, queued or in progress, and `tasks` prints "mark <PR> ready" only then, and at the merge ask `delivery_gate.py` prints `next: hold the ask until the required CI has finished green on this head.` The pinned sentence "Do not invoke local fallback, push the trunk, merge, or clean up an owned worktree unless the specific action is authorized" (pins `readme-keeps-delivery-rules` and `worker-opens-draft-pr`, and the implementation and validation principles) is untouched; the approved question is the authorization it names.

(2) In `kc-dev-flow-2/scripts/delivery_gate.py` the constant `ASK` ("next: ask for merge with this text.", 7 words) becomes "next: merge this head if the approved question named the merge and he did not say he merges, else ask for merge with this text." (25 words), with the docstring clause "one last `next:` line, which is always the ask line" reworded and the three literals of `test_delivery_gate.py` that spell the old line updated. Without it the script prints "ask" at the exact moment the README says FO acts, which is the prose-against-script split this workflow keeps paying for. The line is text only: the script reads no question and decides nothing, so the one-bit grant ("the approved question said so") stays with FO and the README, and none of the class-grant logic that merge-gatekeeper's narrowing removed returns. Its existing test that the output holds exactly one `next:` line, last, and never `--auto` or `--admin` still applies.

Existing-code check: `delivery_gate.py` stays the only merge gate and gains no merge command. A checker for "merged without the sentence in the question" is not proposed: it is `fo-write-checks` territory and would need a second feature to pay for itself.

### Words FO reads at each lifecycle moment

Counting rule `len(text.split())`, base `origin/main` c60e89e1 against the drafted candidate, README spans as FO reads them; the mod (48 words) and script outputs are unchanged.

| Moment | Base | Candidate | Note |
|---|---|---|---|
| Startup and resume (README read whole, plus the 48-word mod) | 5477 | 5477 | net 0 by the cut above |
| Dispatch build (Stages paragraph) | 368 | 368 | untouched |
| Ideation gate prepare (`ideation` section) | 329 | 329 | untouched |
| Merge ask (`## Delivery authority`) | 447 | 447 | +18 added, −15 CI sentence, −3 ("and the merge still") |
| Merge ask, last `next:` line of `delivery_gate.py` | 7 | 25 | +18 words at the moment the line is acted on |
| Idle on an open PR, idle on a merged PR, after the archive | unchanged | unchanged | `pr_watch.py`, `observer_check.py` unchanged |

learning.md's "each moment required to fall below its base" is the threshold for a change whose goal is cutting what FO reads (its Applicability clause); this goal is cutting Captain asks, so the README threshold here is "no moment above its base" (AC-2). The script line rises by 18 words at one moment; that is the price of the line and is stated, not offset.

### ADR draft (no number; FO reserves it at implementation)

Short title: `a-delivery-gate-question-may-carry-the-merge-of-the-validated-head`. Ruling: his approval of a delivery gate question that names the merge of the validated head and the removal of the task's clean, pushed worktree is his answer to those asks; ADR 0011's never-delegated list is unchanged because he is still asked. Its Words line quotes his answer at this gate.

### Batch overlap

Files this design would change: `kc-dev-flow-2/references/sd/workflow.md` (`## Delivery authority`, three small hunks); `kc-dev-flow-2/scripts/test_sd_dispatch.py` (one pin, `delivery-question-carries-merge`); `kc-dev-flow-2/scripts/delivery_gate.py` (the `ASK` constant and one docstring clause); `kc-dev-flow-2/scripts/test_delivery_gate.py` (three literals); `docs/adr/<reserved>.md`; the adopters' `docs/dev2/README.md` copies by refit. Not changed: `lint-skills.py` (the README count equals its budget before and after, so no step is added), the logic of `delivery_gate.py`, `pr_watch.py`, `observer_check.py`, `decision_ledger.py`, ADR 0011.

| Other batch-3 task | Same file or check | Effect on order |
|---|---|---|
| number-guards-readme-shrink (design written) | `workflow.md` Number guards section and one `lint-skills.py` budget step (cut of 55 words, README to 5374) | different hunk of `workflow.md`; I add no budget step, so either order works and my AC-2 numbers become 5374 and 447 if it lands first |
| chat-only-evidence-observer-blind (backlog text only) | `workflow.md` validation and Delivery authority, the sentence "present the exact candidate and PR body before authorized push/create"; observer checks | same paragraph as my hunk; whichever lands second rebases the paragraph; it owns any record or check that the merge grant leaves in state |
| fo-write-checks (backlog text only) | `delivery_gate.py`, `laws_check.py`, `dispatch_records.py`; `workflow.md` Reserve and observer lines; budget step list | `delivery_gate.py` is shared but my hunk is the `ASK` constant and one docstring clause, its checks are elsewhere in the file, so the later PR rebases; if it adds a check that the merged PR's approved question named the merge, it needs this sentence to land first |
| merge-grant-need-poc (named at the batch-3 approval; not in state on 2026-10-19) | the README sentence and `delivery_gate.py` merge ask | this fold is the "pre-authorized merge already covers it" usage that POC was to measure; land mine first so it measures the real wording |

Recommended order: number-guards-readme-shrink, then this task, then chat-only-evidence-observer-blind.

### Limits

- The 22-answer count comes from a machine-local transcript and my reading of the FO message before each answer; the ledger confirms only the 18 gate rows. The next batch's count uses the same script and the same reading.
- Counting answers is not counting effort: a one-word 「合併」 and a 「再簡報一次」 each count 1. Minutes per answer were not measured.
- One batch of six tasks; one task drove 7 of 22. No claim is made that batch 3 will show 21.
- The effect of an allow rule for worker pushes on the refused-push class is unmeasured.
- If FO forgets the sentence in a delivery question the rule fails safe: he is asked again, as today. A check that the merged PR's approved question named the merge would live in `fo-write-checks`, not here.

### Unresolved decisions for the Captain

- **D1: land the sentence (merge of the validated head and worktree removal named in the delivery question) at net zero README words, together with the new text of `delivery_gate.py`'s last `next:` line?** Recommend yes, both together; the sentence alone leaves the script telling FO to ask at the moment FO should merge. It removes one answer certainly and a second unless he merges himself, at the price of one small change and 18 more words in one script line. Worse under yes: a quick approval is no longer followed by a pause before FO merges; the head check, CI check and base check still run, but a Material change he would have caught at the second ask has one fewer chance. Worse under no: 22 stays 22 and the worktrees keep asking. If the implementation cannot reach net zero it does not land and returns to FO; no raise step is requested (ADR 0020).
- **D2: keep asking for each learning PR and the Release PR on its own (no stacking)?** Recommend yes. It follows his 「一題題來」 and ADR 0009 and leaves 4 answers a batch that a class grant could remove later; the route is the `merge-grant-need-poc` and ADR 0009's per-class unlock, not this task. Worse under yes: those 4 stay 4.

## Acceptance criteria

**AC-1** The batch-2 count reproduces: the ledger command prints 18 batch-2 gate rows, all approve and 0 `override`; the transcript script prints 33 Captain messages in the window; the classification table sums to 22 answers, 63 asks and the 7/6/5/4 split by kind.
Verified by: run both commands and recount the two tables. Falsifier: a different row or message count from the same commands, or a table that does not sum. Current evidence: run 2026-10-19; ledger 18 rows and 0 override, script 33 messages, tables sum to 22 and 63. Limit: the transcript is machine-local and the 22-way classification is a reading of FO's prior message.

**AC-2** After the change the README is not longer than 5429 words and `## Delivery authority` not longer than 447, `python3 <package>/scripts/lint-skills.py` passes with no raise step, and each pinned sentence of `readme-keeps-delivery-rules` and `worker-opens-draft-pr` still passes.
Verified by: `len(text.split())` on the candidate; `lint-skills.py`; `test_sd_dispatch.py`. Falsifier: add the 18 words and keep the CI sentence: the count is 5444 and `lint-skills.py` exits 1 naming the budget. Current evidence: drafted on a `/tmp` copy, 5429 to 5429 and 447 to 447; the lint and pins not yet run on it.

**AC-3** The merge stays conditional on the check and on the question: the README says FO merges only the head `delivery_gate.py check` passes, unless he says he merges, keeps "Preserve manual merge authority" and the pinned worktree sentence; the last `next:` line of `delivery_gate.py` on a passing run reads "next: merge this head if the approved question named the merge and he did not say he merges, else ask for merge with this text."; ADR 0011 is unchanged.
Verified by: a pin `delivery-question-carries-merge` in `FIXES` whose `need` strings are "merging the head `delivery_gate.py check` passes unless he says he merges" and "removing its clean, pushed worktree afterwards"; `python3 -B <package>/scripts/test_delivery_gate.py` with the three literals updated; `git diff <base> -- docs/adr/0011-*` empty. Falsifier: the swap deleting the first phrase turns the pin red; reverting `ASK` to the old line fails the updated literals; a diff on ADR 0011 fails the criterion. Current evidence: not yet verified.

**AC-4** The change adds no new script and no new check: the diff names only `workflow.md`, `test_sd_dispatch.py`, `delivery_gate.py`, `test_delivery_gate.py`, the reserved ADR and adopter README copies, and the `delivery_gate.py` hunk is the `ASK` assignment and one docstring clause.
Verified by: `git diff --name-only <base>..<head>` and `git diff -U0 <base>..<head> -- kc-dev-flow-2/scripts/delivery_gate.py`, whose changed lines are those two; the existing tests that the output holds exactly one `next:` line, last, and never `--auto` or `--admin` still pass. Falsifier: a changed line in `delivery_gate.py` other than those two, or a path under `kc-dev-flow-2/scripts/` other than the two test files and `delivery_gate.py`. Current evidence: not yet verified.

**AC-5** Batch 3 reports its Captain answers per task with the same script and the same classification as AC-1, and the rule is judged by the two removable kinds: no standalone merge ask for a delivery PR whose approved question carried the sentence, and no worktree-cleanup ask.
Verified by: FO runs the transcript script over the batch window at batch close and records answers and asks per task by kind in the batch note, beside the batch-2 figures (22 answers, 3.7 per task, 63 asks); each delivery gate question is read from `<task>/review/validation/briefing-N/index.json`. The per-task number is reported without a threshold (one task drove 7 of 22 in batch 2; batch 3 differs in size and profile). Falsifier: one answer of either removable kind, or a batch note without the per-task figures. Current evidence: not yet verified; batch 2 had 1 certain and 1 conditional.

## Captain amendments

### Amendment 1 — 2026-10-19, chat
Captain: 「授權修改 Delivery authority 合併措辭，照 D1 設計。但我要你明確跟我說，當我同意/核准驗證關卡時，等於授權你也合併 PR，除非我有顧慮暫時不合併。但這裡必須要硬前提，ＰＲ 必須是 ready 狀態，合理嗎？」 (chat, this FO session)
Asked: FO's chat question after the implementation worker's edit of the Delivery authority merge wording was refused by the permission check: 「你明確再授權一次（建議）：給我一句可以引用的話，例如「授權修改 Delivery authority 合併措辭，照 D1 設計」……放棄 D1：合併照舊每次單獨問你。」
Supersedes: none

## Number guards

ADR: 0023

## Stage Report: ideation

- DONE: A design (PRFAQ and Mermaid) for the measured count of every Captain decision per batch-2 task by kind (stage gates, Needs decisions, amendments, merge asks, procedural asks such as a refused push, a throwaway repository, a PR-body edit), from the decision ledger, gate briefings and task files of this workflow (2026-10-17 to 10-19); which kinds a written standing rule could settle without him and the rule text; which stay his under ADR 0011; the expected asks per task after the change
  `## Design`: 22 answers and 63 asks by kind and per task, 22-row replay, one README sentence (net 0 words), expected 21 answers (20 if he never opts out) from 22, via one README sentence (net 0 words) and the text of one `delivery_gate.py` line; chat-only kinds were read from the FO session transcript, outside the named sources, and are marked machine-local.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch-3 task (fo-write-checks, chat-only-evidence-observer-blind, captain-question-load, number-guards-readme-shrink) that changes the same file or check, so FO can order implementation
  `### Batch overlap` names `workflow.md`, `test_sd_dispatch.py`, `delivery_gate.py`, `test_delivery_gate.py`, the ADR and adopter copies; number-guards-readme-shrink read as written, the other two from Scope text only; merge-grant-need-poc is not in state.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  `### Words FO reads at each lifecycle moment`: startup 5477 to 5477, merge ask 447 to 447, the `delivery_gate.py` next line 7 to 25 words, others untouched; counted with `len(text.split())` on a `/tmp` copy of origin/main c60e89e1.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  Five `**AC-n**` declarations and D1, D2 under `### Unresolved decisions for the Captain`; `design_surfaces.py check` from the 0.25.0 package root printed `captain-question-load.md: design surfaces presentable`, exit 0.
- DONE: AC-1 the batch-2 count reproduces
  Run 2026-10-19: ledger 18 batch-2 gate rows, all approve, 0 override; transcript script 33 Captain messages; tables sum to 22 answers and 63 asks.
- SKIPPED: AC-2 README and Delivery authority not longer than 5429 and 447 words, lint and pins pass
  Not yet verified: drafted at 5429 and 447 on a `/tmp` copy; `lint-skills.py` and `test_sd_dispatch.py` not run on it, they belong to implementation.
- SKIPPED: AC-3 the merge stays conditional on the check and on the question
  Not yet verified: the pin `delivery-question-carries-merge`, the updated `ASK` literals and the ADR 0011 diff check are implementation work.
- SKIPPED: AC-4 no new script and no new check in the diff
  Not yet verified: `git diff --name-only` and the `delivery_gate.py` hunk exist only once there is a candidate.
- SKIPPED: AC-5 batch 3 per-task recount and no removable answer
  Not yet verified: needs the batch-3 transcript and its delivery questions.

### Summary

Measured 22 answers, 63 asks and 33 Captain messages in the window; 20 of the 22 stay his by ADR 0011, README step 4, ADR 0009, his own ruling or the permission check, or are too rare for a rule, so the design is one net-zero README sentence, the text of one `delivery_gate.py` line and one ADR, removing 1 answer and conditionally 1. Two things FO should know: the transcript is outside the named sources, and I ran one `git fetch` in the qnow clone (ref update only). D1 is the real decision: land a small change or close the task on the measurement.
