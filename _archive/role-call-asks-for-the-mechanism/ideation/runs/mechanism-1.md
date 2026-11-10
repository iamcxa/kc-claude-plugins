# Chief Engineer advice: owner-vehicle-kept-after-name, before implementation repair 5

**Answer.** One mechanism produces 10 of the 12 distinct findings from implementation-1 through validation-2. The booking attempt has no identity of its own. Its parts sit in four holders, each with a different lifetime. When an async callback resolves late, it decides "is this still my booking?" by checking whichever holder it captured at the start, and that holder can say "same booking" after the owner has moved to a different one.

The one change that closes the class: keep the whole attempt as one record with one token in the existing root draft store. Advance that token on every change to the booking's context, not only when the plate or note is written. No callback may navigate, write the draft or drop the request key unless that token still matches.

The owed call's symptom text is the task's original complaint: choosing the car twice, not seeing the plate step, no back control. Validation-1 and validation-2 both saw that complaint fixed on the normal path: one car choice, the plate on confirm, one summary, and a sent booking with database readback. The findings that keep coming back belong to a different class, and this task's own design created it. The design added memory that lives as long as the app and holds the plate across sign-in (amendment 4). It also added back and cancel exits on the sign-in, verify and name/consent screens (amendment 6).

```yaml
chief_engineer_advice:
  outcome: A first-time owner picks the car once, fills the plate on confirm and sends after one summary. This works on the normal path at 35fd5f65. What remains is making sure a late callback or a reused request key cannot change or block the booking the owner is making now (F5, F6).
  next_step: Dispatch implementation-5 as one repair for the whole class, not as two separate F5/F6 fixes. Define the attempt token, list the call sites in scope, require the no-typing regressions, and require the bounded grep check described under "The one change" below.
  material_risk: The Captain's ruling binds callbacks and the request key to "the current draft revision". bookingDraftRevision advances only inside setBookingDraft, and no slot pick or back path calls it. In validation-2, both F5 and F6 were reproduced with a typed replacement plate and note, which does advance the revision. A repair that checks only the revision would therefore pass F5 and F6 as reproduced and still leave the no-typing versions open. Saved car, Back, pick another time, send gives the same key and IDEMPOTENCY_KEY_REUSED again. A late profile 200 after Back and a new time, with nothing typed, restores the old date and time again. That would be the "another late-callback defect of this kind" that the Captain made the trigger for a scope choice.
  decision_needed: None for the Captain. The FO owns the dispatch wording, which should define "current draft revision" as the attempt token below. That stays inside the Captain's "fixed at the root" ruling.
  defer: [F4 typed-car revival (Captain recorded it as deferred risk with no repair; report it only if the change closes it as a side effect), physical phone/IME/screen reader/200% text/full error matrices, regression tests for each finding beyond the ones listed below, any reshaping of the draft-store API beyond the token]
  recommendation: adjust
```

## Mechanism

The four holders at candidate 35fd5f65:

- **Route params.** Service, car IDs, date and time live in the URL. Redirect strings, such as the `returnTo` used by sign-in and complete, are captured when a detour starts.
- **Root draft store.** `lib/booking-draft.ts` is new in this task. It holds the plate, note, typed car and cancel destination under `draftKey`, which is only shop plus car. `pickDraft` deliberately carries the note across cars at the same shop.
- **Per-screen component state.** In `BookingSummaryScreen`, `idempotencyKey` comes from a `useState` initializer, so it is read once per mount. `BookingVehicleScreen` keeps its `before` snapshot and the typed brand and model.
- **The auth session.**

The new exits, `bookingCancelPath` and the service-page home back, let a screen's in-flight callback outlive the screen that started it.

| Finding | Which holder gave the wrong answer |
| --- | --- |
| impl-1: cancelling a car change restores the prior owner's car and plate | Component snapshot outlived the owner |
| impl-1: a completed car change drops the note | Note keyed by car, not by attempt |
| impl-1: a still-loading old class clears a same-class time | Late class lookup |
| impl-2: existing-booking exits keep the draft | No point where the attempt ends |
| impl-2: a send waiting on its token survives a session swap | Late submit callback |
| F1: home exit keeps the note | No point where the attempt ends; note scoped to the shop |
| F2: a late 201 redirects and clears the replacement draft | Late submit callback |
| F4 (deferred): typed car survives the session going off and on | Component state outlived the session |
| F5: a late profile 200 restores the old date and time | `CompleteProfileScreen` calls `dismissTo(returnTo)` after the PUT with no guard, and `returnTo` was captured at PUT start |
| F6: the replacement send reuses the old key | Key fixed at mount while date and time changed through params |

Two findings fall outside this class: the empty-right Backspace (impl-1) and the redundant comment (F3).

**Why it keeps coming back.** Each repair dispatch said "fix Fn with a regression test that fails before the fix". Each fix was proven with controller tests in which the router, auth and network were mocked. So each round added one more local guard at the named site: a generation counter in round 2, a session check in round 3, and in round 4 a revision counter, a submission sequence and focus invalidation. Then the once-per-round review of base..candidate found the next site without a guard.

**What is still unguarded at 35fd5f65.** These are the async callbacks that navigate or write the draft after an `await` without any guard:

- `CompleteProfileScreen` submit: PUT, then `dismissTo(returnTo)` (this is F5).
- The verify screen: `verifyPhoneCode`/`setActive`, then `replace`/`dismissTo`. F5 left this late-verify branch unverified.
- The sign-in entry: `setActive`, then `replace`; and `sendPhoneCode`, then `push` to verify.

`BookingSummaryScreen` submit is guarded, but only by its own local `stale()`.

## The one change

1. **One attempt record in the root store.** It holds service, car identity, date, time, plate, note, typed car and cancel destination. Every booking screen saves its selection there, including the slot pick and both back paths. The token advances when any of these fields changes, on an owner or session change, and on each existing clear: send success, home exit, existing-booking exits. The URL keeps carrying the allowlisted IDs and slot fields so a reload can recover, so AC-51 is unchanged. The store becomes the one place a callback can read what is current.
2. **One guard.** Capture the token when an async operation starts. Navigate, write the draft or drop the key only if the token still matches. Use this guard at every site listed above and in `BookingSummaryScreen` submit, where it replaces the local `stale()`.
3. **Request key looked up at send time.** Read the sessionStorage key for the current code/service/date/time when the owner sends, not in the `useState` initializer. This keeps both the reload-duplicate protection and the same-key retry of an ambiguous send. Minting a new key for every revision and holding it only in memory would lose the reload-duplicate protection, because a reload wipes memory.

**Acceptance for implementation-5:**

- F5 and F6 as validation-2 reproduced them.
- Their no-typing versions, where the owner changes only the time and types nothing on the replacement summary. For the send, use a saved car. For the late profile 200, use the plate already entered on confirm.
- A late verify held until after Back.
- A bounded check: in the booking and sign-in screens, no `router.replace/push/dismissTo` or `setBookingDraft` follows an `await` except through the guard, with the grep output kept as evidence.

Validation-3 reruns those chains on the built screen with database readback.

The built-screen design review has been missing since implementation-1. Repair 5 should change no rendered screen, so the FO can run that review in parallel; it is not on this repair's path.
