1. Q: Must the First Officer’s actual write commands refuse invalid writes, or does running a separate checker satisfy this story?
   Story: fo-write-checks
   Grounds: Story: “at the moment FO writes”; `references/sd/laws.md` explicitly says the existing runner does not block a dispatch or push.
   Why it matters: This determines whether the work needs integration with the workflow runtime or only additional script checks.
2. Q: Does this story reopen the accepted decision to leave FO paraphrases in `Design:` unchecked, or is that failure class outside automatic enforcement?
   Story: fo-write-checks
   Grounds: `docs/adr/0016-the-amendment-check-refuses-an-unnamed-move-and-an-unmarked-replacement.md` rejects scanning `Design:` because valid pointers and paraphrases cannot reliably be separated.
   Why it matters: Including this class requires changing an accepted boundary, not merely extending an existing check.
3. Q: What recorded evidence must distinguish a Captain amendment from ordinary feedback when the Captain’s ruling exists only in chat?
   Story: fo-write-checks
   Grounds: Story: “a Captain ruling recorded as a Feedback Cycle instead of an amendment”; `kc-dev-flow-2/skills/observer/SKILL.md` treats unrecorded exchanges as outside what state shows.
   Why it matters: A script cannot identify a missing amendment from text that never records the ruling.
4. Q: What durable evidence must prove worker investigation preceded distinct FO repair authorization?
   Story: fo-write-checks
   Grounds: `docs/dev2/README.md`, “FO steps: review findings,” requires investigation without mutation followed by authorization through the addressable-worker boundary; `dispatch_records.PARTS` checks neither event.
   Why it matters: Checking that a dispatch mentions investigation would not establish that investigation actually happened before permission to repair.
5. Q: Must the amendment check allow the temporary state after FO records an amendment but before the worker moves its superseded criteria?
   Story: fo-write-checks
   Grounds: `docs/adr/0005-a-captain-amendment-is-recorded-by-fo-and-moved-by-the-next-worker.md`: “Between FO’s record and the worker’s move the task shows both, and `check` says so.”
   Why it matters: Applying the full existing check to every FO write could prevent the worker dispatch needed to complete the amendment.
6. Q: Which six observer reports and exact state revisions define the required regression examples for these failure classes?
   Story: fo-write-checks
   Grounds: Story: “Measured from the six batch-2 observer reports” and “each class above, with the observer report that names it.”
   Why it matters: The supplied counts alone cannot establish whether new checks catch the original failures.
7. Q: Must a decline check require only a reason, or also the finding identity, candidate revision, and supporting lines or evidence required by the workflow?
   Story: fo-write-checks
   Grounds: `docs/dev2/README.md`, review-findings step 2, requires all those details; `test_delivery_gate.PointTests.CASES["fo-decline"]` accepts “the logging nit (not now)” as a successful gate check.
   Why it matters: The answer separates a narrow missing-reason check from enforcement of the existing decline contract.
8. Q: Which artifact must contain the authoritative FO Material assessment that the script checks?
   Story: fo-write-checks
   Grounds: Story: “a Material claim without the `value-ac[...]` field form”; `docs/dev2/README.md`, “Review-finding disposition,” defines four evidence fields without specifying a machine-readable assessment record.
   Why it matters: The script needs a defined assessment location to distinguish an FO decision from quoted findings or worker advice.
9. Q: Does the reserved-number check cover an omitted reservation entirely, or only an existing `ADR: NNNN` reservation omitted from dispatch scope notes?
   Story: fo-write-checks
   Grounds: Story names the missing scope-notes line; `number_guards.reserve` prints a reservation, while `number_guards.task_facts` reads reservations already recorded in the task.
   Why it matters: These are different failure cases and require different evidence to detect.
10. Q: Must delivery preparation rerun the architecture decision record lint on the exact proposed code revision, or may it trust the validator’s saved command and exit code?
    Story: fo-write-checks
    Grounds: `docs/dev2/README.md`, “Decision records,” requires successful lint; `delivery_gate.check` checks the pull request revision but never invokes `adr_lint.py`.
    Why it matters: A saved success and a fresh check establish different protection against stale or mismatched evidence.
