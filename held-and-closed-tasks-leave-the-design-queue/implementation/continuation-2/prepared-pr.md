fix(kc-dev-flow-2): distinguish held tasks at startup and idle

Startup and idle tasks output now names held tasks by stage and requests a Held section when its reopen or close quote cannot be verified against the newest hold reason or a Captain amendment. Invalid or failed held-task queries exit 2. ADR 0081 records the approved ideation ruling; task-body edits remain FO-owned.

Stacked base: 77e240d46ced4980ec1f6f2dc61a692f27857af1 (PR #854).
Candidate: 455846c6d30d4ab650c1c4503bc591722231586d. Product code is unchanged in the continuation.

Captain amendment 2 replaces the fixed 30-word increase bound with at most three added words per held task plus six fixed words. The native query returns 14 held tasks; their unchanged fact line has 32 words, below the amended maximum of 48. A 49-word mutation is rejected with exit 1. The superseded 30-word failure remains in the original evidence.

Validation: 164 related pytest items passed (250 JUnit entries including subtests). The historical origin-less base and the current real-workflow tasks entrances both exit 0; the base names none of the ten ideation holds and the candidate fact names all 14 native held rows. The original five behavior mutations and candidate removal remain applicable to these identical source bytes. Skill lint, ADR lint requiring 0081, number guards with refreshed state refs, design-surfaces and comment-ratio checks exit 0; added-comment ratio is 0.7%, maximum 5%.

The actual Held sections remain a First Officer state-edit step; the journey-canvas task stays unchanged under its own ruling. The all-Held scratch projection verifies the quote mechanism without changing live task bodies or frontmatter. The default upstream status display is outside this package change.

Product push, Draft PR creation, RoboRev and hosted CI are not run by the worker. CI cost was not measured; no CI configuration or package version changed. Evidence and the superseding report are in the public state task's implementation/continuation-2 folder; state commits remain local under the follow-up instruction.
