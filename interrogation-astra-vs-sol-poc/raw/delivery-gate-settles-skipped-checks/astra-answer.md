1. **Q:** When GitHub’s required-check rules and an adopter’s aggregate job disagree, which determines whether delivery proceeds?
   **Story:** delivery-gate-settles-skipped-checks
   **Grounds:** Story: “GitHub's own model of required checks … and each adopter's aggregate job … before the package judges CI meaning itself.”
   **Why it matters:** The story names two authorities without deciding their precedence.

2. **Q:** Should a failed or still-running non-required check continue to hold delivery?
   **Story:** delivery-gate-settles-skipped-checks
   **Grounds:** Story candidate: “consult only required checks”; `ci_problem()` in `kc-dev-flow-2/scripts/delivery_gate.py` currently holds every non-successful check.
   **Why it matters:** Required-only evaluation would change behavior beyond the reported skipped and neutral checks.

3. **Q:** Should a required check concluding SKIPPED or NEUTRAL be accepted when GitHub considers that requirement satisfied?
   **Story:** delivery-gate-settles-skipped-checks
   **Grounds:** Story candidate: “settle SKIPPED, and NEUTRAL on a check that is not required”; `HoldTests.HOLDS` in `kc-dev-flow-2/scripts/test_delivery_gate.py` rejects both conclusions.
   **Why it matters:** The answer decides whether package policy follows GitHub or deliberately remains stricter.

4. **Q:** Does settling an intentional skip also cover an entire skipped workflow run, or only individual check runs?
   **Story:** delivery-gate-settles-skipped-checks
   **Grounds:** `check()` independently calls `ci_problem()` and `runs_problem()` in `kc-dev-flow-2/scripts/delivery_gate.py`; the latter rejects a skipped workflow unless a newer run supersedes it.
   **Why it matters:** Changing check-run handling alone could leave the same delivery blocked elsewhere.

5. **Q:** What should happen when the adopter’s existing credentials can read check results but cannot read the protection or ruleset information needed to classify them?
   **Story:** delivery-gate-settles-skipped-checks
   **Grounds:** Story proposes consulting branch protection or rulesets; `pr_facts()` and `pr_runs()` in `kc-dev-flow-2/scripts/delivery_gate.py` currently query neither.
   **Why it matters:** New permission requirements could replace the skip-related hold with an access-related hold.

6. **Q:** What evidence must distinguish a repository with no required checks from a required check that has not appeared in the rollup?
   **Story:** delivery-gate-settles-skipped-checks
   **Grounds:** `PartialRollupTests.test_a_workflow_run_still_in_progress_holds_though_the_rollup_shows_only_a_green_check` in `kc-dev-flow-2/scripts/test_delivery_gate.py` protects against incomplete check visibility.
   **Why it matters:** Filtering only visible results could accept a missing requirement as an empty set.

7. **Q:** May delivery proceed when every visible check is skipped or neutral and no check has actually succeeded?
   **Story:** delivery-gate-settles-skipped-checks
   **Grounds:** Story promises an “all-green adopter PR”; `ci_problem()` in `kc-dev-flow-2/scripts/delivery_gate.py` currently requires a nonempty rollup of successful results.
   **Why it matters:** Accepting individual skipped results does not settle whether some positive execution evidence remains mandatory.

8. **Q:** Would using `mergeStateStatus` make delivery wait for non-check requirements, such as outstanding reviews, as well as check results?
   **Story:** delivery-gate-settles-skipped-checks
   **Grounds:** Story names `mergeStateStatus`; `pr_facts()` in `kc-dev-flow-2/scripts/delivery_gate.py` currently requests only `mergeable`, while “No applicable checks” in `kc-dev-flow-2/skills/learn/SKILL.md` describes BLOCKED as waiting on a check or review.
   **Why it matters:** This could expand the gate from checking delivery evidence into enforcing additional repository requirements.

9. **Q:** If an adopter-declared skip list is chosen, who may authorize its entries, and may the pull request being judged change the list that judges it?
   **Story:** delivery-gate-settles-skipped-checks
   **Grounds:** Story candidate: “an adopter-declared list of checks that may skip”; `find_readme()` in `kc-dev-flow-2/scripts/delivery_gate.py` reads local workflow configuration.
   **Why it matters:** The configuration’s authority determines whether a candidate can weaken its own delivery conditions.

