1. Q: For each cited rule, should the First Officer (FO) leave durable evidence, or should the observer explicitly exclude that rule as chat-only?
   Story: chat-only-evidence-observer-blind
   Grounds: Story: “whether each rule should name the record FO leaves … or be accepted as chat-only and dropped from the observer’s checks.”
   Why it matters: This determines which obligations and observer checks actually change.
2. Q: Is the scope limited to the seven listed obligations, or does it include newer chat-dependent authority such as approval carrying permission to merge?
   Story: chat-only-evidence-observer-blind
   Grounds: `docs/adr/0023-a-delivery-gate-question-may-carry-the-merge-of-the-validated-head.md`: “Nothing checks that a merged PR’s approved question named the merge.”
   Why it matters: The snapshot contains another instance of the same evidence gap.
3. Q: Does an FO-authored statement establish that an action happened, or only that FO recorded a claim about it?
   Story: chat-only-evidence-observer-blind
   Grounds: `kc-dev-flow-2/extensions/learn/EXTENSION.md`: “the check proves a non-blank file is committed, not that the observer wrote it.”
   Why it matters: Adding records could otherwise turn unknown behavior into unsupported `ok` findings.
4. Q: When a newly required record is missing, should the observer report a recordkeeping violation, retain `can't tell` about the underlying action, or report both?
   Story: chat-only-evidence-observer-blind
   Grounds: `kc-dev-flow-2/skills/observer/SKILL.md`: “`can't tell` names the evidence that is outside state.”
   Why it matters: Missing documentation and failure to perform an action are different conclusions.
5. Q: Should missing evidence prevent the relevant gate or delivery action, or remain something the observer reports afterward?
   Story: chat-only-evidence-observer-blind
   Grounds: `kc-dev-flow-2/extensions/learn/EXTENSION.md`: “nothing here changes the task, unlocks a delivery or merge.”
   Why it matters: Preventive enforcement requires a different build from retrospective reporting.
6. Q: What retained evidence is sufficient to show that the Captain received every acceptance step beside its observed output, rather than that FO merely generated those materials?
   Story: chat-only-evidence-observer-blind
   Grounds: `docs/dev2/README.md`, validation gate: “presents every step in full beside its observed output.”
   Why it matters: A saved execution log alone does not establish presentation to the Captain.
7. Q: For goal sufficiency and minimal necessity, should the observer verify only FO’s recorded conclusion and evidence references, or assess whether that conclusion is justified?
   Story: chat-only-evidence-observer-blind
   Grounds: `docs/dev2/README.md` requires both confirmations; `kc-dev-flow-2/skills/observer/SKILL.md` says “Do not judge product content, design quality or worker reports.”
   Why it matters: The latter interpretation expands the observer into substantive validation.
8. Q: Can evidence first committed after an action satisfy a rule requiring a check or presentation before that action?
   Story: chat-only-evidence-observer-blind
   Grounds: `docs/dev2/README.md`: “Before recommending delivery,” “Before the merge ask,” and “before authorized push/create.”
   Why it matters: Record presence does not establish the required ordering.
9. Q: Which records must be renewed when the candidate changes during an externally reviewed repair?
   Story: chat-only-evidence-observer-blind
   Grounds: `docs/dev2/README.md` requires confirmation from “the same candidate’s existing route evidence” while allowing later repair rounds under an earlier grant.
   Why it matters: Evidence for an earlier candidate could otherwise satisfy checks on different bytes.
10. Q: What evidence should satisfy the presentation rule when an implementation worker opens the Draft pull request (PR) under a quoted grant?
    Story: chat-only-evidence-observer-blind
    Grounds: `docs/dev2/README.md`, Delivery authority: “that grant stands in for a presented body.”
    Why it matters: A universal requirement to save a presented PR body would contradict this established exception.
11. Q: Must the retained authority evidence identify the exact candidate, PR body and approval together?
    Story: chat-only-evidence-observer-blind
    Grounds: `delivery_gate.check()` in `kc-dev-flow-2/scripts/delivery_gate.py` saves PR identity and head but omits the supplied gate text and PR body.
    Why it matters: The existing receipt cannot reconstruct exactly what the Captain authorized.
