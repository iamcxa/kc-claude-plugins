# Chief Engineer advice: owner-vehicle-kept-after-name, before implementation repair 5

**Answer:** One mechanism produces these findings. A booking in progress has no identity of its own. Its pieces live in several places, each with a different lifetime and each keyed on only part of the booking. Whenever the booking changes along a dimension one of those places does not track, that place keeps acting on the old booking. Every repair round so far guarded one place against one dimension, and the next review found the next one.

**The one change:** make the existing draft store the single record of the booking attempt, and have every late reply and every send check that record.

```yaml
chief_engineer_advice:
  outcome: >
    The original symptom is delivered on the ordinary paths. Validation-2 observed a first-time owner
    choose the car once, type the plate on confirm, see one summary and get a 201 with database readback;
    Back is partially verified (AC-23). What is being delivered now is the same flow with no data crossing
    between booking attempts: a late reply, an old request key or a leftover draft must never act on a
    booking the owner has since changed or left.
  next_step: >
    Dispatch repair 5 as one change. Make the draft store in lib/booking-draft.ts the single
    booking-attempt record. It also records serviceId, car identity, date and time. URL navigation stays
    as it is, because AC-51/AC-57 and bookingCancelPath need the slot fields in routes. Any change to the
    slot or the car is then also a draft write. Two consequences:
    (1) Every async continuation captures bookingDraftRevision plus owner and session when it starts. That
    covers continueSignedIn and the sendPhoneCode push in the sign-in screen, handleVerify,
    CompleteProfileScreen.submit and BookingSummaryScreen.submit. After each await, a continuation that
    finds any mismatch drops its navigation and its draft writes. Whether a cancelled verify still
    completes setActive is an AC-57 detail for the implementer.
    (2) The request key comes from the record's current slot, not from the summary's mount-time useState
    initializer. It is new when service, date or time changes: the same slot the base storage key
    (bookingKeyStorageKey) already names. It stays the same across car, plate and note edits and across a
    reload for the same slot. It is forgotten on success.
    Prove it for the whole class, not per finding. Use one table test of every continuation site against
    every kind of attempt change. That must include a date/time change with no plate or note edit, and
    reload-duplicate.spec.ts C0-C5 must still pass.
  material_risk: >
    In the code as it stands, the Captain's "current draft revision" does not mean the booking attempt.
    bookingDraftRevision advances only inside setBookingDraft, and service, date and time are never written
    to the draft: slots keeps them in component state and the URL.
    If the ruling is built literally, take an owner who presses Back while the profile save is pending,
    picks a new time and types nothing. The late profile 200 still passes the check, and
    dismissTo(returnTo) lands on the old time (F5 again). A request key tied to that unchanged revision is
    reused for the new slot (F6 again). That is the "another late-callback defect" which the Captain
    already ruled sends validation-3 to a scope choice.
    The other literal reading, a new key on every revision, breaks idempotent retry. Every plate and note
    keystroke advances the revision, and the app recognises an already-filed booking only through
    IDEMPOTENCY_KEY_REUSED (alreadyBooked). Under that reading, reload-duplicate C1 (edit the note after a
    lost response, still one booking) and AC-42's same key on an ambiguous send would fail.
  decision_needed: >
    None before dispatch. On the request key, the brief departs from the Captain's literal words: taken
    literally (a new key on every revision), his key clause conflicts with AC-42, which the same F6 sentence
    cites. The brief chooses the slot-bound key, and the Captain's own AC-42 citation settles that choice.
    FO should record it in the dispatch record and the validation-3 gate briefing as a stated choice, not
    as something the Captain already approved.
  defer:
    - F4 (manual-car text returns after the same session is reactivated); the Captain already recorded it as a deferred risk
    - Per-site guards for any new RoboRev finding outside this class; record them as open, as in rounds 2-4
    - Physical phone, IME, screen reader, 200% text, full four-width geometry and the unverified error/expiry matrices
  recommendation: adjust
```

## Mechanism

Where the pieces of one booking attempt live today, at candidate 35fd5f65:

| Where it lives | What it is keyed on | What it cannot see | Findings it produced |
| --- | --- | --- | --- |
| Draft store (`draftKey`, `pickDraft`) | shop + car | service, date, time; the attempt ending | impl-1 note lost on car change; impl-2 existing-booking exit kept the draft; F1 |
| Summary request key (`useState` initializer) | summary mount | route params changing under a still-mounted screen | F6 |
| Detour `redirect` captured in sign-in, verify and complete | the booking as it was when the detour started | everything after that | F5 (R4-2) |
| `BookingVehicleScreen` component state (`before` snapshot, typed text) | vehicle mount | owner or session change | impl-1 cancel restored the prior owner's car; F4 |
| Summary submit closure | car key, owner and session before round 4 | mount, date and time | F2; impl-2 session replacement during a pending send |

The rounds show the pattern directly:

- **Round 2 note fix led to F1.** It fixed "note dropped on car change" by making `pickDraft` carry the note across any car at the same shop. That stretched the note's lifetime to "same shop", and F1 followed: an abandoned note reached the next booking at that shop.
- **Round 4 F2 fix exposed F6.** It stopped the stale 201 from redirecting. With the redirect gone, the summary's mount-time key is now reused for a new slot. That key code is unchanged base code; the old redirect simply hid it.
- **Round 4 did not reach F5.** Its guard covered only summary submit, so the profile-save continuation in `CompleteProfileScreen` kept navigating to its captured `returnTo`.

Nine of the twelve distinct findings across the four implementation rounds and two validations fit this mechanism. The other three are outside it: the plate Backspace key, a comment that narrated the code, and a same-class time cleared during a pending class lookup.

Why the root is one store and not more guards: Captain amendment 4 put the plate before sign-in and allowed it only in app memory. So the app needs exactly one root-lifetime holder for the attempt. That store already exists (`lib/booking-draft.ts`), but it holds only half the attempt.

## For the repair-5 brief

- **Fix the symptom line.** Every dispatch record still carries the original symptom ("choose the car twice / could not see the plate step / no visible back"). The defect the rounds keep hitting is different: "a late reply or leftover state from an earlier booking attempt acts on the current one." Brief repair 5 with that.
- **Prove the class.** List every `await` that is followed by a navigation or a draft write, and show that each one drops its navigation and its draft writes on a stale attempt. The sites are `continueSignedIn`, the `sendPhoneCode` push, `handleVerify`, `CompleteProfileScreen.submit`, `BookingSummaryScreen.submit` and the `BookingVehicleScreen` cancel snapshot. Note that `CompleteProfileScreen.submit`'s stale sign-in branch also calls `setBookingDraft(null)`, so it can clear a newer draft.
- **Rerun F5 and F6 without typing.** Validation-3 should rerun both triggers with no plate or note edit after Back. That variant is the one a literal revision check misses.

## Evidence limits

- This is from reading the source at 35fd5f65, the validation-1 and validation-2 `findings.json`, and the task file. The no-typing variants of F5 and F6 are reasoned from the source; nobody has run them.
- Only `apps/qnow-app` was supplied. I did not check whether the API has its own duplicate guard per owner and slot besides the idempotency key.
- The findings from implementation rounds 1-4 come from the stage-report summaries. Their `findings.json` files were not in the inputs.
