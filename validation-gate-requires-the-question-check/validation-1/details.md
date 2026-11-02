# Independent validation of pull request 767

Verdict: **REJECTED pending two Needs decision dispositions**, not a demonstrated product defect. Observed 2026-11-02 at 07:37 UTC. Pilot scope is the supplied-text check; no binding hook or truthful-review-count guarantee is promised.

## Identity and boundaries

- Candidate: `6c34942164ecec9452c93f915e36241479f19dc5`.
- Current parent pull request 766: `1c0dbb540f354300b75dba5a119d2614c8fb0c02`; GitHub's baseRefOid agrees. This is the comparison base for this task's three-file delta.
- Trunk observed by fetch: `146727ded0d4ce8014ea0b41a45dc3409d6b269b`.
- Assigned worktree: `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-validation-gate-requires-the-question-check`; branch `spacedock-ensign/validation-gate-requires-the-question-check`.
- Candidate execution used its detached `.context/validation-767-detached` checkout; tracked product bytes stayed unchanged. Mutation copies were nested under it. The validation and acceptance throwaway worktrees were removed afterward; the assigned worktree remains owned by the workflow.
- Skill root resolved to `/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0`, per the loaded skill's relative-root rule. The dispatch's `.claude` path was not substituted for this root.
- Task state remains validation, pull request remains OPEN/Draft and stacked. No agents started; a scoped Paseo inventory returned no additional agents for the assigned cwd. No product push, review request, comment, ready mark or merge was made.

## Findings and dispositions owed

### F1 — Needs decision: criterion and mandated stack use different baselines

- Released user and normal workflow: First Officer validates this approved task stacked on current pull request 766, as this dispatch explicitly requires.
- Observable impact: the literal command in AC-6 is not empty. It reports adoption.md (4 lines) and workflow.md (8 lines), inherited from the parent stack. No task-owned workflow regression is demonstrated; declaring every criterion passed would hide the mismatch.
- Protected statement: `value-ac[AC-6]` promises an empty `git diff --stat origin/main -- kc-dev-flow-2/references/sd/`, while the dispatched base includes parent edits.
- Trigger evidence: `literal-main-diff.log` and `stacked-reference-diff.log`, repeated in acceptance step 4. Their exit-code comparisons are 1 and 0 respectively. WORKFLOW_BUDGET_STEPS and the entire lint script are identical to the assigned base.
- Recommendation: FO resolves the accepted comparison wording through the existing scope/ruling route. Keep parent edits; no code repair is proposed. This validator does not waive or rewrite AC-6.

### F2 — Needs decision: installed checker predates authorized completion wording

- Released user and normal workflow: this Paseo worker must use final-reply completion, expressly required in both implementation and validation dispatches.
- Observable impact: the required installed 0.34.0 dispatch checker exits 1 on those two records for lacking a main-recipient sentence. Their actual canonical final-reply sentence is accepted by the candidate checker inherited from the approved worker-completion parent.
- Protected statement: `contract[kc-dev-flow-2/skills/validation/principles.md#Validation principles]` requires checking dispatch records and returning failures to FO; `captain-ruling[2026-11-02]` and ADR 0048 authorize final-reply completion through Paseo.
- Trigger evidence: `dispatch-installed.log` versus `dispatch-candidate.log`: installed exit 1, candidate exit 0, four records complete. The workflow lists paseo and the records carry the exact authorized sentence.
- Recommendation: FO records the checker-version disposition before treating the required installed check as clean. No plugin update or dispatch-history rewrite was made. Do not restore the superseded main-recipient behavior.

No Material finding is claimed. The unavailable RoboRev daemon is an existing delegated review obligation, not a new product finding.

## Acceptance evidence and falsifiers

