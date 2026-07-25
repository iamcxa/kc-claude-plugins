---
title: Prove Step 5.6 cross-model arbitration end-to-end
status: backlog
source: follow-up to PR #58 (agy migration) — the path is wired but has never been observed producing a verdict, 2026-07-25
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: qcpq726mh76gqxdjcfmcxjn5
---

PR #58 restored Step 5.6 arbitration to a working binary (`agy`), and the gate, resolver, and auth signals are unit-tested. What has **not** been observed is the whole path running: a real `kc-pr-review --codex` where Claude and Codex actually disagree, producing `ARB <id> <verdict>` lines that `cross_model_arb_parse` accepts and that move confidence through the §6a gate.

This matters because the failure this fixes was silent. Every intermediate state — unavailable arbiter, empty agy output, unparseable output, all ids rejected — collapses to the same downstream text ("disputes surfaced unresolved") and the same unchanged confidence. Unit tests cover the gate; they cannot distinguish "arbitrated and agreed" from "never arbitrated".

Note the three agy failure modes that each return empty output rather than an error: prompt piped instead of passed as the `--print` value, `--print-timeout` (default 5m) elapsed, and an agentic tool request with no TTY to approve it.

## Acceptance criteria

**AC-1 — A real review with a genuine Claude/Codex dispute produces at least one parsed `ARB` verdict, and the §6b-cm table shows a Gemini verdict rather than "unavailable" or "unresolved".**
Verified by: the captured arbiter stdout plus the §6b-cm table from that run, showing dispute ids that match the emitted `KNOWN_IDS_CSV`. Falsified by: an empty or unparseable arbiter response, or every id rejected by the parser.

**AC-2 — The unavailable path is still distinguishable from the arbitrated path in the review output.**
Verified by: running the same review with the arbiter forced unavailable (e.g. `CROSS_MODEL_GEMINI_BIN=/nonexistent`) and confirming the report says arbitration was skipped, not that there were no disputes. Falsified by: the two runs producing indistinguishable review text.
