1. Q: Does the "merge grant by default" the story floats conflict with ADR 0011, which says merge is never delegated at any level? If it does, does the story need a Captain ruling that supersedes the ADR, or is "pre-authorized" a different thing from "delegated"?
Story: captain-question-load
Grounds: "Authority, gate approval, merge, outward-facing actions, irreversible changes and money are never delegated at any level" (ADR 0011). The Delivery authority section of `docs/dev2/README.md` says "Preserve manual merge authority" and "the merge still go[es] to him". The story scope says "a delivery gate that carries the merge grant by default".
Why it matters: The biggest saving may need a new ADR, a new grant form, or a different story. Building it as a gate-wording tweak would break a written invariant.

2. Q: What exactly does `delivery_gate.py` do with `verdict = "merge"`, and who acts on it? Nothing in the snapshot reads it, and `emit` prints `ASK` in both cases.
Story: captain-question-load
Grounds: `verdict = "merge" if not points and cls != "never" else "ask"` in `delivery_gate.check`. It is saved to `merge/ask-<N>.json` with `"next": ASK`. The `check` docstring says "one last `next:` line, which is always the ask line".
Why it matters: The mechanism for skipping a merge ask may half-exist as a dead field. The story must say whether it builds on that field, replaces it, or removes it.

3. Q: Can `decision_ledger.py` measure the story's split at all? It reads only gate `resolution` and `withdrawal` entries and the `## Captain amendments` count. It has no row for a Needs decision, a merge ask, a procedural ask, or a plain approval.
Story: captain-question-load
Grounds: `gate_entries` yields only `("resolution", "withdrawal")`. `task_rows` carries `amended_after`, a count, not a decision row. The story says "split into stage gates, Needs decisions, amendments, merge asks, and procedural asks".
Why it matters: If the ledger can't produce the baseline, "measure first" means new tooling or hand-counting from chat. The story should say which, and who owns the count.

4. Q: How is "answered with a plain approval of FO's recommendation" detected? The ledger stores `decision`, `reason`, `conn_quote` and `question`, but nothing marks whether the quote was bare approval or an edit.
Story: captain-question-load
Grounds: the `conn_quote` / `conn_source` / `question` fields in `task_rows`. ADR 0011: "No gate record carries an `Override:` line". `OVERRIDE` needs the `Override: recommended X; Captain chose Y; area: Z` form.
Why it matters: With zero Overrides on record, "approved FO's recommendation" and "FO never recorded the disagreement" look the same. The agreement rate that justifies any standing rule could be unmeasurable.

5. Q: Where do procedural asks live as data? A refused push, a throwaway repository, a PR-body edit and a waiver are not gates, so they have no `gates:` entry.
Story: captain-question-load
Grounds: story scope "procedural asks (a push the permission check refused, a throwaway repository, a PR-body edit, a waiver)". The `pr-merge.md` mod's "PR APPROVAL GUARDRAIL — Do NOT push or create a PR without explicit captain approval". The ledger reads only `gates:` frontmatter.
Why it matters: These may be the largest uncounted share of the load, and no stored record would let the story prove it.

6. Q: Is the "PR approval guardrail" (present the PR body, wait for "push it") one of the FO questions to remove? Or is it an outward-facing action that must stay his under ADR 0011?
Story: captain-question-load
Grounds: `docs/dev/_mods/pr-merge.md`: "Wait for the captain's explicit approval before pushing. Do NOT infer approval from … the gate approval that preceded this step". The README says "the implementation worker opens the task's Draft PR before validation; that grant stands in for a presented body".
Why it matters: Two grants already cover part of this, and the rest is ambiguous. Without a ruling, the story may add a third overlapping grant.

7. Q: When a delivery-gate approval covers later review rounds, what is the limit if a repair adds a new `NEVER_PATH` file, a new `db` surface, or a prod profile? The README says the "no Material or Needs decision finding" repair is recorded by FO and pushed.
Story: captain-question-load
Grounds: README Delivery authority ("a repair whose validation passes with no Material or Needs decision finding is recorded by FO under that grant"). `NEVER_PATH` and the `points_for` kinds `path`, `profile` and `surface`.
Why it matters: The "repair inside an approved design" rule needs a boundary stated in the same terms as `points_for`, or FO's repairs can drift past what he approved.