12. Q: Which workflow-rule version should govern tasks that began before the new evidence requirements and finish afterward?
    Story: chat-only-evidence-observer-blind
    Grounds: `kc-dev-flow-2/skills/observer/SKILL.md` takes an adopted `RULES` README and a bounded `FROM`–`TO` history window without specifying a rules revision.
    Why it matters: Applying new requirements retrospectively could misclassify previously compliant work.
13. Q: Must every evidence source be read at the observer’s requested `TO` revision?
    Story: chat-only-evidence-observer-blind
    Grounds: The observer accepts `TO`, but `ledger()` and `question()` in `kc-dev-flow-2/scripts/decision_ledger.py` read current files from disk.
    Why it matters: Historical findings could incorporate records or questions written after the audited window.
14. Q: How should overlapping FO sessions preserve competing evidence records for the same task?
    Story: chat-only-evidence-observer-blind
    Grounds: `write_record()` in `kc-dev-flow-2/scripts/delivery_gate.py` selects `max(existing numbers) + 1` and writes the resulting filename without locking.
    Why it matters: Concurrent checks can select the same filename and overwrite evidence.
15. Q: What explicit evidence should distinguish a ruling that needs no architecture decision record (ADR) from a ruling whose ADR assessment was skipped?
    Story: chat-only-evidence-observer-blind
    Grounds: `docs/dev2/README.md`, FO steps: decision records: cross-task rulings become ADRs, while a ruling governing only the current task “stays in the task.”
    Why it matters: Having no reserved ADR number cannot distinguish these cases.
16. Q: What must seed-check evidence identify so the observer can distinguish FO’s pre-backlog run from the worker’s later backstop check?
    Story: chat-only-evidence-observer-blind
    Grounds: `docs/dev2/README.md`, Seed check: “An FO that skips this step still dispatches; the worker’s own check is the backstop.”
    Why it matters: A later successful check does not prove the specific FO obligation was performed.
17. Q: After a session restart or machine change, does watch evidence need to establish registration in the new session or only registration at some earlier point?
    Story: chat-only-evidence-observer-blind
    Grounds: `default_state()` in `kc-dev-flow-2/scripts/pr_watch.py` uses session-local storage; `kc-dev-flow-2/skills/learn/SKILL.md` says not to add an already listed PR.
    Why it matters: A permanent “added” record may outlive the actual monitoring.
18. Q: What evidence should the observer accept when observed command output must be redacted because it contains a secret?
    Story: chat-only-evidence-observer-blind
    Grounds: `docs/dev2/README.md` requires full observed output and separately says “Never read or print a value” under Secrets.
    Why it matters: The evidence contract must support safe omissions without treating them as concealed failures.
19. Q: If a rule is intentionally chat-only, must the observer still name that exclusion in `Coverage`?
    Story: chat-only-evidence-observer-blind
    Grounds: `kc-dev-flow-2/skills/observer/SKILL.md`: “Then `Coverage:` … each rule you could not evaluate.”
    Why it matters: Removing findings could otherwise make reduced visibility look like improved compliance.
20. Q: Must acceptance include a fresh observer distinguishing compliant, missing, stale and inapplicable evidence without access to the originating chat?
    Story: chat-only-evidence-observer-blind
    Grounds: `kc-dev-flow-2/scripts/test_observer_check.py` tests committed-file presence, blank reports and waivers; the story concerns the observer’s inability to determine compliance.
    Why it matters: Passing file-presence tests would not establish that the original blindness is resolved.
21. Q: What added recording effort and model-reading cost is acceptable before an obligation should remain explicitly unaudited?
    Story: chat-only-evidence-observer-blind
    Grounds: `docs/adr/0020-a-rise-in-the-workflow-word-budget-needs-a-captain-ruling-recorded-with-it.md` limits startup text growth; the observer report is capped at 500 words.
    Why it matters: Full steps, outputs and authority records can increase both routine effort and context consumption.
