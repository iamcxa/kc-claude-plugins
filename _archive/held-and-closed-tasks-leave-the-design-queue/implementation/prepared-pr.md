fix(kc-dev-flow-2): distinguish held tasks at startup and idle

The startup and idle `tasks` command now names held tasks by stage and asks for a `## Held` section when its reopen or close quote cannot be verified against the newest hold reason or a Captain amendment. Failed or incomplete held-task queries return exit 2. ADR 0081 records the approved ideation ruling; held task bodies remain FO-owned.

Stacked base: `77e240d46ced4980ec1f6f2dc61a692f27857af1` from PR #854.
Candidate: `455846c6d30d4ab650c1c4503bc591722231586d`.

Validation: 164 related tests passed; five behavior mutations and removal of the candidate each fail the held tests with `python3 -B` and cleared caches. The real Spacedock query and candidate fact line both name 14 held tasks across stages, including all ten ideation holds. Skill lint, ADR lint requiring 0081, number guards with refreshed state refs, design-surfaces and comment-ratio checks pass. Added-comment ratio: 0.7%, maximum 5%.

Blocked acceptance: NP-3 measures 32 added words for the approved fact-line shape, exceeding its 30-word bound. Its fixed total bounds are below the limits in this run, but the increase bound still fails. No product repair or word-budget increase was made; the one-cycle stage returns this decision to FO. Actual Held sections remain unwritten by this worker. NP-5 (plain upstream status display) is outside the accepted package change.

The origin-less full-command replay also retained exit-2 diagnostics from the inherited scratch sweep needing an origin and the sandbox's GitHub connection failure; it proves the held line, not a clean full replay. See the state task's `implementation/` evidence and handoff for the normal-workflow rerun result.

Product branch push, Draft PR creation, RoboRev and hosted CI are not run by the worker and remain FO-owned. CI cost was not measured; no CI configuration changed. Do not describe this candidate as fully accepted until the word-bound decision and remaining state verification are resolved.
