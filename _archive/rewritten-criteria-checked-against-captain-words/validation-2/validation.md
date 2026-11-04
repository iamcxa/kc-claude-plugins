# PR #770 independent revalidation

Verdict: PASSED for the bounded behavior, with F1 Deferred risk and F2/F3 Polish; no delivery approval.

Candidate: b81c628facd2cd38568018beec47b6c4566c0aae. Base: 2bda2e98304261d46b0ae7205a29ddc9038d2b4d. State corpus: de81585004ce636732a2515fd759f2b07c2980cd.

Pilot, Surfaces: none. Observable CLI behavior, no application screen. The accepted integration recheck changes baseline measurements: raw historical exit 1 on both sides and workflow 5836 words, while this task alone adds the named diagnostic. Original static exit-0/5781 clauses are not claimed as literal current observations.

## Minimal acceptance script

Prerequisites: Git, Python 3, the explicitly named repository/state checkout and installed package from the dispatch. No sign-in or secret. Five steps; final script ran unchanged in a fresh Bash shell, exit 0. Setup first encountered a sandbox denial creating worktree metadata; the unchanged route passed with approved filesystem access. The failed setup log is retained.

Run from any working directory:

```sh
/bin/bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/rewritten-criteria-checked-against-captain-words/validation-2/acceptance.sh
```

Complete commands and expected observations:

```bash
#!/bin/bash
set -euo pipefail
# Step 1 — isolate the exact candidate. Expected: STEP 1 PASS with the full SHA.
export PR770_SOURCE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-rewritten-criteria-checked-against-captain-words'
export PR770_STATE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state'
export PR770_HEAD=b81c628facd2cd38568018beec47b6c4566c0aae
export PR770_BASE=2bda2e98304261d46b0ae7205a29ddc9038d2b4d
export PR770_RUN
PR770_RUN=$(mktemp -d "$PR770_SOURCE/.context/pr770-acceptance.XXXXXX")
export PR770_FIXTURE
PR770_FIXTURE=$(mktemp -d /tmp/pr770-acceptance.XXXXXX)
cleanup() {
  if test -e "$PR770_RUN/candidate/.git"; then
    git -C "$PR770_SOURCE" worktree remove "$PR770_RUN/candidate"
  fi
  rm -rf "$PR770_RUN" "$PR770_FIXTURE"
}
trap cleanup EXIT
git -C "$PR770_SOURCE" worktree add --detach "$PR770_RUN/candidate" "$PR770_HEAD"
test "$(git -C "$PR770_RUN/candidate" rev-parse HEAD)" = "$PR770_HEAD"
test -z "$(git -C "$PR770_RUN/candidate" status --porcelain)"
echo "STEP 1 PASS: $PR770_HEAD"

# Step 2 — replay the historical widening and deletion control. Expected: raw 1/1 with one candidate-only 41-word diagnostic; normalized 0/1; deletion 0/0.
mkdir "$PR770_RUN/base"
git -C "$PR770_SOURCE" archive "$PR770_BASE" kc-dev-flow-2 | tar -x -C "$PR770_RUN/base"
git -C "$PR770_STATE" archive b4e88ece4 peer-status-reaches-fresh.md peer-status-reaches-fresh/dispatch | tar -x -C "$PR770_FIXTURE"
python3 -B - <<'PY'
import os,subprocess
from pathlib import Path
root=Path(os.environ['PR770_RUN']); fixture=Path(os.environ['PR770_FIXTURE'])
record=fixture/'peer-status-reaches-fresh/dispatch/validation-2.md'
task=fixture/'peer-status-reaches-fresh.md'
def check(side):
    return subprocess.run(['python3','-B',str(root/side/'kc-dev-flow-2/scripts/dispatch_records.py'),'--names','--strict',str(record)],capture_output=True,text=True)
a,b=check('base'),check('candidate')
assert (a.returncode,b.returncode)==(1,1)
assert a.stdout=='' and a.stderr==b.stderr and "no 'Symptom:' line" in a.stderr
assert len(b.stdout.splitlines())==1 and 'AC-9 (Captain amendment 3)' in b.stdout and 'words: revision, link;' in b.stdout
assert len(b.stdout.split(':1: ',1)[1].split())==41
print('STEP 2 raw PASS: base=1 candidate=1; shared Symptom hint; candidate-only revision, link; 41 words')
record.write_text('Symptom: none\n'+record.read_text())
a,b=check('base'),check('candidate')
assert (a.returncode,a.stdout,a.stderr)==(0,'','') and b.returncode==1 and b.stderr==''
assert 'words: revision, link;' in b.stdout
print('STEP 2 normalized PASS: base=0 candidate=1; widening held')
task.write_text(task.read_text().replace('include source revision/link.','include source.'))
for side in ('base','candidate'):
    r=check(side)
    assert (r.returncode,r.stdout,r.stderr)==(0,'','')
print('STEP 2 deletion PASS: base=0 candidate=0; both silent')
PY

# Step 3 — exercise controls, repair dispatches, Symptom integration and event-time classification. Expected: Ran 23 tests, OK.
(cd "$PR770_RUN/candidate/kc-dev-flow-2/scripts" && python3 -B -m unittest test_design_surfaces.AddedWordsTests test_dispatch_records.RewrittenCriterionTests test_dispatch_records.SymptomDispatchTests test_laws_check.L2Test.test_rewritten_criterion_is_an_event_violation_and_later_clearance_is_not_retroactive -q)
echo 'STEP 3 PASS: comparison, Symptom and event-time checks'

# Step 4 — check unchanged workflow words and decision record. Expected: 5836 words; lint passes; 53 ADR files, 0 legacy.
cmp "$PR770_RUN/base/kc-dev-flow-2/references/sd/workflow.md" "$PR770_RUN/candidate/kc-dev-flow-2/references/sd/workflow.md"
test "$(wc -w < "$PR770_RUN/candidate/kc-dev-flow-2/references/sd/workflow.md" | tr -d ' ')" = 5836
(cd "$PR770_RUN/candidate" && python3 -B kc-dev-flow-2/scripts/lint-skills.py)
(cd "$PR770_RUN/candidate" && python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since "$PR770_BASE" --require 0057)
git -C "$PR770_RUN/candidate" diff --check "$PR770_BASE" "$PR770_HEAD"
echo 'STEP 4 PASS: workflow unchanged at 5836 words; lint and ADR checks passed'

# Step 5 — verify unchanged product and remove the scratch worktree. Expected: STEP 5 PASS.
test -z "$(git -C "$PR770_RUN/candidate" status --porcelain)"
cleanup
trap - EXIT
test ! -e "$PR770_RUN"
test ! -e "$PR770_FIXTURE"
echo 'STEP 5 PASS: product clean; temporary worktree and fixtures removed'
```

