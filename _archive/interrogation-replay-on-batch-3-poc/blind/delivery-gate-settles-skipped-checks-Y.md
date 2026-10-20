1. Q: Should a required check concluding `SKIPPED` pass whenever GitHub considers it satisfied, or must the repository separately establish that skipping was intentional?
   Story: delivery-gate-settles-skipped-checks
   Grounds: Story: “GitHub's own model of required checks … before the package judges CI meaning itself.”
   Why it matters: This decides whether GitHub’s acceptance is sufficient evidence for the central behaviour.
2. Q: Should every non-required `NEUTRAL` check pass, or only checks whose neutral result means nothing applicable changed?
   Story: delivery-gate-settles-skipped-checks
   Grounds: Story proposes “NEUTRAL on a check that is not required,” but the observed examples concern unchanged Netlify rules.
   Why it matters: A general exemption would cover more circumstances than the reported incidents establish.
3. Q: If only required checks are consulted, should a failed or still-running optional check stop blocking delivery?
   Story: delivery-gate-settles-skipped-checks
   Grounds: Story candidate: “consult only required checks”; `ci_problem()` in `kc-dev-flow-2/scripts/delivery_gate.py` currently examines every result.
   Why it matters: This candidate changes failure and waiting behaviour beyond skipped checks.
4. Q: Must the gate detect a required check that never appears in the rollup, even when every returned check passes?
   Story: delivery-gate-settles-skipped-checks
   Grounds: `ci_problem()` examines returned entries; `PartialRollupTests` in `kc-dev-flow-2/scripts/test_delivery_gate.py` covers an existing workflow still running, rather than an absent required check.
   Why it matters: Filtering returned results alone cannot establish that all required evidence exists.
5. Q: Should GitHub’s `mergeStateStatus` block delivery when the check policy passes but GitHub still reports the pull request blocked?
   Story: delivery-gate-settles-skipped-checks
   Grounds: Story explicitly names `mergeStateStatus`; `pr_facts()` in `kc-dev-flow-2/scripts/delivery_gate.py` requests `mergeable` but not that field.
   Why it matters: The proposed upstream authority currently has no input into this decision.
6. Q: Does settling an intentional skip also apply to an entirely skipped workflow, or only to individual check runs?
   Story: delivery-gate-settles-skipped-checks
   Grounds: `runs_problem()` in `kc-dev-flow-2/scripts/delivery_gate.py` independently holds skipped workflows unless a later run supersedes them.
   Why it matters: Changing check-result handling alone can leave an adopter blocked by the second guard.
7. Q: When the authenticated account cannot read the applicable protection or ruleset policy, must delivery hold or may another identified source establish requiredness?
   Story: delivery-gate-settles-skipped-checks
   Grounds: Story proposes consulting branch protection or rulesets; `gh()` and `check()` in `kc-dev-flow-2/scripts/delivery_gate.py` currently turn failed remote reads into holds.
   Why it matters: Policy discovery could introduce new permission requirements for otherwise working adopters.
8. Q: May a successful check from another workflow or publishing app satisfy the aggregate requirement merely because it has the same name?
   Story: delivery-gate-settles-skipped-checks
   Grounds: Story names relay’s aggregate job `ci-gate`; `ci_problem()` in `kc-dev-flow-2/scripts/delivery_gate.py` currently makes no aggregate identity decision.
   Why it matters: Name matching alone could trust an unrelated check.
9. Q: If an adopter-declared skip list is chosen, may the pull request change the declaration used to judge itself?
   Story: delivery-gate-settles-skipped-checks
   Grounds: Story candidate: “an adopter-declared list of checks that may skip”; `find_readme()` in `kc-dev-flow-2/scripts/delivery_gate.py` reads local workflow configuration.
   Why it matters: The policy’s source determines whether a candidate can weaken its own delivery conditions.
10. Q: What should happen when policy discovery succeeds but the repository has no required checks?
    Story: delivery-gate-settles-skipped-checks
    Grounds: Story candidate: “consult only required checks”; `ci_problem()` currently requires a non-empty successful rollup.
    Why it matters: An empty required-check set could otherwise turn the gate into an unconditional pass.
