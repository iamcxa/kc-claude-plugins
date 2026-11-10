# Chief Engineer advice: owner-vehicle-kept-after-name, before implementation repair 5

**Short answer.** Repair 5 should go ahead, but the outcome first asked for already works on the running candidate, and repair 5 does not touch it. Repair 5 fixes a second problem, and its two defects can be tested now with browser chains the validator already built. After repair 5, the task will most likely stall on missing evidence, not on another defect. Validation-2 recorded 0 of 20 criteria PASSED, and no implementation round can produce most of what is missing.

## 1. Is this still the outcome first asked for?

No. The first-asked outcome works on the ordinary paths at `35fd5f65`: the owner picks the car once, sees that the plate is the missing step, and has a visible back.
- **First-time owner (validation-2):** services, then one BMW 1 Series choice, plate on confirm, SMS sign-in, name and consent, one summary, then 201 with a correct DB row.
- **Saved owner:** direct to confirm, one summary, then 201.
- **Evidence:** `first-summary.json`, `db-first-sent.json`, `returning-summary.json`.

The Captain widened the scope six times. That widening was his decision, not drift.

Every round since implementation-1 has worked on a second problem, which the approved design created: late responses landing on the memory-only booking draft after the owner goes back. role_triggers counts four dispatches against a symptom that has not come back since implementation-1. The second problem is still real, and the Captain has already ruled the repair:
- **F5:** a deliberate send wrote the earlier time (booking `0500a6e3`).
- **F6:** a valid replacement booking is refused with a false 「這個時段你已經預約了」.

## 2. Can the gap be tested now, or are we waiting?

- **F5 and F6: testable now.** Validation-2 built held-response browser chains with DB readback: `profile-held.json` through `profile-after-release.json`, and `f2-final-*.json` through `f2-next-send-blocked.json`.
  - Implementation-4 was told a browser run was optional. Its F2 test checked that the replacement was kept, not that it could then be sent, and F6 was sitting right behind it.
  - This round, the implementer should run both chains itself: failing before the fix, passing after.
- **Built-screen design review: testable now.** FO owns it and it has not run yet. `design_surfaces` exits 1 on the missing record in implementation-4, validation-1 and validation-2.
  - Validation-2 already has 46 current captures, enough to run the review alongside repair 5.
  - Repair 5 should change no rendering, and validation-3 can confirm that from the diff.
- **Real phone keyboard and screen reader: genuinely waiting.** Local-only runs cannot produce this evidence.

## 3. What breaks if this criterion or process is deleted?

- **The F5/F6 repair.** Without it, wrong-time bookings and refused replacement bookings ship. Keep it.
- **The one RoboRev run per round that feeds validation.** It found three of the four Material defects (F1, F2, F5). Keep it.
  - What should go is fixing one instance per round.
  - Open findings handed back per implementation round went 4, 2, 2, 2, and F2's fix exposed F6.
  - A flat curve like that means the rounds are fixing instances of a defect class, not the class.
- **The open evidence matrices.** Validation-2 has 2 FAILED, 16 PARTIAL, 2 UNVERIFIED and 0 PASSED.
  - Across both validation runs, all four Material findings were draft-lifetime or late-response defects. None came from widths, contrast, 200% text, no-match search, or the full refusal and foreign-ID matrices.
  - Deferring those matrices breaks nothing observed so far. They are still accepted commitments, so only the Captain can move them.
  - Without his ruling, validation-3 cannot return PASSED even after a perfect repair 5.
  - The one clause I would not defer is a real-phone keyboard pass on the two-box plate field. The control is new, its empty-right Backspace already failed once under desktop keys, and the Captain's original reactions came from phones.

```yaml
chief_engineer_advice:
  outcome: >-
    The first-asked outcome works on the ordinary first-time and saved-owner paths at
    35fd5f65: the car is chosen once, the plate shows as the missing step, there is a
    visible back, and one correct booking is sent. Repair 5 delivers a different thing:
    a late response can no longer change or block the owner's current booking
    (AC-57, AC-42, AC-51).
  next_step: >-
    Dispatch implementation repair 5 as one fix for the whole defect class, inside the
    Captain's ruling.
    (a) Define one booking-attempt identity: draft revision + route serviceId/date/time
    + owner/session. Check it after every await, before any route push, draft write or
    key reuse.
    (b) Ship an inventory of every await continuation in the booking and sign-in
    screens, each row naming its guard or why it cannot touch a booking. At 35fd5f65:
    summary `submit` is guarded, but against the draft store only. complete `submit` is
    unguarded, which is F5. verify `handleVerify` and the sign-in `handleSend` /
    `continueSignedIn` are unguarded, and their late paths were never exercised. The
    `useCustomer`/`useLoad` loaders must state their cancellation.
    (c) The request key follows the slot and stays the same for an identical retry.
    (d) Add tests that fail before the fix and pass after: the time-only F5 variant,
    the F6 replacement actually booking one row, and an identical ambiguous retry
    keeping its key.
    (e) The implementer reruns validation-2's two held-response browser chains at the
    new SHA.
    (f) A RoboRev finding that is a missing binding on an await is fixed in this round,
    as part of "every callback". Any other finding is recorded open.
  material_risk: >-
    Binding to the draft revision alone, as the ruling is worded, does not see a change
    of time. Date and time live in the route, not the draft store. Choosing a slot in
    slots.tsx and pressing the sign-in back control (AuthLayout `onBack`) write nothing
    to the store, so `bookingDraftRevision` does not move when only the time changes.
    Validation-2's F5 chain typed a new note on the replacement summary, and that note
    is a store write. So a revision-only fix can pass the reproduced chain while this
    path still restores the old time: back, pick a new time, edit nothing, then the old
    profile 200 arrives. That is exactly the "another late-callback defect" that the
    Captain said brings a scope choice to him instead of a fourth round.
    F6 has the same root. The `idempotencyKey` is minted once per summary component (a
    useState initializer), even though its sessionStorage name already includes date
    and time. Tying the key to the store revision instead would also change it on a
    note edit, which breaks AC-42's same-key retry after an ambiguous send.
  decision_needed: >-
    Captain: the acceptance boundary for validation-3. Which of the 16 PARTIAL and 2
    UNVERIFIED criteria must be proven for this Pilot task, and which move to a named
    follow-up (for example device and accessibility checks, and the full error
    matrices)? Ask now, while repair 5 runs, so validation-3 is dispatched against what
    can actually PASS. His existing rule for another late-callback defect stays as he
    wrote it.
  defer:
    - F4 (Captain-deferred; needs a natural-expiry or second-owner trigger before any claim)
    - new pictures or layout work in repair 5 (no rendering change is in scope)
    - non-timing evidence matrices (320/768 widths, contrast, 200% text, no-match search,
      full refusal and foreign-ID matrices) until the Captain rules the boundary
    - RoboRev findings outside the await-binding class inside repair 5 (record them, do not fix)
  recommendation: adjust
```

Evidence was read only under `/tmp/rcm/inputs`: the task file at state commit `27f04824`, dispatch records `implementation-4.md` and `validation-2.md`, `evidence/validation-2/{findings,acceptance}.json`, `run-notes.md`, the F5 trigger files, and candidate source (`lib/booking-draft.ts`, `app/sign-in/{complete,verify,index}.tsx`, `s/[code]/{summary,slots}.tsx`, `components/auth-layout.tsx`, `lib/customer.ts`). The material risk comes from reading that source. It has not been reproduced at runtime.