Observed output (exit 0):

```text
Preparing worktree (detached HEAD b81c628fa)
HEAD is now at b81c628fa Merge origin/main and align rewritten-criterion symptom fixtures
STEP 1 PASS: b81c628facd2cd38568018beec47b6c4566c0aae
STEP 2 raw PASS: base=1 candidate=1; shared Symptom hint; candidate-only revision, link; 41 words
STEP 2 normalized PASS: base=0 candidate=1; widening held
STEP 2 deletion PASS: base=0 candidate=0; both silent
----------------------------------------------------------------------
Ran 23 tests in 7.217s

OK
STEP 3 PASS: comparison, Symptom and event-time checks
PASS: basic frontmatter, declared profile routes, role bindings and package script paths
references/sd/workflow.md: 5836 of 5836 words; no unlisted passage repeats it
Not checked: full Agent Skills conformance or host/workflow behavior
53 ADR file(s) checked, 0 legacy
STEP 4 PASS: workflow unchanged at 5836 words; lint and ADR checks passed
STEP 5 PASS: product clean; temporary worktree and fixtures removed
```

Coverage: exact identity, historical hold/control, 23 focused checks, workflow parity, decision record and cleanup. This smoke does not repeat the full corpus, 13 mutations, hosted suite or review; those runs are recorded below. It does not establish general semantic rewrites, translation equivalence, native delivery, adoption or merge authority.

## Primary comparison evidence

### base

Exit: 1

Stdout:

```text

```

Stderr:

```text
/tmp/pr770-revalidation-b81c628f/replay/peer-status-reaches-fresh/dispatch/validation-2.md:1: no 'Symptom:' line; before first '## ' heading add 'Symptom: <failure, named the same way each time>' or 'Symptom: none'
```

