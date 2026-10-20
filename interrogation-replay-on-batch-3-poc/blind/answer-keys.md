# Answer keys for the blind second reader (five batch-3 tasks)

Built only after all ten runs were saved. Source for every item: the archived task under
`/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/<task>.md`
(read only). The story each arm was given is the task's first committed seed (title, intro, `## Scope`).

## How to read a key item

- Tier 1 (assigned key): a Captain decision (D-item, amendment, residual or waiver he accepted) or a P1 / roborev High finding that was a design gap.
- Tier 2 (secondary, below the assigned bar): a Codex P2, engineering-reviewer adjust item, validation Needs decision or Deferred risk that was a design gap. Score tier 2 in its own column; do not mix it into the tier 1 count.
- `Askable: A` = the question could have been asked before the build from the seed story plus the code snapshot. `Askable: L` = it could not: the cause is named (a refused edit, a waiver, a Captain phrase or scope addition that came later, a finding about text or code that did not exist yet). Score L items too, but report them apart.
- Not in any key: Polish findings, false positives, and stylistic items. A question that matches them is not a hit.

## Scoring rule (the first run's rule, unchanged)

hit = answering the question forces the key decision or gap to be stated; partial = same artifact, neighbouring decision (counted only in a lenient column); miss = not asked. One question counts toward one key item. Ungrounded = a question whose Grounds line cites nothing that resolves in the snapshot or the story. Recreate a snapshot with `git -C <repo> archive <base> | tar -x` into an empty directory outside every repository (bases are in `READER.md`).

---

## number-guards-readme-shrink (base c60e89e1)

No P1, no roborev High (Codex round 1 clean; roborev:865 clean). The Captain's ruling on both D-items was 「照建議」 at the ideation gate.

| Key | Tier | Source | Decision or gap | Askable |
|---|---|---|---|---|
| NG1 | 1 | D1, `## Unresolved decisions` | Build a 55-word task at all (the passage is 745 words, only three clauses are cuttable because only three script messages tell the reader the next step), or fold the cuts into `fo-write-checks` so one README edit carries both, which couples two gates | A |
| NG2 | 1 | D2, `## Unresolved decisions` | Who owns the "ADR number reserved but missing from the dispatch scope notes" check (8 of 11 implementation-1 records lack the line): `fo-write-checks` at dispatch write time in `dispatch_records.py`, or `number_guards.py`; until it lands the Reserve clause cannot shrink | A |

## fo-write-checks (base c60e89e1)

No P1, no roborev High (roborev:866 and 868 clean; roborev:870 verdict pass). The Captain's ruling on D1 and D2 was 「照建議」 at the ideation gate; the delivery gate accepted the declines into `fo-write-checks-followups`.

