1. Q: Must this story reduce late number reservations, or is a shorter README with unchanged reservation behaviour sufficient?
   Story: number-guards-readme-shrink
   Grounds: Story: “Bite to confirm at ideation: the observer's count of number-guard violations”; `check()` in `kc-dev-flow-2/scripts/number_guards.py` checks recorded numbers but not when they were reserved.
   Why it matters: These outcomes require different acceptance evidence and could change the implementation scope.
2. Q: Do the October 16/17 observations represent two distinct late reservations or repeated reports of one event, and which records establish that distinction?
   Story: number-guards-readme-shrink
   Grounds: Story: “an ADR number reserved after the first implementation dispatch happened twice”; `kc-dev-flow-2/skills/observer/SKILL.md` requires findings grounded in state commits and an explicit observation window.
   Why it matters: The claimed frequency cannot support an acceptance baseline until the events are distinguished.
3. Q: May this task change failure messages to make more prose removable, or must eligibility be judged solely against the current messages?
   Story: number-guards-readme-shrink
   Grounds: Story: “whose message tells the reader what to do”; `check()` in `kc-dev-flow-2/scripts/number_guards.py` prints “base already has…” and “is not in the task's…lines” without describing the recovery procedure.
   Why it matters: This determines whether the change covers documentation alone or also changes the script’s user-facing contract.
4. Q: How should an architecture decision record number collision be recovered when the collision instructions describe only migration recovery?
   Story: number-guards-readme-shrink
   Grounds: `check()` reports an existing architecture decision record number as `R5` in `kc-dev-flow-2/scripts/number_guards.py`; “Collision” in `kc-dev-flow-2/references/sd/workflow.md` includes that failure but instructs the reader to delete a `Migration:` line, while `reserve()` returns an existing `ADR:` reservation unchanged.
   Why it matters: A pointer to the existing message leaves this recovery path unspecified.
5. Q: What acceptance evidence must demonstrate that the shortened instructions preserve deployment-evidence requirements and Captain-only database-reset authority?
   Story: number-guards-readme-shrink
   Grounds: “Applied” and “Collision” in `kc-dev-flow-2/references/sd/workflow.md` impose those requirements; `test_a_not_applied_line_in_place_of_the_record_leaves_the_edit_unfrozen()` in `kc-dev-flow-2/scripts/test_number_guards.py` explicitly accepts a `Not applied:` line without supporting evidence.
   Why it matters: Passing the script’s tests cannot establish that these permission boundaries survived the deletion.
6. Q: Is the reader guaranteed to run the shortened check from the candidate’s worktree, or must the retained instruction identify the repository and candidate commit explicitly?
   Story: number-guards-readme-shrink
   Grounds: The “Check” command in `kc-dev-flow-2/references/sd/workflow.md` supplies neither `--repo` nor `--head`; `main()` in `kc-dev-flow-2/scripts/number_guards.py` defaults them to the current directory and `HEAD`.
   Why it matters: An otherwise successful command can inspect a different checkout or commit from the candidate being approved.
7. Q: Does this task deliver the cut only in the package template, or also in this repository’s adopted workflows?
   Story: number-guards-readme-shrink
   Grounds: The story names `kc-dev-flow-2/references/sd/workflow.md`; `docs/dev2/README.md` and `docs/dev2-poc/README.md` contain the same passage, and `kc-dev-flow-2/references/sd/adoption.md` says package updates do not rewrite adopted READMEs.
   Why it matters: A template-only change leaves current users reading the original passage.
8. Q: What must the replacement pointer direct readers to: a command invocation, command help, or the script’s source?
   Story: number-guards-readme-shrink
   Grounds: Story: “shrinks to one pointer sentence”; `main()` in `kc-dev-flow-2/scripts/number_guards.py` exposes help, while the actionable failure text lives inside `check()` and appears only for matching failures.
   Why it matters: These destinations give readers different instructions and impose different reading costs.
9. Q: Is success measured solely by the README word reduction, or must any additional reading introduced by the pointer also be counted?
   Story: number-guards-readme-shrink
   Grounds: `docs/adr/0020-a-rise-in-the-workflow-word-budget-needs-a-captain-ruling-recorded-with-it.md` identifies startup/resume reading and attention as the concern; `workflow_size_and_duplicates()` in `kc-dev-flow-2/scripts/lint-skills.py` measures only the template’s words.
   Why it matters: The budget can fall without reducing the reader’s total workload.
10. Q: What evidence will distinguish an equivalent wording cut from a lost instruction when existing tests require the original phrases?
    Story: number-guards-readme-shrink
    Grounds: `FIXES["applied-none"]` and `FIXES["late-ruling-adr"]` in `kc-dev-flow-2/scripts/test_sd_dispatch.py` pin prose; `test_the_derived_poc_readme_carries_the_migration_rule_to_both_worker_stages()` in `kc-dev-flow-2/scripts/test_poc_readme.py` checks literal phrases.
    Why it matters: Updating those assertions to match shorter prose could remove the regression protection without demonstrating equivalent reader behaviour.