### candidate

Exit: 1

Stdout:

```text
/tmp/pr770-revalidation-b81c628f/replay/peer-status-reaches-fresh/dispatch/validation-2.md:1: AC-9 (Captain amendment 3) adds words in a sentence kept from the criterion it replaces that are not in his words: revision, link; remove them, or ask the Captain and record his answer as an amendment, then run this check again
```

Stderr:

```text
/tmp/pr770-revalidation-b81c628f/replay/peer-status-reaches-fresh/dispatch/validation-2.md:1: no 'Symptom:' line; before first '## ' heading add 'Symptom: <failure, named the same way each time>' or 'Symptom: none'
```

### clean_base

Exit: 1

Stdout:

```text

```

Stderr:

```text
/tmp/pr770-revalidation-b81c628f/replay/peer-status-reaches-fresh/dispatch/validation-2.md:1: no 'Symptom:' line; before first '## ' heading add 'Symptom: <failure, named the same way each time>' or 'Symptom: none'
```

### clean_candidate

Exit: 1

Stdout:

```text

```

Stderr:

```text
/tmp/pr770-revalidation-b81c628f/replay/peer-status-reaches-fresh/dispatch/validation-2.md:1: no 'Symptom:' line; before first '## ' heading add 'Symptom: <failure, named the same way each time>' or 'Symptom: none'
```

### normalized_base

Exit: 0

Stdout:

```text

```

Stderr:

```text

```

### normalized_candidate

Exit: 1

Stdout:

```text
/tmp/pr770-revalidation-b81c628f/replay/peer-status-reaches-fresh/dispatch/validation-2.md:1: AC-9 (Captain amendment 3) adds words in a sentence kept from the criterion it replaces that are not in his words: revision, link; remove them, or ask the Captain and record his answer as an amendment, then run this check again
```

Stderr:

```text

```

### normalized_clean_base

Exit: 0

Stdout:

```text

```

Stderr:

```text

```

### normalized_clean_candidate

Exit: 0

Stdout:

```text

```

Stderr:

```text

```

### clearance

Exit: 1

Stdout:

```text
/tmp/pr770-revalidation-b81c628f/replay/peer-status-reaches-fresh/dispatch/validation-2.md:1: Captain amendment 4 named in no dispatch checklist; write 'Captain amendment 4' in a checklist line of this record, then run this check again
```

Stderr:

```text
/tmp/pr770-revalidation-b81c628f/replay/peer-status-reaches-fresh/dispatch/validation-2.md:1: no 'Symptom:' line; before first '## ' heading add 'Symptom: <failure, named the same way each time>' or 'Symptom: none'
```

### normalized_clearance

Exit: 0

Stdout:

```text

```

Stderr:

```text

```

### implementation-4-message-2.md

Exit: 1

Stdout:

```text

```

Stderr:

```text
/tmp/pr770-revalidation-b81c628f/replay/peer-status-reaches-fresh/dispatch/implementation-4-message-2.md:1: no 'Symptom:' line; before first '## ' heading add 'Symptom: <failure, named the same way each time>' or 'Symptom: none'
```

### validation-2-message-1.md

Exit: 1

Stdout:

```text
/tmp/pr770-revalidation-b81c628f/replay/peer-status-reaches-fresh/dispatch/validation-2-message-1.md:1: AC-9 (Captain amendment 3) adds words in a sentence kept from the criterion it replaces that are not in his words: revision, link; remove them, or ask the Captain and record his answer as an amendment, then run this check again
```

Stderr:

```text
/tmp/pr770-revalidation-b81c628f/replay/peer-status-reaches-fresh/dispatch/validation-2-message-1.md:1: no 'Symptom:' line; before first '## ' heading add 'Symptom: <failure, named the same way each time>' or 'Symptom: none'
```

### normalized_implementation-4-message-2.md

Exit: 0

Stdout:

```text

```

Stderr:

```text

```

### normalized_validation-2-message-1.md

Exit: 1

Stdout:

```text
/tmp/pr770-revalidation-b81c628f/replay/peer-status-reaches-fresh/dispatch/validation-2-message-1.md:1: AC-9 (Captain amendment 3) adds words in a sentence kept from the criterion it replaces that are not in his words: revision, link; remove them, or ask the Captain and record his answer as an amendment, then run this check again
```

