---
title: FO asks the Captain to raise concurrency, with the reason, when work waits on the cap
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain at the batch-4 sitting, question 17 (2026-10-20): 「第三條應該改成，如果發現 concurrency 不足，應該主動要求提高並說明原因，然後要定義concurrency不足是怎樣的狀況。」 Recorded as fo-batch-sittings Amendment 3, replacing the interim rule "at most three concurrent workers".
- Bite: none measured yet. Measuring how often dispatchable work waited on the cap, per adopter, is the first ideation step; without a waiting case the task proposes closing.
- Shape asked for: a definition of insufficient concurrency, and an FO step that, when it holds, asks the Captain to raise the workflow's `concurrency:` with the reason (which tasks waited, how long, the machine load if read).
- Upstream first: Spacedock's own concurrency handling in `status --next` / `--boot` (whether it already reports work held by the cap), then kc-dev-flow-2 `pr_watch.py tasks` and the FO idle step.
- Non-goals: changing any adopter's `concurrency:` value without his word; machine-load management beyond reporting it.

## FO alignment

Alignment: needed at ideation; the definition of insufficient is his to accept.
Surfaces: none
Visible change: none
Outside this repository's surfaces: each adopter's workflow README `concurrency:` value.
