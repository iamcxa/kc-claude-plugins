1. Q: Do the two reported late reservations represent violations in two distinct tasks or two dispatches of the same task?
   Story: number-guards-readme-shrink
   Grounds: Story: “prod-security-review-gates 2026-10-16/17”; `kc-dev-flow-2/skills/maintain-flow/SKILL.md`: “A rule broken in two tasks becomes a package change.”
   Why it matters: The distinction determines whether the existing escalation rule applies.
2. Q: Must this task demonstrate fewer late reservations, or is shorter documentation with unchanged reservation behavior sufficient?
   Story: number-guards-readme-shrink
   Grounds: Story: “Bite to confirm at ideation: the observer's count of number-guard violations”; `check()` in `kc-dev-flow-2/scripts/number_guards.py` checks reservation membership but not when the reservation happened.
   Why it matters: A reservation added after implementation can pass the script while repeating the incident that motivated the story.
3. Q: When a failure message identifies a problem without explaining its remedy, may this task change the message, or must the explanatory prose remain?
   Story: number-guards-readme-shrink
   Grounds: Story permits shrinking a rule “whose message tells the reader what to do”; `check()` in `kc-dev-flow-2/scripts/number_guards.py` reports “number … is not in the task's … lines” and “base already has …” without recovery instructions.
   Why it matters: This determines both the implementation boundary and how much text qualifies for removal.
4. Q: If concurrent reservation calls print the same number before either task records it, who owns resolving that collision before implementation starts?
   Story: number-guards-readme-shrink
   Grounds: `reserve()` in `kc-dev-flow-2/scripts/number_guards.py` reads task files and prints a number without writing or locking; `ReserveTests.test_reserve_never_collides_and_never_fills_a_gap` records the first result before calling the second reservation.
   Why it matters: The documented coordination responsibility cannot be replaced by a claim that the script prevents concurrent collisions.
5. Q: What recovery should a reader follow for an architecture decision record number collision?
   Story: number-guards-readme-shrink
   Grounds: `check()` reports ADR collisions through `R5` in `kc-dev-flow-2/scripts/number_guards.py`; “FO steps: number guards → Collision” in `kc-dev-flow-2/references/sd/workflow.md` mentions `R5` but describes deleting a `Migration:` line and handling database state.
   Why it matters: The existing recovery passage does not explain the ADR-only case that its failure reference includes.
6. Q: Does “reserves no number” prohibit a proof of concept task from reserving an architecture decision record number as well as a migration number?
   Story: number-guards-readme-shrink
   Grounds: “Number guards → POC” in `kc-dev-flow-2/references/sd/workflow.md` says “reserves no number,” while “Decision records” requires reserved ADR numbers and `reserve()` has no profile restriction.
   Why it matters: Compressing this sentence could silently choose between conflicting readings of the current contract.
7. Q: Who must supply the migration-check command for a proof of concept task that has no `## Number guards` section?
   Story: number-guards-readme-shrink
   Grounds: `kc-dev-flow-2/references/sd/workflow.md` applies the POC check to every such task but omits the section from its task template; implementation and validation principles condition their checks on the section being present.
   Why it matters: A shorter pointer cannot produce a failure message if no participant knows to run the check.
8. Q: Is the First Officer’s recorded `Not applied:` line sufficient to unfreeze a migration, or must validation independently verify its supporting rejection or Captain-authorized reset evidence?
   Story: number-guards-readme-shrink
   Grounds: “FO steps: number guards → Applied/Collision” in `kc-dev-flow-2/references/sd/workflow.md` requires confirmation and reserves database resets for the Captain; `AppliedFreezeTests.test_a_not_applied_line_in_place_of_the_record_leaves_the_edit_unfrozen` accepts a line without evidence.
   Why it matters: The script does not enforce the evidence or permission boundary on which safe unfreezing depends.
9. Q: What unchanged reservation-timing rule will govern before-and-after observer counts if this edit removes or rewrites the sentence the observer currently evaluates?
   Story: number-guards-readme-shrink
   Grounds: Story names observer violation counts as the bite; `kc-dev-flow-2/skills/observer/SKILL.md` tells the observer to collect applicable sentences whose subject is the First Officer from the adopted README.
   Why it matters: Removing an observable obligation could reduce reported violations without improving behavior.
10. Q: Which observable safety behavior must remain proven if the shrink removes wording currently required literally by the proof of concept README test?
    Story: number-guards-readme-shrink
    Grounds: `DeriveTests.test_the_derived_poc_readme_carries_the_migration_rule_to_both_worker_stages` in `kc-dev-flow-2/scripts/test_poc_readme.py` requires `FAIL R6`, the boundary marker, and “not repaired in place” inside the POC bullet.
    Why it matters: Preserving those strings and preserving the intended workflow are different acceptance conditions.
11. Q: Does completion include synchronizing `docs/dev2/README.md` and `docs/dev2-poc/README.md`, or only changing the package template and its budget?
    Story: number-guards-readme-shrink
    Grounds: Story names `kc-dev-flow-2/references/sd/workflow.md`; `kc-dev-flow-2/references/sd/adoption.md` says existing adopters receive changes through a separate README synchronization, and both local adopted READMEs retain the passage.
    Why it matters: A template-only cut lowers the measured budget while the repository’s active workflows continue loading the original text.
