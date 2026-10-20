---
title: pr_watch.py tasks round-3 follow-ups (frontmatter list form, stale reviewer flags)
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: done
verdict: REJECTED
completed: 2026-10-20T05:10:50Z
archived: 2026-10-20T05:10:50Z
---

Declined under the round-3 rule from the third Codex review round of iamcxa/kc-claude-plugins PR #643 (head 5b280387, review:5513822090), 2026-10-14, task `fo-lifecycle-mod`. Neither is P1 or Material, so neither started a repair cycle there; the same round's P1 is repaired in that task.

## Scope

- Codex P2 (`scripts/pr_watch.py`, frontmatter read): `extensions:` written as an indented YAML block sequence (`- codex`, `- learn`) is read as empty, so `tasks` silently skips the configured reviewers and the learn observer and archive path. Decline reason: every adopter workflow on this machine writes the flow form `[...]` (checked in docs/dev2, qnow, relay and ss-web READMEs), and the README template ships `extensions: []`.
- Codex P2 (`scripts/pr_watch.py`, `read_flags()`): a PR kept in the watch file keeps its stored `watch-codex` or `watch-copilot` flag after that extension is removed from the README, so `tasks` still runs its reader. Decline reason: no workflow has removed a listed reviewer; the effect is an extra read, not a missed one.
- Codex round 4 P2 (review:5514369233, head 5eb6bf05, `scripts/pr_watch.py` around line 271): a restart after `pr-merge` writes `pr: pr-merge:N` but before the `after pr-merge:` lines run leaves the archived task with no observer check or learn, since `tasks` scans only live task files. Decline reason: the design records it as a limit; candidate fix: recognize the sentinel or scan archived tasks with no learn job.
- Codex round 8 P2 (review:5519854860, head 3a3cfc30, `scripts/pr_watch.py` around line 148): a Copilot quota refusal (`not-run`) or a reader `error` prints `next: read the ... round` although no round or evidence id exists, and the reader's reason is discarded, so FO cannot write the required `copilot not run: <reason>` from the watcher output. Decline reason: FO still runs the reader at the gate, which prints the reason (`copilot_review.py`, `codex_review.py`); the watcher line only wakes FO.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Alignment: not needed before ideation; the findings and decline reasons above are the scope.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none

## Closed

Closed by the Captain 2026-10-20 (「照建議關掉 19 張。」) on FO's follow-up triage against origin/main ad44f0cb: block-list extensions unused by any adopter; the other items are design limits now caught by laws L1 or the gate reader.