| Criterion | Independent observation | Counterexample exercised |
| --- | --- | --- |
| AC-1 | Absent, fenced, bulleted, invalid and duplicate counts exit 1, print problem/next, and create no record. | Remove the call: target assertions fail, exit 1, no import error. |
| AC-2 | 0, 2, 003, 1., 2. detail and 1; detail pass, one record, unchanged complete stdout. | Require nonzero: the zero-case assertion fails. |
| AC-3 | Seven unedited questions/summaries from historical index.json files at state 99e8bb36 give all specified results. | At the current assigned base, all four missing-count texts pass; candidate holds them. |
| AC-4 | Real CLI/task/configuration and gh reading real pull request 767; only missing-count text has the count diagnostic/next line. | Removed-call disposable copy on the same real PR loses those two lines. |
| AC-5 | question/text_problems syntax trees equal base; complete stdout equals base; existing question inputs unchanged. | Moving the rule into text_problems fails the legacy no-count question test. |
| AC-6 | Assigned-base reference/mod/lint diff empty, lint 5781 words; literal origin/main comparison unmet as F1. | One additional workflow word in a disposable package fails lint at 5782. |
| AC-7 | Exact Captain answer/question and four Limits manually compared; ADR lint passes. | Removing Words, Recommended or the protected code pointer fails lint. Asked alone does not. |

`prove.py` reuses the implementation evidence runner, adjusting only candidate checkout, current base, evidence directory and disposable-mutation location. It was independently executed with `python3 -B`; no author-produced result was accepted as a rerun. Provider facts, task history and role calls are fixture controls: this replays supplied texts, not historical live GitHub or FO execution. `proof-run.log`, `proof-results.json` and the three mutation logs retain results.

The four missing-count rows (batch10-after-release-obligations, peers-paseo-rule-matches-practice, names-check-says-what-it-skipped, peer-status-reaches-fresh) change base 0 to candidate 1, print the count problem and next line, and save no ask. paseo-human-surfaces-visible-and-reachable briefing 1 stays 1 with the reviewer-declaration problem; its briefing 2 and model-roster-per-repo briefing 1 stay 0. All three unaffected rows have byte-identical base/candidate stdout.

## Real GitHub seam

Each command used the detached candidate, actual task/workflow, `--pr iamcxa/kc-claude-plugins#767`, and no fake gh or `--head` override. The exact command shape is below; substitute live-present.txt for the second run and `.context/live-no-count-rule/delivery_gate.py` for the third run's script. The third copy changed only the new assignment to `missing = []`.

```bash
C='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-validation-gate-requires-the-question-check/.context/validation-767-detached'
S='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state'
python3 -B "$C/kc-dev-flow-2/scripts/delivery_gate.py" check "$S/validation-gate-requires-the-question-check.md" --pr 'iamcxa/kc-claude-plugins#767' --text-file /tmp/validation-767-evidence/live-missing.txt --workflow-dir "$S/.."
```

The text files explicitly identify validation probes; they are not real review or approval declarations. The initial sandbox attempt could not reach GitHub inside Python; all final evidence runs read GitHub successfully after approved network escalation. All three exit 1 for Draft/non-trunk base. The missing form additionally prints the count problem/next line; the present and removed-call forms are identical. See `live-missing.log`, `live-present.log`, `live-no-count-rule.log`. No task merge/ask record existed afterward. Expected Draft/stack holds are separate from the count rule.

## Suite, checks and document review

All 26 commands listed by `.github/workflows/kc-dev-flow-2-tests.yml` exit 0 locally, with 1021 unittest cases including 124 delivery-gate tests, plus passing dispatch/recovery integration scripts. `ci-results.json` records exact commands, duration and logs. Local execution used Darwin/arm64 Spacedock 0.27.2 and plugin source downloaded from `https://api.github.com/repos/spacedock-dev/spacedock/tarball/4d158a484ec73e184861067f8ed1e20087fdc26a`, not installed plugin 0.27.3.

