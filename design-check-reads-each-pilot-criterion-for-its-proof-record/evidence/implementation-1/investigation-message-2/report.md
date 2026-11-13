# Investigation of RoboRev job 1848

Analysis start: 2026-11-13 19:43:24 Asia/Taipei. Analysis end: 2026-11-13 20:03:18 Asia/Taipei. Source: clock.curr_time UTC readings converted by +08:00.

Both findings reproduce on 9dd03d805d11c0c833699b1247fd11d99a74d52f. No candidate file, commit, PR text or review was changed. PR #866 and job 1848 are FO-supplied context; I did not rerun RoboRev or inspect hosted CI.

Recommendation: do not authorize a distinct-span-only patch as closure of finding 1. The declaration-coverage repair for finding 2 is ready for separate FO authorization, within the existing named files and without a new required line.

## Finding 1 — one snippet supplies two proof fields

Real. Run `python3 -B <scratch>/reference/kc-dev-flow-2/scripts/design_surfaces.py check <scratch>/repro/log-only/task.md` and the same command for `command-only`: both exit 0. The first criterion contains only `exit 0` plus a log-path code span; the second contains only `exit 0` plus a command code span. Outputs: repro/log-only/candidate.log and repro/command-only/candidate.log. reproduce.py regenerates the synthetic inputs; repro.json records exact commands, exits and outputs.

The overlap is literal: PROOF_COMMAND accepts any nonempty code span, and PROOF_PATH can match inside that span. A path by itself therefore supplies both cues; a command containing scripts/check.py does the same. Merely requiring unequal match positions is insufficient because the command match contains the path match. The tested proposal requires non-overlapping spans.

The smallest tested non-overlap probe adds 4 lines and removes 0 (distinct.diff). It changes both bare examples from exit 0 to 1 without adding a required line, label or order. It does not close the general missing-field problem: `Evidence command: exit 0; <one log code span>`, `Evidence command: exit 0; <one command code span>` and two path-only code spans still exit 0. The word command supplies a separate match without recording a command; two log spans can supply the two roles.

It also rejects an otherwise complete record: `ran <python3 scripts/check.py > evidence/result.log in one code span>; observed exit 0` changes from 0 to 1. The command and its output destination are both written, but belong to the same code span. This is a false refusal under the approved no-label/no-order syntax.

All 501 fresh snapshot tasks retain the same output and exit in both check modes under the non-overlap probe. The two Stop-condition designs remain run1 exit 1 (AC-3 only) and run2 exit 0. The existing 248-test suite also passes with this insufficient probe, so that suite alone does not establish closure.

Authority: the non-overlap mechanism needs no new line, so it does not itself trip the Stop condition about a mandatory line. It is nevertheless not a sufficient repair. The approved FAQ explicitly accepts the word command or a code span and acknowledges a path-as-command. A stronger field-role definition would change that accepted recognition contract; obtain the Captain's ruling before treating it as an implementation repair. FO can instead retain/decline the already accepted weak-recognition risk, with these counterexamples stated. I found no complete small repair that both establishes the stronger role claim and preserves the approved loose grammar.

## Finding 2 — criterion collection and proof coverage use different grammars

Real. Run `python3 -B <scratch>/reference/kc-dev-flow-2/scripts/design_surfaces.py check <scratch>/repro/inline-missing/task.md`: exit 0, despite an inline bold AC-1 and no record. Output: repro/inline-missing/candidate.log.

`check_criteria()` searches AC_DECLARATION anywhere on every raw line in the selected Acceptance criteria section: `\*\*(AC-[A-Za-z0-9]+)[^*\n]*\*\*`. It includes inline text, tables/headings, later IDs on one line and fenced text. `proof_gaps()` first removes backtick-fenced content, then uses criterion_blocks(), whose DECLARATION_LINE is anchored at line start after optional whitespace, quote/list prefixes. That reader takes the first declaration on a line and stores one block per ID. The collected set and the checked blocks can therefore differ.

