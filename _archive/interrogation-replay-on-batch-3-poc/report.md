# Interrogation replay on batch 3: captain-question-load

Verdict: the falsifier did not fire on this one task. Codex with the engineering-reviewer lens (arm 4) asked 4 of 7 key items in substance (57%) at 0 ungrounded questions; the two Claude arms asked 1 of 7 each. One task, one run per arm, one rater: this is a signal, not a measurement of variance.

## Method (as run)

- Snapshot: `git archive 18dbf490 | tar -x` into a temp directory outside every repository (`/tmp/replay-w0OHE1/snap`, 1377 files, no history). 18dbf490 is the base the archived task's implementation and validation reports name ("baselined on origin/main 18dbf490"); the task's seed was filed earlier the same day, so the snapshot is the implementation-start tree, not the ideation-start tree.
- Story: the seed of `captain-question-load` taken from its first committed version (state-branch commit 41654262: title, intro line, `## Scope` bullets) pasted verbatim into the prompt. The task had no journey.yaml, so the prompt says "Story map: none". Prompt = kc-journey-map `references/interrogation.md` (origin/main) with brackets filled. Arms 2 and 4 append the `## Assess` section of `kc-dev-flow-2:engineering-reviewer` (0.26.0) as a "Reviewer lens" block and say the output format is unchanged. Both prompts are in `raw/`.
- Arms (all four started in parallel, same minute):
  1. `claude -p --model sonnet` (effort not passed: default), plain prompt.
  2. `claude -p --model opus --effort high` (resolved to claude-opus-5-5), lens prompt.
  3. `codex exec -m gpt-6.1-sol -c model_reasoning_effort="high"`, plain prompt.
  4. Same Codex flags, lens prompt.
  Common to the Claude arms: `--tools Read,Grep,Glob --allowedTools Read,Grep,Glob --strict-mcp-config --disable-slash-commands --output-format stream-json --verbose`. The reference command lacks `--strict-mcp-config`; a probe with the reference flags showed the session still exposed ~200 MCP tools (Notion, Drive, Slack and others) to the model and a 197k-token context, so isolation by `--tools` alone is not real. With the flag the tool list was exactly Glob, Grep, Read. Codex: `--sandbox read-only --skip-git-repo-check --cd <snap> --json -o <file> -`. `run.sh` in `raw/` holds the exact commands.
- Codex pin: `-m` is listed in `codex exec --help`; there is no dedicated effort flag there, so effort goes through the documented `-c key=value` override. `~/.codex/models_cache.json` lists gpt-6.1-sol with `high` among its supported levels and ranks it first in the list; the user config default is gpt-6-astra. I did not verify that the effort setting was applied (the event stream does not echo it; `reasoning_output_tokens` was nonzero: 2216 and 3213). "gpt-6.1-sol is the strongest available" is not established, only that it is first in the cache list.
- Both CLIs also load the user's global instruction files (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`); the reference invocation does too. Not controlled.
- The answer key was built only after all four arms had finished and their answers were saved. Before that I read from the archived task only the base SHA lines (`grep base`, which also returned three short fragments of its stage reports) and the seed Scope.

## Isolation audit

| Arm | Calls | Result |
|---|---|---|
| 1 | 18 tool_use: Read, Grep, Glob only | every `file_path`/`path` inside the snapshot; no `..` in any input |
| 2 | 23 tool_use: Read, Grep, Glob only | same. The result also bills `claude-fable-5-1` (71,982 input, 6,618 output tokens) next to opus; the stream has 5 `advisor` mentions: Opus ran with an advisor sidecar, which reads no files but may have shaped questions |
| 3 | 27 `command_execution` (rg, cat, sed, ls) | absolute paths all under the snapshot; no `git`, `~`, `$HOME` or `..` |
| 4 | 23 `command_execution` | relative paths from cwd=snapshot, plus one `ls -a` of the snapshot; no `git`, `~`, `..` |

