# Replay grading (rubric: grader.md, pre-registered 2026-11-09T14:44:25Z)
| run | arm | verdict | quoted line |
|---|---|---|---|
| current-1 | current | PASS | runs/current-1.md:52 "(a) Define one booking-attempt identity: draft revision + route serviceId/date/time + owner/session. Check it after every await" (with :34 "fixing instances of a defect class, not the class") |
| current-2 | current | FAIL | runs/current-2.md:31-32 two separate bindings: callbacks "act only while their own screen or detour is still current"; "The request key belongs to the booking attempt's slot" - no single attempt identity |
| current-3 | current | PASS (generous; strict FAIL) | runs/current-3.md:11 "one class: an await whose continuation navigates or clears the draft without checking that it is still the same booking attempt"; does not say the attempt lacks an identity |
| mechanism-1 | mechanism | PASS | runs/mechanism-1.md:3 "The booking attempt has no identity of its own." |
| mechanism-2 | mechanism | PASS | runs/mechanism-2.md:18 "The class is \"the attempt has no identity,\" not \"callbacks are unguarded.\"" |
| mechanism-3 | mechanism | PASS | runs/mechanism-3.md:3 "A booking in progress has no identity of its own." |
Result: mechanism 3/3; current 2/3 generous, 1/3 strict. Rule (strictly more) met under both gradings.
Opening sentence: mechanism 3/3 open with the mechanism; current 3/3 open with "the outcome is delivered / not the original symptom".
Limits: Claude opus only, n=3 per arm, one grader (the ideation worker), margin 1 run under generous grading.
