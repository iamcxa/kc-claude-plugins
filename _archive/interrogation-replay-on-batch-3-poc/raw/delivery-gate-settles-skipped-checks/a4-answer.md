1. Q: What evidence makes a skipped check “by design”: GitHub’s required-check decision, a successful adopter aggregate, or explicit adopter approval?
   
   Story: delivery-gate-settles-skipped-checks  
   Grounds: “Upstream first” names GitHub’s required checks and each adopter’s aggregate; the candidate directions remain unchosen.  
   Why it matters: This determines whether settlement follows provider policy or needs adopter configuration.

2. Q: Should a required check concluding SKIPPED or NEUTRAL pass when GitHub considers that conclusion acceptable?
   
   Story: delivery-gate-settles-skipped-checks  
   Grounds: The story proposes “settle SKIPPED, and NEUTRAL on a check that is not required”; `ci_problem()` rejects both in `kc-dev-flow-2/scripts/delivery_gate.py`.  
   Why it matters: Required and optional checks may need different acceptance rules.

3. Q: Should a failed non-required check continue to hold delivery when all required checks pass?
   
   Story: delivery-gate-settles-skipped-checks  
   Grounds: “Consult only required checks” is a candidate direction, while `ci_problem()` currently rejects every failed check.  
   Why it matters: That direction could remove an existing failure hold beyond the reported skip defect.

4. Q: Does settlement also cover an intentionally skipped whole workflow run?
   
   Story: delivery-gate-settles-skipped-checks  
   Grounds: `runs_problem()` in `kc-dev-flow-2/scripts/delivery_gate.py` independently rejects skipped workflow runs unless superseded.  
   Why it matters: Accepting skipped individual checks could still leave the same delivery blocked.

5. Q: Must a running workflow still hold delivery when GitHub’s required checks have already passed?
   
   Story: delivery-gate-settles-skipped-checks  
   Grounds: `PartialRollupTests.test_a_workflow_run_still_in_progress_holds_though_the_rollup_shows_only_a_green_check()` in `kc-dev-flow-2/scripts/test_delivery_gate.py` protects against incomplete rollups.  
   Why it matters: Consulting only required checks could bypass this existing safeguard.

6. Q: Must delivery detect and hold a required check that never appears in the returned check rollup?
   
   Story: delivery-gate-settles-skipped-checks  
   Grounds: `ci_problem()` examines only returned entries, and `pr_facts()` does not request required-check definitions in `kc-dev-flow-2/scripts/delivery_gate.py`.  
   Why it matters: A successful returned subset does not establish that every required check exists.

7. Q: What should govern settlement in a repository that genuinely has no required checks configured?
   
   Story: delivery-gate-settles-skipped-checks  
   Grounds: “Every adopter” is the consumer, while “consult only required checks” assumes an authoritative required set.  
   Why it matters: An empty required set could otherwise make every optional failure or skip irrelevant.

8. Q: If the adopter’s credentials cannot read the applicable protection or ruleset information, should delivery hold or use another acceptance rule?
   
   Story: delivery-gate-settles-skipped-checks  
   Grounds: The story names “branch protection or rulesets”; `gh()` and `check()` currently turn failed provider reads into holds in `kc-dev-flow-2/scripts/delivery_gate.py`.  
   Why it matters: Unreadable policy must remain distinguishable from a repository with no requirements.

9. Q: Can delivery pass when every returned check is SKIPPED or NEUTRAL and no check actually succeeded?
   
   Story: delivery-gate-settles-skipped-checks  
   Grounds: The card promises an “all-green adopter PR,” while `ci_problem()` currently requires SUCCESS for every entry.  
   Why it matters: Accepting terminal skip states does not settle whether any executed verification is mandatory.

