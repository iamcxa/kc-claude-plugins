1. **Q:** Must each delivery approval explicitly include the merge grant, or does this story seek to change the prohibition on standing delegation of merge authority?  
   **Story:** captain-question-load  
   **Grounds:** Story: “a delivery gate that carries the merge grant by default”; architecture decision record 0011: “merge … [is] never delegated at any level.”  
   **Why it matters:** This determines whether the work changes approval wording or the authority model.

2. **Q:** Does this story finish with measurements and proposed standing rules, or include activating those rules in running workflows?  
   **Story:** captain-question-load  
   **Grounds:** Story: “Measure first” and “Then find which kinds a written standing rule could settle”; “Non-goals: to be set at ideation.”  
   **Why it matters:** These outcomes require substantially different implementation and acceptance evidence.

3. **Q:** Which supplied evidence set will establish that every batch-2 Captain decision is accounted for when the snapshot contains no corresponding task-state checkout or gate briefings?  
   **Story:** captain-question-load  
   **Grounds:** Story requires decisions from 2026-10-17 through 10-19; `docs/dev2/README.md`, “Workflow State,” places mutable records in an ignored, separate `.spacedock-state` checkout.  
   **Why it matters:** Missing source records could make the baseline incomplete before any rule is evaluated.

4. **Q:** Is success measured by fewer individual decisions, fewer Captain replies, or fewer interruptions across batch sittings?  
   **Story:** captain-question-load  
   **Grounds:** Card: “answers fewer FO questions per delivered task”; motivation: “most of his turns … were answering FO’s questions”; First Officer approval bundling is described in `docs/dev2/README.md`, “FO steps: review findings.”  
   **Why it matters:** One reply can settle several decisions without reducing their number.

5. **Q:** Does the baseline include all decisions answered during the three-day window or all decisions over the lifetime of tasks delivered during that window?  
   **Story:** captain-question-load  
   **Grounds:** Story combines “2026-10-17 to 10-19” with “every Captain decision per task” and “per delivered task.”  
   **Why it matters:** The cohort changes both the numerator and treatment of unfinished tasks.

6. **Q:** What qualifies a task as delivered for this metric: recorded completion, a recorded merge, or independently confirmed delivery?  
   **Story:** captain-question-load  
   **Grounds:** `kc-dev-flow-2/VALIDATION.md` separately counts archived tasks and tasks recording `pr: pr-merge:`; `docs/dev2/README.md` says gate approval and pull-request creation do not prove merge.  
   **Why it matters:** Counting completed state records as delivery could make question reduction look better without more delivered work.

7. **Q:** What source will supply procedural asks and merge asks that never became gate resolutions?  
   **Story:** captain-question-load  
   **Grounds:** Story includes refused pushes, throwaway repositories, pull-request body edits and waivers; `gate_entries()` in `kc-dev-flow-2/scripts/decision_ledger.py` emits only resolutions and withdrawals.  
   **Why it matters:** The existing ledger cannot by itself measure all requested categories.

8. **Q:** How should one approval covering a stage gate, a recommendation, and a merge grant be counted across the requested categories?  
   **Story:** captain-question-load  
   **Grounds:** Story requests a split into stage gates, Needs decisions, amendments, merge asks and procedural asks; `task_rows()` emits one row per gate event.  
   **Why it matters:** Overlapping categories can inflate totals or hide bundled decisions.

9. **Q:** What evidence distinguishes plain agreement with a recommendation from an approval whose underlying recommendation is missing or unstated?  
   **Story:** captain-question-load  
   **Grounds:** `summary()` in `kc-dev-flow-2/scripts/decision_ledger.py` counts overrides but no explicit agreement; `docs/dev2/README.md` requires the gate question to say when approval accepts a recommendation.  
   **Why it matters:** Absence of an override does not establish agreement.

10. **Q:** Should a missing briefing question make agreement unclassifiable rather than count as an ordinary approval?  
    **Story:** captain-question-load  
    **Grounds:** `question()` in `kc-dev-flow-2/scripts/decision_ledger.py` returns `None` for missing or unreadable briefing indexes; `test_question_comes_from_the_briefing_room()` accepts that result.  
    **Why it matters:** Silent evidence gaps could become false support for delegation.

11. **Q:** How will an amendment be linked to the particular decision it reverses rather than every earlier decision on the task?  
    **Story:** captain-question-load  
    **Grounds:** `task_rows()` counts every amendment dated on or after each ruling; architecture decision record 0011 explicitly says this approximation “can over-count.”  
    **Why it matters:** Incorrect reversal attribution could reject useful standing rules or support unsafe ones.

