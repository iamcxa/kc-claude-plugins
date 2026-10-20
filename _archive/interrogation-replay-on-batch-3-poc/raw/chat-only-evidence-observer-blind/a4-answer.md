1. **Q:** Which listed First Officer (FO) obligations must leave durable evidence, and which should remain chat-only and leave the observer’s checks?
   **Story:** chat-only-evidence-observer-blind
   **Grounds:** Story: “whether each rule should name the record FO leaves … or be accepted as chat-only and dropped from the observer’s checks.”
   **Why it matters:** This determines the actual scope before recording requirements or observer behavior change.

2. **Q:** Should a record prove only that FO documented an action, or support the stronger conclusion that the action happened before the Captain?
   **Story:** chat-only-evidence-observer-blind
   **Grounds:** `kc-dev-flow-2/skills/observer/SKILL.md`: “You read those writes as someone who was not there”; the story concerns actions “in front of the Captain.”
   **Why it matters:** A written assertion and evidence of presentation support different conclusions.

3. **Q:** Once a rule explicitly requires a record, should its absence produce `violation` rather than `can't tell`?
   **Story:** chat-only-evidence-observer-blind
   **Grounds:** `kc-dev-flow-2/skills/observer/SKILL.md`: “`can't tell` names the evidence that is outside state.”
   **Why it matters:** This defines whether the change detects noncompliance or merely documents uncertainty.

4. **Q:** Must missing evidence remain an after-the-fact observation, or should it prevent the affected gate or delivery action?
   **Story:** chat-only-evidence-observer-blind
   **Grounds:** `kc-dev-flow-2/extensions/learn/EXTENSION.md`: “nothing here … unlocks a delivery or merge”; `pr_watch.py::tasks` invokes the observer check after detecting a merged pull request.
   **Why it matters:** Prevention would add runtime enforcement beyond the existing observer’s role.

5. **Q:** Which workflow revision should govern a task whose observed history spans a rule change?
   **Story:** chat-only-evidence-observer-blind
   **Grounds:** `kc-dev-flow-2/skills/observer/SKILL.md` accepts state commit bounds but only a supplied `RULES` README; `docs/adr/0017-history-laws-judge-only-the-events-a-push-adds.md` documents failures caused by judging events that predated rules.
   **Why it matters:** New recording duties could otherwise turn historically acceptable work into apparent violations.

6. **Q:** What must FO record to distinguish its own confirmation of goal sufficiency and minimal necessity from simply citing the validator’s conclusion?
   **Story:** chat-only-evidence-observer-blind
   **Grounds:** `kc-dev-flow-2/references/sd/workflow.md`, validation: “FO confirms both goal sufficiency and minimal necessity”; `skills/validation/principles.md` separately assigns those assessments to validation.
   **Why it matters:** The new evidence must establish whether the separate FO obligation was fulfilled.

7. **Q:** For “presents every step in full beside its observed output,” must durable state contain the complete step/output pairs or can an immutable reference satisfy the record requirement?
   **Story:** chat-only-evidence-observer-blind
   **Grounds:** `kc-dev-flow-2/references/sd/workflow.md`, validation: “never a pointer or a shortened step.”
   **Why it matters:** The existing presentation rule does not specify what must survive in state.

8. **Q:** For publication that requires advance presentation, what evidence must connect the presented candidate and PR body to the Captain’s authorization and the actual publication?
   **Story:** chat-only-evidence-observer-blind
   **Grounds:** `kc-dev-flow-2/references/sd/workflow.md`, Delivery authority: “present the exact candidate and PR body before authorized push/create”; it separately permits a quoted implementation-worker grant to stand in for a presented body.
   **Why it matters:** Recording approval alone cannot establish that it covered the bytes published.

9. **Q:** Is the existing saved merge-check record sufficient evidence of the head read, given that it retains neither the supplied question nor the summary?
   **Story:** chat-only-evidence-observer-blind
   **Grounds:** `kc-dev-flow-2/scripts/delivery_gate.py::check` reads `--text-file`, while `write_record` saves the PR, head, classification, verdict, points and time.
   **Why it matters:** Existing records may establish a head check while leaving the wording and authority of the ask unverifiable.