Self-reported "Reads" did not match the streams: arm 1 said 11 (18 calls), arm 2 said 17 (23), arm 3 said 17 (27), arm 4 said 27 (23). The time-box self-reports (8, 12, 10, 2 minutes) also disagree with wall time. Only the stream counts are used below.

## Answer key (built after the arms ran, from the archived task)

Assigned items: D1, D2, amendments 1 and 2, the Codex P1s, the roborev High that was a design gap. Seven key items:

| Key | Source in `_archive/captain-question-load.md` | The decision or gap |
|---|---|---|
| K1 | Unresolved decisions D1 | Should the validated-head delivery approval carry the merge (and worktree removal), landed as a README sentence at net zero words plus the new text of `delivery_gate.py`'s last `next:` line, with ADR 0011 unchanged |
| K2 | D2 | Keep asking for each learning PR and the Release PR on its own (no stacking, no class grant now; ADR 0009 per-class unlock later) |
| K3 | Captain amendment 1 | Captain's quoted authorization to edit the Delivery authority merge wording after the permission check refused the worker's edit; his terms: approval authorizes the merge unless he has a concern and pauses, hard precondition the PR is ready |
| K4 | Captain amendment 2 | Waive the Codex round-2 P2 and the roborev High into `fo-write-checks-followups` (enforcement of "the question named the merge" later, outside this task) |
| K5 | Cycle 1 Codex P1 (review:5569526052) | An approval that says wait or do not merge yet must hold the carried merge; "unless he says he merges" did not cover it |
| K6 | Cycle 2 Codex P1 (review:5569986438) | The carried merge is not bound to the checked head; a push after the last check could land an unvalidated head (`--match-head-commit`) |
| K7 | roborev:875/878/881 High | `delivery_gate.py` prints the merge line without reading the approved question or a hold (text-only, not enforced) |

Outside the assigned key, noted but not scored: Codex round-2 P2 (merge-time recheck writes a second `merge/ask-N.json`), and validation's F7 (the `ASK` line prints on every exit 0, even with `class: never`). 

Scoring rule: hit = answering the question forces the key decision or gap to be stated; partial = same artifact, neighbouring decision (counted only in the lenient column); miss = not asked. A question counts toward one key item. One rater (me), no second reader: the 11 partial calls are the soft spot.

## Scoring

| Key | Arm 1 sonnet | Arm 2 opus+lens | Arm 3 codex | Arm 4 codex+lens |
|---|---|---|---|---|
| K1 merge carried by delivery approval | hit Q1 | hit Q4 (also Q3) | hit Q1 | hit Q1 |
| K2 learning/Release PRs asked singly | partial Q24 | partial Q5 | miss | miss |
| K3 Captain's quoted authorization, hold/ready terms | partial Q23 | miss | miss | partial Q14 |
| K4 enforcement deferred, not in this task | partial Q20 | partial Q9 | partial Q22 | hit Q4 |
| K5 hold/"wait" opt-out | miss | miss | miss | miss |
| K6 merge bound to checked head | partial Q7 | miss | hit Q15 | hit Q13 |
| K7 merge line printed without reading the question | partial Q2 | partial Q3 | partial Q14 | hit Q15 |
| Strict hits (of 7) | 1 (14%) | 1 (14%) | 2 (29%) | 4 (57%) |
| Hits + partials | 6 | 4 | 4 | 5 |
| Questions asked | 25 | 23 | 22 | 20 |
| Ungrounded questions | 0 | 0 | 0 | 0 |
| Key hits per question asked (strict) | 0.04 | 0.04 | 0.09 | 0.20 |

Union across arms, strict: K1, K4, K6, K7 = 4 of 7 (57%); with partials 6 of 7. K5 was asked by no arm. Only arm 4 hit K4 and K7 strictly.

Quotes for every hit (question, then the key text it answers):