12. **Q:** Which fixed task-state revision and briefing versions define a reproducible baseline while tasks are being amended or archived?  
    **Story:** captain-question-load  
    **Grounds:** `ledger()` scans active files and `_archive` separately, while `question()` reads companion files from their current paths in `kc-dev-flow-2/scripts/decision_ledger.py`.  
    **Why it matters:** Concurrent workflow activity can change the measured evidence during collection.

13. **Q:** Should decisions already settled by existing rules be reported as failures to follow those rules, separately from decisions needing new standing rules?  
    **Story:** captain-question-load  
    **Grounds:** Story proposes “a repair inside an approved design”; `docs/dev2/README.md` already permits First Officer authorization of owned repairs and says accepted architectural precedents are not asked again.  
    **Why it matters:** The remedy may be reliable execution of existing policy rather than additional policy.

14. **Q:** If a standing merge grant makes the saved delivery verdict actionable, what evidence must establish that validation actually passed?  
    **Story:** captain-question-load  
    **Grounds:** `delivery_gate.py` says it “reads no validation verdict”; `test_the_check_reads_no_validation_report_and_claims_no_verdict()` in `kc-dev-flow-2/scripts/test_delivery_gate.py` explicitly exercises rejected and absent reports.  
    **Why it matters:** A check supporting a human merge question does not necessarily establish readiness for an automatic action.

15. **Q:** What happens to an earlier merge grant when another worker changes the candidate after its delivery check?  
    **Story:** captain-question-load  
    **Grounds:** `kc-dev-flow-2/scripts/test_delivery_gate.py` preserves a declined finding: “a force push between two reads can mix revisions in the record,” justified because “nothing reads the record yet.”  
    **Why it matters:** Giving that record a consumer changes the consequence of the existing concurrency gap.

16. **Q:** How does a Captain correction or withdrawal of a standing rule affect workers already running under its previous version?  
    **Story:** captain-question-load  
    **Grounds:** Architecture decision record 0011 permits reopening delegated precedents; `kc-dev-flow-2/VALIDATION.md` says stage-entry content is not sealed and dispatch records do not pin the content a worker read.  
    **Why it matters:** A correction must not leave concurrent workers exercising superseded authority.

17. **Q:** When a check holds because records or provider data cannot be read, which cases still require a Captain decision rather than operational recovery under existing authority?  
    **Story:** captain-question-load  
    **Grounds:** `delivery_gate.py` returns a hold for unreadable inputs or provider data; `docs/dev2/README.md` requires the First Officer to show failed delivery checks to the Captain.  
    **Why it matters:** Removing decision questions may otherwise leave the same interruption load under error handling.

18. **Q:** How will refused permission checks be distinguished between guard false positives and genuine requests for new authority before either is classified as removable overhead?  
    **Story:** captain-question-load  
    **Grounds:** Story includes “a push the permission check refused”; architecture decision record 0003 records both secret leaks and a guard refusing harmless test text.  
    **Why it matters:** Similar-looking procedural interruptions can represent very different permission boundaries.

19. **Q:** Do accepted standing rules apply only to this workflow, or also to its proof-of-concept route and other adopting repositories?  
    **Story:** captain-question-load  
    **Grounds:** Story limits measurement to “this workflow” but cites another project’s batching numbers; `docs/dev2/README.md` and `docs/dev2-poc/README.md` declare different stage routes.  
    **Why it matters:** Different approval opportunities make rule portability and comparisons nontrivial.

20. **Q:** Are the batching note and the other project’s owed measurements prerequisites for choosing rules, or supporting evidence that may remain unavailable?  
    **Story:** captain-question-load  
    **Grounds:** Story lists “fo-batch-sittings-interim” and “the qnow R11 batching numbers the qnow FO owes” as existing pieces.  
    **Why it matters:** Their dependency status determines whether this story can reach a decision with its own baseline.

21. **Q:** What added model cost, review work, and workflow-document growth are acceptable in exchange for fewer Captain questions?  
    **Story:** captain-question-load  
    **Grounds:** Architecture decision record 0020 says the workflow document is read whole at startup and resume and requires a Captain ruling for budget increases; the story sets no cost boundary.  
    **Why it matters:** Question reduction could shift substantial cost into repeated agent work and larger instructions.

22. **Q:** What independently judged cases and field results must pass before claiming that questions decreased without losing a Captain-owned decision?  
    **Story:** captain-question-load  
    **Grounds:** Card requires both outcomes; `kc-dev-flow-2/VALIDATION.md` says gate correctness is unproven and the observer and ledger “do not prevent a wrong record.”  
    **Why it matters:** Lower recorded question counts alone cannot demonstrate preserved decision authority.

Reads: 17, minutes: 10