Stderr:

```text

```

### raw_without_added_words

Exit: 1

Stdout:

```text

```

Stderr:

```text
/tmp/pr770-revalidation-b81c628f/replay/peer-status-reaches-fresh/dispatch/validation-2.md:1: no 'Symptom:' line; before first '## ' heading add 'Symptom: <failure, named the same way each time>' or 'Symptom: none'
```

## Corpus

51 amended tasks; 10 held; 18 added diagnostics. Base/candidate otherwise have identical stdout, stderr and exit behavior. Per-record results: proof.json.

```text
/tmp/pr770-revalidation-b81c628f/corpus/_archive/dev2-laws-check/dispatch/validation-4.md:1: AC-14 (Captain amendment 1) adds words in a sentence kept from the criterion it replaces that are not in his words: report, quoting, l2; remove them, or ask the Captain and record his answer as an amendment, then run this check again
/tmp/pr770-revalidation-b81c628f/corpus/_archive/dev2-laws-check/dispatch/validation-4.md:1: AC-18 (Captain amendment 1) adds words in a sentence kept from the criterion it replaces that are not in his words: one, run, per, push, tip, whose, names; remove them, or ask the Captain and record his answer as an amendment, then run this check again
/tmp/pr770-revalidation-b81c628f/corpus/_archive/dev2-laws-check/dispatch/validation-4.md:1: AC-19 (Captain amendment 1) adds words in a sentence kept from the criterion it replaces that are not in his words: d1; remove them, or ask the Captain and record his answer as an amendment, then run this check again
/tmp/pr770-revalidation-b81c628f/corpus/_archive/dev2-laws-check/dispatch/validation-4.md:1: AC-20 (Captain amendment 1) adds words in a sentence kept from the criterion it replaces that are not in his words: ci, job's; remove them, or ask the Captain and record his answer as an amendment, then run this check again
/tmp/pr770-revalidation-b81c628f/corpus/_archive/fo-interviews-extension/dispatch/validation-3.md:1: AC-8 (Captain amendment 1) adds words in a sentence kept from the criterion it replaces that are not in his words: retaining, their, predictions; remove them, or ask the Captain and record his answer as an amendment, then run this check again
/tmp/pr770-revalidation-b81c628f/corpus/_archive/fo-lifecycle-mod/dispatch/validation-8.md:1: AC-8 (Captain amendment 3) adds words in a sentence kept from the criterion it replaces that are not in his words: package's, references, sd, mods, kc-dev-flow-2, md; remove them, or ask the Captain and record his answer as an amendment, then run this check again
/tmp/pr770-revalidation-b81c628f/corpus/_archive/fo-lifecycle-mod/dispatch/validation-8.md:1: AC-14 (Captain amendment 3) adds words in a sentence kept from the criterion it replaces that are not in his words: through, pr_watch, slug, dispatch, attempted, then; remove them, or ask the Captain and record his answer as an amendment, then run this check again
/tmp/pr770-revalidation-b81c628f/corpus/_archive/fo-lifecycle-mod/dispatch/validation-8.md:1: AC-15 (Captain amendment 3) adds words in a sentence kept from the criterion it replaces that are not in his words: one, file, sync; remove them, or ask the Captain and record his answer as an amendment, then run this check again
/tmp/pr770-revalidation-b81c628f/corpus/_archive/fo-lifecycle-mod/dispatch/validation-8.md:1: AC-18 (Captain amendment 5) adds words in a sentence kept from the criterion it replaces that are not in his words: replay, plan, counted; remove them, or ask the Captain and record his answer as an amendment, then run this check again
/tmp/pr770-revalidation-b81c628f/corpus/_archive/kc-decision-log-cli/dispatch/validation-2.md:1: AC-12 (Captain amendment 6) adds words in a sentence kept from the criterion it replaces that are not in his words: shows, skills, read-adr, ac4, text_check, py, asserts, ac4, install-falsifiers, txt, 2026-10-22; remove them, or ask the Captain and record his answer as an amendment, then run this check again
/tmp/pr770-revalidation-b81c628f/corpus/_archive/new-work-starts-from-a-story-map/dispatch/validation-4.md:1: AC-13 (Captain amendment 2) adds words in a sentence kept from the criterion it replaces that are not in his words: replaces, arm, arm, alone, does, count, node, kc-journey-map, lib, journey-review, test, mjs; remove them, or ask the Captain and record his answer as an amendment, then run this check again
/tmp/pr770-revalidation-b81c628f/corpus/_archive/paseo-human-surfaces-visible-and-reachable/dispatch/validation-2.md:1: AC-10 (Captain amendment 1) adds words in a sentence kept from the criterion it replaces that are not in his words: must, pass; remove them, or ask the Captain and record his answer as an amendment, then run this check again
/tmp/pr770-revalidation-b81c628f/corpus/_archive/peers-paseo-rule-matches-practice/dispatch/validation-3.md:1: AC-9 (Captain amendment 2) adds words in a sentence kept from the criterion it replaces that are not in his words: steer, successful, true, actual, steer, notify, true, send, arguments, recipient-side, record, matching, finish, event, information-only, notice, notice, finish, callback, causes, another, action, treated, proof, understanding, amendments-2, 3, exact-head; remove them, or ask the Captain and record his answer as an amendment, then run this check again
/tmp/pr770-revalidation-b81c628f/corpus/_archive/peers-paseo-rule-matches-practice/dispatch/validation-3.md:1: AC-11 (Captain amendment 4) adds words in a sentence kept from the criterion it replaces that are not in his words: policy; remove them, or ask the Captain and record his answer as an amendment, then run this check again
/tmp/pr770-revalidation-b81c628f/corpus/_archive/prod-security-review-gates/dispatch/validation-4.md:1: AC-14 (Captain amendment 2) adds words in a sentence kept from the criterion it replaces that are not in his words: question, he, answered; remove them, or ask the Captain and record his answer as an amendment, then run this check again
/tmp/pr770-revalidation-b81c628f/corpus/_archive/read-adr-honors-adr-folder/dispatch/validation-1.md:1: AC-7 (Captain amendment 1) adds words in a sentence kept from the criterion it replaces that are not in his words: one, host; remove them, or ask the Captain and record his answer as an amendment, then run this check again
/tmp/pr770-revalidation-b81c628f/corpus/_archive/read-adr-honors-adr-folder/dispatch/validation-1.md:1: AC-8 (Captain amendment 1) adds words in a sentence kept from the criterion it replaces that are not in his words: absolute, without, absolute-path, conversion, unusable; remove them, or ask the Captain and record his answer as an amendment, then run this check again
/tmp/pr770-revalidation-b81c628f/corpus/_archive/seed-check-requires-schema-fields/dispatch/validation-3.md:1: AC-10 (Captain amendment 1) adds words in a sentence kept from the criterion it replaces that are not in his words: comparison; remove them, or ask the Captain and record his answer as an amendment, then run this check again
```