- K1. Arm 1 Q1: "Does the 'merge grant by default' the story floats conflict with ADR 0011 ... does the story need a Captain ruling that supersedes the ADR, or is 'pre-authorized' a different thing from 'delegated'?" Arm 2 Q4: "How does 'a delivery gate that carries the merge grant by default' fit with ADR 0011, and which ADR wins: 0011 or 0009?" Arm 3 Q1: "Must each delivery approval explicitly include the merge grant, or does this story seek to change the prohibition on standing delegation of merge authority?" Arm 4 Q1: "Does 'a delivery gate that carries the merge grant by default' require an explicit Captain grant in that gate's question, or a change to the existing prohibition on delegated merge decisions?" Key: D1, "land the sentence (merge of the validated head ... named in the delivery question) ... together with the new text of delivery_gate.py's last next: line".
- K4. Arm 4 Q4: "Must a missing Captain decision stop the action beforehand, or is detecting it afterward sufficient?" (grounded in VALIDATION.md: the observer and ledger "do not prevent a wrong record"). Key: amendment 2 puts the question-reading check in `fo-write-checks-followups`, an after-the-fact check, and accepts the text-only script meanwhile.
- K6. Arm 3 Q15: "What happens to an earlier merge grant when another worker changes the candidate after its delivery check?" Arm 4 Q13: "Which changes after a delivery approval invalidate its merge grant?" Key: round-2 P1, "a carried merge is not bound to the checked head; a push after the last check could land an unvalidated head".
- K7. Arm 4 Q15: "What durable evidence must a resumed FO have before continuing under an earlier combined delivery and merge grant?" (grounds: `delivery_gate.write_record()` saves PR, head, classification and verdict "but no Captain grant or approved question"). Key: roborev High, "delivery_gate.py prints the merge line without reading the question or a hold".

The partials, one line each: arm 1 Q24 asks about release-please branches and prod/db under a default merge grant (adjacent to D2's Release PR, does not ask whether to keep them single); arm 2 Q5 asks whether the rule is an L2 precedent or an L3 class grant (adjacent to D2's no-class-grant ruling); arm 1 Q23 and arm 4 Q14 touch a recorded Captain grant and a refused push, not the quoted authorization of the edit; arm 1 Q20, arm 2 Q9, arm 3 Q22 ask how losing a decision would be tested, not where enforcement lives; arm 1 Q7 asks what a repair after approval may add, not head binding; arm 1 Q2, arm 2 Q3, arm 3 Q14 ask about the saved `verdict` field or validation evidence, not about the question or a hold.

Ungrounded check, mechanical plus spot: I extracted every backticked symbol, path and quoted string from each question's Grounds line and searched the snapshot plus the story text. 0 of 90 questions had no resolvable ground. The unresolved fragments were regex artifacts (backticks inside quotes), paraphrases with ellipses (checked by hand against `delivery_gate.py`), paths the code writes at run time (`merge/ask-N.json`, `room/index.json`) and one case difference. Four factual claims spot-checked and true: "168 gate resolutions" (ADR 0011), `WORKFLOW_BUDGET_START = 5511`, "six batch-2 ideation gates" (ADR 0021), no reader of `verdict` outside `delivery_gate.py`. Not a full check of every claim. A question can be grounded and still match no key item: 16 of arm 4's 20 and 24 of arm 1's 25 questions were grounded and not strict hits.

Falsifier check:
- "fewer than 25% of the key items asked in substance by any arm": union 57%, best single arm 57%. Not fired (also not fired on strict counts alone).
- "best arm's hits come with more than three ungrounded questions per hit": 0 ungrounded for 4 hits. Not fired. Grounded non-hit questions per strict hit, the triage load a human carries: arm 4 is 4.0 (16 over 4), arm 3 is 9, arms 1 and 2 are 24 and 22.

## Cost and wall time

