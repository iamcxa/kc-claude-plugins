---
title: worker-loads-declared-package follow-ups declined at validation of #661 (old-README FO behaviour, laws.md wording)
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined by FO at the #661 delivery gate (head 7d169549, 2026-10-17); reasons also in that task's gate summary.

- Deferred risk: whether an FO on a README older than 0.23.0 acts on a printed `--names` line that is not a script name (the 0.22.1 README says it "rewrites each name it lists"). Unmeasured; an FO-only step cannot be replayed. Material if an old-README FO is seen ignoring the line and holding at the merge ask.
- Deferred risk: a laws workflow pinned to a tag with this change, over a README still at 0.22.1, reports an L2 violation once per pushed Candidate-less validation record. Not seen on any adopter; no adopter runs the laws workflow yet.
- Polish: `kc-dev-flow-2/references/sd/laws.md` L2 Rule ("every part dispatch_records.py requires") covers the Candidate line without naming it; the L2 violation text for it ends "(line 1)"; the new test name says "exactly" and the maintain-flow sentence says "only" (bounded by the parity test).
- Observed (FO, 2026-10-19, kc-dev-flow-2 0.25.0): `dispatch_records.py --names` requires a 40-hex Candidate line on every validation record, including a POC validation that has no code candidate (merge-grant-need-poc); FO bound it to the state commit holding the results. The POC route needs a stated form for that case.
