No. The outcome first asked for is already delivered. Repair 5 fixes defects on routes this task built itself. It still belongs in this task: the Captain ruled it at the 09:21 gate, and both defects break a real booking on a path one tap away. But repair 5 only ends the loop if it closes the whole class of defect, not just the two instances. The gap can be tested now with tools validation-2 already committed. The one thing genuinely waiting is a real-phone keyboard check that no worker can perform.

**1. Is this still the outcome first asked for?**

No. The first-asked outcome is runtime-proven twice: the car chosen once, the plate shown as the missing step, and a visible back. Validation-1 and validation-2 each ran this path: services, one BMW 1 Series choice, plate on confirm, slots, Clerk SMS, name/consent, one summary, 201. Each read back a correct 600/60 database row. Validation-2 also took the returning owner through to a 201.

Repair 5 solves something else: late async callbacks on routes this task added.
- F5. The profile-save success navigation (`CompleteProfileScreen` `submit` → `router.dismissTo(returnTo)`) is unchanged from base. What changed is the AC-57 booking Back arrow this task added, which turns "leave while the save is pending" into one tap. The harm: the summary silently reverts to the old date/time, and a later send in validation-2 booked the old time.
- F6. Repair 4 created this one. Base called `forgetBookingKey()` on every success. Repair 4's stale guard returns before `forgetKey()`. The summary's `idempotencyKey` is minted once per mount (`useState`, unchanged from base), so the kept replacement summary reuses the old slot's key. The result is 409 `IDEMPOTENCY_KEY_REUSED` plus a false 「這個時段你已經預約了」.

Every round since implementation-2 has found the next instance of one class: an await whose continuation navigates or clears the draft without checking that it is still the same booking attempt. The sequence:
- implementation-2: submit during a session replacement
- implementation-3: a late response after unmount
- validation-1: F1 and F2
- implementation-4: R4-2
- validation-2: F5, plus F6 created by the F2 fix

This is drift by instance, not scope creep.

**2. Can this gap be tested now, or am I waiting?**

F5 and F6 can be tested now, with nothing external needed. Validation-2 committed `browser-init.js`, which holds a real response after the server has processed it, and `captain-acceptance.md`, whose steps 3–5 state each pass condition.

Code reading at 35fd5f65 finds the same unguarded pattern at sites that have not been reproduced at runtime. All of them sit behind the same AC-57 back arrow:
- sign-in `index.tsx`: `continueSignedIn` (setActive → `router.replace(returnTo)`) and send-code → push verify.
- `verify.tsx`: `handleVerify` (verifyPhoneCode/setActive → replace complete or `dismissTo(returnTo)`).
- `complete.tsx`: the no-token and 401 branches, which call `setBookingDraft(null)`. A late one would wipe a replacement draft.

Validation-2 recorded "late verify/401 branches unverified", so these are the branches validation-3 is set up to probe. Under the Captain's stop rule, one more late-callback defect at validation-3 means a scope choice, not another round.

The only thing genuinely waiting is the AC-52/AC-56 real-phone soft-keyboard walk at the two-box plate field. It has been carried as owed in every stage report. No implementation or validation run produced it, and a sandboxed worker cannot.

Testable now but never run: the FO-owned built-screen design review. `design_surfaces.py` exits 1 because it is missing, so it blocks the gate whatever repair 5 does.

**3. What breaks if this criterion or process is deleted?**

- The F5/F6 repair. Without it, the flow ships a wrong-time booking and a send that dead-ends with a false message, both one tap from the AC-57 back arrow. Keep.
- The clause in the implementation-3 and -4 dispatches, "No browser run is required unless a fix cannot be proven by a test". Nothing breaks without it, and it is how F6 escaped. Repair 4's controller test proved the old 201 no longer redirects, but nobody tapped send again on the built screen. Delete it for repair 5.
- Scoping each repair to the named findings. Nothing breaks without it; this scoping is what keeps the loop going. The Captain's 09:21 text already says "bind every async callback (profile save, verification, submit)". The dispatch must list the sites, so "every" is not read as F5's one line.
- The real-phone keyboard clause in AC-52 and AC-56. Keep the check. The plate control depends on key events, and every run so far used desktop key events. The original Scope already lists "whether a real phone shows the same thing" as not yet known. But as a validation-3 pass condition it can never be met, so its owner has to change. That is the decision below.
- Screen-reader evidence. AC-52 already says "Separately state screen-reader/physical-device limits", so there is nothing to delete.
- One RoboRev run per round. Keep: R4-2 became F5, a reproduced wrong-time booking.

There is one trap inside the F6 fix: the summary key has two duties that pull against each other.
- `booking.test.tsx` asserts the same key across two mounts of the same slot, so a reload does not mint a new key. AC-42 also keeps idempotent retry.
- F6 needs a fresh key for a replacement attempt.

The Captain's wording ("bind each send's request key to the current draft revision") and validation-2's wording ("scope ... to the actual booking attempt/slot") are not the same rule. Validation-3 must prove both directions:
- a same-slot retry after a dropped response still resolves to the original booking;
- a replacement after Back gets a fresh key and books.

```yaml
chief_engineer_advice:
  outcome: >-
    The Captain-amended owner booking keeps the car and plate: service first, car
    chosen once, plate on confirm, sign-in and name only if missing, one summary,
    explicit send. Validation-1 and validation-2 both proved it at runtime with a
    database readback. Repair 5 makes that route safe against late callbacks the
    route itself introduced; it is not the original symptom.
  next_step: >-
    Dispatch repair 5 as one class fix under the Captain's 09:21 ruling. List every
    site where an await is followed by a navigation or a draft clear: complete.tsx
    success, no-token and 401; verify.tsx handleVerify; sign-in index.tsx
    continueSignedIn and send-code; the summary submit key. Bind each one to the
    current booking attempt. Done means a held-continuation unit test per site,
    plus captain-acceptance.md steps 3-5 passing on the built repaired candidate,
    run by the implementer with validation-2's browser-init.js. Step 5 must end in a
    201 and one new database row for the replacement slot. Remove "no browser run
    required" from the dispatch. In parallel, the FO runs the missing built-screen
    design review on 35fd5f65. Repair 5 should change no visible state, so that
    review carries forward.
  material_risk: >-
    Validation-3 has no defined way to return PASSED. At validation-2, 0 of 20
    criteria passed (2 failed, 16 partial, 2 unverified), and AC-52/AC-56 require a
    real-phone keyboard walk that no sandboxed validator can produce. A perfect
    repair 5 can still end in a non-PASS verdict and another round.
  decision_needed: >-
    Captain: who produces the AC-52/AC-56 real-phone keyboard check at the plate
    field. Either he walks it on his own phone against a build he can open before
    merge, or it becomes a named residual checked on staging after merge. This is
    needed before validation-3 is dispatched, not before repair 5.
  defer:
    - F4 manual-car revival after a session change (Captain already deferred it)
    - screen-reader evidence (AC-52 already says to state the limit)
    - the remaining partial matrices (320/768 widths, 200% text, refusal, expiry, foreign IDs); these belong to validation-3's sweep, not repair 5's checklist
    - the stale "Unresolved decisions" text listing proposals (a)-(c) as pending, although ideation gate 5 approved (a)-(d); housekeeping only
  recommendation: adjust
```
