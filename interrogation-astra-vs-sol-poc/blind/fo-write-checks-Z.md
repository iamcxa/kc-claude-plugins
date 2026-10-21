1. Q: Must “checked … at the moment FO writes” prevent an invalid first-officer dispatch or gate presentation, or can a failure reported after the state push satisfy this story?
   Story: fo-write-checks
   Grounds: The story’s timing promise; architecture decision record `docs/adr/0017-history-laws-judge-only-the-events-a-push-adds.md`: “The run detects after the push and cannot stop `merge guard`.”
   Why it matters: Prevention requires integration with the writing operation, while the existing history checker only reports completed writes.
2. Q: Is checking the first officer’s own words in `Design:` intended to reopen the accepted decision that explicitly leaves this judgment to the observer?
   Story: fo-write-checks
   Grounds: `docs/adr/0016-the-amendment-check-refuses-an-unnamed-move-and-an-unmarked-replacement.md`: “no text rule separates a pointer from a paraphrase.”
   Why it matters: This determines whether the story changes an accepted policy or excludes a class that cannot currently be checked reliably.
3. Q: Which six observer reports, state revisions, and offending passages define the regression cases for this story?
   Story: fo-write-checks
   Grounds: The story says “Measured from the six batch-2 observer reports” and “each class above, with the observer report that names it,” without identifying those reports.
   Why it matters: The actual cases determine which failures remain reproducible and prevent building checks around summaries that omit decisive context.
4. Q: What must pass when the first officer records an amendment but its superseded acceptance criteria legitimately remain in place until the next worker moves them?
   Story: fo-write-checks
   Grounds: `docs/adr/0005-a-captain-amendment-is-recorded-by-fo-and-moved-by-the-next-worker.md`: “Between FO’s record and the worker’s move the task shows both, and `check` says so”; `check_amendments()` in `kc-dev-flow-2/scripts/design_surfaces.py` rejects still-declared superseded criteria.
   Why it matters: Applying the completed-state check at the first officer’s write could block the dispatch needed to complete the amendment.
5. Q: What recorded evidence must distinguish a Captain amendment from an ordinary gate revision when checking a ruling recorded as a Feedback Cycle?
   Story: fo-write-checks
   Grounds: `kc-dev-flow-2/references/sd/workflow.md`, “Captain amendments,” distinguishes changes to accepted work from changes requested while its acceptance gate remains open; `kc-dev-flow-2/skills/observer/SKILL.md` says an unrecorded exchange is outside what state shows.
   Why it matters: A heading check cannot establish whether prior acceptance existed or what the Captain changed.
6. Q: Which durable evidence must prove that worker investigation preceded distinct first-officer repair authorization, without accepting the worker’s own classification as that authorization?
   Story: fo-write-checks
   Grounds: `kc-dev-flow-2/references/sd/workflow.md`, “FO steps: review findings,” makes worker classifications advisory and requires investigation, distinct `fix` authorization through the addressable-worker boundary, then independent validation.
   Why it matters: This defines whether the checker verifies permission and ordering or merely accepts a claim that they occurred.
7. Q: How must a decline reason be associated with its particular finding when a gate summary contains several findings and shared explanatory prose?
   Story: fo-write-checks
   Grounds: `points_for()` in `kc-dev-flow-2/scripts/delivery_gate.py` collects lines matching `declined` or bullets under `FO declines`, while the workflow requires the finding, reason, candidate revision, and supporting lines or evidence.
   Why it matters: Finding any reason somewhere in the summary could incorrectly validate an unexplained decline.
8. Q: Must the Material-claim check resolve `value-ac[...]`, `captain-ruling[...]`, and `contract[...]` references to supporting evidence, or only verify their spelling and a nonblank claim?
   Story: fo-write-checks
   Grounds: `kc-dev-flow-2/references/sd/workflow.md`, “Review-finding disposition,” allows those three reference forms and defines Material as evidenced harm to a protected boundary or value criterion.
   Why it matters: A syntactically valid reference can still name missing, withdrawn, or unrelated evidence.
9. Q: Which later dispatches must repeat reserved `ADR: NNNN` lines, including validation dispatches and messages resuming an existing worker?
   Story: fo-write-checks
   Grounds: `kc-dev-flow-2/references/sd/workflow.md` requires reservation lines in dispatch scope notes and says a follow-up message is also a dispatch; `PARTS` in `kc-dev-flow-2/scripts/dispatch_records.py` currently checks neither reservation lines nor their relationship to the task.
   Why it matters: The answer determines which dispatch records require comparison with the task’s reserved numbers.
