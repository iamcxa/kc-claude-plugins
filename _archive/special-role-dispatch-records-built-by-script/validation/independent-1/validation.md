# Independent validation of PR #827

Verdict: **REJECTED** at `8574e879b85197d31239ee2d9a9af0c5d0cb5392`.
Base: `6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1` (`origin/main` at dispatch).
The product worktree was clean and stayed on the assigned branch. Checks ran
from a `git archive` export. Mutations used a separate disposable export;
no product commit, PR write, reviewer request, merge or live agent launch occurred.
Evidence paths below are relative to this document's directory.

## Finding

**F1 Material — valid CRLF inputs lose their byte identity.**

- Released user and normal workflow: FO invokes the documented `dispatch_stage.py --role engineering-reviewer` with UTF-8 checklist and scope-note files using CRLF line endings. The command accepts these files; the contract declares no LF-only restriction.
- Observable harm: the command returns 0 and commits a record after replacing CRLF with LF. Neither supplied file's exact bytes can be found in the record. This breaks the promised correspondence between source inputs and the persisted dispatch; no semantic loss of the plain-text words is claimed.
- Affected criterion: `value-ac[AC-1]` requires `## Checklist` and `## Scope notes` to hold the two supplied files' bytes. `dispatch_stage.py:184-185` uses `Path.read_text()`, which normalizes line endings; line 242 also reads the record as normalized text for stdout.
- Trigger evidence: `evidence/probes.json`, `evidence/crlf-checklist.txt`, `evidence/crlf-notes.txt`, and `evidence/crlf-record.md` preserve the reproduction. `evidence/acceptance.log` repeats it from a fresh pinned export: exit 0 for the role command, both byte-preservation checks false, then assertion failure.
- Why existing green tests miss it: `test_role_commits_complete_record_before_printing_exact_inputs` generates LF inputs and constructs its expected result with `read_text()` too. The baseline suite therefore passes while this accepted boundary fails.
- Repair recommendation for FO disposition: preserve original newline bytes through input reading, record construction, retry comparison and stdout; add a raw-byte regression. No repair is applied by this validation.

## Acceptance criteria

- AC-1: **FAILED** for CRLF source-byte preservation (F1). The existing LF record/header/SHA/model/commit/stdout case passes. Removing the role state commit fails the HEAD assertion (`evidence/AC-1-no-commit.log`).
- AC-2: **PASSED**. Missing both required scope fields refuses without output or saved record; independent probes also remove each field separately. Skipping record checks prints the invalid prompt and fails the expected refusal (`evidence/AC-2-no-checks.log`, `evidence/probes.json`).
- AC-3: **PASSED**. Commit refusal withholds stdout and retains the pending record; retry refuses until reconciliation and then reuses the committed record. Printing before commit fails the empty-stdout assertion (`evidence/AC-3-early-prompt.log`).
- AC-4: **PASSED**. The owed chief-engineer fixture calls state commit and never dispatch build. Routing through build is caught by the spy (`evidence/AC-4-build-path.log`). The fixture uses five implementation headings, representing four repair passes under the existing trigger; the test verifies that a call is actually owed before dispatch.
- AC-5: **PASSED**. Sonnet refuses; Opus and the supplied Astra string pass. Removing the rank check makes Sonnet exit 0 and fails the refusal assertion (`evidence/AC-5-no-floor.log`). An initial mutation run timed out and is excluded as proof; the narrow rerun supplies the asserted failure.
- AC-6: **PASSED**. All eight stage-only options and design-director refuse with exit 2 and unchanged state. Allowing advance fails the option/state assertions (`evidence/AC-6-allow-advance.log`).
- AC-7: **PASSED**. Role-local numbering and immediate committed retry reuse pass. Global numbering fails the chief-engineer-1 assertion (`evidence/AC-7-global-numbers.log`). Original test functions are unchanged at the AST level (`evidence/retained-test-cases.json`); full suite outcomes are in `evidence/checks.json` and `evidence/test_dispatch_stage.log`.
- AC-8: **PASSED**. The required workflow sentence, reviewer-record check and Captain-quoted +6 budget step are present. Removing the instruction fails the integration assertion; removing the step makes 5937 exceed 5931 (`evidence/AC-8-no-instruction.log`, `evidence/AC-8-no-budget.log`, `evidence/lint-skills.log`).
- AC-9: **PASSED**. ADR 0074 matches the Captain's recorded D1-D3 decision. The prescribed installed linter exits 0; removing Words produces its single missing-Words defect (`evidence/adr-lint-prescribed.log`, `evidence/AC-9-no-words.log`). An initial validator invocation used an incorrect quoted Git metadata path and exited 2; the corrected and prescribed invocations both exit 0. It is not counted as a candidate failure.
- AC-10: **PASSED**. `wc -w` captures startup 5931 to 5937 and each role stdout/stderr. Successful outputs contain 39–44 words and empty stderr; refusals contain empty stdout and 4–49 stderr words (`evidence/wc-words.log`, `evidence/words.json`). Diff-stat and exact unchanged-file comparison cover idle/archive/merge readers; an added idle output is caught (`evidence/diff-stat.log`, `evidence/unchanged-lifecycle.log`, `evidence/AC-10-changed-idle.log`).