8. Q: Does "a repair inside an approved design" need a machine-checkable test for "inside"? Today the closest tests are the README's four evidence fields and `Surfaces:`.
Story: captain-question-load
Grounds: README `## FO steps: review findings` step 4 ("Scope, value, threshold, tolerance, risk-acceptance and acceptance-criteria changes require the Captain"). Story: "a repair inside an approved design".
Why it matters: Without a check, "inside the design" is FO's own reading. ADR 0005 shows that when FO's reading went unchecked, criteria were silently rewritten.

9. Q: If L2 "decide by precedent" already exists, why do the questions still reach him? Was `Precedent:` used in batch 2, and how often? Is it blocked because most past rulings lack a `Words:` line?
Story: captain-question-load
Grounds: README: "A decision an accepted ADR already settles is not asked again … `Precedent: ADR <number> — 「<Words line>」`". ADR 0011: 9 of 168 resolutions were FO-recorded. ADR 0011 says "the Captain may reopen it".
Why it matters: The cheapest reduction may be to use an existing rule more. Writing a new rule would then duplicate it.

10. Q: Is the expected reduction measured per task, per batch, or per Captain turn, and against which baseline? The card says "fewer FO questions per delivered task", but the motivation is "most of his turns … were answering FO's questions rather than reviewing PRs".
Story: captain-question-load
Grounds: the card title and the 2026-10-16 quote 「從一直在追每個 FO 過程中解放出來」.
Why it matters: Batching questions into one sitting cuts turns but not questions. A rule cuts questions but not turns. The goal picks which mechanism to build.

11. Q: What is the "reopen" path if the Captain wants to reverse a delegated decision after the PR is pushed or merged? The reopen clause is recorded only for L2 and not defined for a delivery or repair grant.
Story: captain-question-load
Grounds: ADR 0011: "Any reversal returns the area to L0" and "Reopen if an L2 precedent is reopened by the Captain twice in one area". `decision_ledger.amended_after` "approximates a later reversal and can over-count".
Why it matters: A grant that can't be undone cheaply is an irreversible-change ask by ADR 0011's own rule.

12. Q: Does `amended_after` (amendments on or after a ruling date) predict a bad delegation, given it "can over-count"? What false-positive rate is acceptable before it blocks an L3 grant?
Story: captain-question-load
Grounds: ADR 0011 Consequences; `AMENDMENT` regex and `d >= date` in `task_rows`.
Why it matters: The story's "which kinds a written standing rule could settle" depends on a noisy signal. An unstated threshold means an arbitrary grant.

13. Q: `area` comes from the task's `Surfaces:` line (ui/db/none), which is a technical surface, not a decision class like "amendment" or "waiver". Can area-based L3 grants even separate decision kinds?
Story: captain-question-load
Grounds: `"area": … surfaces.group(1)` in `task_rows`. ADR 0011 reopen condition: "if the ledger cannot separate areas well enough to support an L3 grant".
Why it matters: The reopen condition for the delegation ladder may already be met by this story's own taxonomy.

14. Q: Which "qnow R11 batching numbers" does the story rely on, and where are they? Nothing in this snapshot holds them or the `fo-batch-sittings-interim` note.
Story: captain-question-load
Grounds: story "Existing pieces: batch sittings (memory note fo-batch-sittings-interim) … the qnow R11 batching numbers the qnow FO owes". A grep of the snapshot finds no `fo-batch-sittings` or `R11`.
Why it matters: The story depends on inputs that are not reproducible from the repo and are owed by another FO. The story needs a stated fallback if they never arrive.

15. Q: A "batch sitting" bundles asks. Are the asks in one sitting independent, or can one answer change another's options? ADR-style dependencies could make a bundle wrong after the first answer.
Story: captain-question-load
Grounds: README Release review signal 4 ("a batch about to enter implementation … single checkpoint"). The story's "batch sittings".
Why it matters: If bundled answers cascade, the sitting needs ordering or re-asking rules, which defeats the fewer-questions goal.

16. Q: What happens to a Needs decision that is no longer asked? README: "Without that sentence a decision he did not address stays open: FO records its handling as FO's reading, never as his ruling". Can a standing rule turn FO's reading into his ruling by default?
Story: captain-question-load
Grounds: README `## FO steps: review findings` ("His plain approval accepts that recommendation only when the gate question says so"). ADR 0011: "A delegated decision is recorded as FO's decision with its basis, never as the Captain's words".
Why it matters: Rules written for one task then count as his words in the ledger, and the ledger evidence for L3 grants becomes circular.