## Falsifiers

All 13 mutants fail through assertions, not syntax/import failures; caches disabled. Mutations affect isolated scratch code, never candidate bytes.

- AC-1 missing call: Mutant rejected with exit 1; mutation-1.log

- AC-2 deleted words counted: Mutant rejected with exit 1; mutation-2.log

- AC-2 evidence tail counted: Mutant rejected with exit 1; mutation-3.log

- AC-3 later words ignored: Mutant rejected with exit 1; mutation-4.log

- AC-4 repair followup held: Mutant rejected with exit 1; mutation-5.log

- AC-5 L2 pattern removed: Mutant rejected with exit 1; mutation-6.log

- AC-6 filler counted: Mutant rejected with exit 1; mutation-7.log

- AC-6 AC ids counted: Mutant rejected with exit 1; mutation-8.log

- AC-6/7 clean output added: Mutant rejected with exit 1; mutation-9.log

- multi-paragraph repair reverted: Mutant rejected with exit 1; mutation-10.log

- short slash sentence filter reverted: Mutant rejected with exit 1; mutation-11.log

- declaration prefix normalization reverted: Mutant rejected with exit 1; mutation-12.log

- AC-7 README sentence added: Mutated README rejected with exit 1; mutation-readme.log


The raw shared-exit mutant removes added_words and still exits 1, but loses the candidate-only diagnostic; exit-only validation would miss this.

## Required checks

### adr

```sh
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since 2bda2e98304261d46b0ae7205a29ddc9038d2b4d --require 0057
```

Exit 0:

