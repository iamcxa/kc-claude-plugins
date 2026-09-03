---
title: "intent.sh lock path breaks on a split-root state checkout (.git is a file)"
status: ideation
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: S9
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue: DEV-93
pr:
mod-block:
id: mw4wasfctgbd79ttr7trmk64
gates:
    version: 1
    records:
        - id: gate:mw4wasfctgbd79ttr7trmk64:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:mw4wasfctgbd79ttr7trmk64-backlog-1
              briefing:
                id: briefing:mw4wasfctgbd79ttr7trmk64:backlog:attempt-1:revision-1
                digest: sha256:cc8548a7672b8f2d1c9265ee4101451aec3fd678df57e52674759519615df5db
                room-ref: ./dev-93-intent-lock-path-split-root/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:mw4wasfctgbd79ttr7trmk64:backlog:1
                briefing: briefing:mw4wasfctgbd79ttr7trmk64:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-03T14:12:59.157098Z"
                decision: approve
                reason: FO admitted DEV-93 as the blocking fix inside the authorized batch's scope; Pilot; one cloud worker.
                conn:
                    quote: 那就按建議走2
                    source: Captain chat, this conversation, 2026-09-03 evening; the batch he authorized cannot dispatch without this fix
              application:
                target-stage: ideation
                state: consumed
---

## The problem

`scripts/ship-flow/intent.sh` (merged in #362, DEV-84) derives its process lock as `<state-dir>/.git/ship-lock.d` and acquires it with `mkdir`. In the repository's real split-root Spacedock checkout `docs/dev/.spacedock-state/.git` is a gitdir file, not a directory, so `mkdir` can never succeed; every `intent.sh commit` waits 150 x 0.2 s and dies with `lock timeout`. DEV-84's falsifiers all ran on plain `git clone`s of the state branch, where `.git` is a directory, so the bug was invisible. The first receipt-driven dispatch (batch 1016352e, DEV-90, 2026-09-03 14:09Z) failed closed at intent commit: no intent written, no workspace created, which is the correct failure shape, but ship-flow cannot dispatch at all from the real holder.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  route: [shape, build, verify-deliver]
  basis: One-path fix in two repo-local scripts plus a behavioural contract-test case; blocks the first real ship batch; no adopter-visible obligation.
  obligations:
    architecture: [Lock path from git rev-parse --git-dir; no change to lock semantics]
    implementation: [Edit scripts/ship-flow/intent.sh and holder.sh; add one contract-test case with a temporary worktree-style state]
    testing: [Negative run on the pre-fix script seen to exit 6 lock timeout; positive run on worktree and clone]
  scope_boundary: No change to intent order, fence, reconcile, README, or kc-dev-flow plugin files.
  semantics_unchanged: true
```

## Accepted outcome

`intent.sh` and `holder.sh` place the lock under the path `git -C <state-dir> rev-parse --git-dir` returns (a directory in both plain clones and worktrees), or beside the state directory; `intent.sh commit` succeeds on the repository's real split-root checkout; a contract-test case runs `intent.sh commit` against a temporary worktree-style state (`.git` as a file) and is seen to fail on the pre-fix script.

## Non-goals

- No change to the intent order, the fence, the reconcile rule, or the README paragraph.
- No change to lock semantics beyond the path; the mkdir/rename/age rules stay.
- No Linear write.

## Acceptance evidence

- **AC-1** `intent.sh commit` on a `git worktree`-style state checkout (`.git` is a file) succeeds and leaves no lock residue; the same call on the pre-fix script exits 6 with `lock timeout`; both runs recorded with `SHIP_LOCK_STALE_S=3` and a 5-iteration wait so the negative run finishes in seconds.
- **AC-2** `intent.sh commit` on a plain clone still succeeds (regression); recorded.
- **AC-3** The contract test gains one behavioural case for AC-1 against a temporary worktree state and reddens on the pre-fix script; recorded.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta.

## Measurement

Not yet measured.