| Arm | Wall time | Tokens | Cost |
|---|---|---|---|
| 1 | 71 s | 16 in, 46,800 cache-write, 240,820 cache-read, 7,987 out (stream result) | `total_cost_usd` 0.291, measured as reported but imputed list price, not a bill |
| 2 | 208 s | opus: 26 in, 70,784 cache-write, 634,309 cache-read, 9,097 out; fable sidecar: 71,982 in, 6,618 out | 1.920 imputed (0.869 opus + 1.051 fable) |
| 3 | 166 s | 552,761 in (470,272 cached), 5,773 out (2,216 reasoning) | not measured: Codex reports tokens only |
| 4 | 213 s | 665,411 in (541,696 cached), 7,194 out (3,213 reasoning) | not measured |

Setup probes (before the arms): one default-flag Claude probe 1.577 imputed (197k-token context from MCP schemas), one trimmed probe 0.098, one Codex probe 29,828 in. Wall times are from `date +%s` around each run; the four ran concurrently, so they include contention that was not measured.

## Recommendation

- Use arm 4 (Codex, pinned model, high effort, engineering-reviewer lens) as the pre-build interrogator. It alone asked the question about where enforcement of the merge grant lives (K4) and about what evidence a grant leaves behind (K7), and it tied arm 3 on head binding (K6).
- Do not read the lens as proven. Lens versus no lens: Codex +2 strict hits (2 to 4), Claude 0 (1 to 1). Each pair is one run; model, lens and run-to-run noise are not separated.
- The Claude arms added nothing to the strict union beyond K1, which every arm asked because the story text names the merge grant and ADR 0011 forbids delegating it. Sonnet got that for 0.29 imputed and 71 s, so if a cheap second view is wanted, sonnet is the cost-sane one; opus plus its sidecar cost 6.6x that for the same one hit. Both Claude lists did ask grounded questions about what the ledger cannot count (procedural asks, plain approval versus missing Override) that no key item covers; whether that is value or noise is not decided by this key.
- K5 (a hold opt-out) was missed by all four; K2 and K3 only partially. Consistent with the earlier reference note (3 concurrency issues missed by both interrogators): interrogation of a story finds decision-shaped gaps, not the review-found wording gaps. Do not drop validation or review for it.
- Extend to the other batch-3 tasks: yes, but only on the Captain's word and as arm 4 plus arm 3 as the noise control, one run each. That repeats this test's weakest point (n=1 per arm) on a second task before any design is committed. This is a proposal for the Captain; I have not run any other batch-3 task.

## What this does not prove

- One task, one run per arm: no run-to-run variance. A single re-run of arm 3 could move it from 2 to 4.
- K1 is nearly in the story text; the harder items (K5 to K7) came from review rounds on the built mechanism. A different task may have a smaller share of text-derived key items.
- The key is mine, written once, after the answers; K3 and K4 are the least crisp. A different reader could promote or demote some of the 11 partials; I did not test inter-rater agreement.
- The snapshot is the implementation-start tree, and the seed's measurement inputs (batch-2 ledger rows, gate briefings) were not available to the arms, so a question the design answered by measurement shows as unanswerable here.
- Whether the effort setting reached Codex and whether Opus's advisor sidecar shaped its list is unverified.
- Nothing here measures what a Captain sitting saves: a question asked ahead of time is a question, not a saved answer.

## Cleanup

Nothing written to any repository, branch or PR. Temp directory `/tmp/replay-w0OHE1` (snapshot, event streams) is left in place for the validator; remove it with `rm -rf /tmp/replay-w0OHE1 /tmp/replay-dir.txt` after validation. Raw answers, both prompts and `run.sh` are copied to `raw/` beside this report.

## Raw question lists (Q lines verbatim; full items with Story, Grounds and Why in `raw/`)

### Arm 1 (Claude sonnet 5.5, default effort, plain prompt)