11. Q: If the target branch or applicable check policy changes while the gate gathers evidence, must it restart before issuing a pass?
    Story: delivery-gate-settles-skipped-checks
    Grounds: `check()` in `kc-dev-flow-2/scripts/delivery_gate.py` reads the head, pull-request facts, files and workflows separately; its consistency check concerns the head.
    Why it matters: An unchanged candidate can still be judged against inconsistent policy observations.
12. Q: Should a workflow unrelated to the pull request block delivery solely because it ran on the same commit?
    Story: delivery-gate-settles-skipped-checks
    Grounds: `pr_runs()` in `kc-dev-flow-2/scripts/delivery_gate.py` selects workflows using only `head_sha`, and `runs_problem()` evaluates all returned runs.
    Why it matters: Repository-wide runs can preserve holds even after the pull request’s checks are settled.
13. Q: Must a newly queued or restarted check invalidate a passing decision when the commit has not changed?
    Story: delivery-gate-settles-skipped-checks
    Grounds: `kc-dev-flow-2/skills/observer/SKILL.md` says the gate runs again just before merging; `references/sd/workflow.md` binds merge execution to the commit with `--match-head-commit`.
    Why it matters: Commit identity alone does not freeze the check results supporting approval.
14. Q: Must a passing record preserve which checks were settled and the policy or aggregate evidence that justified each settlement?
    Story: delivery-gate-settles-skipped-checks
    Grounds: `check()` and `write_record()` in `kc-dev-flow-2/scripts/delivery_gate.py` save the head and verdict but no check results or requiredness evidence.
    Why it matters: The existing record cannot later explain why a skipped or neutral result was accepted.
15. Q: Must the Captain’s printed summary distinguish checks accepted as successful from checks accepted as intentionally skipped or neutral?
    Story: delivery-gate-settles-skipped-checks
    Grounds: `docs/dev2/README.md` requires the first officer to show the gate’s output; successful output from `check()` currently contains no check settlement summary.
    Why it matters: Removing a hold could otherwise hide the exception that made delivery possible.
16. Q: Must existing adopters work with their current GitHub CLI version, or may this release require an upgrade to obtain required-check information?
    Story: delivery-gate-settles-skipped-checks
    Grounds: `pr_facts()` currently uses a fixed `gh pr view --json` field list; the story proposes additional upstream policy information.
    Why it matters: The selected source can turn a package update into an adopter tooling migration.
17. Q: Is settling an entirely empty rollup outside this story’s scope despite the watcher already treating some no-check pull requests as settled?
    Story: delivery-gate-settles-skipped-checks
    Grounds: `pr_watch.py::settle()` accepts an unchanged empty rollup after 60 seconds under stated conditions; `delivery_gate.py::ci_problem()` always holds it.
    Why it matters: This sets a concrete non-goal at an existing behaviour boundary.
18. Q: What additional API-request, waiting-time and CI-run budget per pull request is acceptable for discovering and verifying settlement policy?
    Story: delivery-gate-settles-skipped-checks
    Grounds: `gh()` in `kc-dev-flow-2/scripts/delivery_gate.py` permits 60 seconds per command; the observer instructions describe gate runs before both approval and merge.
    Why it matters: Additional discovery and retries multiply across adopter delivery attempts.
19. Q: Must acceptance demonstrate that a deliberately skipped child check remains blocked when its aggregate fails to validate the skip?
    Story: delivery-gate-settles-skipped-checks
    Grounds: Story says relay’s skipped jobs are “checked by ci-gate both ways”; `HoldTests.HOLDS` in `kc-dev-flow-2/scripts/test_delivery_gate.py` models skipped and neutral results without aggregate evidence.
    Why it matters: Passing the reported examples alone would not prove that accidental omissions remain blocked.
20. Q: Does “fixed before this release” require captured incident replays to pass, live gate checks in both adopter repositories without overrides, or completed adopter upgrades?
    Story: delivery-gate-settles-skipped-checks
    Grounds: Story: “把 #677 排在這次發版之前修好”; `kc-dev-flow-2/references/sd/adoption.md` distinguishes plugin updates from separately synchronizing adopter workflow instructions.
    Why it matters: These are different delivery boundaries with different release prerequisites.
