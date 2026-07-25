---
title: Reviewer agent returns have a prose convention, not a contract the orchestrator can reject
status: backlog
source: agent-native audit of the kc-pr-review kit, 2026-07-26 — third gap, deliberately not in this sprint
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: q0qddpj2pt1wm3e7bnnqv8sj
---

Step 4 dispatches five to seven reviewer agents whose findings come back in a prose
convention: `[SEVERITY] (confidence: N/10) file:line — description`
(`reference/review-triage.md:207`). Step 5.5's cross-model reconciliation does run
deterministically — `scripts/cross-model.sh` is all awk over TSV — but the model produces that
TSV by reading its own prose. The contract boundary sits inside the model, so the orchestrator
cannot reject a malformed return; it can only best-effort interpret one, and a finding that
fails to parse disappears without a trace.

`e2e-pipeline` has already filed the identical class as `e2e-agent-return-contracts` (ey).
This is that entity's kc-pr-flow counterpart.

It is also the missing precondition for `review-citation-verifier` (dk): mechanically checking
a `file:line` citation requires a structured citation to check. Today dk would have to parse
prose first, which is the same problem one layer down.

Not scheduled into the 2026-07-26 sprint on purpose — it touches how findings and coverage are
represented, which is exactly what `prescan-coverage-honesty` is settling. It should be cut
after that lands, so it inherits one representation instead of inventing a second.

**AC-1 — A reviewer return that does not satisfy the contract is reported as unparsed, not silently dropped.**
Verified by: a fixture round mixing well-formed and malformed findings; the malformed ones
appear in a rejection list with a count that reconciles against the agent's claimed finding
count. Falsified by: a malformed finding vanishing, or a count that does not reconcile.