1. Does the "merge grant by default" the story floats conflict with ADR 0011, which says merge is never delegated at any level? If it does, does the story need a Captain ruling that supersedes the ADR, or is "pre-authorized" a different thing from "delegated"?
2. What exactly does `delivery_gate.py` do with `verdict = "merge"`, and who acts on it? Nothing in the snapshot reads it, and `emit` prints `ASK` in both cases.
3. Can `decision_ledger.py` measure the story's split at all? It reads only gate `resolution` and `withdrawal` entries and the `## Captain amendments` count. It has no row for a Needs decision, a merge ask, a procedural ask, or a plain approval.
4. How is "answered with a plain approval of FO's recommendation" detected? The ledger stores `decision`, `reason`, `conn_quote` and `question`, but nothing marks whether the quote was bare approval or an edit.
5. Where do procedural asks live as data? A refused push, a throwaway repository, a PR-body edit and a waiver are not gates, so they have no `gates:` entry.
6. Is the "PR approval guardrail" (present the PR body, wait for "push it") one of the FO questions to remove? Or is it an outward-facing action that must stay his under ADR 0011?
7. When a delivery-gate approval covers later review rounds, what is the limit if a repair adds a new `NEVER_PATH` file, a new `db` surface, or a prod profile? The README says the "no Material or Needs decision finding" repair is recorded by FO and pushed.
8. Does "a repair inside an approved design" need a machine-checkable test for "inside"? Today the closest tests are the README's four evidence fields and `Surfaces:`.
9. If L2 "decide by precedent" already exists, why do the questions still reach him? Was `Precedent:` used in batch 2, and how often? Is it blocked because most past rulings lack a `Words:` line?
10. Is the expected reduction measured per task, per batch, or per Captain turn, and against which baseline? The card says "fewer FO questions per delivered task", but the motivation is "most of his turns … were answering FO's questions rather than reviewing PRs".
11. What is the "reopen" path if the Captain wants to reverse a delegated decision after the PR is pushed or merged? The reopen clause is recorded only for L2 and not defined for a delivery or repair grant.
12. Does `amended_after` (amendments on or after a ruling date) predict a bad delegation, given it "can over-count"? What false-positive rate is acceptable before it blocks an L3 grant?
13. `area` comes from the task's `Surfaces:` line (ui/db/none), which is a technical surface, not a decision class like "amendment" or "waiver". Can area-based L3 grants even separate decision kinds?
14. Which "qnow R11 batching numbers" does the story rely on, and where are they? Nothing in this snapshot holds them or the `fo-batch-sittings-interim` note.
15. A "batch sitting" bundles asks. Are the asks in one sitting independent, or can one answer change another's options? ADR-style dependencies could make a bundle wrong after the first answer.
16. What happens to a Needs decision that is no longer asked? README: "Without that sentence a decision he did not address stays open: FO records its handling as FO's reading, never as his ruling". Can a standing rule turn FO's reading into his ruling by default?
17. Is a plain approval of a gate with a "approving accepts the recommendation" sentence recorded differently from a plain approval without it? If not, two kinds of approval look identical in `decision_ledger.py`.
18. What stops FO from writing "approving accepts the recommendation" into every gate question to cut asks? Is there a limit on L1 usage per gate, and who audits it?
19. Who verifies that the Captain still reads the gate summary after he stops answering? Delivery "verdict: merge" with `points` empty means nothing was flagged, but `points_for` is regex over prose.
20. What counts as "losing a decision that is his"? How would anyone detect one decision dropped, if the loss is silent by definition?
21. Should an auto-settled decision that turns out wrong be counted in the next ledger, and how? `Override:` lines are written only when FO records them, and none exists today.
22. The ledger covers one adopter's state branch (168 resolutions). Does batch 2 of this workflow have its own state branch and enough rows for the split, or is the evidence a few dozen rows?
23. Do standing rules need the Captain's quoted words to be valid, and where is the quote stored? ADR 0011 requires a "Captain grant recorded as its own ADR" for L3. A merge grant would need one too, but ADR numbers are reserved per task.
24. Are there security or cost effects when a merge or push happens without a live ask, for example a prod-profile task with a `db` surface or a `release-please--` branch? Both are in `points_for` today.
25. How is the result tested? `test_delivery_gate.py` and `test_decision_ledger.py` run in CI, but no end-to-end test shows a gate with fewer asks and the same decisions kept.

