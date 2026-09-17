# backlog gate — learning-serialize-evaluation

FO admission record. This boundary has no worker report by workflow design.

## Variant and profile

- `variant: kc-dev-flow-2`
- `profile:` unset, pending the Captain's selection. Recommended: **pilot**.

The recorder is days old (#461, #462), has one local adopter (this repository), and
the change is expected to be revised when cross-clone learning is taken up. That is a
bounded first use with likely iteration, not an operated capability.

## Verified inputs

- `learning.py` on `main` (`32cd8890`): the `claim` branch refuses changed evidence
  for an existing job; `recover` refuses completed jobs; `job_key` derives from
  workflow and task id only.
- `learn/SKILL.md` § Prepare a changed proposal states that drift and conflicting
  concurrent proposals require review.
- Both existing jobs in this clone's learning store have delivery state `merged`, so
  the hold blocks nothing on arrival.

## Evidence needed before ideation starts

1. The Captain's selected profile recorded on the task.
2. The approved outcome, scope, non-goals and stop condition above.
3. No UI is involved, so no FO design-alignment preview is required.
