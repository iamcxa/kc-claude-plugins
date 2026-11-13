# Pilot ideation

Define the smallest useful end-to-end slice, who will use it, its real seams,
acceptance evidence and explicit non-goals. Identify any new obligation that
would require a profile change; leave that decision with the user.

## Probe

Build the probe as the first paragraph of [POC implementation](../../implementation/profiles/poc.md)
builds a proof: falsify the riskiest assumption first; when it holds, widen toward the
slice and check the next. Work in `.worktrees/poc-<slug>` from the trunk. Under `Probe:`
in the design, record the branch, base and last commit and each hypothesis with its
result; remove the worktree before reporting and keep the branch.

## Data kept across screens or sign-in

When a `ui` design keeps something a person typed or chose while they move between
screens or through sign-in, add `### Kept data` to the design. For each item, state
where it starts; every way it ends: sent, abandoned by back or another tab, replaced
by a newer choice, a different person or session, a reload; and every writer,
including a reply that lands after the person has moved on, and what that reply may
still change. Give each end and each late writer an acceptance criterion.