17. Q: Is a plain approval of a gate with a "approving accepts the recommendation" sentence recorded differently from a plain approval without it? If not, two kinds of approval look identical in `decision_ledger.py`.
Story: captain-question-load
Grounds: README sentence "approving accepts the recommendation for D2; say if you object". The ledger's `by`, `decision` and `conn_quote` fields only.
Why it matters: The measure of "plain approvals of FO's recommendation" could count approvals that never covered the recommendation.

18. Q: What stops FO from writing "approving accepts the recommendation" into every gate question to cut asks? Is there a limit on L1 usage per gate, and who audits it?
Story: captain-question-load
Grounds: README L1 sentence; `delivery_gate.py` checks second reviewers, declines, head and CI but not the gate-question wording.
Why it matters: The incentive to look good on this metric sits with FO. Without an audit, a lower question count can mean less oversight rather than fewer needless questions.

19. Q: Who verifies that the Captain still reads the gate summary after he stops answering? Delivery "verdict: merge" with `points` empty means nothing was flagged, but `points_for` is regex over prose.
Story: captain-question-load
Grounds: `DEFERRED`, `NOT_RUN` and `AC_NOT_RUN` regexes in `delivery_gate.py`; the docstring "this proves a bracket exists, not that it is a reason".
Why it matters: A merge grant that depends on prose regexes can pass a PR whose problems were worded differently. That is a missed "decision that is his".

20. Q: What counts as "losing a decision that is his"? How would anyone detect one decision dropped, if the loss is silent by definition?
Story: captain-question-load
Grounds: card "without losing a decision that is his"; ADR 0011 list (authority, approval, merge, outward-facing actions, irreversible changes, money).
Why it matters: The story has no acceptance test for the second half of its title. It needs a sample of auto-settled decisions that he reviews after the fact.

21. Q: Should an auto-settled decision that turns out wrong be counted in the next ledger, and how? `Override:` lines are written only when FO records them, and none exists today.
Story: captain-question-load
Grounds: ADR 0011 ("No gate record carries an `Override:` line"); `OVERRIDE` regex in `decision_ledger.py`.
Why it matters: The feedback loop that keeps a standing rule honest has no producer yet. The story may need to add one.

22. Q: The ledger covers one adopter's state branch (168 resolutions). Does batch 2 of this workflow have its own state branch and enough rows for the split, or is the evidence a few dozen rows?
Story: captain-question-load
Grounds: ADR 0011 "over one adopter's state branch"; story "batch-2 decision ledger rows and the gate briefings … (2026-10-17 to 10-19)", a three-day window.
Why it matters: Percentages from three days of rows may be too small to justify a standing rule. The story should state a minimum sample.

23. Q: Do standing rules need the Captain's quoted words to be valid, and where is the quote stored? ADR 0011 requires a "Captain grant recorded as its own ADR" for L3. A merge grant would need one too, but ADR numbers are reserved per task.
Story: captain-question-load
Grounds: ADR 0011 L3 definition; ADR 0025 "a reserved ADR lands or is released"; delivery_gate "reserved ADR … has no … file at PR head".
Why it matters: Each new grant costs an ADR and a Captain ruling, and these are themselves asks. Count them against the questions saved.

24. Q: Are there security or cost effects when a merge or push happens without a live ask, for example a prod-profile task with a `db` surface or a `release-please--` branch? Both are in `points_for` today.
Story: captain-question-load
Grounds: `release_pr`, `profile_prod` and the `Surfaces:.*\bdb\b` check feeding `classify`; `("profile","prod")` and `("surface","db")` points.
Why it matters: ADR 0011 puts irreversible change and money with him. A default merge grant needs a stated exclusion list that matches these checks, or it can bypass a prod security review.

25. Q: How is the result tested? `test_delivery_gate.py` and `test_decision_ledger.py` run in CI, but no end-to-end test shows a gate with fewer asks and the same decisions kept.
Story: captain-question-load
Grounds: `.github/workflows/kc-dev-flow-2-tests.yml` runs `test_decision_ledger.py`. The `journey-dev2-loop-smoke.yml` paths include `decision_ledger.py`. Unit tests prove isolated logic, not the wiring FO follows.
Why it matters: The story changes FO behaviour, which is prose. A before/after replay of batch-2 gates is the only evidence that the rule works on real tasks.

Reads: 11, minutes: 8