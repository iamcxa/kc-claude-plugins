# Chief Engineer: owner-vehicle-kept-after-name, before implementation repair 5

## Answer

**Mechanism.** Nothing in the app says "this is the current booking attempt." One attempt's facts sit in places that each live for a different length of time:

- **URL parameters** hold service, car IDs, date and time. A copy of them is frozen into the `redirect` string when a sign-in detour starts (`slots.tsx` `continueBooking`, `summary.tsx` `comeBack`).
- **An app-lifetime memory draft** (`lib/booking-draft.ts`) holds plate, note and typed car. It is keyed `shop:car`, so service, date and time are not part of it.
- **State inside screens the stack keeps mounted** holds the rest. The request key is a `useState` initializer in `BookingSummaryScreen`, read once per mount. The other two are the `before` snapshot and the typed brand/model in `BookingVehicleScreen`.

An owner can back out mid-flight, pick a different date or car, and continue. When they do, any late reply, exit or remount acts on whichever of these places it captured. It writes old values into one place while another already holds the new attempt.

**Each repair added one more local guard at the place the last finding named.** That runs generation, then owner/session binding, then revision, submission sequence and focus cleanup. The next review then found the next unguarded place. You can see this in the source at 35fd5f65:

- `summary.tsx` `submit` carries a five-part `stale()` check.
- `complete.tsx` `submit` (`router.dismissTo(returnTo)` after the profile PUT), `verify.tsx` `handleVerify` (after `setActive`) and `sign-in/index.tsx` `continueSignedIn` all navigate after an `await` with no check at all.

**The class is "the attempt has no identity," not "callbacks are unguarded."** F6 is not a late callback. It is a fresh, deliberate send carrying a request key bound to the screen's mount rather than to the attempt. A repair worded only as "guard every async callback" closes F5-shaped defects and leaves F6-shaped ones open.

## Trace (from stage reports and findings.json)

| Finding | Place that held the stale value |
| --- | --- |
| impl-1: cancel restores the prior owner's car/plate; a completed car change drops the note | vehicle `before` snapshot; draft keyed by car, not attempt |
| impl-2: existing-booking exits keep the draft; session swap during a send | exits had to be listed one by one; submit continuation |
| val-1 F1 (home exit keeps note), F2 (late 201 redirects and clears the new draft) | draft outlives the attempt; submit continuation outlives the summary |
| val-2 F5: late profile 200 resets the summary to Nov 10 13:00 while keeping the new plate/note | frozen `redirect` URL against the live draft: a hybrid of two attempts |
| val-2 F6: replacement send refused with `IDEMPOTENCY_KEY_REUSED` | request key bound to the mounted summary, not to the slot |
| F4 (deferred): typed brand/model come back after the session is reactivated | `BookingVehicleScreen` local state outlives owner/session |

Outside the class: the PlateInput Backspace bug, the same-class time cleared while a class lookup is still loading, and the F3 comment.

**The same mechanism predicts two more defects. Both are in the source and neither has been observed.**

- In `complete.tsx`, a late failure (missing token at the `getToken` check, or a sign-in outcome) calls `setBookingDraft(null)`. That would wipe a newer attempt's plate. Validation-2 named this branch as not exercised.
- `verify.tsx` and `sign-in/index.tsx` both navigate to the frozen `redirect` after `setActive` resolves.

## The one change

Make the existing draft store the **attempt store**, and give it an `attemptId`:

1. **What it holds.** The attempt is shop, service, car, date, time, owner and session, plus plate, note, typed car and the request key.
2. **New id.** Any change to shop, service, car, date, time, owner or session mints a new `attemptId` and a new request key. A plate or note edit keeps the id. The same key is reused only to re-send an identical payload, as AC-42 requires for an ambiguous send.
3. **One guard.** Every continuation captures `attemptId` at start. That covers the profile PUT, verify `setActive`, sign-in `continueSignedIn`, submit and class lookup. Its only check is `isCurrent(id)`, and a stale result is dropped with no navigation and no draft write.
4. **Where a detour returns.** The destination comes from the current attempt in the store, never from the frozen `redirect`. The URL stays only as the way to rebuild the attempt after a full reload, which the design already accepts loses the plate.
5. **Exits.** Every exit (home, sent, existing-booking link, owner/session change, expiry) calls one `endAttempt()`.
6. **Old guards go.** The store replaces the generation, revision, submission and session comparisons; it does not sit on top of them.

This is the Captain's 2026-11-09 "bind every async callback … and each send's request key to the current draft revision" ruling done at the root. It needs no new decision.

**Read literally, that ruling fails.** The existing `bookingDraftRevision` never advances when only the slot changes:

- `slots.tsx` writes no draft.
- `useBookingCar` only reads the draft.
- The key is `shop:car`.

So if the owner re-picks only the date and time and edits nothing, a late profile 200 still passes a revision check and moves the time back. The validator's F5 run typed a new plate and note, which is why it does not separate the two readings. The repair 5 brief must state the identity in point 1, or validation-3 will hit the Captain's stop rule.

## Acceptance for repair 5

- **Falsifier, in two runs.** In one run, hold a real profile 200 (the F5 path). In the other, hold a real booking 201 (the F6 path). In each run, press Back, change only the date and time, edit nothing, then release the held reply. Assert:
  - no navigation and no draft write;
  - a different request key on the next deliberate send, which then gets a 201;
  - an identical re-send of an ambiguous request keeps its key.
- **Source check.** List every post-`await` `router.*` or `setBookingDraft` in `app/sign-in/*` and the booking screens. Show that each one passes through `isCurrent`. This replaces finding the next instance by review.

The role_triggers symptom text ("chose the car twice, no visible plate step, no back") is the task's original complaint. That works on the ordinary path in both validations: one car choice, one summary, a 201 with readback. Do not brief repair 5 around it.

```yaml
chief_engineer_advice:
  outcome: The approved service-first booking route (car chosen once, plate on confirm, summary once) with no stale-attempt defects. At 35fd5f65, AC-42 and AC-57 are the only FAILED criteria.
  next_step: Dispatch implementation-5 as one change. Turn lib/booking-draft.ts into an attempt store with an attemptId; the identity is shop + service + car + date + time + owner + session, and the store carries the request key. Every continuation (complete PUT, verify setActive, sign-in continueSignedIn, summary submit, vehicle lookup) and every exit goes through isCurrent/endAttempt, and that replaces the existing generation/revision/submission guards. Gate it on the date/time-only hold-and-release falsifier and the post-await source check.
  material_risk: If repair 5 binds to the existing draft revision, a date/time-only change is not caught, or verify/sign-in continuations stay outside the guard. Validation-3 then finds one more late-callback defect and the Captain's stop rule turns round 5 into a scope choice.
  decision_needed: none. The Captain's 2026-11-09 ruling already orders the root fix and a stop rule after validation-3; FO owns the brief's identity definition.
  defer:
    - F4 deferred risk (closes as a side effect if typed fields move into the attempt; not a requirement)
    - the PARTIAL and UNVERIFIED rows in validation-2 acceptance.json (phone, screen reader, 200% text, full matrices), as validation-3 scope
    - the FO-owned built-screen design review
  recommendation: adjust
```
