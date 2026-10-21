# chief-engineer-1

Reviewer: kc-dev-flow-2:chief-engineer, opus, 2026-10-20. Read-only. State HEAD fe2d90ff.

Recommendation: adjust. Narrow rule 4 to the parts that touch what actually went wrong, take the `Merges:` line machinery out of this task, and send D1, D3, D4, D5, D6 and D7 to the ideation gate now. Do not run a third engineering-reviewer read on D2.

Why. The merge half has needed new conditions on each of the two reads. It guards task-PR merges, and no wrong task-PR merge is on record. The one merge that went wrong (Release PR #672) has no task, so the `Merges:` line can never reach it. Two more fixes (the digest check and the repair-under-grant question) would add surface and add asks to the Captain, which works against his goal of fewer questions.

```yaml
chief_engineer_advice:
  outcome: "The four FO-write rules of #684 are checked by the script FO already runs at the write. Rules 1-3 (D1, D4, D5) are settled and measured. Rule 4 is the drifting half."
  next_step: "Cycle 3 of ideation is a narrowing, not a new fold. Rule 4 in this task becomes: (a) the named-carry sentence ('Every other PR, the Release PR included, is asked one at a time') appended to the existing 0.26.0 ASK line; (b) D3's '(verdict ask)' tag on the class line. Remove the Merges: grammar, head binding, approved() Captain-only read, 「」 echo, no-quote guard, teaching clause and amended_after from this task. Record them as the deferred design of the D7 task, or as a reopen condition. Rewrite D2 in the gate question as that scope choice. Trim AC-1, AC-2, AC-8, AC-10, AC-11 and AC-13 to match. Then prepare the ideation gate with D1-D7."
  material_risk: "D7 is unproven. The second read's disproof condition is open: a PreToolUse hook returning 'ask' may not prompt under auto mode, which would force a 'deny' route. If D7 fails that, the #672 shape is guarded only by a sentence FO reads, which is not enforced. Present D7 as the route to enforcement, not as a safe swap."
  decision_needed: "Captain, at the ideation gate: accept narrowing rule 4 to the named-carry sentence plus the verdict tag, with the Merges: line deferred and #672's shape routed to the D7 guard task? This changes the scope he approved at backlog (#684 rule 4), so it is his ruling and goes in as an amendment if he says yes."
  defer:
    - "Merges: line grammar, head binding and the digest check (round-2 finding i)"
    - "The repair-under-grant reversal question (round-2 finding ii). It disappears with head binding."
    - "The 「」 echo and no-quote guard (spans are FO's transcription, per round 2)"
    - "Live item 1 of fo-write-checks-followups (the carried line does not read the approved question). Stays open with its reason."
    - "A third engineering-reviewer read on D2"
  recommendation: adjust
```

What gets worse under this:

- Until D7 lands, the 0.26.0 line still says "merge if the approved question named the merge", which FO matches from memory. Live item 1 stays open.
- ADR 0023's reopen condition fired on #672. The new ADR closes it by routing #672's shape to D7, not by changing the mechanism.
- If D7's hook cannot force a prompt under auto mode, rule 4 has no deterministic stop for some time.

Counts re-verified (2026-10-20, read-only):

- 34 Captain validation approvals in `decision_ledger.py` at state fe2d90ff; 29 name a head and a PR.
- `gh pr view` on all 29: 28 merged at exactly the approved head. Exception: #652's first approval (8d051de7), superseded by his second approval of the merged head ef7a360e.
- 3 of 27 archived observer reports flag a Delivery-authority violation; none is a wrong task-PR merge: observer-before-merge-guard (head differed from the validated candidate, disclosed, Captain approved that head); prod-security-review-gates (a Draft-PR grant attributed to the wrong day's question); special-role-calls-fire-when-needed (#672).
- #672: head branch `release-please--branches--main`, merged 2026-10-20T03:07:06Z, 3m50s after #682 (03:03:16Z). The observer writes "Whether chat asked about that merge is outside state", so even the only bite is not confirmed as an unauthorized merge.
- D7 needs no new record fields: 0.26.0 `delivery_gate.py` already saves `pr` and `head` in `merge/ask-N.json` (the `write_record` call in `check`).

Not verified by the chief-engineer and not driving the conclusion: "5 carried merges in two days" (the design's number) and "155 of 155 digests match" (reviewer 2's number).
