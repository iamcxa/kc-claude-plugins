## FO steps: review findings

Apply this checkpoint to findings from implementation, validation, detached audits,
consequential FO quick work and rejected gates.

1. Reviewers observe; workers' classifications and `actor:ensign` Resolutions are
   advisory. Preserve findings and assess the four evidence fields above, separating
   materiality, ownership and disposition. Missing required evidence or unresolved
   classification requires investigation or hold.
2. Within approved boundaries, FO may explicitly decline evidenced Deferred risk or
   Polish in the existing committed gate summary, naming the finding, reason, candidate
   revision and the lines or evidence it rests on. When that summary is already
   consumed, FO writes the decline under `### FO declines` in the task file, committed
   with `spacedock state commit <slug> --workflow-dir <dir>`, and the terminal gate
   lists each entry there. This FO-authored decision requires no live worker or reviewer
   rerun for acknowledgement; preserve worker reports and verdicts.
3. Repairs require worker investigation without candidate mutation, distinct FO
   `fix` authorization through the runtime's addressable-worker boundary, then
   independent validation. Without that authorization, hold.
4. Scope, value, threshold, tolerance, risk-acceptance and acceptance-criteria
   changes require the Captain. Material findings cannot use the record-only lane;
   hold/route-for-decision forbids repair and reviewer rerun.
5. A round is one verdict of an external reviewer of the delivery on the PR head (Codex
   on the PR, RoboRev or another); FO counts rounds and records the count in the
   committed gate summary. A reviewer that a listed extension covers is read the way its
   `EXTENSION.md` says (`## Extensions`). A finding assessed Material, or labelled P1 by
   the reviewer, blocks in every round: a reviewer P1 is fixed and revalidated, or
   waived by the Captain with the reason recorded (step 4). For an external reviewer
   that has no P1 label, its highest severity level counts as P1 (e.g. RoboRev). Rounds
   1 and 2 follow steps 1 to 4. From round 3 a finding that is neither does not start a
   repair cycle: FO declines it in the committed gate summary, naming the finding, and
   files it as a new backlog task with `spacedock new` whose body carries the finding
   and the decline reason, or names the backlog task that already holds it when a later
   round repeats it; it never enters an open task's Scope. The terminal gate lists each
   such task.

Rejection routing carries evidence, classifications, authorized dispositions and assignment
without re-triage.

Materiality and ownership are independent. Owned Material is eligible for an
FO-authorized fix; out-of-scope Material holds as Needs decision. Deferred risk
or Polish may use the recorded FO decline above within existing risk acceptance.

A Needs decision put to the Captain at a gate carries FO's recommendation. His
plain approval accepts that recommendation only when the gate question says so,
for example "approving accepts the recommendation for D2; say if you object".
Without that sentence a decision he did not address stays open: FO records its
handling as FO's reading, never as his ruling, and asks him.

A decision an accepted ADR already settles is not asked again: FO applies it and states it
in the gate summary as `Precedent: ADR <number> — 「<that ADR's Words line>」`, and the
Captain may reopen it. An ADR with no Words line is quoted by the decision sentence it
applies, as `Precedent: ADR <number> (no Words line) — 「<that sentence>」`. Authority, a gate approval, a merge, an outward-facing action, an
irreversible change and money are always asked, whatever an ADR says, and an ADR on one
of them is never a `Precedent:` line.

A Captain ruling is his reply to the question it settles, given after that question
was put. FO never records as his ruling: silence on a decision the question did not
state approval accepts, consent he gave earlier to a different question, or a choice
he raised but did not make. FO answers a question the Captain asks at a gate before
dispatching on it, and returns a choice he raised to him rather than to a worker.

When the Captain chooses differently from the recommendation, FO writes
`Override: recommended <option>; Captain chose <option>; area: <area>` in the gate
resolution reason, so later workers find past rulings with `git grep 'Override:'` in
the state checkout.

