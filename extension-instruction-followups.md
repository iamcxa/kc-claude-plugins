---
title: dispatch_records.py extension-instruction check follow-ups declined at the #652 delivery gate
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined at the validation gate of task `extension-instruction-reaches-dispatch` (iamcxa/kc-claude-plugins PR #652, head 8d051de7), each with its reason in that gate summary.

## Scope

- Deferred risk: the follower allowlist refuses a real script path followed by `:` or `**` (fails closed; no real record ends that way).
- Deferred risk: an `extensions:` list written as a YAML block is read as empty, so the check skips; `<name> not run:` also matches inside prose.
- Polish: the unused `Misconfigured` import and a one-element loop in `dispatch_records.py`.
- Codex round 4 P2 (review:5555483675, #652 ef7a360e), declined under the round-3 rule: `dispatch_records.py` reads `extensions:` only inline, so a YAML block list reads as none while `laws_check.py` reads block lists. Decline reason: no README on this machine uses a block list (docs/dev2 and the workflow template are inline); fix is to share one parser.
- Codex round 4 P2 (same review), declined under the round-3 rule: the package root for the instruction check is the first `Package root:` anywhere in the record, not the one in Scope notes. Decline reason: every record FO writes carries one `Package root:` line, in Scope notes (dispatch_records.py's own PARTS check); a record with two roots is not observed.
- Deferred risk (validation cycle 5): L2 judges against the README supplied at run time, so a record written before an extension was listed, or a re-run of an old push, is judged against the newer list.
- Polish (validation cycle 5): PR body counts (dropping --readme fails 10 tests, not 7; "affects later pushes only" is not true for re-runs); laws.md L2 "Judged by" omits `--readme`.
