---
title: delivery_gate.py Candidate-line follow-ups declined at the #647 delivery gate
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: done
verdict: REJECTED
completed: 2026-10-20T05:10:57Z
archived: 2026-10-20T05:10:57Z
---

Declined under the round-3 rule at the validation gate of task `delivery-gate-verdict-form` (iamcxa/kc-claude-plugins PR #647, head aa6fcc91, Codex round 4 clean at comment:6187737631). Validation cycle 4 recorded these five findings, none Material; per `## FO steps: review findings` step 5 none starts a repair cycle there, and each is filed here with its decline reason.

## Scope

- F1 Deferred risk: a `Candidate:` line inside a code fence above the first `## ` heading of a validation dispatch record is accepted (validator probe, exit 0). Decline reason: the record header is FO-written and no record quotes an example line there; it becomes Material if a header quotes a `Candidate:` example and a merge ask passes on it.
- F2 Polish: a record line with upper-case hex holds (exit 2) while `--head` is lower-cased. Decline reason: fail-closed, and `git rev-parse` prints lower case.
- F3 Polish: the cycle 5 implementation report does not restate `updated` or `unaffected` for the two documents `doc_impact.py` lists (`kc-dev-flow-2/README.md`, `references/sd/adoption.md`). Decline reason: the cycle 1 report carries both and the reason still holds at aa6fcc91.
- F4 Polish: the exit 0 line prints the head as given (a prefix) where the record has 40 characters, and the exit 1 line for a validated-but-unpushed repair does not name pushing as a remedy. Decline reason: wording only; the exit codes are right.
- F5 Polish: the `dispatch-record` swaps entry in `scripts/test_sd_dispatch.py` deletes the whole passage, so it is not specific to the `Candidate:` clause. Decline reason: the validator's direct removal of the clause fails the entry, so the pin holds.

## Closed

Closed by the Captain 2026-10-20 (「照建議關掉 19 張。」) on FO's follow-up triage against origin/main ad44f0cb: each item fails closed or sits in archived text; triggers never fired.
