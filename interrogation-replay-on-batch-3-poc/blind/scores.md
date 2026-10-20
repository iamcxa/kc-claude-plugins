# Blind scores (second reader, sonnet ensign `interrogation-replay-on-batch-3-poc-validation`)

Read before scoring: `READER.md`, `answer-keys.md`, the ten `<task>-X/Y.md` lists, and git-archive snapshots of the three bases. Not opened before this commit: `../sealed/`, `../raw/`, `../extension.md`, `../report.md`, the task file's stage reports. No model was run.

Rule: hit = answering forces the key decision or gap to be stated; partial = same artifact, neighbouring decision (lenient column only); miss = not asked. One question counts toward one key item; one key item may be matched by several questions. Quotes are the question number and its Q line, shortened.

## number-guards-readme-shrink (X 11 Qs, Y 9 Qs)

| Key | X | Y |
|---|---|---|
| NG1 build a 55-word task at all / fold into fo-write-checks | miss | partial: Y8 "Does acceptance require lower total model input ... or only the specified reduction in README words?" (value of the cut, not whether to build or fold) |
| NG2 owner of the "ADR reserved but missing from scope notes" check | partial: X2 "Must this task demonstrate fewer late reservations, or is shorter documentation ... sufficient?" (reservation timing, no owner named) | partial: Y1 "If ideation confirms late number reservations, must this task prevent recurrence ...?"; Y7 "Which fresh FO scenarios will establish that reservation still happens before dispatch ...?" |

Tier 1 A: X 0 hit, 1 partial. Y 0 hit, 2 partial.

## fo-write-checks (X 20 Qs, Y 20 Qs)

| Key | X | Y |
|---|---|---|
| FW1 (T1) form a declined item must carry | partial: X14 "Should decline wording or reasons inside quoted reviewer evidence count toward an FO decline's required fields?" | HIT: Y7 "Must a decline check require only a reason, or also the finding identity, candidate revision, and supporting lines or evidence ...?" |
| FW2 (T1) may a reserved ADR stay unlanded at merge | miss | miss |
| FW3 (T2) the two decisions owe an ADR | miss | miss |
| FW4 (T2) what counts as a reason | miss | miss (Y7 is spent on FW1) |
| FW5 (T2) how the reserved line is recognised in scope notes | partial: X9 "Must reserved ADR: NNNN lines appear in every subsequent dispatch ...?" | partial: Y9 "Does the reserved-number check cover an omitted reservation entirely, or only an existing ADR: NNNN reservation omitted from dispatch scope notes?" |
| FW6 (T2) which checklist must name an amendment | miss | partial: Y11 "Which amendments must a resumed worker's next dispatch checklist name ...?" (which amendments, not which checklist) |
| FW7 (T2) check reaches this repo only after the pin moves | partial: X16 "Does 'only this repo' limit the new checks to this repository's adopted workflows, or should updating the package activate them for other adopters?" | partial: Y15 "Does the repository-only approval authorize these new checks on both adopted workflows, or only the state branch ...?" |
| FW8, FW9 (T2, L) | miss | miss |

Tier 1 A: X 0 hit, 1 partial (FW1). Y 1 hit (FW1), 0 partial. Tier 2 A: X 0 hit, 2 partial (FW5, FW7). Y 0 hit, 3 partial (FW5, FW6, FW7). L: 0 both.

## chat-only-evidence-observer-blind (X 19 Qs, Y 21 Qs)

| Key | X | Y |
|---|---|---|
| CO1 which rules the observer stops judging | HIT: X1 "Which listed FO obligations must leave durable evidence, and which should remain chat-only and leave the observer's checks?" | HIT: Y1 "For each cited rule, should the FO leave durable evidence, or should the observer explicitly exclude that rule as chat-only?" |
| CO2 confirmation record (Sufficiency / Necessity clauses) | HIT: X6 "What must FO record to distinguish its own confirmation of goal sufficiency and minimal necessity from simply citing the validator's conclusion?" | partial: Y7 "For goal sufficiency and minimal necessity, should the observer verify only FO's recorded conclusion and evidence references, or assess whether that conclusion is justified?" (presupposes a record, does not ask what it holds or whether it exists) |
| CO3 acceptance steps in full: chat-only or saved file | HIT: X7 "must durable state contain the complete step/output pairs or can an immutable reference satisfy the record requirement?" | HIT: Y6 "What retained evidence is sufficient to show that the Captain received every acceptance step beside its observed output ...?" |
| CO4 (P1) label found anywhere: stated vs mentioned | partial: X19 "What verdict must a fresh observer return when evidence is present but belongs to another candidate or gate attempt?" (Grounds: presence tests vs "merely present text") | partial: Y20 "Must acceptance include a fresh observer distinguishing compliant, missing, stale and inapplicable evidence ...?" |
| CO5 (T2) `ok` rule on re-run asks | partial: X10 "Which evidence must be renewed when a repair changes the head of an already approved PR?" | partial: Y8 "Can evidence first committed after an action satisfy a rule requiring a check or presentation before that action?" |
| CO6 (T2, L) | miss | miss |

Tier 1 A: X 3 hits (CO1, CO2, CO3), 1 partial (CO4). Y 2 hits (CO1, CO3), 2 partial (CO2, CO4). Tier 2 A: X 0 hit, 1 partial. Y 0 hit, 1 partial. L: 0 both.

## delivery-gate-settles-skipped-checks (X 18 Qs, Y 20 Qs)

