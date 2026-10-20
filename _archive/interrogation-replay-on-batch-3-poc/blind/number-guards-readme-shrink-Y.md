1. Q: If ideation confirms late number reservations, must this task prevent recurrence, or is completion limited to shortening the README?
   Story: number-guards-readme-shrink
   Grounds: Story: “Bite to confirm at ideation”; `check()` in `kc-dev-flow-2/scripts/number_guards.py` checks reserved numbers’ presence, not when they were reserved.
   Why it matters: Preventing late reservations would require work beyond removing redundant prose.
2. Q: Which records establish whether the October 16/17 observations were violations in two separate tasks or repeated observations of one task?
   Story: number-guards-readme-shrink
   Grounds: Story names `prod-security-review-gates` twice; `kc-dev-flow-2/skills/maintain-flow/SKILL.md` says, “A rule broken in two tasks becomes a package change.”
   Why it matters: The distinction determines whether the documented trigger for stronger enforcement applies.
3. Q: May this task improve failure messages to make more prose removable, or must eligibility be judged against the messages already shipped?
   Story: number-guards-readme-shrink
   Grounds: Story requires messages that tell readers what to do; `check()` in `kc-dev-flow-2/scripts/number_guards.py` reports number collisions and missing reservation lines without describing the complete correction.
   Why it matters: The answer changes both the implementation scope and the achievable reduction.
4. Q: What should the First Officer do when an architecture decision record number collides, given that the collision procedure instructs deletion of a `Migration:` line?
   Story: number-guards-readme-shrink
   Grounds: `check()` in `kc-dev-flow-2/scripts/number_guards.py` detects architecture decision record collisions; “FO steps: number guards” in `kc-dev-flow-2/references/sd/workflow.md` says, “The renumbering task deletes its `Migration:` line.”
   Why it matters: Following that instruction leaves the architecture decision record reservation unchanged, and `reserve()` returns it again.
5. Q: Can a proof-of-concept task reserve an architecture decision record number when a ruling requires that record?
   Story: number-guards-readme-shrink
   Grounds: `kc-dev-flow-2/references/sd/workflow.md` applies reservation to tasks landing decision records, but its proof-of-concept bullet says the task “reserves no number.”
   Why it matters: The shortened passage must preserve a coherent rule for this overlap.
6. Q: What acceptance evidence must demonstrate that the shorter passage preserves the Captain’s exclusive authority to reset or delete a shared database?
   Story: number-guards-readme-shrink
   Grounds: “FO steps: number guards” in `kc-dev-flow-2/references/sd/workflow.md` requires a Captain hold for an applied migration’s renumbering; `check()` only tells readers to “revert it and add a new migration.”
   Why it matters: Passing the script cannot establish that the permission boundary survived the edit.
7. Q: Which fresh First Officer scenarios will establish that reservation still happens before dispatch, including when a decision record first becomes necessary during feedback?
   Story: number-guards-readme-shrink
   Grounds: `kc-dev-flow-2/references/sd/workflow.md` requires reservation “before the next dispatch”; “Behaviour replay” in `kc-dev-flow-2/skills/maintain-flow/SKILL.md` requires scenario questions for rules only the First Officer follows.
   Why it matters: Existing number-guard tests cannot distinguish timely reservation from a reservation added afterward.
8. Q: Does acceptance require lower total model input after any additional script or help reads, or only the specified reduction in README words?
   Story: number-guards-readme-shrink
   Grounds: Story requires the budget to fall by removed words; `kc-dev-flow-2/skills/maintain-flow/SKILL.md` identifies startup and dispatch reading costs, while the measured passage contains 277 worker-facing words and 468 First Officer-only words.
   Why it matters: A smaller README alone does not establish the size of the overall reading-cost reduction.
9. Q: Must this task deliver the reduction only in the package template, or also in this repository’s adopted workflow READMEs?
   Story: number-guards-readme-shrink
   Grounds: Story names `kc-dev-flow-2/references/sd/workflow.md`; both adopted READMEs contain the same passage, and `kc-dev-flow-2/references/sd/adoption.md` says package updates do not rewrite adopters’ READMEs.
   Why it matters: The answer determines which files change and which active readers receive the reduction.
