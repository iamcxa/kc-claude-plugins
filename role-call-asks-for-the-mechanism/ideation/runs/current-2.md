# Chief Engineer advice — owner-vehicle-kept-after-name (pilot, ui), before implementation repair 5

Proceed with repair 5 as the Captain ruled, with two changes. First, the worker must replay validation-2's F5 and F6 trigger chains in a real browser before handing back. Second, the dispatch must carry the Captain's "draft revision" binding as the two observable outcomes he asked for, because the literal mechanism does not cover where the state lives (see the material risk below). The built-screen design review is unblocked and can run now, alongside the repair.

## 1. Is this still the outcome first asked for?

Not the original symptom. The original symptom has been fixed for three rounds.
- The original problem had three parts: the owner chose the car twice, could not see that the plate was the missing step, and had no visible back. All three are observed working on the built candidate. Implementation-1, validation-1 and validation-2 each ran a real Clerk SMS first-time journey: one catalog choice, one pre-send summary, POST 201 and a database readback. Validation-2 also observed the icon back (AC-23), the empty-plate stop on confirm (AC-38), and a single summary visit (AC-50).
- Implementation rounds 2–5 fix a different class of bug: a late response from an abandoned send, sign-in or profile step acts on the owner's newer booking. The approved design created this class. Amendment 4 holds the plate in memory across the sign-in detour, and amendment 6 puts sign-in before the summary. The class is inside Captain-approved criteria (AC-42, AC-51, AC-57), so this is not unauthorized drift. But the `Symptom:` line on dispatches 1–4 no longer describes what is being repaired. Keep the line as it is, so the trigger count stays honest, and state the real target in the brief.
- The FO's own budget estimate was one ideation pass and one implementation pass. The actual count is 11 ideation cycles, 4 implementation rounds and 2 validation rounds.

## 2. Can this gap be tested now, or am I waiting?

- **F5 and F6: yes, now.** Validation-2 left complete local trigger chains: `profile-held.json` → `profile-after-release.json` for F5, and `f2-final-*.json` → `f2-next-send-blocked.json` for F6, plus the database readbacks. The setup is local API, throwaway database and Clerk dev code 424242. Nothing outside the machine is pending.
- **Built-screen design review: yes, now. Nothing outside the FO blocks it.** `design_surfaces.py` has exited 1 for the missing built-screen review since implementation-1. F5 and F6 change callbacks and the request key, not rendered output, so the review can run now on validation-2's 46 captures. Re-run it only if repair 5 touches a rendered file.
- **The other 18 criteria: no dispatch has been asked to close them.** Validation-2 recorded 0 of 20 in-force criteria as passed: 16 PARTIAL, 2 UNVERIFIED, 2 FAILED (AC-42, AC-57). Repair 5 can move at most the two FAILED ones. Most of the PARTIAL matrices could be tested locally today: class pending or failed, refusal, foreign IDs, 320 and 768 widths, keyboard, local expiry and 401. Each round has carried them forward in `remaining-unverified.json`. One part does wait on a person with a device: AC-52's real-phone keyboard walk, plus soft keyboard, IME (phone input method) and screen reader. No worker can produce that.

## 3. What breaks if this criterion or process is deleted?

- **One RoboRev review per round: keep it.** It has caught real defects. Of the last four findings it raised, three reproduced as Material: F1 and F2 from implementation-3, and F5 from implementation-4's R4-2.
- **The rule "no browser run is required unless a fix cannot be proven by a test" (implementation-3/4 scope notes): delete it for lifecycle repairs.** Nothing has relied on it. It has a cost: F6 is the direct consequence of F2's fix, which was proven only in a controller test. Replaying the F2 chain through to the next send would have shown F6 in the same round.
- **The PARTIAL evidence matrices and AC-52's physical-device walk: no Material finding has come from them.** Every Material defect came from runtime probing of named findings. But the Captain approved these criteria at the ideation gate, so cutting them, or recording them as known limits, is his decision, not the FO's.

## Material risk: the ruling's mechanism does not match where the state lives

