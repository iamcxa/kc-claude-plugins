---
title: A follow-up dispatch to a reused worker leaves a dispatch record before it is sent
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「照建議」 (chat, 2026-10-27), answering FO's batch-7 retrospective list (items a to d).
- Bite: kc-ops-inbox task ops-metric-event-protocol (PR #727, two rejected validation cycles; its observer report at state commit f25c224f6, relayed by its FO 2026-10-27): no dispatch records for the implementation or validation dispatches sent to reused workers, and the misses that followed (no delivery_gate question before validation briefings 1 and 2, no Override line, polish items left out of FO declines) all sat on that path, where no `dispatch build --stamp` runs and nothing prompts the record. The README already says a follow-up message to a worker FO resumes is a dispatch.
- Upstream first: the README's Stages (follow-up dispatch rule), `scripts/dispatch_records.py`, `scripts/pr_watch.py tasks`, Spacedock `dispatch build`.

## FO alignment

Alignment: needed before ideation; where the check or rule lives is a package design choice.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