10. **Q:** What identifies a trusted aggregate or skip-list entry when two check producers use the same displayed name?
    **Story:** delivery-gate-settles-skipped-checks
    **Grounds:** Story names relay’s `ci-gate` and Netlify checks; `ci_problem()` in `kc-dev-flow-2/scripts/delivery_gate.py` currently uses names only for diagnostics.
    **Why it matters:** A name-based policy could apply an exception to a different producer’s check.

11. **Q:** What evidence distinguishes skips that remain intentional after a pull request becomes ready from draft-era skips awaiting replacement jobs?
    **Story:** delivery-gate-settles-skipped-checks
    **Grounds:** “Delivery authority” in `kc-dev-flow-2/references/sd/workflow.md` says to wait for jobs after marking ready; the `merge-gatekeeper` excerpt in `kc-dev-flow-2/scripts/test_delivery_gate.py` records a known delay before ready-triggered runs appear.
    **Why it matters:** Accepting skips could allow delivery during an already acknowledged visibility gap.

12. **Q:** Should an earlier failed workflow on the same head still block delivery after a later run succeeds?
    **Story:** delivery-gate-settles-skipped-checks
    **Grounds:** `runs_problem()` in `kc-dev-flow-2/scripts/delivery_gate.py` ignores superseded cancelled or skipped runs but retains failures; `PartialRollupTests` explicitly tests “older run failed” as a hold.
    **Why it matters:** Following GitHub’s current required-check result may conflict with the gate’s existing historical-run policy.

13. **Q:** If required-check discovery adds separate reads, what must happen when the pull request’s base or applicable rules change between those reads?
    **Story:** delivery-gate-settles-skipped-checks
    **Grounds:** `check()` in `kc-dev-flow-2/scripts/delivery_gate.py` reads pull-request facts, files and workflow runs sequentially and compares head identity; the story introduces branch-dependent requirement discovery.
    **Why it matters:** A stable head alone would not establish that the results were evaluated under one consistent set of requirements.

14. **Q:** Must the watcher’s reported “green” state agree with the delivery gate’s new policy?
    **Story:** delivery-gate-settles-skipped-checks
    **Grounds:** `checks()` in `kc-dev-flow-2/scripts/pr_watch.py` already accepts skipped and neutral conclusions, while `ci_problem()` in `kc-dev-flow-2/scripts/delivery_gate.py` rejects them.
    **Why it matters:** Leaving different definitions could continue to tell operators a pull request is green while delivery remains blocked.

15. **Q:** What explanation of accepted skipped or neutral checks must appear in the delivery output and saved ask record?
    **Story:** delivery-gate-settles-skipped-checks
    **Grounds:** `write_record()` and its caller in `kc-dev-flow-2/scripts/delivery_gate.py` save the head, classification and summary clauses, but no check results or acceptance basis.
    **Why it matters:** Once overrides disappear, the record otherwise cannot explain why an unexecuted check was accepted.

16. **Q:** Must the fix work immediately for existing adopters after a package update, or may it require a workflow configuration update first?
    **Story:** delivery-gate-settles-skipped-checks
    **Grounds:** Story consumer: “every adopter FO's merge ask”; `kc-dev-flow-2/references/sd/adoption.md` says the package does not rewrite adopter READMEs and updates require a per-adopter merge.
    **Why it matters:** A configuration-dependent solution changes rollout work and when the reported problem is actually resolved.

17. **Q:** What release acceptance evidence must demonstrate that the three reported cases proceed without overrides while an unexpectedly skipped required test still holds?
    **Story:** delivery-gate-settles-skipped-checks
    **Grounds:** Story records three overridden deliveries and requires the fix before release; `pr_json()` and `HoldTests` in `kc-dev-flow-2/scripts/test_delivery_gate.py` currently use synthetic results with no required-check metadata.
    **Why it matters:** Existing tests cannot establish the intended distinction between an authorized skip and missing required execution.

18. **Q:** What added request count and waiting time per merge ask are acceptable for discovering and confirming required checks?
    **Story:** delivery-gate-settles-skipped-checks
    **Grounds:** Story applies to every adopter merge ask; `gh()` in `kc-dev-flow-2/scripts/delivery_gate.py` allows 60 seconds per command, and `check()` already makes several sequential remote reads.
    **Why it matters:** Additional discovery or retries could make routine delivery materially slower and increase API usage.

Reads: 25, minutes: 2