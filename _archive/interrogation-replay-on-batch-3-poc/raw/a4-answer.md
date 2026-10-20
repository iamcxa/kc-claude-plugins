1. **Q:** Does “a delivery gate that carries the merge grant by default” require an explicit Captain grant in that gate’s question, or a change to the existing prohibition on delegated merge decisions?  
   **Story:** captain-question-load  
   **Grounds:** Story example above; “Authority, gate approval, merge … are never delegated” in `docs/adr/0011-fo-decides-for-the-captain-by-a-delegation-ladder.md`.  
   **Why it matters:** These imply different authority boundaries and different permissible implementations.

2. **Q:** What reduction in Captain questions per delivered task counts as success?  
   **Story:** captain-question-load  
   **Grounds:** “The Captain answers fewer FO questions per delivered task” in the story.  
   **Why it matters:** Without a target, almost any reduction could satisfy the card.

3. **Q:** Does this story finish with measurements and approved standing rules, or include changing workflow behavior to apply those rules?  
   **Story:** captain-question-load  
   **Grounds:** “Measure first” and “Then find which kinds a written standing rule could settle”; “Non-goals: to be set at ideation.”  
   **Why it matters:** The story does not yet distinguish an investigation deliverable from an operational change.

4. **Q:** Must a missing Captain decision stop the action beforehand, or is detecting it afterward sufficient?  
   **Story:** captain-question-load  
   **Grounds:** “Without losing a decision that is his”; `kc-dev-flow-2/VALIDATION.md` says the observer and ledger “measure FO’s gate records after the fact” and “do not prevent a wrong record.”  
   **Why it matters:** An after-the-fact audit cannot establish a preventive guarantee.

5. **Q:** Which immutable evidence export supplies the batch-2 task records, briefing questions, and Captain replies for the measurement?  
   **Story:** captain-question-load  
   **Grounds:** The story specifies ledger rows and gate briefings, while `docs/dev2/README.md` places mutable task state in an ignored `.spacedock-state` checkout that is absent from this snapshot.  
   **Why it matters:** The baseline cannot be reproduced from the supplied code and decision documents alone.

6. **Q:** When one Captain reply approves six task gates together, does the primary measure count one interruption or six answered questions?  
   **Story:** captain-question-load  
   **Grounds:** `docs/adr/0021-prod-validation-security-review-reaches-past-the-diff.md` records one 「那就照建議」 approving six batch-2 ideation gates.  
   **Why it matters:** Gate counts can remain unchanged while batching substantially reduces the Captain’s interruptions.

7. **Q:** Which tasks belong in the denominator when their questions occur during October 17–19 but their delivery occurs outside that window?  
   **Story:** captain-question-load  
   **Grounds:** The story combines “per delivered task” with a dated measurement window; `decision_ledger.task_rows()` records ruling timestamps rather than delivery timestamps in `kc-dev-flow-2/scripts/decision_ledger.py`.  
   **Why it matters:** Different task cohorts can produce materially different baseline rates.

8. **Q:** How should one approval that settles a stage gate, several Needs decisions, and a merge request contribute to the requested category counts?  
   **Story:** captain-question-load  
   **Grounds:** The story requests separate categories; `docs/dev2/README.md` allows a gate question to state that approval also accepts its recommendations.  
   **Why it matters:** Counting both the approval and its component decisions without an explicit rule can inflate the apparent burden.

9. **Q:** How must procedural asks and standalone amendments be counted when they have no gate resolution row?  
   **Story:** captain-question-load  
   **Grounds:** `decision_ledger.gate_entries()` emits only resolutions and withdrawals, while `task_rows()` attaches amendment counts to those rows in `kc-dev-flow-2/scripts/decision_ledger.py`.  
   **Why it matters:** The existing ledger does not directly enumerate every decision category named by the story.

10. **Q:** When the briefing question or recommendation is missing, must apparent plain approvals remain unclassified rather than count as agreement with FO?  
    **Story:** captain-question-load  
    **Grounds:** `decision_ledger.question()` returns `None` for unreadable briefings; `docs/dev2/README.md` says plain approval accepts a recommendation only when the question explicitly says so.  
    **Why it matters:** Absence of an override does not prove informed acceptance of FO’s recommendation.

