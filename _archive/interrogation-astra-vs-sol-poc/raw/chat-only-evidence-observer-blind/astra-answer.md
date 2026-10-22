1. **Q:** Which of the seven cited checks must gain durable evidence, and which should remain chat-only?
   **Story:** chat-only-evidence-observer-blind
   **Grounds:** Story: “whether each rule should name the record FO leaves … or be accepted as chat-only and dropped from the observer's checks.”
   **Why it matters:** This determines the actual scope before implementation.

2. **Q:** For actions performed in front of the Captain, should `ok` mean the First Officer recorded performing them, or require evidence beyond that officer’s assertion?
   **Story:** chat-only-evidence-observer-blind
   **Grounds:** `kc-dev-flow-2/skills/observer/SKILL.md`: “You read those writes as someone who was not there.”
   **Why it matters:** Recording an assertion can remove uncertainty about documentation without proving the interaction happened.

3. **Q:** Should a missing newly required record only produce an observer violation, or also prevent gate presentation or delivery?
   **Story:** chat-only-evidence-observer-blind
   **Grounds:** `kc-dev-flow-2/references/sd/laws.md`: “The run reports; it does not block `merge guard`, a dispatch or a push.”
   **Why it matters:** Reporting omissions and preventing progression require different behavior and authority.

4. **Q:** For delivery paths that still require presenting the exact candidate and pull-request body, what retained evidence must identify the bytes presented and the authorization that followed?
   **Story:** chat-only-evidence-observer-blind
   **Grounds:** `kc-dev-flow-2/references/sd/workflow.md`, Delivery authority: “present the exact candidate and PR body before authorized push/create”; the same section exempts the worker’s Draft route under a quoted grant.
   **Why it matters:** A generic presentation statement cannot distinguish approval of one candidate or body from approval of another.

5. **Q:** Which rule revision should govern tasks that began before the new recording requirements or before a delivery-authority exception was adopted?
   **Story:** chat-only-evidence-observer-blind
   **Grounds:** The story dates from October 13; architecture decision `docs/adr/0015-the-implementation-worker-opens-the-draft-pr-before-validation.md` dates from October 14; `docs/dev2/README.md` and the packaged workflow also contain different merge-authority wording.
   **Why it matters:** Applying later requirements to earlier tasks could create false violations.

6. **Q:** When one validation dispatch names multiple candidate revisions, must acceptance outputs and sufficiency confirmations identify which candidate each covers?
   **Story:** chat-only-evidence-observer-blind
   **Grounds:** `test_the_highest_numbered_record_decides_and_a_record_may_name_several_heads()` in `kc-dev-flow-2/scripts/test_delivery_gate.py`; the workflow requires confirmation from “the same candidate’s existing route evidence.”
   **Why it matters:** An unqualified confirmation could be reused for a revision it never assessed.

7. **Q:** When state advances during observation, should the decision ledger and new evidence records be read at the observer’s supplied ending revision rather than from current files?
   **Story:** chat-only-evidence-observer-blind
   **Grounds:** `kc-dev-flow-2/skills/observer/SKILL.md` defines a `FROM`–`TO` commit window, while `ledger()`, `task_rows()`, and `question()` in `kc-dev-flow-2/scripts/decision_ledger.py` read filesystem contents.
   **Why it matters:** Concurrent updates can otherwise combine decisions from different moments into one finding.

8. **Q:** If the observer consumes saved merge-check records, does the previously accepted risk of mixing revisions across provider reads remain acceptable?
   **Story:** chat-only-evidence-observer-blind
   **Grounds:** The `merge-gatekeeper` excerpt in `kc-dev-flow-2/scripts/test_delivery_gate.py` declines “a force push between two reads can mix revisions in the record” because “nothing reads the record yet.”
   **Why it matters:** Introducing a consumer changes the premise under which that risk was accepted.

9. **Q:** Must durable acceptance evidence retain every command and output in full, or may it omit or redact sensitive material?
   **Story:** chat-only-evidence-observer-blind
   **Grounds:** `kc-dev-flow-2/references/sd/workflow.md` requires presentation of “every step in full beside its observed output,” while Dispatch facts says never to read or print a secret value.
   **Why it matters:** Moving presentation evidence into committed history creates a retention boundary that the presentation rule does not define.

