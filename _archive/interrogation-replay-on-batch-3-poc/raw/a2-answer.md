1. Q: Where is the batch-2 record for the three kinds of decision the ledger cannot see (Needs decisions asked in chat, merge asks, procedural asks), and does "measure first" allow hand-counting from chat?
Story: captain-question-load
Grounds: `decision_ledger.py` (`gate_entries`, `task_rows`) only reads the SD `gates:` block, `Override:` lines and `### Amendment` headings. Merge asks live elsewhere, in `<task>/merge/ask-N.json` written by `delivery_gate.py::write_record`. A refused push, a throwaway repository, a PR-body edit and a waiver leave no record that any script reads.
Why it matters: Only two of the five kinds the story names can be counted from a record. Without an answer, the baseline is partly a guess, and the "fewer" target cannot be checked.

2. Q: What counts as a "plain approval of FO's recommendation" in the count: a gate question carrying the L1 sentence, any resolution without an `Override:` line, or something else?
Story: captain-question-load
Grounds: README: "His plain approval accepts that recommendation only when the gate question says so". ADR 0011 Context: "No gate record carries an `Override:` line". `task_rows` takes `question` from `room/index.json` and returns `None` when that file is missing.
Why it matters: No `Override:` line exists anywhere, so "no override" would count every ruling as a plain approval. That would make most asks look delegable.

3. Q: Is "pre-authorized merges at delivery gates" something that already exists, or is it what batch 3 builds?
Story: captain-question-load
Grounds: The story lists it under "Existing pieces". README `## Delivery authority` says the opposite: "A rejected repair, a Needs decision, a scope change and the merge still go to him." `delivery_gate.py` computes `verdict = "merge" if not points and cls != "never" else "ask"`, but always prints `ASK` ("always the ask line"), and nothing reads `verdict`.
Why it matters: If it does not exist, the story's main example is a new grant of merge authority, not a reuse.

4. Q: How does "a delivery gate that carries the merge grant by default" fit with ADR 0011, and which ADR wins: 0011 or 0009?
Story: captain-question-load
Grounds: ADR 0011: "Authority, gate approval, merge … are never delegated at any level". README: "a merge … always asked, whatever an ADR says". ADR 0009 allows full-auto merge, but only for unlocked change classes and only after "N set when the mechanism is built".
Why it matters: The example in the scope may be forbidden by the ADR the same story says must hold. Only the Captain can settle that conflict.

5. Q: Is a "written standing rule" an L2 precedent (an accepted ADR settles one decision) or an L3 class grant (a Captain grant recorded as its own ADR, on ledger evidence)?
Story: captain-question-load
Grounds: ADR 0011: L2 applies "a decision an accepted ADR already settles"; L3 is "not built" and needs ledger evidence "that his rulings in that area agreed with FO and were not later amended".
Why it matters: Settling whole kinds of asks is L3, and its evidence bar cannot be met yet. If the story means L2, it settles much less.

6. Q: What does "area" mean for this story, given that the ledger falls back to the `Surfaces:` value (`ui`/`db`/`none`) when no override exists?
Story: captain-question-load
Grounds: `task_rows`: `"area": over.group("area") … else (surfaces.group(1) …)`. The story's own split is stage gates, Needs decisions, amendments, merge asks and procedural asks.
Why it matters: L3 grants and the ADR 0011 reopen condition are per area. With the wrong grouping, a reversal in one kind of decision hides inside another.

7. Q: Which procedural asks are even eligible, given that a refused push is enforced by the harness and a throwaway repository is an outward-facing creation?
Story: captain-question-load
Grounds: The story's list: "a push the permission check refused, a throwaway repository, a PR-body edit, a waiver". ADR 0011 never delegates "outward-facing actions". README step 5: a P1 is "waived by the Captain with the reason recorded".
Why it matters: If most procedural asks fall in kinds that must stay his, a workflow rule cannot be the fix. The fix would sit in permission config outside this package.

8. Q: Who decides that a repair is "inside an approved design", and which record proves it?
Story: captain-question-load
Grounds: The story's example "a repair inside an approved design". README: "A repair that outgrows what its assignment names returns to FO as a scope change". README step 4: scope, threshold and acceptance-criteria changes "require the Captain".
Why it matters: This line separates a saved question from a lost decision. Today no check draws it.

9. Q: How is "without losing a decision that is his" tested: which record shows that no merge, authority, outward-facing, irreversible or money decision was settled without him?
Story: captain-question-load
Grounds: Card: "without losing a decision that is his". ADR 0011: "A delegated decision is recorded as FO's decision with its basis, never as the Captain's words." No script checks that a protected kind was never recorded with `by: agent:first-officer`.
Why it matters: The story's guardrail has no test. A rule that removes questions could pass review while silently taking his decisions.

10. Q: How is a decision settled by a standing rule recorded, so the batch-3 measurement can tell it apart from an L1 approval and from a delivery-grant record?
Story: captain-question-load
Grounds: README offers two forms: `Precedent: ADR <number> — 「<Words line>」` and `gate record --actor agent:first-officer --conn-quote … --conn-source`. `summary` only splits on `by` (`captain` vs `fo_delegated`).
Why it matters: If the forms are not distinct, the "after" number cannot show which rule saved which question, and nobody can audit a reversal.

11. Q: Who notices a reversal, and from which record, so that "Any reversal returns the area to L0" actually happens?
Story: captain-question-load
Grounds: ADR 0011: "Any reversal returns the area to L0" and "`amended_after` … approximates a later reversal and can over-count". `amended_after` counts every amendment dated on or after a ruling.
Why it matters: Without a reliable reversal signal, a delegation that once goes wrong stays on.

