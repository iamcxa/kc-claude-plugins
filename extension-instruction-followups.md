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