### Arm 2 (Claude opus 5.5, effort high, engineering-reviewer lens)

1. Where is the batch-2 record for the three kinds of decision the ledger cannot see (Needs decisions asked in chat, merge asks, procedural asks), and does "measure first" allow hand-counting from chat?
2. What counts as a "plain approval of FO's recommendation" in the count: a gate question carrying the L1 sentence, any resolution without an `Override:` line, or something else?
3. Is "pre-authorized merges at delivery gates" something that already exists, or is it what batch 3 builds?
4. How does "a delivery gate that carries the merge grant by default" fit with ADR 0011, and which ADR wins: 0011 or 0009?
5. Is a "written standing rule" an L2 precedent (an accepted ADR settles one decision) or an L3 class grant (a Captain grant recorded as its own ADR, on ledger evidence)?
6. What does "area" mean for this story, given that the ledger falls back to the `Surfaces:` value (`ui`/`db`/`none`) when no override exists?
7. Which procedural asks are even eligible, given that a refused push is enforced by the harness and a throwaway repository is an outward-facing creation?
8. Who decides that a repair is "inside an approved design", and which record proves it?
9. How is "without losing a decision that is his" tested: which record shows that no merge, authority, outward-facing, irreversible or money decision was settled without him?
10. How is a decision settled by a standing rule recorded, so the batch-3 measurement can tell it apart from an L1 approval and from a delivery-grant record?
11. Who notices a reversal, and from which record, so that "Any reversal returns the area to L0" actually happens?
12. Where does the new rule live (README, ADR or `_mods`), and does the Captain accept that landing it costs a quoted ruling for each word-budget raise?
13. Is the reduction expected in this repository, where `delivery_gate.py::NEVER_PATH` classes almost every change as `never`, or in adopters such as qnow?
14. What is in memory note `fo-batch-sittings-interim` and in the "qnow R11 batching numbers", and does the story depend on them or only cite them?
15. If the qnow FO still "owes" the R11 numbers, does batch 3 wait for them, or measure only this workflow?
16. In a batch sitting, can one approval cover gates from several tasks, and if so, how is each task's L1 sentence and each `Needs decision` kept separate?
17. Is the metric "decisions per delivered task", "Captain turns per delivered task", or "questions FO asked"? FO's batch-2 report was about turns.
18. What makes the batch-2 baseline frozen and reproducible: a state-branch commit, or a list of task files under `_archive/`?
19. Does the story include filling the `"model": "not run"` field in the merge record, meaning a model judges each ask, and what would that cost per PR?
20. If a standing rule lets FO decline or settle a decision, what stops a later validator or the merge ask from asking it again?
21. Can a rule settle `Follow-up:` lines and round-3 backlog filings without him, or do they stay Needs decisions?
22. What evidence turns a kind of ask into "settled by rule": a minimum count of batch-2 plain approvals, zero later amendments, or a Captain ruling per kind?
23. Does a standing rule apply to all adopters through `refit`, or only to this repository's workflow?

### Arm 3 (Codex gpt-6.1-sol, effort high, plain prompt)

