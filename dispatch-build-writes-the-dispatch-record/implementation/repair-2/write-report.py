#!/usr/bin/env python3
"""Write completion evidence only after every exact-head command succeeds."""
import json
from pathlib import Path
import re
import subprocess

state = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
slug = 'dispatch-build-writes-the-dispatch-record'
root = state / slug / 'implementation/repair-2'
entity = state / (slug + '.md')
code = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-dispatch-build-writes-the-dispatch-record')
sha = '778367adde2e20e0b3e51966ddba2d9f77f9e614'
assert subprocess.check_output(['git','-C',str(code),'rev-parse','HEAD'],text=True).strip() == sha
assert (root/'fresh/candidate.txt').read_text().strip() == sha
ci = json.loads((root/'package-ci/results.json').read_text())
assert len(ci) == 28 and all(row['exit'] == 0 for row in ci)
mutants = json.loads((root/'exact-scope-falsifiers/results.json').read_text())
original_mutants = json.loads((root/'fresh/falsifiers/results.json').read_text())
assert len(mutants)==9 and len(original_mutants)==13
assert all(row['status']=='passed' for row in mutants+original_mutants)
scope = json.loads((root/'scope-summary.json').read_text())
assert scope['matrix_cases']==92 and scope['refusal_snapshots']==98 and scope['all_preserved']
counts = dict(commands=len(ci), tests=sum(row['tests'] or 0 for row in ci), skipped=sum(row['skipped'] for row in ci))
(root/'verification.json').write_text(json.dumps(dict(candidate=sha, package=counts, scope=scope,
    original_falsifiers=13, scope_falsifiers=9, publication='FO-owned; not run',
    concurrency='exclusive same-task writer required; no transaction guarantee'),indent=2)+'\n')