11. **Q:** Must later amendments be linked to the particular decision they reverse before that decision can support a standing rule?  
    **Story:** captain-question-load  
    **Grounds:** `task_rows()` counts every amendment dated on or after a ruling; architecture decision 0011 explicitly acknowledges that this approximation can over-count reversals.  
    **Why it matters:** An unrelated scope addition could otherwise disqualify a sound precedent or distort the agreement rate.

12. **Q:** Does acceptance include eliminating asks that existing rules already authorize, separately from introducing new standing rules?  
    **Story:** captain-question-load  
    **Grounds:** `docs/dev2/README.md` already permits throwaway-checkout probes and FO-authorized fixes within approved boundaries, both related to examples in the story.  
    **Why it matters:** Repeated questions may reflect failure to follow current rules rather than missing authority.

13. **Q:** Which changes after a delivery approval invalidate its merge grant?  
    **Story:** captain-question-load  
    **Grounds:** `docs/dev2/README.md` permits later repairs on the same pull request under a grant, while `delivery_gate.check()` binds its checks to a candidate commit in `kc-dev-flow-2/scripts/delivery_gate.py`.  
    **Why it matters:** A grant needs a decided boundary when the candidate, scope, or review evidence changes.

14. **Q:** What must FO do when a permission check rejects a push already covered by the Captain’s recorded grant?  
    **Story:** captain-question-load  
    **Grounds:** The story includes “a push the permission check refused”; `docs/dev2/README.md` requires failures to hold delivery pending an explicit choice.  
    **Why it matters:** Repeating an authorization question may not resolve the actual permission failure.

15. **Q:** What durable evidence must a resumed FO have before continuing under an earlier combined delivery and merge grant?  
    **Story:** captain-question-load  
    **Grounds:** `delivery_gate.write_record()` saves the pull request, head, classification, and verdict, but no Captain grant or approved question, in `kc-dev-flow-2/scripts/delivery_gate.py`.  
    **Why it matters:** Restarting must neither lose valid permission nor reconstruct permission from an advisory verdict.

16. **Q:** Must repeated measurements use one fixed state revision when tasks can move between active and archived locations during collection?  
    **Story:** captain-question-load  
    **Grounds:** `decision_ledger.ledger()` separately scans live files and `_archive` without pinning a revision in `kc-dev-flow-2/scripts/decision_ledger.py`.  
    **Why it matters:** Concurrent archival can make the same measurement omit or duplicate a task.

17. **Q:** Can this story proceed without the batch-sittings note and the batching figures owed by the qnow First Officer?  
    **Story:** captain-question-load  
    **Grounds:** The story names `fo-batch-sittings-interim` and “the qnow R11 batching numbers … owes,” neither supplied in this snapshot.  
    **Why it matters:** Their status determines whether the baseline is complete and whether batching already addresses the main burden.

18. **Q:** Are the resulting standing rules authorized only for this workflow, or intended for other adopting projects too?  
    **Story:** captain-question-load  
    **Grounds:** The story measures “this workflow”; `kc-dev-flow-2/references/sd/adoption.md` requires an approved, adopter-specific workflow synchronization and preserves existing task authority.  
    **Why it matters:** A package rule does not itself update or authorize every adopter’s workflow.

19. **Q:** What ceiling applies to additional model runs, workflow reading, and review work introduced to reduce Captain questions?  
    **Story:** captain-question-load  
    **Grounds:** `kc-dev-flow-2/skills/maintain-flow/SKILL.md` requires measuring added reading, and architecture decision 0021 requires another security review for each new candidate head.  
    **Why it matters:** Fewer Captain replies could otherwise come with an undecided increase in operating cost.

20. **Q:** What behavioral evidence must show that a redundant question disappears while a decision outside FO’s authority still reaches the Captain?  
    **Story:** captain-question-load  
    **Grounds:** `kc-dev-flow-2/skills/maintain-flow/SKILL.md` requires fresh FO scenarios including a case where the rule must not apply; `InjectionTests` in `kc-dev-flow-2/scripts/test_delivery_gate.py` currently preserves an explicit ask even when a saved verdict says `merge`.  
    **Why it matters:** Text checks and lower question counts alone cannot prove that the Captain retained his decisions.

Reads: 27, minutes: 2