The Captain asked to bind every async callback and each send's request key to the current draft revision. The candidate's source shows two problems with doing that literally:
- `bookingDraftRevision()` moves only inside `setBookingDraft` in `lib/booking-draft.ts`. The chosen date and time are not in the draft. They live in the route parameters and in local state in `slots.tsx` (`setSelectedDate`/`setSelectedTime`). Separately, in `complete.tsx`, `submit` calls `router.dismissTo(returnTo)` after the profile save with no staleness check at all. So a revision-only guard misses the simplest F5 case: Back, pick a different slot, edit nothing, then the late 200 arrives.
- `idempotencyKey` in `summary.tsx` is created once per mount (`useState`) from `bookingKeyStorageKey`. Every note or plate keystroke goes through `setBookingDraft`, and each call advances the revision. If the key followed the revision, an ambiguous send followed by a note edit and a resend would carry a fresh key. That breaks AC-42's "same idempotency key after ambiguous send", which implementation-1's `ambiguous-replay` control proved, and it reopens the risk of a double booking.

What the Captain's intent needs instead:
- Late profile, verify and submit callbacks act only while their own screen or detour is still current: still mounted or focused, with the same redirect target. `summary.tsx`'s `submission` counter already works this way.
- The request key belongs to the booking attempt's slot (shop, service, date and time). A new slot gets a new key; retrying the same slot reuses the key.

The FO should state this reading in the repair-5 brief and in the next gate text ("Captain said revision; applied as X because Y"), not apply it silently. Three regressions separate a correct fix from a wrong one:
1. F5: change only the slot, with no draft edit, then release the held 200. The newer date and time stay.
2. AC-42: an ambiguous send, then a note edit, then a resend for the same slot. Same key, and one row in the database.
3. F6: a replacement on a different slot gets a fresh key, a 201 and the correct row.

Under the Captain's stop rule, repair 5 is the last round. If validation-3 finds another late-callback defect, the next step is a scope choice for the Captain, not another round. Getting this binding right decides whether the task closes or escalates.

```yaml
chief_engineer_advice:
  outcome: >-
    Original outcome delivered and runtime-proven three times: car chosen once, the
    plate visibly the missing step, visible back. Current work is the approved design's
    late-response class (AC-42/51/57): a late profile success must not change the
    owner's newer date/time (F5), and a replacement booking's deliberate send must not
    be refused by a reused request key (F6).
  next_step: >-
    Dispatch repair 5 for F5 and F6 only. The callbacks are bound to the lifetime of
    their own detour or screen, and the request key is scoped to the slot. Disclose
    this as the rendering of the Captain's "draft revision" ruling. Add the three
    regressions: slot-only change, then late profile 200; ambiguous send, note edit,
    resend on the same slot keeps the key and leaves one row; replacement on a new
    slot gets a fresh key and a 201. The worker replays validation-2's F5 and F6
    browser chains with a database readback on the built candidate before handing
    back. RoboRev runs once and its findings stay open, as now. In parallel, FO runs
    the built-screen design review on validation-2's 46 captures.
  material_risk: >-
    Applying "bind to draft revision" literally: date/time never advances
    bookingDraftRevision(), so the slot-only F5 case stays broken; and a key that
    follows the revision changes on every note keystroke, breaking AC-42's same-key
    retry. Either one produces another late-callback defect at validation-3, which
    triggers the Captain's stop rule.
  decision_needed: >-
    Captain: which of the 18 non-FAILED criteria (16 PARTIAL, 2 UNVERIFIED) validation-3
    must prove at this pilot gate, and which become recorded known limits or follow-up.
    In particular: AC-52's real-phone keyboard, IME and screen-reader walk, which no
    worker can produce, and the full refusal/expiry/401/different-owner matrices. Ask
    now, alongside repair 5. Without a ruling, validation-3 has no evidence plan that
    reaches PASSED.
  defer:
    - F4 same-session manual-text revival (already ruled deferred risk by the Captain)
    - any new RoboRev finding outside the late-callback class (record it, do not repair it in round 5)
    - the PARTIAL evidence matrices and device walk until the Captain rules the evidence boundary
    - LINE login (already routed to sign-in-with-line)
    - relabelling the dispatch Symptom line
  recommendation: adjust
```
