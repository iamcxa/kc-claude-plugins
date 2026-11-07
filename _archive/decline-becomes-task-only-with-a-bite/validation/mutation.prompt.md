Read-only interpretation check. Do not use any tools. Do not read files, edit anything, run commands, write git state, push, or message anyone. Your only task is to answer the five records below using the supplied rule; output only the five requested lines.

You are reading a workflow's records as an outside observer. Below is the workflow rule (step 5 of "FO steps: review findings"), then five decline records from five tasks.

For each record A to E, answer on one line: `<letter> | violation|ok | <the rule words you relied on, quoted> | <one-sentence reason>`. A record is a violation when the rule requires something of FO for that finding that the record shows FO did not do. Judge only against the quoted rule.

RULE:
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

RECORDS:
Each line is the only decline record for its finding; the summary names no backlog task for any of them, and none exists in the workflow.

A. (task fo-tries-what-it-asks-the-captain; External rounds: 6.) Declined: Polish, Codex round 6 P2 comment 4457041237: a path an acceptance step deliberately removes is held as missing (a sixth-round P2, below the P1 that blocks every round).
B. (task model-roster-question-needs-both-families; External rounds: 3.) Declined: a deeper-indented block item read as a list entry (review:5734678752 on workflow_extensions.py: FO judges it unreachable because template-generated workflows write one flat list, and validation-3 shows no harm; a hand-edited malformed list could be misread).
C. (task rewritten-criteria-checked-against-captain-words; External rounds: 4.) Declined: Deferred risk, validation F1 and Codex round 3 P2 comment 4455001433: a tilde-fenced example declaring the same AC id can overwrite the live criterion (no committed acceptance section of 191 has that shape).
D. (task learn-delivery-follow-through; External rounds: 4.) Declined: Polish, Codex round 4 P2 comment 4401220019: dispatch_records.py passes a follow-up dispatch record with no Package root line (observed: records implementation-3, -5 and -7 of this task sent three workers no package root, and each had to search for the scripts).
E. (synthetic task repeated-label-suggestion; External rounds: 4.) Declined: Polish, Codex round 4 P2: a reviewer suggests changing the caption "Review" to "Review notes" (the same suggestion was reported in external round 3 and repeated unchanged in external round 4; it is below P1 and assessed non-Material; no observed failure or harm exists, no user is affected, and the Captain has not asked for a task).