10. **Q:** What must a recorded goal-sufficiency and minimal-necessity confirmation contain for the observer to assess compliance without judging product or design quality?
    **Story:** chat-only-evidence-observer-blind
    **Grounds:** The validation gate requires both confirmations in `kc-dev-flow-2/references/sd/workflow.md`; `kc-dev-flow-2/skills/observer/SKILL.md` says “Do not judge product content, design quality or worker reports.”
    **Why it matters:** A checkbox may prove only that words were recorded, while evaluating the reasoning could exceed the observer’s remit.

11. **Q:** For the backlog seed check, must evidence establish that the command ran before gate preparation, or only that the task satisfied its checks?
    **Story:** chat-only-evidence-observer-blind
    **Grounds:** The workflow requires `design_surfaces.py check --seed` before `gate prepare`; `check_task(seed=True)` in `kc-dev-flow-2/scripts/design_surfaces.py` inspects current task content and saves no execution record.
    **Why it matters:** Rechecking valid content later cannot establish that the required earlier action occurred.

12. **Q:** Should the monitoring check establish historical registration of a pull request or that monitoring was active in each session responsible for following it?
    **Story:** chat-only-evidence-observer-blind
    **Grounds:** The story names `pr_watch.py add`; `kc-dev-flow-2/scripts/pr_watch.py` stores watches per session, and `tasks()` also registers open task pull requests.
    **Why it matters:** A durable registration record can survive a session whose monitoring no longer exists.

13. **Q:** Must every ruling explicitly record whether it requires an architecture decision record, including a reason when it governs only the current task?
    **Story:** chat-only-evidence-observer-blind
    **Grounds:** `kc-dev-flow-2/references/sd/workflow.md`, FO steps: decision records: “A ruling that governs only this task’s own work stays in the task.”
    **Why it matters:** Without a recorded classification, an absent decision document remains ambiguous between a deliberate exemption and an omission.

14. **Q:** If a session ends after presenting evidence but before committing its record, what may the next session record without repeating the presentation?
    **Story:** chat-only-evidence-observer-blind
    **Grounds:** `kc-dev-flow-2/extensions/learn/EXTENSION.md`: “The observer reads committed state only”; the story proposes a line in a committed gate summary.
    **Why it matters:** Recovery must distinguish a late account from contemporaneous evidence of a required sequence.

15. **Q:** Would the new recording obligations apply to adopters that do not enable the learning extension or routinely run an observer?
    **Story:** chat-only-evidence-observer-blind
    **Grounds:** The packaged workflow defaults to `extensions: []`, and its Extensions section says an unlisted extension “adds nothing”; the observer runs automatically through the learning extension.
    **Why it matters:** This determines whether all users incur the recording work or only users requesting the audit.

16. **Q:** If a rule is deliberately excluded as chat-only, should the observer still disclose that exclusion in its coverage statement?
    **Story:** chat-only-evidence-observer-blind
    **Grounds:** The story proposes dropping checks; `kc-dev-flow-2/skills/observer/SKILL.md` requires `Coverage:` to name “each rule you could not evaluate.”
    **Why it matters:** Removing findings without disclosing exclusions could make reduced coverage appear to be improved compliance.

17. **Q:** What additional per-task recording and observer-reading cost is acceptable if full acceptance outputs become durable evidence?
    **Story:** chat-only-evidence-observer-blind
    **Grounds:** `docs/adr/0020-a-rise-in-the-workflow-word-budget-needs-a-captain-ruling-recorded-with-it.md` constrains workflow-text growth because the README is read whole; the observer’s report is limited to 500 words.
    **Why it matters:** Brief instructions can still introduce large recurring evidence-reading costs.

18. **Q:** What acceptance evidence must demonstrate that an actual First Officer leaves usable records and an independent observer distinguishes compliant, missing, and stale evidence?
    **Story:** chat-only-evidence-observer-blind
    **Grounds:** `check()` in `kc-dev-flow-2/scripts/observer_check.py` accepts any committed nonblank report; `kc-dev-flow-2/VALIDATION.md` states that gate correctness is unproven.
    **Why it matters:** File-presence tests alone cannot establish that this story resolves the reported blind spots.

Reads: 34, minutes: 3