10. Q: What evidence must bind a passing `adr_lint --require` result to the exact delivery candidate and the complete set of required decision-record numbers?
    Story: fo-write-checks
    Grounds: `kc-dev-flow-2/references/sd/workflow.md`, “Decision records,” requires numbers from both reservations and the implementation report; `check()` in `kc-dev-flow-2/scripts/delivery_gate.py` checks candidate identity but does not invoke decision-record lint.
    Why it matters: An earlier successful run or one omitting a required number could otherwise permit the reported delivery failure.
11. Q: Which modifications to existing dispatch records, gate summaries, and amendment entries must trigger a fresh check?
    Story: fo-write-checks
    Grounds: `l2_dispatch_record_complete()` in `kc-dev-flow-2/scripts/laws_check.py` judges newly added dispatch records and qualifying renames, excluding ordinary modifications.
    Why it matters: Reusing that event definition would leave later edits outside the new protection.
12. Q: What should happen if an amendment, reservation, or gate summary changes after its check passes but before the corresponding dispatch or presentation occurs?
    Story: fo-write-checks
    Grounds: `kc-dev-flow-2/references/sd/workflow.md` separates checker calls from dispatch; `check()` in `kc-dev-flow-2/scripts/delivery_gate.py` reads local task and gate files separately from remote candidate checks.
    Why it matters: A successful check needs a defined validity boundary when its inputs can change before use.
13. Q: If a write is rejected, which effects may already exist, such as a dispatch stamp, prepared gate, or merge-request record?
    Story: fo-write-checks
    Grounds: `kc-dev-flow-2/scripts/test_sd_dispatch.py` exercises `dispatch build --stamp` and `gate prepare`; `write_record()` in `kc-dev-flow-2/scripts/delivery_gate.py` creates numbered `ask-*.json` records.
    Why it matters: Rejection semantics determine whether retrying can leave misleading records or duplicate work.
14. Q: Should a new dispatch be blocked by older noncompliant records belonging to the same task?
    Story: fo-write-checks
    Grounds: `main()` in `kc-dev-flow-2/scripts/dispatch_records.py` checks every dispatch record in the task folder, whereas `docs/adr/0017-history-laws-judge-only-the-events-a-push-adds.md` limits history checks to newly introduced events.
    Why it matters: Strengthening the shared checker could unexpectedly require historical cleanup before current work can continue.
15. Q: Does the Captain’s repository-only authorization cover strengthening shared checkers for existing adopters, or only enabling automatic invocation in this repository?
    Story: fo-write-checks
    Grounds: The story quotes 「可以那就只開啟這個repo」; `kc-dev-flow-2/references/sd/adoption.md` separates package updates, workflow synchronization, and per-adopter activation of state checks.
    Why it matters: Changes to shared scripts can affect repositories beyond the explicitly authorized rollout.
16. Q: How must a write behave when checking is impossible because an input is missing, a checker crashes, or its output is unrecognized?
    Story: fo-write-checks
    Grounds: `run_check()` and `l2_dispatch_record_complete()` in `kc-dev-flow-2/scripts/laws_check.py` distinguish violations from unjudgeable results and parse a restricted set of diagnostic shapes.
    Why it matters: New checks need an operational outcome for uncertainty, and new diagnostic wording must not silently change that outcome.
17. Q: If checking prevents a state push, how can the first officer persist the correction or hold record needed to recover without also permitting the rejected dispatch or gate?
    Story: fo-write-checks
    Grounds: The story includes “state push” as a checking point; `kc-dev-flow-2/references/sd/workflow.md` requires amendments and declines to be recorded durably through state commits.
    Why it matters: A blocking rule must leave a usable recovery path for the state that explains or repairs its failure.
18. Q: What added latency per write and automation cost per completed task are acceptable before these checks are enabled?
    Story: fo-write-checks
    Grounds: `kc-dev-flow-2/references/sd/state-laws.workflow.yml` fetches full state history and performs three checkouts; `delivery_gate.py` makes multiple remote calls; `references/sd/adoption.md` explicitly leaves private-run minutes unverified.
    Why it matters: Moving checks onto frequent writing operations changes both waiting time and paid execution frequency.
19. Q: What acceptance test must demonstrate that a malformed write is caught through the real workflow command even when the first officer omits the manual checker call?
    Story: fo-write-checks
    Grounds: The story seeks to replace repeated reminders with scripts; `kc-dev-flow-2/references/sd/workflow.md` currently instructs the first officer to run checks, while `kc-dev-flow-2/scripts/test_sd_dispatch.py` already exercises real dispatch transport.
    Why it matters: Passing checker tests alone would not prove that the original omission can no longer recur.