A tiny raw-tokenizer prototype adds 5 lines and removes 1 (all-raw.diff). It reads every raw declaration, but wrongly allows a real criterion's record to come from a fenced example. The existing test_fenced_record_does_not_complete_a_criterion fails under it. Do not use that shortcut.

The smallest tested repair preserving the current fenced-record exclusion adds 21 code lines and removes 1: a proof-only reader uses AC_DECLARATION for declaration identity and range boundaries, preserves IDs inside fences (including marker lines), removes fenced record text, and retains heading boundaries and the existing duplicate-ID policy. It leaves check_criteria(), criterion_blocks() and amendment readers untouched. Code-only patch: all-safe.diff.

The complete proposed regression/fixture patch is declarations-repair.diff: design_surfaces.py +21/-1; test_design_surfaces.py +16/-0; test_sd_dispatch.py +1/-1; total +38/-2. The CLI parity fixture gains its proof outside its fence. No workflow, version, ADR, required field label or mandatory line is added.

The new regression method fails on the exact candidate in 8 subcases, and the proposed tree passes 249 tests (4 skipped) plus the real model-free SD dispatch harness. Commands/exits/logs are in commands.json. Across the 501-task, both-mode comparison, this proposal changes no output or exit; every ID recognized by the old collector is visited by its proof reader (0 uncovered IDs). Both Stop-condition replays remain 1/0.

Authority: this is coverage repair inside the approved requirement to read every criterion and the already named files; separate FO repair authorization is sufficient. Restricting the older collector to line-start declarations instead would change accepted syntax and could impose the new required declaration line the Stop condition sends to the Captain. That is not the proposed repair.

## Siblings and remaining recognition limits

- Placement family, reproduced and covered by the declaration proposal: heading/table/nonstandard-bullet IDs, a second ID on one line, the first ID borrowing the second ID's record, and IDs inside a code fence or on its marker line.
- Field-role family, reproduced and not closed by non-overlap: the standalone word command, two path-only spans, an exit token only inside the command, and the output-path cue read from the bold declaration while the command cue is stripped from it. These expose lexical role limits; they do not prove any command ran.
- Fenced-record boundary: a tilde-fenced example still supplies fields because the existing FENCE matcher recognizes backticks only. Neither proposed change broadens that shared helper. A guard-local follow-up would need its own authorization.
- Falsifier boundary: `Falsifier: fabricate Evidence: ...` resumes recognition at Evidence: and passes. This is the existing explicit restart heuristic, not execution proof; a stronger clause grammar belongs with finding 1's recognition decision.
- Duplicate IDs retain last-block-wins behavior; a later empty occurrence overwrites an earlier complete record. No new duplicate policy is proposed.
- Eligibility fields, canonical approval-record limitations and the five older status-pattern consumers from implementation-1-message-1 are unchanged; this investigation does not claim to repair them.

## Corpus and scope limits

Snapshots were read from the same three authorized sources, with 246/155/100 total tracked flat/archive task files (501 total). They are fresh snapshots with the same counts, not claimed byte-identical to the deleted private scratch from the previous run. Only aggregate counts are archived. Check and check --seed were exercised via frozen modules' main(argv) entrypoints. The raw-tokenizer shortcut adds one diagnostic to one already failing private task but changes no exit; the recommended and distinct-span probes change none.

Not archived (private): adopter snapshots, source paths/revisions and per-file comparison output; reproduce: `git -C <adopter-state-checkout> archive HEAD | tar -x -C <scratch>/corpora/<label>`, then run compare.py on frozen candidate/probe trees. The original unmatched 137-Pilot corpus remains outside this reproduced set.

The declaration proposal touches one of the two test files shared with budget-form-counts-ideation-rounds-and-times-each-round: test_sd_dispatch.py's fenced declaration parity case. It also touches the already approved design_surfaces.py and test_design_surfaces.py. No shared production-code file with that sibling is added.

All patches are investigation artifacts in scratch/state evidence. Candidate 9dd03d805 remains clean and unchanged; applying any repair, pushing product changes and revising PR #866 await separate authority.