All negative controls run against disposable copies with `python3 -B` and no
copied `__pycache__`. `evidence/mutations.json` indexes the decisive logs. The
initial mutation driver had a no-op budget-removal pattern; it stopped before
running that control. The corrected driver ran only the remaining controls.

The complete rerun finished with 28 command exits of 0: 1270 unittest cases,
including 11 optional skips (`evidence/checks.json`, `evidence/summary.json`).
The 35 real-binary stage cases have no skips (`evidence/test_dispatch_stage.log`).
Skipped cases and native worker execution are not claimed verified.

## Captain acceptance

There is no changed application screen. Four observable command steps substitute
for a UI walk. Prerequisites are this repository with the exact commit available,
Python 3, Git, tar, bash, and `/Users/kent/.local/bin/spacedock` (0.27.2 here).

Run unchanged in a fresh shell:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/special-role-dispatch-records-built-by-script/validation/independent-1/acceptance.sh
```

1. Export the pinned commit: expect its full SHA and a new `/tmp/pr827-acceptance.*` path.
2. Exercise committed output and commit-failure recovery: expect two tests, OK.
3. Exercise malformed notes, an owed role, the model floor and excluded flags: expect four tests, OK.
4. Compare raw CRLF input bytes: acceptance requires both preservation checks true, followed by PASS.

Observed exactly as written: steps 1–3 pass; step 4 prints both preservation
checks false and exits 1 (`evidence/acceptance.log`). This script fits within
five minutes. It does not launch a reviewer, prove instruction-following,
publish anything, or cover every legacy stage path.

## Scope, documents and limits

The six changed files map to the role implementation, its regression checks,
the accepted workflow instruction and budget, and ADR 0074. Their removal
controls justify retaining them; no unrelated file is changed. Goal sufficiency
is incomplete only at the byte-preservation boundary described by F1.

`evidence/doc-impact.json` repeats the installed doc scan at the exact base/head;
`evidence/doc-verdicts.json` records and checks every listed document against the
implementation report. Its verdicts remain valid. The new ADR pointer is the
only added comment; `evidence/comment-ratio.log` reports 1/135, 0.7%, under 5%.
`evidence/number-guards.log` has no findings or fetch warning.

Implementation limits judged independently:

- Completely manual calls without any record remain outside D3's accepted scope. A dated qualifying Reviewer line still clears an owed call with no dispatch file (`evidence/limits.json`). This is an accepted limit, not a new repair request.
- Role mode checks only the Opus floor. A prod engineering-reviewer role can be emitted with Opus, but the later trigger continues to demand Fable/Astra even after its Reviewer line is recorded (`evidence/limits.json`). The approved design explicitly retains this boundary; database tasks use the same retained higher-floor rule.
- Unknown model families refuse without a record (`evidence/probes.json`), matching the recorded limit. No equivalence between model capabilities is inferred from their rank.
- Local integration uses the real Spacedock CLI 0.27.2 and active plugin root 0.27.3. Hosted run 42769870457 at the exact head completed successfully, including checkout/install of the pinned 0.27.2 dependency and stage/transport/recovery tests (`evidence/ci.json`, `evidence/ci-full.log`). This closes the implementation's hosted-CI evidence delegation for this candidate, while model dispatch and adoption remain untested.
- PR publication is now observed as OPEN/Draft at the pinned head. Reviews and inline comments were empty when read (`evidence/pr-refresh.json`, `evidence/pr-review-comments.json`). RoboRev remains FO-owned and is not claimed clean by this validator.
- CI triggers are unchanged; cost per PR was not measured. Other tasks' word-budget/ADR changes require FO's normal landing-order and recount check if the base changes.

The final PR observations are in `evidence/pr-final.json` and
`evidence/pr-review-comments-final.json`. Both overlapping tasks remain at
validation, and remote main still equals the stated base
(`evidence/overlap-state.json`, `evidence/remote-main.txt`).

FO retains finding disposition, repair authorization, gate and delivery ownership.
The state report does not approve a merge or change the task's frontmatter.
