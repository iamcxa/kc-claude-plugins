---
id: geef7a3dy7w12g7tq89h21te
title: "Work whose output is knowledge cannot terminalize: pr-merge requires a merged PR that such work never has"
status: backlog
source: "Blocked while closing digest-effect-unmeasured, 2026-08-20. That task's accepted output was a measurement verdict, not a diff. It has no PR and no worktree, and the mechanism refused its terminal transition: 'workflow has merge hook(s) [pr-merge] that have not run (pr field is empty and mod-block is empty)'."
product: repo-platform
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
---

## Problem

Two statements in this workflow's own configuration contradict each other, and the runtime
implements the stricter one.

`docs/dev/README.md:69` scopes the hook conditionally:

> PR lifecycle | Spacedock `pr-merge`, **only when a PR is the selected delivery artifact**.

`docs/dev/_mods/pr-merge.md:342` scopes terminalization absolutely:

> The workflow's terminal `done` state **requires an authenticated merged product PR**, which
> those failure paths cannot provide.

and again at `:346`, instructing the agent to refuse to "claim or write terminal success"
without one. The `spacedock` binary implements the second reading: it refused
`--set digest-effect-unmeasured status=done` with `pr field is empty and mod-block is empty`.

So an entity whose accepted outcome is **knowledge rather than a diff** has no terminal path.
Concretely: a measurement that returns a verdict, a reverse-recovery audit, a keep-or-retire
decision, a spike that answers a question and produces no code. Each of these can be shaped,
worked, and finished, and then cannot be closed.

This is not hypothetical. `digest-effect-unmeasured` did exactly its job — its Step 0 kill
switch fired, it returned "no headroom, do not ship", and it saved the 480-run budget its own
plan had estimated. It is sitting at `backlog` because the correct answer produced no PR.

### What the workarounds cost

- `--force` bypasses a guard whose refusal message says a refusal "usually means a ceremony
  step was skipped". Using it here trains the habit of forcing past a guard that is usually
  right, to work around a case it does not model.
- Attaching an unrelated PR to make the field non-empty makes the tracker lie about what
  delivered the outcome.
- Leaving it open forever means the backlog stops distinguishing "not started" from "answered".

## Reproduced, 2026-08-20 — two separate defects

Run against `digest-effect-unmeasured` (status `backlog`, no `pr`, no worktree). Both were
discriminated by experiment, not inferred.

### 1. Every exit is gated, not just the terminal one

`--archive` is refused by the same guard as a terminal `--set`:

```
entity digest-effect-unmeasured cannot be archived — workflow has merge hook(s)
[pr-merge] that have not run (pr field is empty and mod-block is empty).
```

So archive is not the escape hatch for answered-without-delivery work. There is no non-forced
exit from the active set for an entity with no PR.

### 2. `merge guard` clears the precondition it then requires

The ceremony verb livelocks. Observed sequence:

1. `merge guard <slug> --verdict passed` prints `armed: mod-block set to merge:pr-merge` and
   **writes nothing** — the entity file is unmodified, `git status` clean.
2. Re-running it fails with `mod-block is empty`.
3. Setting the field by hand works: `--set <slug> mod-block=merge:pr-merge` writes
   `mod-block: merge:pr-merge`. So the field is writable and the value is accepted.
4. Running `merge guard` again with the block genuinely armed still reports `mod-block is
   empty` — **and clears the field**.

The verb's own help documents the shape of the bug: "the mod-block is cleared in its own step
first, then application, terminal status, verdict, and completed move in ONE locked write."
The clear is outside the locked write, so a failing terminal step leaves the entity stripped of
the precondition rather than rolled back. Each invocation therefore destroys the state the next
invocation demands.

This is independent of defect 1: it would strand a PR-delivered entity too, any time the
terminal write fails after the clear commits. Fixing the knowledge-output gap does not fix it.

### Where this points

Defect 2 is in the `spacedock` binary, not in the vendored `pr-merge.md` prose — the mod is
never reached. That answers the shape stage's first open question for defect 2 and narrows
defect 1's candidates to the binary's guard versus the mod's absolute claim at
`pr-merge.md:342`.

## Work profile receipt

## Accepted outcome and non-goals

A knowledge-output entity can reach `done` through a declared, non-forced path, and the
workflow's two statements about `pr-merge`'s scope agree with each other and with the runtime.

Open questions the shape stage owns:

1. **Where the defect is.** Three candidates, and the answer decides who owns the fix:
   the vendored `pr-merge.md` overreaches (it should gate PR-delivered entities, not all
   terminalization); or the `spacedock` binary's guard is broader than the mod it enforces;
   or `README.md:69`'s conditional scoping is the inaccurate line and terminalization
   genuinely should require a PR. Read the binary's guard before assuming the mod is wrong.
2. **What authenticates a knowledge outcome**, if not a merged PR. The candidate already
   present in this workflow is the entity's own recorded evidence plus a Captain gate — the
   same authority that admits the work. Whatever is chosen has to be as hard to fake as a
   merged PR, or the guard has been weakened rather than scoped.
3. **Whether the fix belongs upstream.** `pr-merge` is vendored from Spacedock. A local edit
   fixes this repository and drifts from source; an upstream change fixes every adopter and
   waits on someone else's release. This is the same keep-local-or-send-upstream question the
   retired improvement transport existed to answer, and it no longer has a mechanism.

Non-goals: changing how PR-delivered entities terminalize, weakening the merged-PR requirement
where a PR *is* the delivery artifact, and relaxing the guard by making `--force` routine.

## Acceptance evidence

A knowledge-output entity terminalizes without `--force`, and a PR-delivered entity still
cannot terminalize on an unmerged or absent PR. Both proven by attempting each, not by reading
the configuration. The two contradicting statements now say the same thing, and something
fails if they diverge again.

## Measurement

Entities stuck non-terminal with an accepted outcome and no delivery artifact. Currently at
least one (`digest-effect-unmeasured`).