10. Q: When a required-check rule restricts the publishing integration, must settlement verify that integration as well as the check name?
    
    Story: delivery-gate-settles-skipped-checks  
    Grounds: “GitHub’s own model of required checks” is the proposed authority; `ci_problem()` currently examines type, status and conclusion without publisher identity.  
    Why it matters: Matching names alone could accept evidence that does not satisfy the actual requirement.

11. Q: When multiple attempts of the same check exist on one commit, which attempt determines whether its skipped result can be settled?
    
    Story: delivery-gate-settles-skipped-checks  
    Grounds: `runs_problem()` selects superseded runs using `workflow_id` and `run_number`, while `ci_problem()` judges rollup entries independently in `kc-dev-flow-2/scripts/delivery_gate.py`.  
    Why it matters: Reruns can leave contradictory evidence without changing the validated commit.

12. Q: If adopter-declared skip permissions are chosen, may the candidate change the configuration that authorizes its own skipped checks?
    
    Story: delivery-gate-settles-skipped-checks  
    Grounds: The story proposes “an adopter-declared list”; `find_readme()` reads a local workflow README in `kc-dev-flow-2/scripts/delivery_gate.py`.  
    Why it matters: The configuration’s authority and revision determine whether a candidate can weaken its own delivery conditions.

13. Q: Should a PR with satisfied checks still hold when `mergeStateStatus` is BLOCKED for a non-CI requirement?
    
    Story: delivery-gate-settles-skipped-checks  
    Grounds: The story explicitly names `mergeStateStatus`, but `pr_facts()` requests only `mergeable` among merge-state fields in `kc-dev-flow-2/scripts/delivery_gate.py`.  
    Why it matters: Using that field could expand this change from CI settlement into enforcing other merge policies.

14. Q: Should the watcher and delivery gate use the same meaning of green after this change?
    
    Story: delivery-gate-settles-skipped-checks  
    Grounds: `checks()` in `kc-dev-flow-2/scripts/pr_watch.py` accepts skipped conclusions as green, while `HoldTests.HOLDS` in `kc-dev-flow-2/scripts/test_delivery_gate.py` explicitly rejects SKIPPED and NEUTRAL.  
    Why it matters: Different meanings can continue to tell an adopter that checks are green immediately before delivery holds.

15. Q: What evidence of accepted skips must appear in the printed summary and saved merge-ask record?
    
    Story: delivery-gate-settles-skipped-checks  
    Grounds: `write_record()` receives the head, classification, points and confirmation clauses, but no check conclusions or settlement basis, in `kc-dev-flow-2/scripts/delivery_gate.py`.  
    Why it matters: Later review needs to distinguish executed success from an authorized skip.

16. Q: Must acceptance replay complete provider responses from the three reported PR heads, or are synthetic fixtures sufficient?
    
    Story: delivery-gate-settles-skipped-checks  
    Grounds: The story supplies three observed incidents; `pr_json()` defaults to one successful check and `STUB_GH` defaults to no workflow runs in `kc-dev-flow-2/scripts/test_delivery_gate.py`.  
    Why it matters: Simplified fixtures can miss the interaction between required checks, skipped jobs, neutral provider checks and workflow-level holds.

17. Q: Does “fixed before this release” require a successful delivery check using the installed candidate in both relay and web?
    
    Story: delivery-gate-settles-skipped-checks  
    Grounds: The story says “before this release” and identifies relay and web as affected adopters; `kc-dev-flow-2/VALIDATION.md` separates local validation from actual adopter use.  
    Why it matters: Package tests and demonstrated relief for affected adopters are different release criteria.

18. Q: What added API-request and elapsed-time budget per merge ask should the candidate approaches be measured against?
    
    Story: delivery-gate-settles-skipped-checks  
    Grounds: The story calls for candidate directions “to measure”; `check()` already performs several provider reads, each with a 60-second subprocess timeout, in `kc-dev-flow-2/scripts/delivery_gate.py`.  
    Why it matters: Policy lookups or polling could replace repeated overrides with a slower or rate-limited delivery step.

Reads: 16, minutes: 3