12. Q: Where does the new rule live (README, ADR or `_mods`), and does the Captain accept that landing it costs a quoted ruling for each word-budget raise?
Story: captain-question-load
Grounds: ADR 0020: a positive `delta` in `WORKFLOW_BUDGET_STEPS` "needs a `captain` value holding a 「…」 quote". `lint-skills.py` has `WORKFLOW_BUDGET_START = 5511`, and the README stood at 5495 words on 2026-10-17.
Why it matters: A rule meant to cut his questions adds at least one approval of its own, and may force cuts elsewhere in the README.

13. Q: Is the reduction expected in this repository, where `delivery_gate.py::NEVER_PATH` classes almost every change as `never`, or in adopters such as qnow?
Story: captain-question-load
Grounds: `NEVER_PATH` matches `docs/adr`, `docs/dev*`, `_mods`, `skills|agents|extensions|references`, `kc-dev-flow-2/scripts/` and any `*gate*`/`*budget*` file. `classify` returns `never` for prod, `db` and release-please PRs.
Why it matters: In this repository a merge-by-default rule could almost never apply, so the measured gain here would be close to zero.

14. Q: What is in memory note `fo-batch-sittings-interim` and in the "qnow R11 batching numbers", and does the story depend on them or only cite them?
Story: captain-question-load
Grounds: The story lists both under "Existing pieces". A search of the snapshot for `batch sitting`, `fo-batch-sittings`, `qnow` and `R11` found no source (only one unrelated qnow mention in `learning.md`).
Why it matters: If design depends on inputs nobody can read, ideation will rebuild them or guess.

15. Q: If the qnow FO still "owes" the R11 numbers, does batch 3 wait for them, or measure only this workflow?
Story: captain-question-load
Grounds: The story: "the qnow R11 batching numbers the qnow FO owes".
Why it matters: It decides the stop condition and whether this task is blocked by another repository's FO.

16. Q: In a batch sitting, can one approval cover gates from several tasks, and if so, how is each task's L1 sentence and each `Needs decision` kept separate?
Story: captain-question-load
Grounds: README: "Without that sentence a decision he did not address stays open". README: FO never records "consent he gave earlier to a different question" as his ruling.
Why it matters: Batching cuts turns but can merge separate decisions into one reply. That breaks the ruling rule and inflates the "fewer questions" number.

17. Q: Is the metric "decisions per delivered task", "Captain turns per delivered task", or "questions FO asked"? FO's batch-2 report was about turns.
Story: captain-question-load
Grounds: Card: "answers fewer FO questions per delivered task". Filing context: "most of his turns in batch 2 were answering FO's questions rather than reviewing PRs". Goal: 「這樣我才可以從一直在追每個 FO 過程中解放出來」.
Why it matters: Batching lowers turns without lowering decisions, and delegation does the reverse. The chosen metric decides which one gets built.

18. Q: What makes the batch-2 baseline frozen and reproducible: a state-branch commit, or a list of task files under `_archive/`?
Story: captain-question-load
Grounds: `ledger` reads `state.glob("*.md")` plus `_archive/*.md` at whatever revision is checked out, and `question()` reads `room/index.json`, which may have changed since. The story's window: "2026-10-17 to 10-19".
Why it matters: If the ledger or the state moves before the "after" measurement, before and after are not comparable.

19. Q: Does the story include filling the `"model": "not run"` field in the merge record, meaning a model judges each ask, and what would that cost per PR?
Story: captain-question-load
Grounds: `delivery_gate.py::check` writes `"model": "not run"` in every `merge/ask-N.json`.
Why it matters: A model call on each merge ask adds tokens to every delivery, and the story names no budget for it.

20. Q: If a standing rule lets FO decline or settle a decision, what stops a later validator or the merge ask from asking it again?
Story: captain-question-load
Grounds: README: "A finding FO declined in a committed gate summary … is settled". `delivery_gate.py::points_for` raises a `point:` for every `Deferred risk`, `declined`, `not run` and amendment line, so these come back at the merge ask.
Why it matters: A question settled earlier but shown again at merge still costs him a turn, so the saving may vanish at the last gate.

21. Q: Can a rule settle `Follow-up:` lines and round-3 backlog filings without him, or do they stay Needs decisions?
Story: captain-question-load
Grounds: README: a `Follow-up:` line that changes behaviour an accepted criterion relies on is returned "to FO as a Needs decision". Step 5: from round 3, FO declines a finding and files it with `spacedock new`.
Why it matters: These are routine sources of asks that may already be delegable by text. Leaving them out understates the gain.

22. Q: What evidence turns a kind of ask into "settled by rule": a minimum count of batch-2 plain approvals, zero later amendments, or a Captain ruling per kind?
Story: captain-question-load
Grounds: ADR 0009: a class unlocks "with N set when the mechanism is built". ADR 0011: L3 needs ledger evidence "that his rulings in that area agreed with FO".
Why it matters: Three days of batch-2 data may be too few to support any grant. The answer decides whether this story builds rules or only a measurement.

23. Q: Does a standing rule apply to all adopters through `refit`, or only to this repository's workflow?
Story: captain-question-load
Grounds: README header `<!-- kc-dev-flow-2 0.25.0 x-release-please-version -->`. `_mods/kc-dev-flow-2.md` is "copied from `<package>/references/sd/mods/`". Global rule: the policy layer is per-repo and is not synced.
Why it matters: A delegation of the Captain's authority synced to every adopter is a much larger grant than one for this workflow.

Reads: 17, minutes: 12