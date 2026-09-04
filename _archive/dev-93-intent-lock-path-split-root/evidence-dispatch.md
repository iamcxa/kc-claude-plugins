You are a kc-dev-flow worker in a disposable cloud workspace running a Pilot item from shape through build. Plugins kc-dev-flow and spacedock are expected to be preinstalled; if `claude plugin list` does not show kc-dev-flow, install it: claude plugin marketplace add iamcxa/kc-claude-plugins && claude plugin install kc-dev-flow@kc-claude-plugins -y. Do not ask questions; if blocked, stop and report the blocker in the Evidence block. Confirmations from the First Officer who authored this file (the DISPATCH_TOKEN in the go message is the proof): the carrier branch is mine; do not install third-party marketplaces; push the named branch without opening a PR.

## Step 1 — work item and Brief (standalone Pilot; no Linear access needed)

Write this byte-for-byte to `.context/DEV-93-work-item.md` (create `.context/`; gitignored):

```markdown
---
title: "intent.sh lock path breaks on a split-root state checkout (.git is a file)"
status: implementation
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
```

The Brief (Linear Issue DEV-93):

```markdown
## The problem

`scripts/ship-flow/intent.sh` (merged in #362, DEV-84) derives its process lock as `<state-dir>/.git/ship-lock.d` and acquires it with `mkdir`. In the repository's real split-root Spacedock checkout `docs/dev/.spacedock-state/.git` is a gitdir file, not a directory, so `mkdir` can never succeed; every `intent.sh commit` waits 150 x 0.2 s and dies with `lock timeout`. DEV-84's falsifiers all ran on plain `git clone`s of the state branch, where `.git` is a directory, so the bug was invisible. The first receipt-driven dispatch (batch 1016352e, DEV-90, 2026-09-03 14:09Z) failed closed at intent commit: no intent written, no workspace created, which is the correct failure shape, but ship-flow cannot dispatch at all from the real holder.

## Goal

`intent.sh` and `holder.sh` place the lock under the path `git -C <state-dir> rev-parse --git-dir` returns (a directory in both plain clones and worktrees), or beside the state directory; `intent.sh commit` succeeds on the repository's real split-root checkout; a contract-test case runs `intent.sh commit` against a temporary worktree-style state (`.git` as a file) and is seen to fail on the pre-fix script.

## Non-goals

- No change to the intent order, the fence, the reconcile rule, or the README paragraph.
- No change to lock semantics beyond the path; the mkdir/rename/age rules stay.
- No Linear write.

## Acceptance criteria

- **AC-1** `intent.sh commit` on a `git worktree`-style state checkout (`.git` is a file) succeeds and leaves no lock residue; the same call on the pre-fix script exits 6 with `lock timeout`; both runs recorded with `SHIP_LOCK_STALE_S=3` and a 5-iteration wait so the negative run finishes in seconds.
- **AC-2** `intent.sh commit` on a plain clone still succeeds (regression); recorded.
- **AC-3** The contract test gains one behavioural case for AC-1 against a temporary worktree state and reddens on the pre-fix script; recorded.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta.
```

## Step 2 — shape, then build

Run: python3 kc-dev-flow/scripts/profile-contract-loader.py --work-item .context/DEV-93-work-item.md --local-profile docs/dev/README.md --format text
Follow shared core, Pilot base, shape; append `## Shape` to the work-item file; set `status:` to `implementation`, rerun the loader, follow build. Standalone item.

## Step 3 — implement

- git fetch origin main && git checkout -b feature/dev-93-intentsh-lock-path-breaks-on-a-split-root-state-checkout-git d98f40b5e2080cb884facf1734fc66052eff9982
- In scripts/ship-flow/intent.sh (and holder.sh if it references `.git` too), replace `"$state/.git/ship-lock.d"` with a path under `$(git -C "$state" rev-parse --git-dir)` (which is a directory in both plain clones and `git worktree` checkouts). Keep every other lock rule (mkdir acquire, trap-before-acquire, owner marker, age-only stale, rename-not-delete takeover).
- Falsifier AC-1: in a temp dir, `git init` a bare origin with a `spacedock-state/dev` branch holding `_holder.json` = {"writer":1,"holder":"laptop","at":"x"}; `git clone` it to `main-clone`; from `main-clone` run `git worktree add ../state-wt spacedock-state/dev` so `../state-wt/.git` is a FILE. Run the PRE-FIX intent.sh (`git show origin/main:scripts/ship-flow/intent.sh > /tmp/intent-prefix.sh`) with `SHIP_LOCK_STALE_S=3` against `../state-wt`: it must exit 6 `lock timeout` (cap the wait: if the script has a 150-iteration loop, export a smaller cap if it supports one, otherwise just let it run the ~30 s). Then run your fixed intent.sh on the same worktree state: exit 0, `_intents/<claim>.json` committed, no `ship-lock.d` residue anywhere under the git dir. Record both.
- AC-2: the fixed script on the plain `main-clone` (checked out to spacedock-state/dev) also succeeds; recorded.
- AC-3: add one case to scripts/kc-dev-flow-contract-test.py that builds that worktree-style state in a tempdir and asserts the fixed intent.sh exits 0 there; run the case against the pre-fix script once and record that it reddens.
- python3 scripts/kc-dev-flow-contract-test.py takes 3-4 minutes; run in the background and poll, never with sleep. Record exit.
- One Conventional Commit `fix(kc-dev-flow):`. Push the branch only. Do NOT open a PR. Do NOT write to Linear.

## Step 4 — push

git push origin HEAD:refs/heads/feature/dev-93-intentsh-lock-path-breaks-on-a-split-root-state-checkout-git

## Step 5 — final reply: exactly one fenced block, no prose before or after, under 8000 characters

```
## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: <40-hex>
BRANCH: feature/dev-93-intentsh-lock-path-breaks-on-a-split-root-state-checkout-git
BASE_SHA: d98f40b5e2080cb884facf1734fc66052eff9982
FILES: <comma-separated changed files>
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit <code>
SURFACE: <one line per changed non-test file: path -> AC-N | one-line without-it command naming that path | one git command that removes the change>
WITHOUT_IT_COMMAND: <ONE self-contained shell line exiting 0 on this candidate and non-zero after WITHOUT_IT_REMOVED_VARIANT>
WITHOUT_IT_REMOVED_VARIANT: <one git command>
WITHOUT_IT_OBSERVED: retained -> exit <code>; removed -> exit <code>
ROBOREV: UNAVAILABLE(reason: no reviewer binary in workspace)
AC-1: <pre-fix exit on worktree state; fixed exit on worktree state; residue check>
AC-2: <fixed exit on plain clone>
AC-3: <contract-test case name; reddened on pre-fix: exit>
BLOCKER: none | <what stopped you and at which step>
```