11. Q: Which amendments must a resumed worker’s next dispatch checklist name when further amendments arrive while that worker is already running?
    Story: fo-write-checks
    Grounds: `docs/dev2/README.md` says FO names an amendment in “the next dispatch’s checklist” and separately treats follow-up messages to resumed workers as dispatches.
    Why it matters: The checker needs a boundary between newly owed amendment instructions and amendments already handled.
12. Q: Must a successful check become invalid if task state or gate text changes before the corresponding dispatch, presentation, or commit?
    Story: fo-write-checks
    Grounds: `delivery_gate.check` independently reads task and gate-text files; `docs/dev2/README.md` permits repair work alongside other workers and warns about shared uncommitted state.
    Why it matters: Otherwise the checked bytes can differ from the bytes that authorize or instruct work.
13. Q: Must the new checks cover edits to existing dispatch records as well as newly added records?
    Story: fo-write-checks
    Grounds: `laws_check.l2_dispatch_record_complete` selects additions and qualifying renames, excluding modifications.
    Why it matters: Extending that law alone would leave later removal of a required instruction unchecked.
14. Q: Should an unrelated new dispatch be blocked by older incomplete records in the same active task?
    Story: fo-write-checks
    Grounds: `dispatch_records.main` checks every dispatch file in the task, whereas `docs/adr/0017-history-laws-judge-only-the-events-a-push-adds.md` limits history enforcement to newly added events.
    Why it matters: The choice determines whether adoption requires repairing old records before current work can continue.
15. Q: Does the repository-only approval authorize these new checks on both adopted workflows, or only the state branch where the existing laws check was enabled?
    Story: fo-write-checks
    Grounds: Story quotes “可以那就只開啟這個repo”; `references/sd/adoption.md` describes separate state branches for `docs/dev2` and `docs/dev2-poc` and rollout once per adopter.
    Why it matters: Package changes and repository activation have different rollout boundaries.
16. Q: What recorded Captain authorization, if any, permits an action to proceed despite a failed new check?
    Story: fo-write-checks
    Grounds: The existing history runner only reports violations, while `docs/dev2/README.md`, review-findings step 5, already permits a Captain waiver for certain blocking findings.
    Why it matters: Blocking checks need a decided exception boundary without letting an FO explanation become permission.
17. Q: Must refusal leave dispatch stamps, prepared gates, and saved success records untouched?
    Story: fo-write-checks
    Grounds: `docs/adr/0005-a-captain-amendment-is-recorded-by-fo-and-moved-by-the-next-worker.md` names `dispatch build --stamp`; `test_delivery_gate.RecordTests` requires a held delivery check to write no record.
    Why it matters: This determines whether failed checks are safe to retry or require recovery of partially completed actions.
18. Q: Does “no new FO words” exclude new record fields and failure diagnostics, or only additional instructions loaded during normal operation?
    Story: fo-write-checks
    Grounds: Story: “absorb with no new FO words”; `docs/adr/0020-a-rise-in-the-workflow-word-budget-needs-a-captain-ruling-recorded-with-it.md` governs growth in the workflow text read at startup and resume.
    Why it matters: The interpretation controls whether missing evidence can receive a structured record without violating the story’s constraint.
19. Q: What measured per-push execution cost is acceptable if the new checks expand the existing state-branch workflow?
    Story: fo-write-checks
    Grounds: `references/sd/adoption.md` explicitly leaves private-adopter minutes unverified; `test_laws_check.WorkflowTemplateTest` forbids cancellation of a push’s check run.
    Why it matters: Every push retains its own run, so added work can affect the acceptable implementation and trigger scope.
20. Q: Must acceptance demonstrate that real workflow commands reject each invalid action when FO omits a voluntary checker invocation?
    Story: fo-write-checks
    Grounds: `docs/adr/0017-history-laws-judge-only-the-events-a-push-adds.md` identifies skipped checker invocation as the original failure layer; `test_sd_dispatch.py` exercises real dispatch transport without spawning a model.
    Why it matters: Script-level passing tests alone would not prove that the repeated process failures are prevented.