```text
53 ADR file(s) checked, 0 legacy
```

### adr-dispatch

```sh
python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since 2bda2e98304261d46b0ae7205a29ddc9038d2b4d
```

Exit 0:

```text
53 ADR file(s) checked, 0 legacy
```

### numbers

```sh
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/number_guards.py check --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 --task /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/rewritten-criteria-checked-against-captain-words.md
```

Exit 0:

```text
migration guard skipped: no migrations-path declared
PASS: no findings
base 2bda2e983042 head b81c628facd2 merge-base 2bda2e983042
```

### design

```sh
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/design_surfaces.py check /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/rewritten-criteria-checked-against-captain-words.md
```

Exit 0:

```text
rewritten-criteria-checked-against-captain-words.md: design surfaces presentable
scope check not run: stage is validation, not ideation
```

### comments

```sh
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/comment_ratio.py 2bda2e98304261d46b0ae7205a29ddc9038d2b4d b81c628facd2cd38568018beec47b6c4566c0aae --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2
```

Exit 0:

```text
code lines 223, comment lines 3, 1.3%
   2/  94 kc-dev-flow-2/scripts/test_dispatch_records.py
   1/  53 kc-dev-flow-2/scripts/design_surfaces.py
maximum 5% (package default) met
```

### doc-impact

```sh
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/doc_impact.py 2bda2e98304261d46b0ae7205a29ddc9038d2b4d b81c628facd2cd38568018beec47b6c4566c0aae
```

Exit 0:

```text
docs/adr/0041-seed-admission-enforces-required-fields.md	review	kc-dev-flow-2/scripts/design_surfaces.py
docs/adr/0045-validation-reruns-require-a-later-recorded-captain-ruling.md	review	kc-dev-flow-2/scripts/dispatch_records.py
docs/adr/0048-paseo-stage-workers-complete-by-final-reply-and-hand-publication-to-fo.md	review	kc-dev-flow-2/scripts/dispatch_records.py
docs/adr/0057-rewritten-criteria-are-compared-with-the-captains-words.md	updated	added_words, kc-dev-flow-2/scripts/design_surfaces.py
learning.md	review	kc-dev-flow-2/scripts/dispatch_records.py, kc-dev-flow-2/scripts/laws_check.py
5 document(s) mention what changed; each needs 'updated' or 'unaffected: <reason>'
```

### dispatch

```sh
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/dispatch_records.py /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/rewritten-criteria-checked-against-captain-words
```

Exit 1:

```text
implementation-1-message-1.md: needs a scope-notes line naming main as the completion recipient
/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/rewritten-criteria-checked-against-captain-words/dispatch/validation-2.md:1: no 'Symptom:' line; before first '## ' heading add 'Symptom: <failure, named the same way each time>' or 'Symptom: none'
```

### dispatch-candidate

```sh
python3 -B /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-rewritten-criteria-checked-against-captain-words/.context/pr770-revalidation-b81c628f/candidate/kc-dev-flow-2/scripts/dispatch_records.py /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/rewritten-criteria-checked-against-captain-words
```

Exit 1:

```text
implementation-1-message-1.md: needs a scope-notes line naming main as the completion recipient
/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/rewritten-criteria-checked-against-captain-words/dispatch/validation-2.md:1: no 'Symptom:' line; before first '## ' heading add 'Symptom: <failure, named the same way each time>' or 'Symptom: none'
```

### diff-check

```sh
git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-rewritten-criteria-checked-against-captain-words/.context/pr770-revalidation-b81c628f/candidate diff --check 2bda2e98304261d46b0ae7205a29ddc9038d2b4d b81c628facd2cd38568018beec47b6c4566c0aae
```

Exit 0:

```text

```

## Full regression and hosted proof

All 26 CI-listed local commands passed; 1104 tests, 7 existing skips. full-suite.json records every command and per-command log. Local Spacedock CLI 0.27.2/plugin 0.27.3 differs from hosted plugin v0.27.2; exact-head hosted tests separately succeeded at https://github.com/iamcxa/kc-claude-plugins/actions/runs/41751257209. CI triggers unchanged; cost per PR unmeasured.

## Limits and disposition evidence

```json
{
  "whole-new-sentence": [],
  "evidence-tail": [],
  "faithful-translation": [
    [
      3,
      "AC-9",
      [
        "link"
      ]
    ]
  ],
  "translation-confirmed": []
}
```