| Key | X | Y |
|---|---|---|
| DG1 settle SKIPPED/NEUTRAL (with floor) or adopter-declared list | HIT: X1 "What evidence makes a skipped check 'by design': GitHub's required-check decision, a successful adopter aggregate, or explicit adopter approval?" (X9 also asks the floor: "Can delivery pass when every returned check is SKIPPED or NEUTRAL and no check actually succeeded?") | HIT: Y1 "Should a required check concluding SKIPPED pass whenever GitHub considers it satisfied, or must the repository separately establish that skipping was intentional?" |
| DG2 mistaken skip beside a successful sibling newly passes, no skip name shown | partial: X15 "What evidence of accepted skips must appear in the printed summary and saved merge-ask record?" (shows the skip name; does not ask about the mistaken-skip class) | HIT: Y19 "Must acceptance demonstrate that a deliberately skipped child check remains blocked when its aggregate fails to validate the skip?" (Grounds: "accidental omissions remain blocked"); Y15 also asks the summary |
| DG3, DG4 (T2, L) | miss | miss |

Tier 1 A: X 1 hit, 1 partial. Y 2 hits, 0 partial. L: 0 both.

## special-role-calls-fire-when-needed (X 23 Qs, Y 21 Qs)

| Key | X | Y |
|---|---|---|
| SR1 ship the review-round count as slice 2 | partial: X2 "Which judgment signals require a call, rather than merely asking the FO to consider one?" | partial: Y1 "Which judgment-based triggers must create an owed consultation even when the script reports zero events?" |
| SR2 threshold: four passes or three | partial: X11 "Should the two existing calls described as 'third repair cycle' count without rewriting their original records?" | partial: Y4 "Should repeated new gaps in the same file trigger consultation even when each finding is below the threshold for another repair?"; Y10 same "third repair cycle" question as X11 |
| SR3 reviewer cases no count sees (authority change, reversed ruling, new surface) | HIT: X8 "Must a reversal of an accepted Captain ruling trigger consultation when it occurs in a new task rather than an amendment ...?"; X7 "Which changes marked Supersedes: none must still trigger independent assurance?" | HIT: Y5 "Does every change to merge, authority or irreversible-action rules owe an Engineering Reviewer call, or only changes with a disputed claim ...?"; Y6 "Must a proposed design that reverses an earlier Captain ruling trigger consultation before approval ...?" |
| SR4 Fable signals, SR5 ADR 0021 D1, SR6 counts not phrases, SR7 stage-2 spend (T1, L) | miss (X19 asks a spending limit for Opus calls, not the Fable choice or ADR 0021 D1) | miss |
| SR8 (T2) what a "review round" is | HIT: X6 "What counts toward 'two or more review rounds finding new gaps' when external review verdicts and validation repair cycles occur in the same task?" | HIT: Y8 "Which review events count toward a circling trigger when external-review rounds, validation returns and Stage Report cycles describe different sequences?" |

Tier 1 A: X 1 hit (SR3), 2 partial. Y 1 hit (SR3), 2 partial. Tier 1 L: 0 both. Tier 2 A: X 1 hit, Y 1 hit.

## Totals per list (X and Y are not yet mapped to arms)

| | X | Y |
|---|---|---|
| Questions | 91 | 91 |
| Tier 1 askable (13 items): strict hits | 5 | 6 |
| Tier 1 askable: partial items (lenient column adds) | 6 | 6 |
| Tier 1 askable: lenient total (hit + partial) | 11 | 12 |
| Tier 1 L (4 items) strict / partial | 0 / 0 | 0 / 0 |
| Tier 2 askable (7 items): strict hits | 1 | 1 |
| Tier 2 askable: partial items | 3 | 4 |
| Tier 2 L (5 items) strict / partial | 0 / 0 | 0 / 0 |
| Ungrounded questions | 0 | 0 |
| Grounded non-hit questions per strict hit (all tiers) | 85 / 6 = 14.2 | 84 / 7 = 12.0 |

Tier 1 askable per task (strict): NG 0/0; FW X 0, Y 1; CO X 3, Y 2; DG X 1, Y 2; SR X 1, Y 1.

## Ungrounded check

Snapshots from `git archive` of bases c60e89e1 (number-guards, fo-write-checks), 5a951034 (chat-only), 891a9a24 (delivery-gate, special-role), each extracted to an empty directory under /tmp/blind-snap. Method: every backticked file path was tested for existence (paths written relative to `kc-dev-flow-2/` resolve there), every backticked symbol and every quoted phrase was grepped in the snapshot (whitespace and markdown punctuation normalised); the leftovers were read by hand. Result: 0 ungrounded questions in X and 0 in Y. Quotes that do not appear in the snapshot are all Story quotes (the seed text is not in the snapshot); each recurs in the other list of the same task, so I took them as resolving in the story. Spot-checked descriptions of code against the snapshot: `ci_problem()` rejects every non-SUCCESS entry, `pr_facts()` requests `mergeable` but not `mergeStateStatus`, `role_triggers.cleared()` requires the literal `Cycle 3`, `check()` prints "N event(s) read". Limit: existence plus these spot checks, not a re-derivation of all 182 descriptions.

## Judgement calls a reader should know about

- Y7 (fo-write-checks) scored a hit for FW1 because it asks for the full set of fields a decline must carry; a stricter reader could call it partial (it names "not now" as an accepted reason, which is nearer FW4).
- CO2 for Y (Y7) and DG2 for X (X15) sit on the hit/partial line; both were scored partial. Scoring them hit would add one hit to Y (CO2) and one to X (DG2).
- Partials are cheap to hand out where a question names the right artifact; the strict column is the one to rely on.
- The key file is named in the checklist as `blind/scores.md`; `READER.md` says `scores-<id>.md`. This file is the checklist's name.
