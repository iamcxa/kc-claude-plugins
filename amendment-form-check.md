---
title: design_surfaces.py does not check a Captain amendment's own form
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: validation
gates:
    version: 1
    records:
        - id: gate:amendment-form-check:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:amendment-form-check-backlog-1
              briefing:
                id: briefing:amendment-form-check:backlog:attempt-1:revision-1
                digest: sha256:14cbf6e42f10d8251d22634c12e4fe1cfec16a908b4d0566a24a3587f0de3797
                room-ref: ./amendment-form-check/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:amendment-form-check:backlog:1
                briefing: briefing:amendment-form-check:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-16T03:13:50.642844Z"
                decision: approve
                reason: 'Captain approved batch 1 (「批准」): schedule as Pilot and enter ideation; as the gate question states, this accepts profile pilot and five parallel ideations with dev2-laws-check''s design read by the other four for overlap.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:amendment-form-check:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:amendment-form-check-ideation-1
              briefing:
                id: briefing:amendment-form-check:ideation:attempt-1:revision-1
                digest: sha256:2e8d81538c69eb6deb407ae7bf99dc5cb51c93b679b558b87b12e34433de6bd5
                room-ref: ./amendment-form-check/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:amendment-form-check:ideation:1
                briefing: briefing:amendment-form-check:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-16T04:17:15.555386Z"
                decision: approve
                reason: Captain approved batch-1 ideation (「准」) after FO presented all five gates together; as the gate question states, this accepts each decision as recommended (and FO's stated change where named), the batch-1 implementation order, and is the push and Draft PR grant for the implementation worker.
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-16T03:14:35Z
worktree: .worktrees/spacedock-ensign-amendment-form-check
pr: iamcxa/kc-claude-plugins#650
---

Filed from a learn package-issue candidate the Captain approved (「好」, chat, 2026-10-15). The observer reports on `delivery-gate-verdict-form` and `fo-lifecycle-mod` found FO-written amendments that break the README `## Captain amendments` rules, and `scripts/design_surfaces.py check` passed both tasks.

## Scope

- An amendment `Design:` line carries FO's own sentences beyond the Captain's words and his `Asked:` question (delivery-gate-verdict-form amendment 2; acceptance criterion AC-12 then attributed one of them to the Captain). Rule: "FO adds no words of its own".
- Replacement criteria AC-9 to AC-14 under amendment 2 lack "Amended by Captain, amendment N" (delivery-gate-verdict-form). Rule: "writes any replacement as a new `**AC-N**` ... that says 'Amended by Captain, amendment N'".
- A `Supersedes:` line reads `none` while criteria were moved under that amendment (fo-lifecycle-mod amendments 3 and 6). `design_surfaces.py` checks only that a superseded id is no longer declared, not that a moved criterion is named in `Supersedes:`.
- Candidates for ideation to keep or drop; the first is a judgement of meaning and may stay with the observer.

## Design

The prototype named below lives on a temporary copy of origin/main `1383c911` under `/tmp`; no repository file, branch or commit changed, and the scratch scripts that read adopter state (read-only) are machine-local, so the committed tests carry one fixture per case instead of a corpus run.

### Ruling

A script checks two of the three breaks, the two that are about where text sits: a moved criterion its `Supersedes:` line does not name, and a replacement no criterion marks with "Amended by Captain, amendment N". FO's own words in `Design:` stay with the observer, because no text rule tells a pointer from a paraphrase (measured below).

### Chain check (read 2026-10-16)

- **Spacedock** 0.27.2: `spacedock status --help` has no amendment or supersede flag (`grep -i 'amend\|supersed'` over it printed nothing); ADR 0005 records that Spacedock reads no task body at dispatch or `gate prepare`. Nothing to reuse.
- **kc-dev-flow-2** at origin/main `1383c911` (0.23.0): `scripts/design_surfaces.py` `check_amendments` refuses an entry with no `Captain:` line and a superseded id still declared. Nothing else reads an entry: `git grep -n 'Superseded text\|Amended by Captain' origin/main -- kc-dev-flow-2/scripts kc-dev-flow-2/skills kc-dev-flow-2/extensions kc-dev-flow-2/references` finds the README prose (`references/sd/workflow.md`) and two test fixtures, never the script. `skills/observer/SKILL.md` reads the README rules and found all three breaks at archive, after the PR.
- **Sibling adopters**: relay, qnow and subspace-web hold no copy of the script (`find` for `design_surfaces*` under the qnow-adopt-dev2, relay and subspace-web checkouts, 2026-10-16, found one worktree copy of the package itself). Their archived tasks are the corpus below.
- **Past rulings**: ADR 0005 is the area; this extends its closing sentence ("`check` exits 1 for an entry without `Captain:` and for a superseded id still declared"). `git -C <state> grep -n 'Override:'` (2026-10-16) hits only prose in archived designs; none bears on amendments.

### Existing-code capability check

Boundary: `check_amendments` plus the README `## Captain amendments` form. Completeness: the two existing refusals work through their journey (tests and the `--ac-scan` parity case in `scripts/test_sd_dispatch.py`). Need, observed 2026-10-16 by running origin/main's `design_surfaces.py check` on the committed `spacedock-state/dev2:_archive/delivery-gate-verdict-form.md` and `_archive/fo-lifecycle-mod.md`: both print `design surfaces presentable` and exit 0, while the observer reports on both name the breaks. The change extends the one function; it adds no script.

### The corpus, read only (2026-10-16)

40 task files with real amendment entries (one copy per file name, largest kept) across this workflow, relay, qnow and subspace-web: 67 entries, 31 of them superseding. Candidate refusals that origin/main does not make: 8 errors on 6 tasks.

| Rule | Entries refused | Cause |
| --- | --- | --- |
| Moved criterion not named by `Supersedes:` | 2 | `fo-lifecycle-mod` amendment 3 (AC-1 to AC-7 moved, line says `none`: the filed break); `staff-multi-branch` amendment 1 (AC-6 and AC-7 partly moved, ids reused in place) |
| Replacement without the phrase | 6 | `delivery-gate-verdict-form` amendment 2 (six replacements, the filed break); `accept-branch-invitation` amendments 1 and 2 (replacements say "replaces AC-13" and "replaces AC-19", no phrase); `booking-outcomes` amendment 1 (AC-1 moved, no replacement criterion at all); `owner-sees-all-feedback-room` amendment 3 and `staff-multi-branch` amendment 1 (criteria moved to a new task, no replacement belongs here) |

The last two are legitimate. Without a way to say "no replacement" the check would push a worker to invent a criterion, so the escape is part of this design: `Supersedes: AC-1, AC-2 (no replacement: moved to a new task)`. A scratch copy of `owner-sees-all-feedback-room` with that line no longer draws the refusal. Rule 1 refused no entry that was fine (0 of 67).

The `Design:` line: 35 entries carry a value other than `none`; 1 is a verbatim quote of text in the file, 34 are FO sentences (a name for the paragraph, or a summary of it). Any text rule flags 34 of 35, including every legitimate pointer the README form allows ("the design paragraph it overrides"), so the first break stays with the observer.

### PRFAQ

**Press release.** An amendment record that breaks the README form now stops at the checker instead of at the observer after the PR. `check` refuses an entry that holds criteria its `Supersedes:` line does not name, and an entry that supersedes criteria when no criterion says "Amended by Captain, amendment N" and the line does not say "no replacement". FO's own words in `Design:` remain the observer's to read.

**FAQ.**
- *Why not check `Design:`?* 34 of 35 non-`none` values in the corpus are FO prose by the form's own allowance; a verbatim rule cannot tell the pointer from the paraphrase. Changing the form so `Design:` must quote its paragraph would rewrite almost every entry and is the Captain's, not a script's.
- *What is a replacement, to the script?* It does not decide. It asks that at least one criterion, in `## Acceptance criteria` or in the moved text of another entry, carries the phrase for this amendment's number. That covers a twice-amended task: a criterion written under amendment 1 and later moved under amendment 2 still counts for amendment 1 (the replay of `delivery-gate-verdict-form` amendment 1 relies on it). It does not prove every replacement is marked; five of six marked passes.
- *Why the exact phrase and not "replaces AC-N"?* The README already says the criterion "says 'Amended by Captain, amendment N'"; accepting a variant would change that rule, and two corpus entries use the variant.
- *Who repairs a refusal?* For a moved criterion the entry does not name, FO edits its own `Supersedes:` line to add the ids (ids, no words; FO wrote `none` before the worker's redo existed). For a missing phrase, the worker who wrote the replacement adds it, or FO adds `no replacement`. Both return as the existing repair finding.
- *What does it not see?* A skipped move (amendment 6 of `fo-lifecycle-mod` changed AC-9 and AC-11 in the report while the section stayed byte-identical and nothing was moved), which ADR 0005 already names as `check`'s limit; and a worker who types `no replacement` falsely.

```mermaid
flowchart TD
  C[Captain amends in his words] --> F[FO appends one entry: Captain, Asked, Supersedes, Design]
  F --> W[Next worker moves each superseded criterion into the entry and writes replacements]
  W --> K{design_surfaces.py check, run by the worker, and by FO before gate prepare}
  K -->|entry holds a criterion Supersedes does not name| X1[exit 1 names the entry and the ids]
  K -->|ids superseded, no criterion says Amended by Captain amendment N, no 'no replacement'| X2[exit 1 names the entry]
  K -->|superseded id still declared, or no Captain line: unchanged| X3[exit 1 unchanged]
  K -->|none of these| P[pass]
  X1 --> FB[repair finding through feedback]
  X2 --> FB
  X3 --> FB
  FB -->|FO edits own Supersedes line, or the worker adds the phrase| W
  P --> O[Observer at archive: FO words in Design, a skipped move, what the script cannot see]
  F -.->|FO sentences beyond his words| O
```

### Replay on the two archived tasks

Method: `git -C <state> show spacedock-state/dev2:_archive/<task>.md > /tmp/x.md`, then `python3 <package>/scripts/design_surfaces.py check /tmp/x.md`; base is origin/main's script, candidate is the prototype.

| Task | Base | Candidate |
| --- | --- | --- |
| `delivery-gate-verdict-form` | exit 0 | exit 1: amendment 2 supersedes AC-1, AC-2, AC-3, AC-5, AC-6, AC-7, AC-8 but no criterion says "Amended by Captain, amendment 2" (amendment 1 is not named: AC-8 carrying the phrase sits in amendment 2's moved text) |
| `fo-lifecycle-mod` | exit 0 | exit 1: amendment 3 holds AC-1 to AC-7 in the entry but its `Supersedes:` line does not name them (amendment 6 is not named: nothing was moved under it) |

Observed mutations of the prototype on the same two files: dropping the moved-criterion rule leaves `fo-lifecycle-mod` at exit 0; dropping the replacement rule leaves `delivery-gate-verdict-form` at exit 0; dropping the chain rule adds a second line (amendment 1) to `delivery-gate-verdict-form`; dropping the escape makes the scratch copy with `no replacement` exit 1.

### Change, in files

- `kc-dev-flow-2/scripts/design_surfaces.py`: `check_amendments` gains the two rules. A criterion counts as moved when `**AC-N**` appears on any entry line that does not start with `Captain:`, `Asked:`, `Supersedes:` or `Design:`; this does not depend on the `Superseded text:` label, and its limit is a `**AC-N**` bold written in a continuation line of `Asked:` or `Design:`, which would read as moved text (none in the corpus). The error lines are one per entry, ids listed.
- `kc-dev-flow-2/scripts/test_design_surfaces.py`: new cases and mutations; the `AMENDMENT` fixture (`Supersedes: AC-2`, no replacement) and the cases built from it change deliberately.
- `kc-dev-flow-2/scripts/test_sd_dispatch.py`: the amendment parity block (the `criteria`/`amendment` fixtures asserting `checked.returncode == 0` for a relocated criterion with no replacement) has the same fixture shape and changes the same way. I did not run it: this machine caches Spacedock plugin 0.27.0 and the binary is 0.27.2, and the test needs `--sd-plugin-root`; CI's pinned root is the proof.
- `kc-dev-flow-2/references/sd/workflow.md`: two edits inside `## Captain amendments`, the `Supersedes:` template line and the check paragraph. The adopted copies `docs/dev2/README.md` and `docs/dev2-poc/README.md` arrive through the usual sync change after release, not this one.
- ADR draft, no number (FO reserves it): short title `the-amendment-check-refuses-an-unnamed-move-and-an-unmarked-replacement`. Ruling: `check` also exits 1 for a criterion held in an entry that `Supersedes:` does not name and for superseding entries no criterion marks, and `Supersedes:` may say "no replacement". It supplements ADR 0005 and leaves its decision standing. Limit it must state: `check` still cannot see a skipped move or FO words in `Design:`.

### Batch overlap

Read as the four other seeds stand on 2026-10-16 (none has a design yet), so this is from their Scope text.

| File | This task | Other batch-1 task on the same file or check |
| --- | --- | --- |
| `kc-dev-flow-2/scripts/design_surfaces.py` | edits `check_amendments` | `dev2-laws-check` lists `design_surfaces.py check` as an existing law; if its runner executes `check` over `_archive/`, this change's 8 new corpus errors become failures on closed tasks nobody can repair under the rules. Recommend this task lands first, or laws-check runs `check` only on tasks not yet archived |
| `kc-dev-flow-2/scripts/test_design_surfaces.py` | edits | none named |
| `kc-dev-flow-2/scripts/test_sd_dispatch.py` | edits the amendment parity block | `names-check-before-dispatch` and `extension-instruction-reaches-dispatch` follow the existing `dispatch-records-check` entry style and may add entries in the same file, different region |
| `kc-dev-flow-2/references/sd/workflow.md` | edits `## Captain amendments` (net minus 1 word) | `names-check-before-dispatch` (README Stages rule) and `extension-instruction-reaches-dispatch` ("or the README's stage text names it") may add text; `prod-security-review-gates` may edit stage text. All five share one word budget: `lint-skills.py` prints `5495 of 5511` at origin/main, so 16 words remain, and this task adds none |
| `kc-dev-flow-2/scripts/lint-skills.py` (`WORKFLOW_WORD_BUDGET`) | untouched | any task that pushes the README past 5511 must raise it with a reason; two raising it in one batch conflict on the constant |
| `kc-dev-flow-2/scripts/dispatch_records.py` | untouched | belongs to `names-check-before-dispatch` and `extension-instruction-reaches-dispatch`, not here |
| `docs/adr/` | one new ADR, number reserved by FO | `dev2-laws-check`, `prod-security-review-gates` may also reserve; FO reserves in dispatch order |

Order: this task first among those editing `workflow.md` and `design_surfaces.py`, since it is net minus 1 word and changes what laws-check would run; the README tasks then recount against the merged text.

### Words FO reads at each moment

Rule: `len(text.split())` over every passage that instructs a step due at that moment and every script output the step runs, counted the same way for origin/main `1383c911` and the prototype text (learning "Measure the words FO reads at each moment, not one file's size"). Moments are the ones this change touches; the five lifecycle moments in that learning (startup, idle on an open PR, idle on a merged PR, after the archive, the merge ask) read no passage this change edits: both README hunks sit inside `## Captain amendments`.

| Moment | Base | Candidate |
| --- | --- | --- |
| FO records an amendment: README `## Captain amendments` section (heading to `## Affected documents`) | 414 | 413 (template line +6, check paragraph 60 to 53) |
| FO prepares the ideation gate: `check` output on a presentable task | 4 | 4 |
| FO receives a repair finding: `check` output on the two replays | 4 (a silent pass of the break) | 24 and 26, only when a break exists |
| Whole `workflow.md` by `lint-skills.py` | 5495 of 5511 | 5494 of 5511 |

### Limits

- The corpus is 40 files from this workflow and three adopters; I did not check which package versions or models wrote them. It shows the rules refuse no fine entry in it, not that none exists. The 6 phrase refusals were classified by reading each entry (4 breaks, 2 legitimate moves).
- The replacement rule asks for one marked criterion per amending entry, not one per replacement.
- The prototype ran the 22 `test_design_surfaces.py` tests: 20 pass and 2 fail, both on the `AMENDMENT` fixture that has no replacement; `lint-skills.py` and `test_lint_skills.py` pass.
- Cost: `test_design_surfaces.py` already runs as a CI step (`.github/workflows/kc-dev-flow-2-tests.yml`); no new job. The 22 existing tests ran in 0.1 s here.
- Non-goals: reading `Design:`; checking that a replacement is faithful to the Captain's words; seeing a skipped move; any change to `skills/observer/SKILL.md`; any Spacedock change.

## Acceptance criteria

Paths are relative to `kc-dev-flow-2/` in `iamcxa/kc-claude-plugins`; base is origin/main `1383c911` (0.23.0). `<state>` is the `.spacedock-state` checkout on `spacedock-state/dev2`. Traces: AC-1 to the third Scope bullet; AC-2 and AC-3 to the second; AC-4 to all three; AC-5 to the first bullet and the closing line ("the first is a judgement of meaning and may stay with the observer"); AC-6 to the dispatch checklist's per-moment words requirement (root `learning.md`); AC-7 to the CI step that already runs these suites.

**AC-1** An entry that holds a criterion its `Supersedes:` line does not name exits 1, naming the entry and the ids.
Verified by: tests in `scripts/test_design_surfaces.py` for an entry with `Supersedes: none` and `**AC-2**` in its moved text (exit 1, message names the entry and AC-2); `Supersedes: AC-1` with AC-1 and AC-2 moved (names only AC-2); `Supersedes:` naming every moved id (exit 0); a `**AC-9**` bold on the `Captain:` line only (exit 0). Replay: `git -C <state> show spacedock-state/dev2:_archive/fo-lifecycle-mod.md > /tmp/x.md` then `python3 scripts/design_surfaces.py check /tmp/x.md` exits 0 at base and 1 at the candidate with one line naming amendment 3 and AC-1 to AC-7 (observed on the prototype 2026-10-16).
Falsifier: delete the rule; the first test fails and the replay exits 0 (observed: mutant exit 0).
Limit: amendment 6 of that task is not refused, because nothing was moved under it.

**AC-2** Superseding entries with no criterion saying "Amended by Captain, amendment N" exit 1, naming the entry and the superseded ids.
Verified by: tests for an entry superseding AC-2 with a replacement lacking the phrase (exit 1); the same with `Amended by Captain, amendment 1` on the replacement's `**AC-N**` block (exit 0); the phrase for amendment 2 on a criterion does not satisfy amendment 1 (exit 1); the phrase only in the intro line above the first `**AC-N**` of `## Acceptance criteria` does not count (exit 1). Replay: `git -C <state> show spacedock-state/dev2:_archive/delivery-gate-verdict-form.md > /tmp/y.md` then `check` exits 0 at base and 1 at the candidate with one line naming amendment 2 and AC-1, AC-2, AC-3, AC-5, AC-6, AC-7, AC-8 (observed on the prototype 2026-10-16).
Falsifier: delete the rule; the first test fails and the replay exits 0 (observed: mutant exit 0).
Limit: one marked criterion satisfies it; a second unmarked replacement passes.

**AC-3** A replacement later moved under another entry still satisfies the entry that wrote it, and `no replacement` on the `Supersedes:` line waives the rule.
Verified by: a test with amendment 1's replacement carrying the phrase inside amendment 2's moved text, entry 1 passing and entry 2 judged on its own (exit 0 when entry 2 has its marked replacement); a test with `Supersedes: AC-1, AC-2 (no replacement: moved to a new task)` and no replacement (exit 0); the replay of `delivery-gate-verdict-form` prints one line, not two.
Falsifier: remove the other-entry lookup; the replay prints a second line for amendment 1 (observed: 2 lines). Remove the waiver; the waiver test exits 1 (observed on a scratch copy: exit 1).

**AC-4** The rules refuse no entry that was fine at the corpus's own reading, and the legitimate moves are covered by the waiver.
Verified by: at the candidate, the check over the 40-file corpus (reproduced by listing task files with a `## Captain amendments` heading and `### Amendment` entries under `~/conductor/repos` and `~/conductor/workspaces`, one copy per file name, running base and candidate `check` and diffing the error lists) prints 8 new errors on 6 tasks, each in the table under `### The corpus, read only`; the 2 legitimate moves (`owner-sees-all-feedback-room` amendment 3, `staff-multi-branch` amendment 1) are the only entries the waiver is for. Not yet verified at validation: that the 2 legitimate moves clear with the waiver text in place (observed for `owner-sees-all-feedback-room` only).
Falsifier: any corpus entry the rules refuse that a reader of it judges fine and the waiver cannot cover fails this criterion.
Limit: the corpus script is machine-local and not committed; the tests carry one fixture per case.

**AC-5** `check` does not read `Design:`.
Verified by: a test whose entry carries a `Design:` line of FO sentences beyond the Captain's words and passes every other rule exits 0; `git diff origin/main -- skills/observer/SKILL.md` is empty at the candidate.
Falsifier: add a rule that scans `Design:`; the test exits 1 and fails.
Limit: the first break (FO's own words in `Design:`) stays with the observer; 34 of 35 non-`none` values in the corpus are FO prose, so a text rule would refuse nearly all of them.

**AC-6** FO reads no more words than at base at any moment this change touches, and none at the five lifecycle moments.
Verified by: `len(text.split())` as in the learning "Measure the words FO reads at each moment": the `## Captain amendments` section of `references/sd/workflow.md` is at most 414 at the candidate (design-time 413); `python3 scripts/lint-skills.py` prints at most `5495 of 5511` (design-time `5494 of 5511`); `check` on a presentable task prints 4 words at base and candidate; `git diff origin/main -- references/sd/workflow.md` has hunks only inside `## Captain amendments`.
Falsifier: add one sentence to that section; its count passes 414 and the comparison fails. Limit: counts text and script output, not a measured FO session; the failing-path output grows from 4 to 24 or 26 words by design.

**AC-7** The tests that pinned the old fixtures follow, and the suites that run in CI pass.
Verified by: `python3 scripts/test_design_surfaces.py` exits 0 at the candidate (at design time the prototype failed exactly 2 of 22, the cases built on the `AMENDMENT` fixture); `python3 scripts/test_sd_dispatch.py --sd-plugin-root <root>` exits 0 where CI's pinned root is available, with the amendment parity block's relocated-criterion fixture carrying a replacement or the waiver; `python3 scripts/lint-skills.py` and `scripts/test_lint_skills.py` exit 0. The commit message names the fixtures that changed deliberately. Not yet verified: `test_sd_dispatch.py` was not run at design time.
Falsifier: restore the old `AMENDMENT` fixture; the two cases fail.

## Unresolved decisions for the Captain

- **D1: refuse a replacement with no marking phrase, with a waiver written on the `Supersedes:` line (recommended), or refuse only a moved criterion the line does not name?** The two parts are coupled because the waiver exists only to make the replacement rule safe. Recommended: both, because 4 of 31 superseding entries in the corpus broke the written replacement rule in two weeks and the observer saw it only after the PR. What gets worse: every FO must know one more token on the `Supersedes:` template, a worker can type `no replacement` to skip the rule falsely, and the README form (which ADR 0005 fixed) changes by 6 words. Without the replacement rule: no waiver, one fewer ADR sentence and no README form change; what gets worse: the `delivery-gate-verdict-form` break stays visible only to the observer, after the PR.

## FO alignment

Alignment: not needed before ideation; the Captain approved filing it.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none

### Feedback Cycles

- Cycle 1 (FO, 2026-10-16): Codex review round 1 on #650 58eb738e (review:5543112471) left three P2, all to fix (rounds 1 and 2 fix every finding); investigation first, then FO fix authorization, then a fresh validation recheck. The validation of 58eb738e dispatched before this finding continues.
  - P2 `scripts/design_surfaces.py`: the superseded-id set is read from the whole `Supersedes:` value, so an id inside the `no replacement` reason counts as named.
  - P2 `scripts/design_surfaces.py`: the 'Amended by Captain, amendment N' marker is matched on any later line, so evidence prose can satisfy it.
  - P2 `scripts/design_surfaces.py`: a bold AC id anywhere in a moved block counts as a moved criterion, so evidence citing another criterion fails a valid move.
- Cycle 2 (FO, 2026-10-16): Codex review on #650 3bc8f647 (review:5543218466) left one P2, to fix (rounds 1 and 2 fix every finding); investigation first, then FO fix authorization, then a fresh validation recheck.
  - P2 `scripts/design_surfaces.py`: `section()` ends the acceptance-criteria section only at a line starting `## `, so an indented sibling heading such as ` ## Notes` lets bold AC-shaped lines from that later section satisfy the replacement-marker check.

## Stage Report: ideation

- DONE: A design (PRFAQ and Mermaid) for which of the three amendment-form breaks a script can check (FO's own words in Design:, replacement criteria without 'Amended by Captain, amendment N', a Supersedes: line that does not name criteria moved under it) and which stays with the observer, with a replay on delivery-gate-verdict-form and fo-lifecycle-mod (archived)
  `## Design`: script checks the moved-criterion and replacement-phrase breaks, observer keeps `Design:` (34 of 35 non-`none` values are FO prose). Replay on both archived tasks: origin/main script exit 0, prototype exit 1 with one line each; four prototype mutations each change the result. Prototype on a `/tmp` copy; no repository file changed. Chain: Spacedock, kc-dev-flow-2, adopters checked, ADR 0005 and `Override:` lines read.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch-1 task (prod-security-review-gates, dev2-laws-check, extension-instruction-reaches-dispatch, names-check-before-dispatch, amendment-form-check) that changes the same file or check, so FO can order implementation
  Seven rows including `design_surfaces.py` (laws-check hazard: 8 new corpus errors on closed tasks), `workflow.md` and `lint-skills.py` (shared 16-word margin), `test_sd_dispatch.py`; the other four tasks are seeds with no design yet, so the rows rest on their Scope text.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  `### Words FO reads at each moment`: 414 to 413 (amendments section), 4 to 4 (`check` on a presentable task), 4 to 24 and 26 on a failing path, `lint-skills.py` 5495 to 5494; the five learning moments read no edited passage.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  `## Acceptance criteria` AC-1 to AC-7 and one decision D1 (recommendation, what gets worse each way). `python3 /tmp/kdf2_main/kc-dev-flow-2/scripts/design_surfaces.py check <task>` (origin/main `1383c911` script): `amendment-form-check.md: design surfaces presentable`, exit 0.
  - AC-1: replay observed (fo-lifecycle-mod base 0, prototype 1, mutant 0); committed tests not yet written.
  - AC-2: replay observed (delivery-gate-verdict-form base 0, prototype 1, mutant 0); tests not yet written.
  - AC-3: chain mutant adds a second replay line and waiver mutant exits 1, both observed; tests not yet written.
  - AC-4: corpus run observed (40 files, 67 entries, 8 new errors on 6 tasks); waiver clearing observed for one of two legitimate moves; the other not yet verified.
  - AC-5: not yet verified; design only (no test, observer file untouched at design time).
  - AC-6: counts observed on the prototype (413, 4, 24 and 26, 5494 of 5511); shipped text not yet counted.
  - AC-7: prototype failed 2 of 22 `test_design_surfaces.py` cases as predicted; `test_sd_dispatch.py` not run (Spacedock 0.27.0 cache, 0.27.2 binary).

### Summary

Two of the three breaks are scriptable and the replay shows both archived tasks, which pass today, would exit 1; FO's words in `Design:` stay with the observer because a text rule would refuse 34 of 35 non-`none` values. One decision for the Captain: add the replacement rule with a `no replacement` waiver (recommended; 2 of 6 corpus hits are legitimate moves out of the task). Implementation order matters for `dev2-laws-check` (it must not run `check` over closed tasks) and for the shared 16-word `workflow.md` margin.

## Number guards

ADR: 0016

## Stage Report: implementation

- DONE: One Draft PR (fix(kc-dev-flow-2): ...) from a branch off origin/main implementing D1 as recommended: kc-dev-flow-2/scripts/design_surfaces.py check refuses a moved criterion its Supersedes: line does not name and a replacement criterion without 'Amended by Captain, amendment N', with the 'no replacement' waiver; every acceptance criterion in the task file green, each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
  PR https://github.com/iamcxa/kc-claude-plugins/pull/650 (Draft), branch `spacedock-ensign/amendment-form-check`, one commit `58eb738e` on origin/main `1383c911`. Files: `design_surfaces.py`, `test_design_surfaces.py`, `test_sd_dispatch.py`, `references/sd/workflow.md`, `docs/adr/0016-...md` (ADR 0016 reserved by FO; `adr_lint.py docs/adr --since origin/main --require 0016` exit 0).
  - AC-1 green: test `test_an_entry_holding_a_criterion_its_supersedes_line_does_not_name_is_refused` (fails if `held - named` rule is dropped; mutation test run) ; replay on archived `fo-lifecycle-mod`: base exit 0, candidate exit 1 naming amendment 3 and AC-1 to AC-7; mutant (rule dropped) exit 0.
  - AC-2 green: tests for no phrase, phrase of another number, number 10 vs 1, phrase only in the intro line (each fails when its rule or the `from_first_criterion` cut is mutated); replay on `delivery-gate-verdict-form`: base 0, candidate 1, one line naming amendment 2 and AC-1, AC-2, AC-3, AC-5, AC-6, AC-7, AC-8; mutant exit 0.
  - AC-3 green: `TWICE` fixture (entry 1's replacement inside entry 2's moved text passes) and the waiver test; mutant without `live + others` prints a second replay line (2 lines vs 1); mutant without the waiver fails the waiver test.
  - AC-4 met with one exception: corpus rerun at candidate (43 files, 74 entries, base vs candidate error diff) prints 10 new errors on 8 tasks, not the design's 8 on 6: the corpus grew by 3 files, and `office-header-shows-phone` (phrase variant "Amended by Captain, validation revise") and `remote-review-waits-and-acts` (partial supersession, already refused at base by the still-declared rule) are the two added. Waiver clears `owner-sees-all-feedback-room` amendment 3 (scratch copy, no error on that entry). `staff-multi-branch` amendment 1 does NOT fully clear: the waiver covers its move to a new task, but it also moved clauses (`**AC-6 fixture clause:**`, `**AC-7 second sentence:**`) of criteria that stay declared; unnamed it draws the moved-criterion error, named it draws the still-declared error. Recorded in ADR 0016 Consequences; the form has no partial move. FO or the Captain may rule whether that entry counts as fine under the AC-4 falsifier.
  - AC-5 green: `test_the_design_line_is_not_read`; mutation that stops excluding `Design:` lines fails it; `git diff origin/main -- skills/observer` is empty.
  - AC-6 green: Captain-amendments section 414 words (base 414, design said at most 414), `lint-skills.py` `5495 of 5511`, `check` on this task prints 4 words, workflow.md hunks only inside `## Captain amendments`. Failing-path output is 23 words (`fo-lifecycle-mod`) and 33 (`delivery-gate-verdict-form`) against the design's 24 and 26. To fit the budget I dropped the old clause "relocation, not annotation in place, is the route"; ADR 0005 still holds it.
  - AC-7 green: `test_design_surfaces.py` 34 tests pass (22 + 12 new, 6 are mutations); `test_sd_dispatch.py --sd-plugin-root <cache 0.27.0>` with the 0.27.2 binary exits 0, and with the old parity fixture restored it fails at `exercise`; `lint-skills.py` and `test_lint_skills.py` exit 0; the other 13 CI unit tests also exit 0 locally.
- DONE: No FO-read word added beyond the design; the candidate's own kc-dev-flow-2/scripts/lint-skills.py exits 0; roborev evidence= line; push without force; CI green on the PR head; CI cost measured or stated as not measured
  Roborev: `clean on 58eb738ea; evidence=roborev:704`. `comment_ratio.py origin/main HEAD`: 99 code lines, 3 comment lines (markdown headings inside test fixtures), 3.0%, maximum 5% met. `doc_impact.py`: `kc-dev-flow-2/README.md` unaffected: names `test_sd_dispatch.py` only as a command to run; `references/sd/adoption.md` unaffected: names the same test only as the sync check. Number guards: no `## Number guards` section needed beyond FO's ADR 0016 record; no migration.
  CI on head `58eb738e` (all four checks pass): unit tests 49 s, version parity 57 s, multi-profile route gate 6 s, GitGuardian 1 s (job times from `gh pr checks 650`); no new job added.

### Summary

`check` now refuses an entry holding a criterion its `Supersedes:` line does not name and an entry superseding ids with no "Amended by Captain, amendment N" criterion, unless the line says "no replacement"; `Design:` is not read. Both archived replays flip from exit 0 to exit 1 with one line each and each mutation changes the result. Open for FO: corpus count is 10 errors on 8 tasks (design: 8 on 6), and `staff-multi-branch` amendment 1 is only partly clearable by the waiver (partial clause moves), so AC-4's "legitimate moves covered by the waiver" holds for one of two legitimate entries.

## Stage Report: validation

- DONE: Independent verdict on PR #650 head 58eb738e against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  Verdict PASSED at head `58eb738eabd9e676191ec4eb6fb31099776adfff` (detached throwaway worktree, removed). Draft PR, 4 checks green on that head (`gh pr view 650`). Suites run by me with `python3 -B`: `test_design_surfaces.py` 34 tests OK; `test_lint_skills.py` OK; `lint-skills.py` 5495 of 5511; `test_sd_dispatch.py --sd-plugin-root ~/.claude/plugins/cache/spacedock/spacedock/0.27.0` with binary `~/.local/bin/spacedock` 0.27.2 exit 0; 11 other CI unit suites exit 0.
  AC-1 replay `fo-lifecycle-mod`: old script exit 0, new exit 1 naming amendment 3 and AC-1..AC-7. Mutant "drop `held - named`" -> replay exit 0 and 3 suite tests fail. AC-2 replay `delivery-gate-verdict-form`: old 0, new 1 naming amendment 2 and AC-1,2,3,5,6,7,8; mutant "drop replacement rule" -> replay exit 0, 6 tests fail.
  AC-3: mutant "drop `others` lookup" prints 2 replay lines instead of 1 and fails 2 tests; mutant "drop waiver" fails 3 tests; scratch copy of `owner-sees-all-feedback-room` with the waiver clears amendment 3. AC-5: mutant adding a `Design:` scan fails `test_the_design_line_is_not_read`; `git diff 1383c911 HEAD -- kc-dev-flow-2/skills/observer` is empty. AC-6: section 414 words (base 414), `check` on a presentable task 4 words both, hunks only in `## Captain amendments`; failing output 23 and 33 words (design said 24 and 26: Polish, the design called them approximate). AC-7: restoring the old parity fixture line in a scratch copy fails `test_sd_dispatch.py` at `exercise` (assert on returncode 0).
  AC-4: my own corpus run (read-only, 41 task files with entries, one copy per file name) gives the same 10 new errors on 8 tasks as the implementation; the design's 8 on 6 is stale (corpus grew). The 2 intended waiver cases: `owner-sees-all-feedback-room` clears with the waiver; `staff-multi-branch` amendment 1 does not, and no wording clears it (waiver alone leaves "holds AC-6, AC-7 not named"; naming them leaves "still declared"). AC-4 names this entry among the legitimate moves, so the call is not mine: Needs decision (below). Limits judged: one marked criterion satisfies a whole entry (bounded, stated in ADR 0016); `no replacement` can be typed falsely (bounded, observer still reads); corpus script machine-local (I reproduced it independently, so the claim does not rest on it).
  Findings by disposition: none Material. Needs decision: does the partial-clause move in `staff-multi-branch` amendment 1 count as a legitimate move AC-4 must cover, or as a form break the refusal is correct for (the README form moves a criterion whole and has no partial move)? The candidate cannot clear it under any wording; the implementation report and ADR 0016 Consequences already state this. Deferred risk: a future Captain partial supersession has no route (trigger unobserved in a released flow; becomes Material if one occurs: ADR 0016 Consequences says reopen). Polish: an amendment title with no number takes its first digit run (`### Amendment — 2026-10-16` reads as "amendment 2026"); the README template always carries the number; the phrase match is case-sensitive.
- DONE: Which of the 10 corpus entries the candidate now refuses sit in active (not archived) tasks of this workflow, relay, qnow or ss-web, so would hold at their next gate after release; and whether the clause the implementation dropped from references/sd/workflow.md ('relocation, not annotation in place, is the route') carries a rule nothing else states
  Of the 10 new errors, 9 are on 7 tasks under `_archive/` at the state branch tip (qnow `accept-branch-invitation`, `booking-outcomes`, `office-header-shows-phone`, `staff-multi-branch`; relay `owner-sees-all-feedback-room`; this workflow `delivery-gate-verdict-form`, `fo-lifecycle-mod`): they hold at no gate. One is on an active task: relay `remote-review-waits-and-acts` (status validation, state tip `origin/spacedock-state/dev2`, amendment 1), and it already exits 1 at base (`supersedes AC-2 but it is still declared`), so release adds a second line, not a new hold. I also ran base and candidate over every non-archived task with amendments on the dev2, dev2-poc and ss-web state tips (about 11 tasks): no other task gains an error (`spacedock-install-beta`, `subspace-tab-icon`, `holder-panel-header-and-polish` fail at base on Preview lines only). qnow has no active task with an amendment.
  Dropped clause: not a rule nothing else states. workflow.md still says the worker "moves each superseded criterion's block verbatim ... into its entry", `check` still refuses a superseded id left declared (that is annotation in place), the new text keeps "cannot see a skipped record or move", and ADR 0005 holds the rejected option (Context line 23, Options line 41, Decision line 58). Cost of the drop: a reader of workflow.md alone no longer sees the word "annotation"; Polish.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  Script below, saved to a temp file and run as `env -i HOME="$HOME" PATH=/usr/bin:/bin:/opt/homebrew/bin:/usr/local/bin bash --noprofile --norc <file>` (the temp file `/tmp/afc-accept.sh` is a leftover of my run; the fenced text is canonical): every step printed its expected output. `adr_lint.py docs/adr --since 1383c911` (also with `--require 0016`): `16 ADR file(s) checked, 0 legacy`, exit 0. Also at the candidate: `comment_ratio.py` 3.0% (3 fixture headings, none narration) met; `doc_impact.py` lists 2 READMEs, implementation recorded `unaffected` with reasons; `number_guards.py check` PASS; `dispatch_records.py` 5 records complete; `design_surfaces.py check` on this task passes. Verdict: PASSED recommended for head 58eb738e, with one open Needs decision (AC-4, `staff-multi-branch`).
  Process note: I ran `git fetch origin spacedock-state/dev2` in two relay state checkouts (`dhaka/.context/v0-dev2-fo`, `beirut-dev2`) to read the live tip; that moved only a remote-tracking ref, not a file, but it was not a read-only command as dispatched.

### Minimal acceptance script

Needs: the checkout `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo` (holds the PR head object), the dev2 state checkout under it, and the installed package at `~/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0`. Run in a fresh shell as `env -i HOME="$HOME" PATH=/usr/bin:/bin:/opt/homebrew/bin:/usr/local/bin bash --noprofile --norc <file>`. Not covered: a task that skips a move, FO's own words in `Design:`, FO behaviour at a live gate, CI.

```bash
export PYTHONDONTWRITEBYTECODE=1
REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo
STATE=$REPO/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state
PKG=/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.23.0
SHA=58eb738eabd9e676191ec4eb6fb31099776adfff
WT=/tmp/afc-accept-wt

echo "### Step 1: check out the candidate head in a throwaway worktree"
git -C "$REPO" worktree add --detach "$WT" "$SHA" 2>&1 | tail -1
echo "# expect: HEAD is now at 58eb738e fix(kc-dev-flow-2): design_surfaces check refuses an unnamed move and an unmarked replacement"

echo "### Step 2: replay the two archived tasks the observer faulted, with the old and the new script"
git -C "$STATE" show spacedock-state/dev2:_archive/fo-lifecycle-mod.md > /tmp/afc-accept-flm.md
git -C "$STATE" show spacedock-state/dev2:_archive/delivery-gate-verdict-form.md > /tmp/afc-accept-dgvf.md
git -C "$WT" show 1383c911:kc-dev-flow-2/scripts/design_surfaces.py > /tmp/afc-accept-base.py
for f in flm dgvf; do
  python3 -B /tmp/afc-accept-base.py check /tmp/afc-accept-$f.md; echo "old script, $f: exit $?"
  python3 -B "$WT/kc-dev-flow-2/scripts/design_surfaces.py" check /tmp/afc-accept-$f.md; echo "new script, $f: exit ${PIPESTATUS[0]}"
done
echo "# expect: old script exit 0 for both; new script exit 1 for both: flm names 'Amendment 3' and AC-1..AC-7 (Supersedes line does not name them); dgvf names 'Amendment 2' and AC-1, AC-2, AC-3, AC-5, AC-6, AC-7, AC-8 (no criterion says 'Amended by Captain, amendment 2')"

echo "### Step 3: the 'no replacement' waiver turns a refusal into a pass"
cat > /tmp/afc-accept-task.md <<'TASK'
---
title: waiver demo
variant: kc-dev-flow-2
profile: pilot
---

## Acceptance criteria

**AC-1**: kept.

## Captain amendments

### Amendment 1 — 2026-10-16, chat
Captain: 「drop AC-2」 (chat)
Supersedes: AC-2
Superseded text:
**AC-2**: the old outcome.

## FO alignment

Surfaces: none
Visible change: none
TASK
python3 -B "$WT/kc-dev-flow-2/scripts/design_surfaces.py" check /tmp/afc-accept-task.md; echo "without waiver: exit ${PIPESTATUS[0]}"
sed 's/^Supersedes: AC-2$/Supersedes: AC-2 (no replacement: dropped)/' /tmp/afc-accept-task.md > /tmp/afc-accept-task2.md
python3 -B "$WT/kc-dev-flow-2/scripts/design_surfaces.py" check /tmp/afc-accept-task2.md; echo "with waiver: exit $?"
echo "# expect: without waiver exit 1 naming Amendment 1, AC-2 and 'no replacement'; with waiver 'design surfaces presentable', exit 0"

echo "### Step 4: the candidate's own suites"
python3 -B "$WT/kc-dev-flow-2/scripts/test_design_surfaces.py" 2>&1 | grep -E '^(Ran|OK|FAILED)'; echo "test_design_surfaces: exit ${PIPESTATUS[0]}"
python3 -B "$WT/kc-dev-flow-2/scripts/lint-skills.py" | grep -E 'words'; echo "lint-skills: exit ${PIPESTATUS[0]}"
echo "# expect: Ran 34 tests / OK / exit 0; 'references/sd/workflow.md: 5495 of 5511 words' / exit 0"

echo "### Step 5: decision-record lint over the candidate's ADRs"
cd "$WT" && python3 -B "$PKG/scripts/adr_lint.py" docs/adr --since 1383c911 --require 0016; echo "adr_lint: exit $?"
echo "# expect: '16 ADR file(s) checked, 0 legacy' / exit 0"

echo "### Step 6: remove the throwaway worktree and temp files"
cd /tmp && git -C "$REPO" worktree remove --force "$WT" && rm -f /tmp/afc-accept-*.md /tmp/afc-accept-base.py; git -C "$REPO" worktree list | grep -c afc-accept-wt
echo "# expect: 0 (the worktree is gone)"
echo "# NOT covered: a task that skips a move, FO's own words in Design:, FO behaviour at a live gate, CI on the PR."
```

### Summary

PASSED at 58eb738e: every AC re-run and each falsifier fails its rule when mutated; the corpus count (10 errors, 8 tasks) reproduces independently. Only one refused entry sits in an active task and it already fails at base. No Material finding; one Needs decision for FO or the Captain (does `staff-multi-branch` amendment 1 count as a legitimate move under AC-4), one Deferred risk (a future partial supersession has no route) and three Polish items.

## Stage Report: implementation (cycle 2, phase 1: reproduce and propose, no fix)

- DONE: Phase 1 only: reproduce the Codex P2 on #650 head 3bc8f647 (review:5543218466) as a failing test, and propose the smallest fix; report and stop, with no commit or push, until FO authorizes the fix
  Reproduced in a throwaway copy `/tmp/afc-p2/scripts` (worktree clean at 3bc8f647, nothing committed or pushed). The P2 is real: `section()` ends only at a line starting `## `, but `AC_HEADING` accepts a heading with leading `GO_SPACE`, so ` ## Notes`, `\t## Notes` and `\xa0## Notes` do not end the criteria section.
  Failing test `test_an_indented_sibling_heading_ends_the_criteria_section` (AmendmentTests, 3 subtests): criteria then an indented `## Notes` then `**AC-9**: Amended by Captain, amendment 1: ...` with Amendment 1 superseding AC-2; asserts the "supersedes AC-2 but no criterion says" error. At 3bc8f647 all 3 subtests fail (errors `[]`, the marker is wrongly satisfied); full suite 41 tests, failures=3.
  Smallest fix (2 lines in `design_surfaces.py`): add `SECTION_END = re.compile(rf"^{GO_SPACE}## ")` and end `section()` at `SECTION_END.match(lines[i])` instead of `lines[i].startswith("## ")`. With it the suite is `Ran 41 tests / OK`. Patches: `/tmp/afc-p2/test.patch`, `/tmp/afc-p2/fix.patch`.
  Side effect to know: `section()` also bounds the amendments section and `check_criteria`, so an indented `## ` line there now also ends the section (same recognition the headings already use); a 4-space-indented `## x` would too. No existing test changed. Not run: `test_sd_dispatch.py` (no pinned root here), `lint-skills.py` (script-only change, no reference words touched).

### Summary

The P2 reproduces and the two-line fix passes the new test and the existing 40; awaiting FO authorization to apply both in the worktree, add a mutation test for the fix, and commit. This report is written to the task file but not committed or pushed, per the Phase 1 instruction.

## Stage Report: implementation (cycle 2, phase 2: fix applied)

- DONE: Apply fix and test patches, add one mutation test, rerun suite and corpus, run test_sd_dispatch.py, commit named files, roborev gate, push without force, report CI
  Commit 458324f8 (files: `scripts/design_surfaces.py`, `scripts/test_design_surfaces.py`), pushed 3bc8f647..458324f8 without force; no PR comment, review request or ready mark.
  Test `test_an_indented_sibling_heading_ends_the_criteria_section` asserts the "supersedes AC-2 but no criterion says" error with an indented `## Notes` (space, tab, no-break space) before a marked `**AC-9**`; fails if `section()` ends only at column-zero `## `. Mutation `test_mutation_restoring_the_plain_section_end_fails_its_cases` swaps back `startswith("## ")` and asserts the mutant returns `[]` for all three headings.
  `test_design_surfaces.py`: Ran 42 / OK. `test_sd_dispatch.py --sd-plugin-root .../spacedock/0.27.0`: exit 0 (spacedock 0.27.2 binary). `lint-skills.py`: `5495 of 5511` unchanged.
  Corpus rerun (29 unique task files with `### Amendment` entries under ~/conductor, not the 40 of design time): base 8 error lines, 3bc8f647 15, candidate 15, diff of the last two identical, so the fix changes no corpus result.
  roborev gate `--base 1383c911`: `clean on 458324f8b; evidence=roborev:715`, exit 0.
  CI on 458324f8: unit tests (python3) pass, version parity pass, multi-profile route gate pass, GitGuardian pass.

### Summary

The indented-sibling-heading P2 is fixed and covered by a test and a mutation; every check above passes on head 458324f8. A side effect accepted by FO: an indented `## ` line now also ends the amendments section.
