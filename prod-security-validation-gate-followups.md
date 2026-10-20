---
title: prod validation security review follow-ups declined at validation of #659 (fabricated empty report, standalone head binding)
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined by FO at validation-1 of prod-security-validation-gate (PR #659, head fce79ed7, 2026-10-17); reasons also in that task's gate summary.

- Deferred risk: `kc-dev-flow-2/scripts/validation_security.py` cannot tell a fabricated `findings: []` report from a real one. Decline reason: no prod task has merged with one; becomes Material if one is found.
- Deferred risk: a worker that skips the review meets the hold at the merge ask, not at the validation gate (D3, ruled by the Captain).
- Deferred risk: Opus and Fable under the Reach brief are one run each; no real refusal has occurred in 17 runs.
- Polish: `validation_security.py check` run on its own accepts a review at any dispatched head; only `delivery_gate.py` binds it to the PR head.
- Polish: a task with no readable `profile:` now holds the merge ask (exit 1) where the design said the check returns early; safer, recorded as a deviation.

## Closed

Closed by the Captain 2026-10-20 (「照建議關掉 19 張。」) on FO's follow-up triage against origin/main ad44f0cb: its deferred risks never fired; the worker-skip hold is enforced by delivery_gate.py calling validation_security.check_task.
