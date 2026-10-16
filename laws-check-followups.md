---
title: laws_check.py follow-ups declined at the #651 delivery gate (readme pass-through after #652, record edits, merge-only events)
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined or deferred at the validation gate of task `dev2-laws-check` (iamcxa/kc-claude-plugins PR #651, head 833b5c16), each with its reason in that gate summary.

## Scope

- Follow-up once #652 lands: pass `--readme` through to the dispatch-records folder check and widen the L2 line parser. Until then a clean push stays green with the extension check not run, and a folder-level violation becomes exit 2 `cannot judge` (still red; no violation turns green).
- Deferred risk (roborev High): a later edit of a dispatch record is not judged; 1 observed case in 11 record edits on the state branch.
- Deferred risk (roborev High): a violation that exists only in a merge commit is not judged; 0 merge commits in 1131 on the state branch.
- Polish: the PR body overstates when exit 2 happens once #652 lands; the concurrency test misses a quoted `"concurrency":` key.