1. Must each delivery approval explicitly include the merge grant, or does this story seek to change the prohibition on standing delegation of merge authority?
2. Does this story finish with measurements and proposed standing rules, or include activating those rules in running workflows?
3. Which supplied evidence set will establish that every batch-2 Captain decision is accounted for when the snapshot contains no corresponding task-state checkout or gate briefings?
4. Is success measured by fewer individual decisions, fewer Captain replies, or fewer interruptions across batch sittings?
5. Does the baseline include all decisions answered during the three-day window or all decisions over the lifetime of tasks delivered during that window?
6. What qualifies a task as delivered for this metric: recorded completion, a recorded merge, or independently confirmed delivery?
7. What source will supply procedural asks and merge asks that never became gate resolutions?
8. How should one approval covering a stage gate, a recommendation, and a merge grant be counted across the requested categories?
9. What evidence distinguishes plain agreement with a recommendation from an approval whose underlying recommendation is missing or unstated?
10. Should a missing briefing question make agreement unclassifiable rather than count as an ordinary approval?
11. How will an amendment be linked to the particular decision it reverses rather than every earlier decision on the task?
12. Which fixed task-state revision and briefing versions define a reproducible baseline while tasks are being amended or archived?
13. Should decisions already settled by existing rules be reported as failures to follow those rules, separately from decisions needing new standing rules?
14. If a standing merge grant makes the saved delivery verdict actionable, what evidence must establish that validation actually passed?
15. What happens to an earlier merge grant when another worker changes the candidate after its delivery check?
16. How does a Captain correction or withdrawal of a standing rule affect workers already running under its previous version?
17. When a check holds because records or provider data cannot be read, which cases still require a Captain decision rather than operational recovery under existing authority?
18. How will refused permission checks be distinguished between guard false positives and genuine requests for new authority before either is classified as removable overhead?
19. Do accepted standing rules apply only to this workflow, or also to its proof-of-concept route and other adopting repositories?
20. Are the batching note and the other project’s owed measurements prerequisites for choosing rules, or supporting evidence that may remain unavailable?
21. What added model cost, review work, and workflow-document growth are acceptable in exchange for fewer Captain questions?
22. What independently judged cases and field results must pass before claiming that questions decreased without losing a Captain-owned decision?

### Arm 4 (Codex gpt-6.1-sol, effort high, engineering-reviewer lens)

1. Does “a delivery gate that carries the merge grant by default” require an explicit Captain grant in that gate’s question, or a change to the existing prohibition on delegated merge decisions?
2. What reduction in Captain questions per delivered task counts as success?
3. Does this story finish with measurements and approved standing rules, or include changing workflow behavior to apply those rules?
4. Must a missing Captain decision stop the action beforehand, or is detecting it afterward sufficient?
5. Which immutable evidence export supplies the batch-2 task records, briefing questions, and Captain replies for the measurement?
6. When one Captain reply approves six task gates together, does the primary measure count one interruption or six answered questions?
7. Which tasks belong in the denominator when their questions occur during October 17–19 but their delivery occurs outside that window?
8. How should one approval that settles a stage gate, several Needs decisions, and a merge request contribute to the requested category counts?
9. How must procedural asks and standalone amendments be counted when they have no gate resolution row?
10. When the briefing question or recommendation is missing, must apparent plain approvals remain unclassified rather than count as agreement with FO?
11. Must later amendments be linked to the particular decision they reverse before that decision can support a standing rule?
12. Does acceptance include eliminating asks that existing rules already authorize, separately from introducing new standing rules?
13. Which changes after a delivery approval invalidate its merge grant?
14. What must FO do when a permission check rejects a push already covered by the Captain’s recorded grant?
15. What durable evidence must a resumed FO have before continuing under an earlier combined delivery and merge grant?
16. Must repeated measurements use one fixed state revision when tasks can move between active and archived locations during collection?
17. Can this story proceed without the batch-sittings note and the batching figures owed by the qnow First Officer?
18. Are the resulting standing rules authorized only for this workflow, or intended for other adopting projects too?
19. What ceiling applies to additional model runs, workflow reading, and review work introduced to reduce Captain questions?
20. What behavioral evidence must show that a redundant question disappears while a decision outside FO’s authority still reaches the Captain?
