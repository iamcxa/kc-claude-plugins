## Captain amendments

A change the Captain makes to what he has accepted, whether at a gate approval,
during implementation or at a validation gate, is an amendment. A change he asks for
while the gate that would accept it is still open is not one: he calls `revise`; at a stage
with no `feedback-to` that dispatches a worker, that stage's worker reworks it; at a stage
whose gate has a `feedback-to`, the revision goes to that target and the stage's worker
re-reviews it; and at `backlog`, which dispatches no worker, FO revises the recorded outcome,
scope or budget, or asks the proposal's author to.

FO appends one entry per amendment to the task's `## Captain amendments` section and
changes nothing else in it. FO adds no words of its own and does not move or rewrite a criterion:

```
## Captain amendments

### Amendment 1 — <date>, <gate or chat>
Captain: 「<his words, verbatim>」 (where he said them)
Asked: <the question or proposal he answered, verbatim, or the commit holding it>
Supersedes: <acceptance-criterion ids, or none> <optional: "(no replacement: <why>)">
Design: <optional: the design paragraph it overrides>
```

`Asked:` is required when his words do not name what they settle, such as 「同意第三點」. FO
names the amendment in the next dispatch's checklist. That worker (implementation, the
repair worker on a feedback route, or the worker of the stage a task is sent back to)
moves each superseded criterion's block verbatim from `## Acceptance criteria` into its
entry under a `Superseded text:` line, writes any replacement as a new `**AC-N**` under
a fresh id that says "Amended by Captain, amendment N", and never reuses an id. A
superseded criterion and the design paragraph named by `Design:` are withdrawn; evidence
and the Captain's acceptance script follow `## Acceptance criteria` plus the entries.

Sending an approved task back to an earlier stage, such as a design redo a release
review asks for, is the Captain's decision and is recorded as an amendment whose
`Design:` names what is redone; FO then runs `spacedock status --workflow-dir <dir>
--set <slug> status=<stage>`, and that stage's gate is approved again before the task
moves on.

`python3 <package>/scripts/design_surfaces.py check <task>`, run by implementation and
validation, exits 1 for an entry with no `Captain:` line, an unnamed moved criterion,
superseded ids no criterion marks "Amended by Captain, amendment N", or a superseded
id still declared; repair findings return through feedback. It cannot see a skipped record or
move, or FO's words in `Design:`.

