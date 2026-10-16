---
title: dispatch_records.py --newest follow-ups declined at the #649 delivery gate
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined at the validation gate of task `names-check-before-dispatch` (iamcxa/kc-claude-plugins PR #649, head a4217cd3), each with its reason in that gate summary.

## Scope

- Deferred risk: when one state commit adds several dispatch records of one task, `--newest` picks the lexicographically last file, so `implementation-9` beats `implementation-10` (validator probe, exit 1 naming -9). History: 3 of 150 record-adding commits added several records for one task. Becomes Material if FO saves two records of one task in one commit with the older one sorting last.
- Polish: the `next:` line does not say a flagged name may be a repository file (a `test_*.py` the task edits) rather than a package script, and it repeats on each idle pass until the task's next record.