Fence reproduction:

```text
live dispatch: 1 design: 0 L2: 1 words: [(3, 'AC-9', ['revision', 'link'])]
backticks dispatch: 1 design: 0 L2: 1 words: [(3, 'AC-9', ['revision', 'link'])]
tilde dispatch: 0 design: 0 L2: 0 words: []
Corpus scan: 192 task files; 0 acceptance sections with tilde fences
```

The only added Python source comment points to ADR 0057; the other two counted lines are fixture headings. doc_impact: ADR 0057 updated; ADR 0041 unaffected (seed checks unchanged), ADR 0045 unaffected (ruling-history predicate unchanged), ADR 0048 unaffected (completion/publication contract unchanged), learning.md unaffected (reading-load, parser-consumer and corpus practices followed).

All eight changed files map to the approved outcome: comparison/helper; validation-only caller; L2 parser; three regression files; laws reference; ADR. No version or CI edit. Without-call/parser and reverted normalization/paragraph/slash checks establish necessity. Whole new sentences, evidence tails and faithful translations remain accepted limits.

## Independent stage report

## Stage Report: validation

- DONE: Independent verdict on PR #770 head b81c628f against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  PASSED for the bounded criteria as explicitly re-measured after main integration at b81c628facd2cd38568018beec47b6c4566c0aae, base 2bda2e98304261d46b0ae7205a29ddc9038d2b4d. Evidence: rewritten-criteria-checked-against-captain-words/validation-2/validation.md; no Material finding or delivery approval.
- DONE: Revalidation after the chief-engineer delivery review (review/chief-engineer-batch13.md): origin/main with #771 was merged in and the RewrittenCriterionTests fixtures numbered 2 or higher gained Symptom lines; re-measure AC-1, AC-2 and AC-7 and every criterion at this head, and carry the earlier F1 (tilde-fence, Deferred risk) and F2 (FO record, Polish) judgments forward if they still hold. Do not start agents you were not asked to
  Main is an ancestor; comparison-parser bytes equal prior 40ced2d65. F1 remains Deferred risk and F2 Polish; new F3 is a separate dispatch metadata finding. No agents started or product repairs made.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  Five-step rewritten-criteria-checked-against-captain-words/validation-2/acceptance.sh ran unchanged under /bin/bash --noprofile --norc, exit 0; validation.md contains every command, expected observation and acceptance.log. ADR lint --since 2bda2e98304261d46b0ae7205a29ddc9038d2b4d exits 0; also --require 0057 exits 0.
- DONE: AC-1 — The historical rewrite is held before validation.
  Untouched b4e88ece4 snapshot: base/candidate exit 1 with identical missing-Symptom stderr, but only candidate stdout names AC-9/amendment 3/revision, link (41 words). Header-normalized replay gives 0→1; removing added_words loses the diagnostic even though raw exit remains 1, and fails the focused assertion.
- DONE: AC-2 — A rewrite adding nothing passes the comparison.
  Deletion-only raw replay gives byte-identical base/candidate exit 1 and empty stdout; with Symptom: none both exit 0 silently. Renumber/marker/evidence controls pass; counting deletions or the evidence tail fails assertions.
- DONE: AC-3 — Later Captain words clear the hold.
  Amendment 4 with Supersedes: none and Asked: revision, link clears the historical diagnostic; a normalized record naming it exits 0. Ignoring later amendments fails the clearance test; Captain-line control also passes.
- DONE: AC-4 — Repair dispatch remains available.
  Historical implementation-4-message-2 has no added-words diagnostic; validation-2-message-1 does. Normalized records exit 0 and 1 respectively; applying the comparison to every record fails the repair-route assertion.
- DONE: AC-5 — L2 classifies a violation at its event.
  Temporary Git events yield violation: L2 dispatch-record-complete, exit 1, with later clearance applying only to later events. Removing the output pattern makes the runner exit 2 and fails the assertion.
- DONE: AC-6 — Corpus bound and no regression.
  State de81585004ce636732a2515fd759f2b07c2980cd: 51 amended tasks' newest-added records, 10 held/18 diagnostics; no other stdout/stderr/exit differences. Every line is in corpus-lines.log; filler, AC-id and extra-output mutants fail. All 26 CI-listed local commands pass: 1104 unittest tests, 7 existing skips.