initial=Path('/tmp/spacedock-dispatch/5c030106-8d82-4542-855e-1498b2563c69-spacedock-ensign-dispatch-build-writes-the-implementation.md').read_text()
initial=[line for line in initial.split('### Completion checklist\n',1)[1].split('### Summary',1)[0].splitlines() if line.strip()]
current=(state/slug/'dispatch/implementation-1-message-4.md').read_text()
current=[re.sub(r'^\d+\. ', '', line) for line in current.split('## Checklist\n',1)[1].split('## Scope notes',1)[0].splitlines() if re.match(r'^\d+\. ',line)]
assert len(initial)==len(current)==4
items=[
('SKIPPED',initial[0],f'Product repair {sha} is local on the assigned branch, parent 0d84d5d1b96fd674dba3a442d69c2e7898cceccd and assigned base 334d91e3165953b2ca7191e3308d80b6c02c4a99. PR #812 remains draft on the parent head (pr-readonly.json); FO owns its push/review/CI. No product push or PR write.'),
('DONE',initial[1],'ADR 0070, its protected main writer pointer, FO-supplied model/roster, separate preflights and follow-up 1 observer correction are retained; only dispatch_stage.py and test_dispatch_stage.py change in this repair. Candidate ADR lint passes; no new ADR or version change.'),
('SKIPPED',initial[2],'All local exact-head acceptance checks and original thirteen mutations pass (fresh/candidate.txt); hosted AC-8 and independent validation of this candidate remain FO-owned. Nine additional whole-scope mutations fail their matching snapshot assertion (exact-scope-falsifiers/).'),
('SKIPPED',initial[3],'Fresh lint, candidate ADR lint, number guards and diff check exit 0; comment ratio is 3/776 = 0.4%, below 5%. Installed 0.35.0 ADR lint still exits 1 for the unchanged historical ADR 0047 assertion; follow-up 2 authorizes the candidate linter. prepared-pr.md is ready; publication/RoboRev/hosted CI are not run and CI cost per PR is not measured; triggers unchanged.'),
('DONE',current[0],'regressions-before.log and before-snapshots.jsonl reproduce the previous writer losing the staged-only retry version. The adopted chief-engineer class design is implemented at '+sha+'; no upstream transaction redesign or new Captain ruling is introduced.'),
('DONE',current[1],'resolve_scope resolves the canonical builder commit unit; check_task_scope runs once before select_record on every route. Literal NUL-safe Git reads compare HEAD/index and raw worktree hashes/executable modes, conflicts/flags and nonignored untracked files; failures name their path, emit no envelope, and invoke neither builder nor cleanup (scope-summary.json; 98 unchanged snapshots).'),
('DONE',current[2],'The 92-row flat/folder matrix covers task/older/reused/new records and nested/literal reports across fresh/retry/new-round/advance, including all three versions, additions/deletions/renames/conflicts/types/modes and hidden flags. Real 0.27.2 builder observers and nine isolated mutations prove each boundary: remove guard/index/worktree/untracked, narrow to record/dispatch, move after creation, bypass retry/advance; each breaks snapshot preservation.'),
('DONE',current[3],f'Unchanged acceptance.sh in fresh bash exits 0 at {sha}; fresh/ has 20 seam, 47 lint and 115 dispatch-record tests plus real transport and thirteen counterexamples. package-ci/results.json: {counts["commands"]} checked-in CI Python commands exit 0, {counts["tests"]} tests reported, {counts["skipped"]} skipped as recorded; local product commit only, no PR reply.'),
('DONE','Preserve follow-up 3 and AC-1 through AC-6 success, failure, retry and advance contracts.','Real controls retain exact received inputs, owned cleanup only, untracked/staged/index-only record refusal, clean immediate reuse, changed-input/later-commit numbering, owner-reconciled dispatch, checker/staged-build failures and committed-then-assembly failure retry. Both layouts preserve unrelated staged/worktree/untracked work outside the dispatch commit; advance commits before emitting its envelope. Removing those boundaries is caught by the original and scope falsifiers.'),
('DONE','AC-7 and local AC-8: approved workflow budget and consumers, real-binary CI wiring and missing-binary hold.','fresh/: lint-skills is 5931/5931; restored-base README, deleted CI step and missing-binary controls still reject their mutations; real test_sd_dispatch passes. Workflow prose/diagram/CI configuration are unchanged by this repair; hosted proof remains unclaimed.'),
('DONE','State the exclusive-writer limit in the report and the PR text; claim no concurrency safety.','Exclusive same-task ownership must last through check/build/commit/cleanup. This single precondition is not a transaction lock; no concurrent-writer guarantee or overlapping-writer proof is claimed. prepared-pr.md repeats this limit; the refusal tells the owner to preserve/reconcile staged/worktree versions before an intentional commit, never blindly state commit divergent data.'),
('DONE','Document the inherited pinned-builder no-op retry limitation.','With unrelated staged work, a no-op retry can fail its empty task-scoped commit because upstream inspects the global cached diff. The allowed-route control proves versions survive, then retries successfully with outside work unstaged; fresh/changed-task dispatches and new-record advance succeed with outside work staged. evidence-notes.md distinguishes this upstream behavior from the repaired loss class.'),
('DONE','Required document dispositions and design-surface check.','doc-impact-verdicts.json itemizes all 13 referenced documents below against the assigned base; this repair edits none. design-surfaces.log says presentable; Scope scan is explicitly not run because the task remains validation. The frontmatter and earlier reports are preserved.'),
]
text='\n\n## Stage Report: implementation\n\n'+'\n'.join(f'- {status}: {item}\n  {evidence}' for status,item,evidence in items)
text+='\n\n### Document dispositions\n\n'
for row in json.loads((root/'doc-impact-verdicts.json').read_text()):
    text+=f'- `{row["doc"]}` — {row["verdict"]}: {row["reason"]}\n'
text+='\n### Summary\n\n'
text+=f'This complete implementation report supersedes both earlier implementation reports: candidate {sha} closes the pre-existing task-work class before any record selection, while retaining owned cleanup and committed retry rules. All local exact-head acceptance and package commands pass; same-task exclusive ownership remains required, and FO owns product publication, new-head hosted CI, RoboRev and independent validation. Evidence is under `{slug}/implementation/repair-2/`; the inherited no-op retry limit is explicit above and in the prepared PR text.\n'
(root/'stage-report.md').write_text(text)
read=subprocess.run(['/Users/kent/.local/bin/spacedock','status','--read',slug,'--workflow-dir',str(state.parent),'--json'],check=True,capture_output=True,text=True)
info=json.loads(read.stdout)
(root/'task-before-append.json').write_text(read.stdout)
assert info['frontmatter']['status']=='validation'
assert int(info['total_lines'])==len(entity.read_text().splitlines())
assert sha not in entity.read_text().split('## Stage Report: implementation')[-1]
with entity.open('a') as target:
    target.write(text)
print(json.dumps(dict(candidate=sha, report_lines=len(text.splitlines()), **counts)))
