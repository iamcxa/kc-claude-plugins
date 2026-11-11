# Pre-registration, round 2

Written 2026-11-11 before any round-2 scored run. Round 1 (`PREREG.md`) stands as run.

## Question

Does the revised convention fix the three holes round 1 found (an ADR per task, an old ADR left Accepted after
being replaced, a deferred idea with no home), and does one architecture file on the fixed skeleton do as well
as a map with topic documents?

## Arms added

| Arm | Layout | Rules |
| --- | --- | --- |
| D | map + topic documents on the revised skeleton (`MAP2`, `BOOKING_DOC2`, `NOTIFY_DOC2`), `docs/journey/later.md` | shipped rules with one phrase narrowed in `principles.md` ("one file per decision" to "one file per ruling a person made") + `CONVENTION2` |
| E | one `docs/architecture.md` on the same skeleton (`SINGLE`), `docs/journey/later.md` | same as D, single-file wording |

D and E carry the whole proposed change at once (layout, convention text and the narrowed phrase), so a
difference from A, B or C cannot be assigned to one of the three. Arm A's world is byte-identical to round 1
(step-0 tree 7435e04d379c106388e6e964e5beb87f449dca56), so round-1 A, B and C chains are the baselines.

## Runs

Codex `gpt-6.1-sol` xhigh: D and E, 2 chains each. Claude `sonnet`: D and E, 2 chains each, and one more A.
Nine chains, 54 runs; hard stop 60. Same six tasks, same prompt.

## Measures

Primary: the same ten facts. Named in advance for the three holes: ADRs added beyond the original four
(one ruling is given, so the target is 1); ADR 0003's Status after the ruling; where the deferred idea is at
the end (target: `docs/journey/later.md` and no architecture document or ADR).
Secondary as round 1, plus for E whether everything stayed in one file.

## Judge

`score.py` gives the script reading (F5 now accepts a bracketed link; `idea_files` and `idea_in_later_md`
added; see `CHANGES.md`). The reported reading is a judge from a different model family reading the end
states with the question list of round 1's reviewer. Gemini through `agy` was chosen by the Captain; four
`agy --print` calls from this session returned nothing, so the judge run is his to launch from his terminal.
If it cannot be run, a fresh-context Claude reviewer is used and the report says so.

## Reading the result (fixed now)

- A hole counts as fixed when all four Codex chains of D and E meet its target; partly when two or three do.
- E is "as good as D" when the Codex means of the ten facts differ by under 1.
- D or E below 9 on the ten-fact mean for Codex is a regression against round 1's B and C and is reported as one.
