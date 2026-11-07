# AC-4: falsifier confounded

FO disposition: dispatch/implementation-1-message-4.md. No alternate falsifier or product wording change was substituted.

Exact mutated rule in both independent runs:

5. A round is one verdict of an external reviewer of the delivery on the PR head (Codex
   on the PR, RoboRev or another); FO counts rounds and records the count in the
   committed gate summary. A reviewer that a listed extension covers is read the way its
   `EXTENSION.md` says (`## Extensions`). A finding assessed Material, or labelled P1 by
   the reviewer, blocks in every round: a reviewer P1 is fixed and revalidated, or
   waived by the Captain with the reason recorded (step 4). For an external reviewer
   that has no P1 label, its highest severity level counts as P1 (e.g. RoboRev). Rounds
   1 and 2 follow steps 1 to 4. From round 3 a finding that is neither does not start a
   repair cycle: FO declines it in the committed gate summary, naming the finding and
   its reason. It never enters an open task's Scope. The terminal gate lists each
   such task.

Run 1: 9ca06dfd-5258-48a8-ace6-321127ec95e8, requested claude/sonnet. D remains violation under "A finding assessed Material, or labelled P1 by the reviewer, blocks in every round"; it says the three workers' search shows real harm. Exact response: missing-bite-1.activity.json.

Run 2: b434816c-ed04-4f53-9e37-1a765b30d89a, requested claude/sonnet. D remains violation under the same Material/P1 sentence; "The record's own evidence (three workers got no package root and had to search) shows real harm, which makes it Material". Exact response: missing-bite-2.activity.json.

The primary candidate rule passed twice (A/B/C ok, D violation); base passed its expected control (A/B/C violation). Deleting the bite clause did not isolate the task-creation requirement from the unchanged Material/P1 boundary. This is failed falsifier evidence, not evidence that the product rule needs another edit.
