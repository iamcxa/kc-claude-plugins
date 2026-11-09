# P3 replay rubric (pre-registered 2026-11-09, before any run)

Source of the nine checks: qnow state booking-attempt-identity.md "Checks the reviewer found standing in
for an attempt identity at candidate 6bd09a1c" (the engineering reviewer's full report is not committed
in qnow state; the parent task's `## FO alignment` holds only its `Reviewer:` line). Each verified present
at qnow code 6bd09a1c (summary.tsx `stale`, lib/booking-continuation.ts scope, vehicle.tsx generation).

A design names a check (score 1) only when its text states BOTH the condition below AND what happens to
the kept data or to the late reply under it. A bare mention, a code identifier without behaviour, or an
outcome without the condition scores 0. Quote the line; a quote not found verbatim in the scored text scores 0.

| # | Stand-in check at 6bd09a1c | Design-level question it answers |
|---|---|---|
| C1 | summary.tsx submission counter | A send's reply that arrives after the owner began a newer send (or pressed send again) does not clear, replace or block the newer attempt. |
| C2 | summary.tsx car key (draftKey: shop + car) | When the chosen car changes, data held for the old car (plate, quote, draft) ends or is replaced, and a reply issued for the old car does not apply to the new one. |
| C3 | summary.tsx owner | When a different person signs in on the device, the kept draft is not carried over or applied for them. |
| C4 | summary.tsx session | When the session ends (sign-out, expiry, deactivate/reactivate), the design says what happens to the kept data, and a reply from the old session is not applied. |
| C5 | summary.tsx draft revision | When the owner edits the draft (date/time, car, plate) while an async step is in flight (profile/name save, verification, quote), the late reply does not restore or overwrite the newer edit. |
| C6 | booking-continuation focus active flag | When the owner leaves the screen (back arrow, tab rail) while an async step runs, its late reply does not navigate or write. |
| C7 | booking-continuation focus epoch | When the owner leaves and returns to the same screen, a reply started during the earlier visit is ignored. |
| C8 | booking-continuation route context string | When the route context (shop, service, slot or redirect target) changed, a reply for the older context does not navigate to it or apply. |
| C9 | vehicle.tsx bookingDraftGeneration | When the draft is discarded or replaced (after send, abandon, or a new booking), a late reply cannot write into it and the next booking starts without the old draft's data. |

Scored text: the lines a run added or changed in the task file (diff against the replay's starting state).
Scorer: a fresh Claude sonnet per run, blind to the arm, given this rubric and the scored text only;
each hit's quote then checked verbatim by script. Outcome per run: count of C1-C9 scored 1 (0-9).
Ship rule (task Stop condition): revised beats current = revised's summed count over its runs exceeds
current's at both amendments, or exceeds it at one and ties at the other. Otherwise close with the table.
Early stop: if the current arm's first run at an amendment scores 9, revised cannot beat it there.
