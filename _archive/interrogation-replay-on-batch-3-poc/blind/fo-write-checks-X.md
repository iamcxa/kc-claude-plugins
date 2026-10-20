1. Q: Which operation must refuse an invalid First Officer (FO) write, given that the current state-law runner detects violations only after a push?
   Story: fo-write-checks
   Grounds: Story: “at the moment FO writes”; `kc-dev-flow-2/references/sd/laws.md`: “The run reports; it does not block … a dispatch or a push.”
   Why it matters: A mandatory write boundary requires different work from another voluntarily invoked check.
2. Q: Does this story reopen architecture decision 0016’s explicit decision to leave FO paraphrases in `Design:` to the observer?
   Story: fo-write-checks
   Grounds: `docs/adr/0016-the-amendment-check-refuses-an-unnamed-move-and-an-unmarked-replacement.md`: “no text rule separates a pointer from a paraphrase.”
   Why it matters: This determines whether that failure class needs a new decision or remains outside script enforcement.
3. Q: Which task, observer report and state revision establish each violation counted in the six-report baseline?
   Story: fo-write-checks
   Grounds: Story: “Measured from the six batch-2 observer reports” and “each class above, with the observer report that names it.”
   Why it matters: Those reports are not included among the snapshot’s observer files, so the reported failures cannot yet become faithful regression cases.
4. Q: What recorded evidence must prove that worker investigation preceded FO repair authorization for the same candidate?
   Story: fo-write-checks
   Grounds: `docs/dev2/README.md`, “FO steps: review findings,” step 3 requires worker investigation, distinct FO authorization and independent validation.
   Why it matters: Requiring a phrase about investigation would not establish the required sequence or authority.
5. Q: What should the checker conclude when distinguishing a Captain amendment from ordinary feedback requires a chat exchange absent from task state?
   Story: fo-write-checks
   Grounds: `docs/dev2/README.md`, “Captain amendments,” distinguishes changes to accepted work from revisions before acceptance; `kc-dev-flow-2/skills/observer/SKILL.md` treats evidence outside state as “can’t tell.”
   Why it matters: The implementation needs a defined outcome for cases that stored records cannot establish.
6. Q: At which write boundary must superseded criteria have been moved, given that recording an amendment legitimately leaves them present until the next worker acts?
   Story: fo-write-checks
   Grounds: `docs/adr/0005-a-captain-amendment-is-recorded-by-fo-and-moved-by-the-next-worker.md`: “Between FO’s record and the worker’s move the task shows both, and `check` says so.”
   Why it matters: Applying the existing completed-amendment check to every write could block the required intermediate state.
7. Q: Must delivery preparation run architecture-record lint against the dispatched candidate, or may it accept a previously recorded successful result?
   Story: fo-write-checks
   Grounds: `delivery_gate.check()` in `kc-dev-flow-2/scripts/delivery_gate.py` does not invoke `adr_lint`; `adr_lint.main()` in `kc-dev-flow-2/scripts/adr_lint.py` reads files from disk.
   Why it matters: The choice determines how a successful lint result is tied to the actual delivery candidate.
8. Q: Must Material checks establish that a referenced value acceptance criterion or protected boundary exists and supports the claim, or only validate the reference’s syntax?
   Story: fo-write-checks
   Grounds: `docs/dev2/README.md`, “Review-finding disposition,” permits `value-ac[AC-N]`, `captain-ruling[YYYY-MM-DD]` and `contract[repo/relative/path#anchor]` plus a nonblank claim.
   Why it matters: A correctly formatted reference can still name a missing, withdrawn or unrelated requirement.
9. Q: Must reserved `ADR: NNNN` lines appear in every subsequent dispatch, including validation and resumed-worker messages, or only the implementation dispatch that reserves them?
   Story: fo-write-checks
   Grounds: `docs/dev2/README.md`, “FO steps: number guards,” requires repeating reservation lines in dispatch scope notes; its dispatch rules also classify resumed-worker messages as dispatches.
   Why it matters: This defines which otherwise valid dispatches the new check must reject.
