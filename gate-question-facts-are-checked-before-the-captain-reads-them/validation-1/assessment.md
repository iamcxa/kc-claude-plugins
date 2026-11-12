# Independent validation

Verdict: **REJECTED** for the whole task at `8d083d3b9b2c48c10e32cee3e5ef693b374c6183` (PR #855). The owned implementation passes its bounded checks. The outstanding acceptance evidence belongs to AC-1 and cannot be waived by the validator or by an implementation skip instruction.

Candidate comparison: prerequisite `d79053d0836c558a9269f9cf1ba222933935b820` (PR #853), not all changes since main. The validator ran product tests from `git archive` exports; repository metadata checks read the clean assigned worktree at the same head. `identity.json` records matching hashes of every net changed file. No product file, branch, approval, or PR was changed.

## Finding

- F1 Needs decision, kind **evidence or form**: AC-1's dependent-candidate replay and hold-removal falsifier remain unrun. The accepted criterion is valid integration evidence; it should not be dismissed as an invalid criterion merely because another task owns the implementation. The explicit design makes this task depend on that listing, and the implementation follow-up says FO will bring the missing proof to validation or the Captain. Neither that instruction nor amendment 1 supersedes AC-1. FO can supply the pinned dependent candidate and authorize its replay; alternatively the Captain can amend acceptance. Do not repair this by adding a state reader to this PR, which would contradict approved design decision D2.
  - Released user and normal workflow: FO choosing tasks from the listing and asking the Captain to continue them.
  - Observable harm: the original question offered five held tasks; the prototype reproduces all five. This candidate itself leaves that state-only question unmarked, as designed. Whether the dependent listing prevents the original path has not been observed.
  - Affected criterion: `value-ac[AC-1]` requires the actual dependent listing replay, not only the prototype. The outcome remains unproven; this is not a demonstrated new code regression.
  - Trigger evidence: `replay.json` has historical 5/5 and 0/5, removal of `hold` changes the first prototype exit from 1 to 0, and the candidate question path adds zero marks to the third false question. `dispatch/implementation-1-message-1.md` explicitly records the missing dependent candidate.

No Material build finding was established. The original task-state failure plus an absent dependent-candidate check does not establish a defect in code this PR was approved to own; hence the disposition is Needs decision, rather than Material.

## Acceptance and limits

- **AC-1: NOT MET for acceptance.** Re-derived the last recorded rulings at both pinned historical state revisions, ran both original prototype commands, and ran the hold-removal mutant. This proves the historical problem and prototype only. The formal dependent-candidate run remains absent.
- **AC-2: PASSED.** Both actual recorded false merge questions gain exactly one mark in the question and summary CLI paths, with the same exit 0 as the prerequisite. The two contradicting primary records were read directly at each question's historical state, not copied from ideation extracts. English-only matching removes the marks. The `check` path also marks ask text and copies an uncited PR-body claim into the ask, without adding a content hold.
- **AC-3: PASSED under the accepted design.** The three original true questions add 0, 1, and 0 marks. The middle true title is intentionally marked until its existing saved output is cited; the cited version adds 0. Missing-file citation adds 1, and accepting missing files removes the warning. The premarked false sentence gains no duplicate. This is the tradeoff explicitly accepted at the ideation gate, not a claim of zero false positives. Repeat writes are byte-identical.
- **AC-4: PASSED for the measured corpus behavior, with the denominator corrected.** Original prototype: 111 questions / 505 spans. Candidate shared splitter: 111 / 549. Both find 11 matching claims in 9 questions, and candidate marks all 4 known false occurrences. Reading the marked occurrences shows one first-case claim, two copies of the second-case claim, and its release-ask restatement. Their falsity follows from the two pinned primary records. The English-only mutant marks 0 of 4. The changed span count is attributable to the approved shared prose/English splitter; it is not evidence of broader accuracy. Do not describe candidate output as 505 sentences.

### Every item formerly not provable

- Writing the mark: now exercised in real `question` subprocesses, with and without summary; `check` is exercised through its real main function with a read-only GitHub fixture. Actual files and exit codes were inspected. Existing draft holds and write-error exit 2 are covered by the candidate tests. This is not live GitHub publication or a native Captain dialog.
- Second corpus: NOT VERIFIED. No newly authorized independent corpus was available; the supplied corpus trained the pattern list. The implementation follow-up explicitly preserves this unknown. No claim of generalization is accepted here.
- Effect on Captain answers: NOT VERIFIED. No controlled observation or real use was supplied. The delivered mechanism is disclosure, not a proven change in his decisions. The gate's promise that currently unprovable items will later be proved must not be repeated as if this one is now settled.
- Third case in a plain dialog: UNCHANGED LIMIT. No checker runs on that path. Approved D2 accepts reliance on consulting the dependent listing; its required listing replay is F1, not waived by this dialog limit.
- Model reader: EXCLUDED BY APPROVAL. A nondeterministic, logged-in model run was neither rerun nor treated as an acceptance check. The historical results remain design evidence only.

## Decision record, necessity and document checks

ADR 0082's item-2 quote exactly matches the ideation gate record. Its D1/D2 description follows the accepted design recommendations; the Chinese count units and shared sentence split are expansion item 3. Amendment 1 permits this one decision file and says no new ruling is added. The record does not add a hold, model reviewer, state reader, or stronger truth guarantee. Older records were not rewritten.

Without this change the prerequisite adds zero marks to both false-claim probes; candidate adds one, at the same successful exit. The old count parser cannot identify the exercised Chinese unit counts; candidate's focused test detects one saved count and three unchecked counts. The two source files, corresponding tests, and authorized ADR each serve those outcomes. Goal sufficiency is bounded by F1. No CI definition changed; CI cost per PR was not measured.

`doc-impact.json` was rerun against the prerequisite and checked against implementation dispositions: 0082 updated; 0044 unaffected (optional summary and legacy path retained); 0051 unaffected (round-count hold retained); 0062 unaffected (quoted approval still compared); 0071 unaffected (head/clause/check-record binding retained); 0072 unaffected as an older ruling extended by 0082 (disclosure and citation boundaries retained); 0078 unaffected (inherited merge-result rules retained). Both added comments are ADR pointers, not implementation narration. `comments.log` measures 2/163 comment lines, 1.2%, under 5%.

## Executed evidence

- `tests.json`: delivery 230 discovered, 229 passed and 1 optional historical presentation replay skipped; learning 50 passed; ADR documentation 9 passed. These are selected affected suites, not a claim that the whole repository suite ran. The optional skip is unrelated to AC-1 and is not counted as passed.
- `checks.json`: lint, ADR lint, number guards, design surfaces, dispatch records, document impact and diff check all exited 0. Number guards initially warned that sandbox fetch failed; `number-guards-authorized.log` is the fresh-ref rerun with no warning. ADR command was `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1/scripts/adr_lint.py docs/adr --since d79053d0836c558a9269f9cf1ba222933935b820 --require 0082`, exit 0, 72 records checked, 0 legacy.
- `replay.json`: independent replay, original deterministic commands, primary-record confirmations, real file-write observations and one falsifier per criterion. `implementation-rerun.json`: supplied implementation evidence command rerun on exported bytes; `rerun-implementation.py` maps only its read-only `git show` lookup to the assigned repository. No product behavior is mocked by that mapping; the tests' own GitHub fixture remains declared above.
- `replay-setup-error.log`: first independent runner failed on a fixture whose task field is null. Only runner input handling was corrected; no product expectation changed. Both final replay and acceptance runs pass.
- `pr-status.json`: observed PR #855 remains open and Draft at the pinned head; six checks succeed and deploy is skipped. This records provider output, not required-check settlement, merge authorization, or delivery. Local RoboRev remains FO-owned.
- Public evidence contains aggregate results and public code/test output only. No raw private source question, task, ruling, or historical output was retained. The existing ideation files were not copied or modified. Export and test scratch are removed by the recorded exact roots; no temporary copy is evidence.

## Captain acceptance: four steps

Prerequisites: this committed state checkout, Python 3 with the existing PyYAML dependency needed by the historical prototype, the assigned clean candidate checkout and its prerequisite/prototype Git objects, and the installed package path named below. No login, model invocation, or network is needed. The script exports source into disposable directories and removes them. It does not prove AC-1's dependent listing, a second corpus, changed Captain behavior, live gate presentation, or delivery.

Run unchanged in a fresh Bash shell, from any directory:

```bash
/bin/bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/gate-question-facts-are-checked-before-the-captain-reads-them/validation-1/acceptance.sh /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/gate-question-facts-are-checked-before-the-captain-reads-them/validation-1
```

1. Pin and export: expected `Step 1: pinned candidate and exported three revisions`.
2. Replay and falsifiers: expected `Step 2: replay assertions passed; AC-1 dependent candidate remains NOT RUN`.
3. Owned behavior tests: expected `Step 3: nine scope tests passed`; `captain-tests.log` records 9 tests and OK.
4. Required decision-record lint: expected `Step 4: required decision-record lint passed`; then `Cleanup: acceptance scratch removed`.

Executed exactly as above in `/bin/bash --noprofile --norc`, exit 0. `captain-acceptance.log` holds the observed five output lines, `captain-replay.json` the aggregate replay, and `captain-adr.log` the lint output. A successful run explicitly preserves the acceptance rejection, rather than masking the missing dependent proof.
