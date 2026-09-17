---
id:
title: serialize learning evaluation while another learning job is in flight
status: backlog
variant: kc-dev-flow-2
profile: pilot
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:learning-serialize-evaluation:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:learning-serialize-evaluation-backlog-1
              briefing:
                id: briefing:learning-serialize-evaluation:backlog:attempt-1:revision-1
                digest: sha256:aaa127818701563086ee037152e348e01ea2fd87b8527128c67be950df131025
                room-ref: ./learning-serialize-evaluation/review/backlog/briefing-1
---

Two closed tasks were evaluated for learning while neither learning PR had merged.
Both evaluations pinned the same root `learning.md` basis. The first PR (#469)
landed and moved that basis; the second proposal (#470) was then an add/add conflict
judged against a file that no longer existed. `kc-dev-flow-2/skills/learn/SKILL.md`
already says "Drift, conflicting concurrent proposals or an already-applied change
requires review", but `kc-dev-flow-2/scripts/learning.py` offers that review no
operation: `claim` refuses changed evidence ("existing task evidence differs; no
automatic re-evaluation") and `recover` refuses completed jobs ("completed results
are immutable"). The re-evaluation ran outside the recorder and its delivery record
still names candidate `638b82a2` while the merged head was `112f66ed`.

Source: Captain ruling 2026-09-17 in the FO session — option 1, serialize learning
evaluation, chosen over adding a re-evaluation operation.

## Scope

In scope: `kc-dev-flow-2/scripts/learning.py`, `kc-dev-flow-2/scripts/test_learning.py`,
and the learn skill / README wording that describes when a claim holds.

`claim` for a new job holds while another job in the same local learning store is
still in flight: its evaluation is pending, or it completed with a proposal whose
delivery is not settled. A job the Captain declines to deliver needs an explicit,
recorded release so it cannot block later jobs indefinitely.

Non-goals: no re-evaluation or supersede operation; no change to `job_key`, to
completed-record immutability, or to delivery identity rules; no coordination across
clones or machines (the README already lists cross-clone deduplication as future
work); no handling of `learning.md` drift that does not come from another learning
job.

Stop condition: if the hold cannot be expressed without changing completed-record
immutability or delivery identity rules, stop and return the design to the Captain.

## Acceptance criteria

**AC-1**: A new job's `claim` is refused, with no directory or record created for it,
while another job is in flight; the refusal names the blocking job and its state.
Verified by: `python3 kc-dev-flow-2/scripts/test_learning.py` cases for each in-flight
state (pending; completed with proposal and delivery missing, uncertain or open),
each shown to fail when the hold is removed.

**AC-2**: A job stops blocking once its evaluation completed with no proposal, its
delivery is merged or closed, or it carries the explicit release record.
Verified by: `test_learning.py` cases for each releasing state, each followed by a
successful claim of another job.

**AC-3**: The release is explicit and recorded: it requires a reason, refuses a job
whose delivery is open or merged, and cannot be undone through the CLI.
Verified by: `test_learning.py` cases for each refusal.

**AC-4**: Re-claiming the same job with identical evidence still returns its existing
view, and every existing `test_learning.py` case still passes.
Verified by: the full `test_learning.py` run on the candidate revision.