The independently read Linux [CI run 41405823880](https://github.com/iamcxa/kc-claude-plugins/actions/runs/41405823880) names the exact candidate and succeeded, including pinned-source checkout, pinned binary install and both integrations. `hosted-ci.json`, `hosted-jobs.json`, `pr767.json` and `pr766.json` retain provider evidence. CI triggers and definitions are unchanged; cost per PR was not measured. Local durations are not billing evidence.

`checks.json` contains exact commands and individual exit codes: ADR lint 0 (50 records, 0 legacy), number guard 0, comment ratio 0 (38 code/1 comment = 2.6%, within 5%), doc impact 0, design surfaces 0, diff-check 0, stacked reference diff 0, literal trunk diff 1, installed dispatch 1, candidate dispatch 0, RoboRev 3. Each also has a named plain-output log. The sole added production comment is the ADR pointer required by lint.

Document dispositions: ADR 0044 is **unaffected**, retained as a historical ruling explicitly amended by ADR 0051. ADR 0051 is **updated** and carries the answer, question, pointer and bounded claims. No candidate diagram or UI screen changed. No version bump occurred.

## Judgment of implementation limits

- Own-PR command deferred to validation: resolved by the real-gh pair and removed-call control.
- Literal origin/main comparison: still unmet as F1; verified stacked-base equivalence does not erase its exact wording.
- Pinned integration source: resolved locally and corroborated by hosted Linux CI.
- Hosted CI: now verified. RoboRev remains incomplete, exit 3, daemon not running; FO retains review ownership.
- Draft/publication: GitHub confirms the exact dispatched head and current parent. FO published before validation; this worker did not. Ready/merge are not approved by this report.
- Historical replay controls remain explicit; no inferred historical timing, review truth, comprehension or native binding proof.
- No forced check/binding order, count presence/form only, new holds for older adopter texts, and checks after a chat answer: accurate bounds recorded in ADR 0051. D1 accepted the narrower outcome; these are not new defects.
- Complete-check output adds zero words against the current base; missing-count output adds 22 (10 problem, 12 next). Workflow/budget remain 5781, including parent edits.
- The claim that removing Asked fails ADR lint is inaccurate: the mutation exits 0. Lint proves neither the exact question nor its authority. This validator manually checked the actual ADR against the task/gate records; no AC-7 content defect was found.
- No CI cost measurement exists; retained local timings describe validation only.

Goal sufficiency: behavioral criteria and the real external seam pass at the accepted check boundary; formal AC-6 and checker-version dispositions remain open. Minimal necessity: the three changed files implement the rule, preserve/falsify compatibility and record the decision. No new hook, command, format, stage or mandatory workflow prose was added.

## Minimal acceptance script

The exact five-step script below ran unchanged with `bash --noprofile --norc /tmp/validation-767-evidence/acceptance.sh` in a fresh shell, exit 0. The initial sandbox attempt could not create Git metadata; the same bytes then completed with approved metadata access. The persisted sibling `acceptance.sh` names its prerequisites and creates/removes its own checkout. It deliberately reproduces the unresolved criterion instead of labeling the change accepted.

It covers visible CLI behavior under existing provider fixtures, ADR structure, budget and reference comparisons. It does not repeat live GitHub, historical replay, the full suite, RoboRev or actual gate binding. Full script and observed output follow.

```bash
#!/usr/bin/env bash
# Prerequisites: this repository, Python 3, Git, and the declared 0.34.0 package.
# No UI exists. This checks the command's observable count boundary and the
# recorded baseline discrepancy; it does not repeat live GitHub or the full suite.

# Step 1 — open the exact candidate in an isolated, detached checkout.
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
TASK_WORKTREE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-validation-gate-requires-the-question-check'
PACKAGE='/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0'
CANDIDATE='6c34942164ecec9452c93f915e36241479f19dc5'
STACK_BASE='1c0dbb540f354300b75dba5a119d2614c8fb0c02'
TRUNK_AT_VALIDATION='146727ded0d4ce8014ea0b41a45dc3409d6b269b'
ACCEPTANCE_DIR=$(mktemp -d "$TASK_WORKTREE/.context/acceptance-767.XXXXXX")
CHECKOUT="$ACCEPTANCE_DIR/checkout"
trap 'cd "$TASK_WORKTREE"; if test -d "$CHECKOUT"; then git -C "$TASK_WORKTREE" worktree remove "$CHECKOUT"; fi; rmdir "$ACCEPTANCE_DIR"' EXIT
git -C "$TASK_WORKTREE" worktree add --detach "$CHECKOUT" "$CANDIDATE"
test "$(git -C "$CHECKOUT" rev-parse HEAD)" = "$CANDIDATE"
printf 'Candidate: %s\n' "$CANDIDATE"

# Step 2 — observe the held and accepted forms using existing provider fixtures.
# Expected: missing=1/0 records; zero and detail=0/1 record; legacy question=0.
python3 -B - "$CHECKOUT" <<'PY'
import importlib.util, sys
from pathlib import Path
scripts = Path(sys.argv[1]) / 'kc-dev-flow-2/scripts'
sys.path.insert(0, str(scripts))
spec = importlib.util.spec_from_file_location('test_delivery_gate', scripts / 'test_delivery_gate.py')
tests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests)
missing = tests.run_check(rounds='')
assert missing.code == 1 and missing.written == {}
assert tests.CheckRoundCountTests.PROBLEM in missing.out
assert tests.CheckRoundCountTests.NEXT in missing.out
print('missing: exit=1, records=0')
print(missing.out, end='')
for value in ('0', '2. two reviews read'):
    result = tests.run_check(rounds=f'External rounds: {value}\n')
    assert result.code == 0 and len(result.written) == 1
    print(f'{value}: exit=0, records=1')
assert tests.QuestionTests().ask('Deliver it.') == (0, 'gate text complete\n')
print('legacy question without count: exit=0, gate text complete')
PY

# Step 3 — check the decision record and unchanged workflow budget.
# Expected: 50 ADR files, 0 legacy; lint PASS, workflow 5781 of 5781 words.
cd "$CHECKOUT"
python3 "$PACKAGE/scripts/adr_lint.py" docs/adr --since "$STACK_BASE" --require 0051
python3 -B kc-dev-flow-2/scripts/lint-skills.py

# Step 4 — distinguish this task's empty diff from the literal AC-6 discrepancy.
# Expected: stacked diff empty; trunk diff names adoption.md and workflow.md.
git -C "$CHECKOUT" diff --exit-code "$STACK_BASE" "$CANDIDATE" -- kc-dev-flow-2/references/sd/ kc-dev-flow-2/scripts/lint-skills.py
printf 'Stacked reference and budget diff: empty\n'
if git -C "$CHECKOUT" diff --quiet "$TRUNK_AT_VALIDATION" "$CANDIDATE" -- kc-dev-flow-2/references/sd/; then
  printf 'Unexpected: literal trunk diff became empty\n'
  exit 1
else
  result=$?
  test "$result" = 1
fi
git -C "$CHECKOUT" diff --stat "$TRUNK_AT_VALIDATION" "$CANDIDATE" -- kc-dev-flow-2/references/sd/
printf 'AC-6 literal trunk comparison: UNMET; inherited changes require disposition\n'

# Step 5 — verify and remove only this script's temporary checkout.
# Expected: no changed files; cleanup complete. This is no delivery approval.
test -z "$(git -C "$CHECKOUT" status --porcelain)"
cd "$TASK_WORKTREE"
git -C "$TASK_WORKTREE" worktree remove "$CHECKOUT"
rmdir "$ACCEPTANCE_DIR"
trap - EXIT
printf 'Acceptance replay complete; temporary checkout removed\n'
```

Observed output:

```text
Preparing worktree (detached HEAD 6c3494216)
HEAD is now at 6c3494216 Merge remote-tracking branch 'origin/spacedock-ensign/second-round-prompts-a-step-back' into spacedock-ensign/validation-gate-requires-the-question-check
Candidate: 6c34942164ecec9452c93f915e36241479f19dc5
missing: exit=1, records=0
summary needs one top-level External rounds: N line (nonnegative integer)
next: hold the ask; record the external round count in the summary.
0: exit=0, records=1
2. two reviews read: exit=0, records=1
legacy question without count: exit=0, gate text complete
50 ADR file(s) checked, 0 legacy
PASS: basic frontmatter, declared profile routes, role bindings and package script paths
references/sd/workflow.md: 5781 of 5781 words; no unlisted passage repeats it
Not checked: full Agent Skills conformance or host/workflow behavior
Stacked reference and budget diff: empty
 kc-dev-flow-2/references/sd/adoption.md | 4 ++--
 kc-dev-flow-2/references/sd/workflow.md | 8 ++++----
 2 files changed, 6 insertions(+), 6 deletions(-)
AC-6 literal trunk comparison: UNMET; inherited changes require disposition
Acceptance replay complete; temporary checkout removed
```

Executed script SHA-256: 112349d446e95c0abc9b71a96c68a255efd11cdc6a40d4ef789b08fdd9a0358e