| Key | Tier | Source | Decision or gap | Askable |
|---|---|---|---|---|
| FW1 | 1 | D1, `### Unresolved decisions for the Captain` | What form a declined item in a gate summary must carry: a bracketed reason `<class>, <finding> (<reason>)` held at `delivery_gate.py check` (A), a bracket or `because`, a dash form, or leave it to the observer (D) | A |
| FW2 | 1 | D2 | May a reserved `ADR: NNNN` stay unlanded when the PR merges: hold the merge until the file lands or the line is deleted, or accept a written `parked` form (merge-gatekeeper kept 0023 reserved by amendment) | A |
| FW3 | 2 | validation-1 finding 1, Needs decision | D1 and D2 are decisions that owe an ADR (Decision records rule: one record per decision with the decider's words); the task cannot reserve the number itself | A |
| FW4 | 2 | Codex P2, Feedback Cycle 1 (1); validation Deferred risk 4 | What counts as a reason in a declined item: `unreasoned_items()` dropped an item with fewer than three tokens, so `Declined: Polish, typo.` passed; a two-word bracket proves a bracket, not a reason | A |
| FW5 | 2 | Codex P2, Feedback Cycle 1 (2); validation-2 Deferred risk 2 | How the reserved line is recognised in the scope notes: an unanchored search let a prose mention such as "does not use ADR: 0020 because ..." count as the reserved line | A |
| FW6 | 2 | validation Deferred risk 5 | Which checklist must name a Captain amendment: any `amendment N` phrase in any checklist of the task folder satisfied the check, though the story says "the next dispatch's checklist" | A |
| FW7 | 2 | validation Deferred risk 3 | The laws check reaches this repository only after `dev2-laws.yml` is re-pinned to a release holding the change; until then the FO-run scripts are the only moment the check fires | A |
| FW8 | 2 | Codex P2, Feedback Cycle 2 (1) | Grammar of the reason bracket: the regex took the innermost parentheses, so a reason that itself contains parentheses (`... (the foo() call is redundant)`) was held as reasonless | L (visible only once the regex was written) |
| FW9 | 2 | Codex P2, Feedback Cycle 2 (2) | Grammar of an amendment list in a checklist: `amendments 1, 2, and 3` named only 1 and 2 | L (visible only once the list parser was written) |

## chat-only-evidence-observer-blind (base 5a951034)

One P1 (Codex review:5573330509, cycle 1); roborev:897 and 903 clean (an earlier run, roborev:895, is not described in the task). The Captain's ruling on D1 to D3 was 「照建議」 at the ideation gate.

| Key | Tier | Source | Decision or gap | Askable |
|---|---|---|---|---|
| CO1 | 1 | D1, `### Needs decision` | Which rules the observer stops judging (acceptance steps in full, package and workflow-checkout runs, answering a Captain question, `--names`, the four-field assessment) while the rest are replayed, read or recorded | A |
| CO2 | 1 | D2 | The confirmation record: `Sufficiency:` and `Necessity:` clauses held by `delivery_gate.py` (presence only), or no record and the rule listed as not judged | A |
| CO3 | 1 | D3 | Acceptance steps in full: accept as chat-only, or FO saves the observed output as a file passed to `gate prepare --reference` so the Captain's digest covers what he was shown | A |
| CO4 | 1 | Codex P1, `### Feedback Cycles`, Cycle 1 | `clause()` finds the label anywhere, so prose that only mentions `Sufficiency:` or `Necessity:` (for example the check's own diagnostic pasted back) passes the hold and the saved record then reads `ok` to the observer: what makes a clause "stated" rather than mentioned | A |
| CO5 | 2 | validation-1 Deferred risk | The observer's `ok` rule "`time` before the ask's briefing commit" fails on real data: re-run asks come after the briefing commit, and the skill gave no verdict for which of several `merge/ask-N.json` counts | A |
| CO6 | 2 | validation-2 Deferred risk | After the P1 fix the anchor treats an abbreviation (`e.g. Necessity: y`) as a stated clause and does not read a bulleted or bold label | L (follows from the fix) |

## delivery-gate-settles-skipped-checks (base 891a9a24)

No P1. roborev:914 raised a High that validation judged false (see "Not in key"). The Captain's ruling on D1 was 「批准」 at the ideation gate; at delivery he accepted the engineering-reviewer's two residuals into `delivery-gate-settles-skipped-checks-followups`.

| Key | Tier | Source | Decision or gap | Askable |
|---|---|---|---|---|
| DG1 | 1 | D1, `## Needs decision` | Settle SKIPPED and NEUTRAL (with a floor: at least one check finished SUCCESS), or make adopters declare which checks may skip; settling reverses the SKIPPED/NEUTRAL clause of merge-gatekeeper AC-1 and changes what "CI" means in ADR 0023's safeguards | A |
| DG2 | 1 | `reviews/engineering-reviewer-1.md` (residuals accepted by the Captain at the delivery gate) | A job skipped by mistake while a sibling job succeeds (a fan-in job without `always()`; an adopter with no fan-in; a web Release Please PR whose release job is skipped) newly passes into a carried merge with no skip name shown to the Captain; the floor is not a guard against that class | A |
| DG3 | 2 | engineering-reviewer adjust item 1; Feedback Cycle 1 | The docstring claims a check run its repository skips "by design" settles, but the code settles every SKIPPED and NEUTRAL check (an absolute with no enforcement point) | L (wording written by the build) |
| DG4 | 2 | validation Polish, Feedback Cycle 1 | `test_settling_a_check_adds_no_gh_call` compared the candidate with itself, so an unconditional `gh` call inside `ci_problem` passed | L (test written by the build) |

## special-role-calls-fire-when-needed (base 891a9a24)

No P1, no roborev High. The Captain's ruling on D1 to D5 was given one by one, all as recommended (「同意」, 「第四輪」, 「Ａ」, 「Ａ」, 「同意」). The seed did not hold the Captain's design direction (backlog gate) or his scope addition (both 2026-10-20, in chat, after the seed).

| Key | Tier | Source | Decision or gap | Askable |
|---|---|---|---|---|
| SR1 | 1 | D1, `## Needs decision` | Ship the review-round count (rounds of external review finding new gaps, read from `pr_watch.py tasks`) as slice 2: it is the only count that catches captain-question-load (P1s across rounds, only two repairs) | A |
| SR2 | 1 | D2 | Threshold for the chief-engineer repair-pass trigger: four passes or three (three adds a false fire; FO's own calls were made at "third repair cycle") | A |
| SR3 | 1 | D3 | The engineering-reviewer cases no count sees (an authority or merge-rule change, a ruling reversed in another task, a new authority surface): accept as judgment, or add an author-declared line such as `Reverses: <gate id | task | none>` | A |
| SR4 | 1 | D4 | Which signals choose Fable for the engineering-reviewer: `profile: prod` or a `db` value on `Surfaces:` only, delivered by the owed line | L (Captain scope addition 「先加第一個，第二個列入評估」, after the seed) |
| SR5 | 1 | D5 | Evaluate ADR 0021 D1 (prod security reviewer fixed on Sonnet): approve a no-model stage 1 now, stage 2 only after its result | L (same scope addition) |
| SR6 | 1 | Captain's design direction at the backlog gate | Triggers come from counts read from structured records (findings, rejected validations, holds, overrides), not from phrase matching | L (Captain phrase 「設計時不應該過度依賴關鍵字，而是可能要依靠犯錯字數觸發，合理嗎？」, after the seed) |
| SR7 | 1 | implementation report, `### Needs decision (Captain)` | After stage 1 found two escapes on one PR: run stage 2 (about 40 USD at assumed prices) or keep ADR 0021 D1; no Captain ruling on it is recorded; the validation briefing leaves it "open for a later decision" | L (depends on stage 1's result) |
| SR8 | 2 | validation F2, Deferred risk | What a "review round" is: reply comments carry their own review ids and would be counted as rounds | A |

## Not in any key (do not count a question as a hit for these)

- delivery-gate-settles-skipped-checks: roborev:914's High (that two `HoldTests` rows "will fail") was a false positive; both rows are a lone check and the floor still holds them (exit 1). The Captain waived it as false.
- All five tasks: Polish findings (an AC text miscount, a test pin missing, a README sentence naming `--help` flags, a PR title), and the implementation-time deviations that touch tests or word counts only.