- DONE: AC-7 — No task-added reading at clean lifecycle moments.
  Workflow bytes and budget are unchanged from integrated main: 5836→5836 (the original 5781 baseline is no longer current; 55 words are inherited). Startup, idle, archive, merge ask and clean output add zero; replay adds only 41 stdout words beyond the shared 20-word Symptom hint. README/clean-output mutants fail; laws 1255→1345 and docstring 745→771 are outside those clean reads.
- DONE: Judge limits, goal sufficiency, minimal necessity, documents and comments.
  Whole-new-sentence/evidence-tail omissions and faithful-translation hold reproduced. Eight changed paths serve comparison, dispatch, event parser, regression proof or retained rules; call/parser/prefix/paragraph/slash falsifiers justify them. All five doc_impact dispositions verified; comment ratio 223 code/3 comment lines (1.3%), no added narrative comment; ADR/number/design/diff checks pass.
- FAILED: Dispatch-record completeness required by validation principles.
  Both declared-package and candidate commands exit 1: implementation-1-message-1 lacks the full completion-recipient line (F2); current validation-2 lacks Symptom (F3). Historical records were preserved; passing product checks does not erase these metadata failures.
- DONE: Verify exact-head hosted proof and preserve ownership.
  GitHub unit-test run 41751257209 succeeded on b81c628facd2cd38568018beec47b6c4566c0aae, separately from local CLI 0.27.2/plugin 0.27.3 versus CI plugin 0.27.2. PR #770 was open/non-Draft at the assigned head. CI triggers unchanged; cost per PR unmeasured.
- DONE: Remove the throwaway detached worktree and retain the candidate.
  Candidate worktree was clean and removed; acceptance script removed its own worktree/fixtures. Assigned branch remains b81c628facd2cd38568018beec47b6c4566c0aae and clean. No product commit, push, PR comment, review request, ready or merge action.
- SKIPPED: Fresh exact-head RoboRev proof, backlog/metadata dispositions and delivery.
  Implementation's daemon-unavailable result is incomplete, not clean review evidence. First Officer owns outstanding review verification, committed decline/backlog routing, F2/F3 disposition and delivery.

### Summary

The integrated candidate passes the accepted bounded comparison with independent historical replay, corpus comparison, all local CI commands, exact-head hosted tests, 13 rejected mutations and fresh-shell acceptance. This supersedes the prior validation's baseline measurements without rewriting Captain criteria: original base exit 0 and 5781 words are no longer true after the accepted main integration; whole rewrites, translations, tilde examples, adoption and delivery are not proved.

### Findings

- F1 Deferred risk (carried forward): released user/workflow is the First Officer checking amended-task validation records. Observable harm: a constructed tilde-fenced duplicate AC-9 changes strict dispatch/L2 from 1 to 0; design check stays 0 and backtick control stays held. Boundary: value-ac[AC-1] protects the historical widening, whose accepted replay passes. Trigger: reproduced at this head, but 0 of 192 committed acceptance sections uses tilde fences; no new normal-workflow harm or changed parser bytes. The chief engineer routes it to backlog with no parser repair here; reclassify if a supported task or accepted fence contract establishes the trigger.
- F2 Polish (carried forward): released workflow is resuming implementation by follow-up. Observable harm: implementation-1-message-1 fails completion-line metadata validation, with no observed lost completion; its full initial instruction is explicitly inherited. Boundary: contract[docs/adr/0048-paseo-stage-workers-complete-by-final-reply-and-hand-publication-to-fo.md#decision] preserves final-reply completion/FO publication. Trigger: the actual committed record still fails both checkers. First Officer disposition remains; do not rewrite historical evidence.
- F3 Polish (new): released workflow is dispatching this second validation. Observable harm: validation-2.md lacks Symptom and the required strict record check exits 1; no lost symptom escalation is established for this integration-only recheck. Boundary: contract[kc-dev-flow-2/references/sd/workflow.md#stages] requires a passing saved-record check before dispatch; this is an FO record defect, not a changed candidate boundary. Trigger: actual record at de81585004ce636732a2515fd759f2b07c2980cd and both checker outputs. First Officer must disposition it; record a later correction without silently rewriting the historical dispatch.