10. Q: Must the check validate the exact instructions delivered to the worker rather than only the separately saved dispatch record?
    Story: fo-write-checks
    Grounds: `dispatch_records.main()` in `kc-dev-flow-2/scripts/dispatch_records.py` checks saved files; `replay_dispatch.build()` in `kc-dev-flow-2/scripts/replay_dispatch.py` passes separate checklist and scope files to the dispatch builder.
    Why it matters: A clean saved record does not establish that the worker received those same instructions.
11. Q: What happens if an amendment, reservation or candidate changes after checking but before the dispatch or gate is finalized?
    Story: fo-write-checks
    Grounds: `delivery_gate.check()` reads task text, dispatch candidates and remote pull-request facts separately; `docs/dev2/README.md` permits repair work to proceed alongside another task’s worker.
    Why it matters: A successful check can become stale before the action it is meant to protect.
12. Q: Should a valid new dispatch be blocked because an older record in the same task fails a newly introduced rule?
    Story: fo-write-checks
    Grounds: `dispatch_records.main()` scans every dispatch record, while `docs/adr/0017-history-laws-judge-only-the-events-a-push-adds.md` limits history judgments to newly added events.
    Why it matters: Reusing the folder-wide checker could unintentionally make historical defects block current work.
13. Q: Should modifying an existing dispatch record trigger the new checks?
    Story: fo-write-checks
    Grounds: `l2_dispatch_record_complete()` in `kc-dev-flow-2/scripts/laws_check.py` selects additions and qualifying renames, excluding modifications.
    Why it matters: Checking only initial creation leaves later edits outside the promised write-time protection.
14. Q: Should decline wording or reasons inside quoted reviewer evidence count toward an FO decline’s required fields?
    Story: fo-write-checks
    Grounds: `points_for()` in `kc-dev-flow-2/scripts/delivery_gate.py` searches combined report and gate prose for decline-related text without establishing authorship.
    Why it matters: Quoted evidence could either cause a false refusal or make an incomplete FO decision appear complete.
15. Q: Who, if anyone, may waive a new blocking failure?
    Story: fo-write-checks
    Grounds: `observer_check.check()` in `kc-dev-flow-2/scripts/observer_check.py` accepts an `observer not run:` record, while `docs/dev2/README.md` reserves changes to risk acceptance and acceptance criteria for the Captain.
    Why it matters: Existing exceptions do not establish authority to bypass these new controls.
16. Q: Does “only this repo” limit the new checks to this repository’s adopted workflows, or should updating the package activate them for other adopters?
    Story: fo-write-checks
    Grounds: Story: 「可以那就只開啟這個repo」; `kc-dev-flow-2/references/sd/adoption.md` requires state-law rollout once per adopter on the Captain’s word.
    Why it matters: Package-level changes could expand enforcement beyond the recorded activation scope.
17. Q: Must a write be held when the adopted workflow README cannot be located?
    Story: fo-write-checks
    Grounds: `dispatch_records.main()` can print “extensions not checked” and still succeed, whereas `laws_check.py` requires a README for its observer law.
    Why it matters: Missing configuration could otherwise silently disable part of the new protection.
18. Q: If a state-push check discovers a violation after its worker has already started, what action must FO take?
    Story: fo-write-checks
    Grounds: `kc-dev-flow-2/references/sd/adoption.md` says the failed-run notice is the whole signal and the runner does not stop dispatches.
    Why it matters: Detection alone leaves recovery and ongoing worker authority undecided.
19. Q: What execution-cost ceiling must the new checks meet before rollout is accepted?
    Story: fo-write-checks
    Grounds: `kc-dev-flow-2/references/sd/state-laws.workflow.yml` fetches full state history and allows ten minutes per run; `adoption.md` says private-adopter minutes were not verified.
    Why it matters: Checking every write may materially change latency and paid runner usage.
20. Q: What acceptance evidence must demonstrate that invalid writes are refused through the real dispatch and gate commands when FO does not explicitly invoke a checker?
    Story: fo-write-checks
    Grounds: `kc-dev-flow-2/scripts/test_sd_dispatch.py` exercises real dispatch transport without models; `test_the_check_reads_no_validation_report_and_claims_no_verdict()` in `test_delivery_gate.py` deliberately allows a rejected or absent validation report.
    Why it matters: Passing individual script tests would not prove the story’s write-time enforcement works.
