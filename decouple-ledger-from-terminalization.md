---
title: Decouple the measurement ledger from delivery terminalization
status: backlog
source: captain direction 2026-07-31 after EM merge-readiness closeout
product: repo-platform
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
ledger_pr:
pr_artifact_v1:
ledger_artifact_v1:
mod-block:
design:
lane:
id: 7rgdvsjypgmzk8wh03h3vst9
---

The current PR lifecycle makes a completed product change wait for a second ledger-only PR and an escaped-defect placeholder before the task can become done. Recover the existing measurement seams into a non-blocking feedback loop: task state remains the delivery authority, completion never waits for ledger maintenance, and process observations may later propose one narrow improvement task. Preserve existing ledger history and read compatibility. Do not add a daemon, automatic process mutation, or universally mandatory token/coverage metrics.