10. **Q:** Which evidence must be renewed when a repair changes the head of an already approved PR?
    **Story:** chat-only-evidence-observer-blind
    **Grounds:** `kc-dev-flow-2/references/sd/workflow.md`, Delivery authority permits later external-review rounds on the same PR; its validation rule requires confirmation from “the same candidate’s existing route evidence.”
    **Why it matters:** Evidence for an earlier candidate must not silently satisfy obligations for a later one.

11. **Q:** What must identify the exact task revision checked by the backlog seed command before gate preparation?
    **Story:** chat-only-evidence-observer-blind
    **Grounds:** `kc-dev-flow-2/scripts/design_surfaces.py::check_task` reads the current task file, and `main` prints success without retaining the input revision.
    **Why it matters:** A later valid task file cannot establish what FO checked before the gate.

12. **Q:** What should durable watch evidence establish after a session restart: that the PR was once registered or that monitoring was resumed?
    **Story:** chat-only-evidence-observer-blind
    **Grounds:** `kc-dev-flow-2/scripts/pr_watch.py::default_state` uses session-local storage; `tasks` registers open task PRs, while `sweep` eventually drops merged or closed PRs.
    **Why it matters:** A historical registration record cannot establish current monitoring, and missing local state cannot establish that registration never happened.

13. **Q:** When FO decides a ruling needs no architecture decision record (ADR), must it record the task-only rationale or should the observer assess only rulings explicitly identified as enduring?
    **Story:** chat-only-evidence-observer-blind
    **Grounds:** `kc-dev-flow-2/references/sd/workflow.md`, FO steps: decision records: “A ruling that governs only this task’s own work stays in the task.”
    **Why it matters:** An absent ADR currently leaves the classification decision itself unstated.

14. **Q:** If an action succeeds but the session ends before its evidence is committed, what may a replacement FO legitimately record?
    **Story:** chat-only-evidence-observer-blind
    **Grounds:** `delivery_gate.py::write_record` writes a working file; `observer_check.py::check` and the observer contract inspect committed state.
    **Why it matters:** Recovery needs to distinguish reconstructed facts from claims that the replacement session cannot verify.

15. **Q:** Are concurrent FO sessions allowed to append evidence for the same task, given that merge-record filenames are allocated without a lock?
    **Story:** chat-only-evidence-observer-blind
    **Grounds:** `kc-dev-flow-2/scripts/delivery_gate.py::write_record` selects `max(existing ask numbers) + 1` and writes that path.
    **Why it matters:** Concurrent writers could overwrite evidence unless task ownership excludes that situation.

16. **Q:** If observed command output contains sensitive information, what evidence may be retained while satisfying the full-output requirement?
    **Story:** chat-only-evidence-observer-blind
    **Grounds:** `kc-dev-flow-2/references/sd/workflow.md` requires full observed output but its Secrets rule says “Never read or print a value”; `docs/adr/0003-secret-reads-are-enforced-by-the-adopter.md` assigns enforcement to the adopter.
    **Why it matters:** Persisting output creates a lasting disclosure obligation that presentation alone does not resolve.

17. **Q:** What additional per-task recording effort, stored output and observer-reading cost is acceptable for making these rules auditable?
    **Story:** chat-only-evidence-observer-blind
    **Grounds:** `kc-dev-flow-2/skills/observer/SKILL.md` limits reports to 500 words; `docs/adr/0020-a-rise-in-the-workflow-word-budget-needs-a-captain-ruling-recorded-with-it.md` records concern about growing startup context.
    **Why it matters:** Full evidence retention and repeated inspection have costs beyond adding a sentence to a rule.

18. **Q:** Which original findings from the two named task reports must change under the accepted policy, and which must remain uncertain?
    **Story:** chat-only-evidence-observer-blind
    **Grounds:** Story: both reports marked the same rules `can't tell`, while learning found that “attribution to an outcome is unknown.”
    **Why it matters:** The original findings provide a concrete acceptance baseline without claiming the underlying actions were proved.

19. **Q:** What verdict must a fresh observer return when evidence is present but belongs to another candidate or gate attempt?
    **Story:** chat-only-evidence-observer-blind
    **Grounds:** `kc-dev-flow-2/scripts/test_observer_check.py` tests committed, nonblank report presence; `test_observer_recovery.py` uses a synthetic report and explicitly runs no model.
    **Why it matters:** Current persistence tests do not establish that an observer distinguishes relevant evidence from merely present text.

Reads: 35, minutes: 3