import datetime, hashlib, json, pathlib, subprocess
E=pathlib.Path("/tmp/opencode/claims-name-their-source-validation")
C=pathlib.Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-claims-name-their-source/.context/validation-777")
S=pathlib.Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state")
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
audit=json.loads((E/'replay-audit.json').read_text())
rows=[]
for r in audit['rows']:
    if r['scenario']=='K':
        rep=int(r['id'].split('-')[-2])
        text=pathlib.Path(r['answer_path']).read_text()
        rows.append(dict(id=r['id'],arm=r['arm'],regrade=r['regrade'],
                         target_claim_attributed=r['arm']=='candidate' and rep in (1,5,6),
                         reason=('The limits heading or count bullet explicitly says validation report, not run.' if r['arm']=='candidate' and rep in (1,5,6) else 'The disputed count has no source label; report language elsewhere does not attach to this limit.'),
                         evidence_lines=r['limit_lines'],source=r['answer_path']))
semantic=dict(date=now,method='Independent reading of saved outputs against the accepted target-count wording; does not modify the frozen grader or replace its mechanical result.',candidate_target_count=3,candidate_runs=6,base_target_count=0,base_runs=3,rows=rows)
(E/'semantic-read.json').write_text(json.dumps(semantic,indent=2)+'\n')
findings=[
dict(id='F1',severity='high',classification='Needs decision',title='The fixed grader does not establish the count-scenario acceptance result',file='claims-name-their-source/validation/implementation-2/replay.py',line=35,
     detail='The frozen grader returns 6/6 candidate passes, but the target wrong-count limit is attributed in only runs 1, 5 and 6. Runs 2, 3 and 4 label other claims, leaving this limit unsourced. All three base answers also false-pass. A title-only counterexample flips from fail to pass without changing the wrong count.',
     fix='FO must return the discrepancy against the original 5-of-6 behavioral bar for a recorded Captain disposition before any product repair or new replay. Do not relabel the narrower 3/6 read as the unchanged mechanical score.',
     released_user_and_normal_workflow='A First Officer writing the accepted validation-gate summary from worker reports.',
     observable_harm='A gate can claim the reporting fix meets its bar while the historical wrong-count claim remains unattributed in half the candidate outputs.',
     affected_value='value-ac[AC-7] preserves the original scenario K target-count rule and five-of-six bar.',
     trigger_evidence='replay-audit.json controls and implementation-2 K candidate runs 2/3 plus implementation-3 K candidate run 4; semantic-read.json.',
     status='open'),
dict(id='F2',severity='medium',classification='Needs decision',title='The required trunk-based number check remains held by the stacked parent',file='claims-name-their-source.md',line=214,
     detail='number_guards.py check --base origin/main exits 1 on ADR 0054, which belongs to parent PR #773; this task reserves 0055. Parent 128fe3e3 is still open and is the actual PR base. The same check against that pinned parent exits 0.',
     fix='FO must reconcile the explicitly assigned origin/main check with stacked delivery or land and recheck the parent through its own authority. Do not add another task\'s number reservation here or silently substitute the passing base.',
     released_user_and_normal_workflow='First Officer preparing the required number-reservation check before this task\'s merge ask.',
     observable_harm='The required origin/main acceptance command is red and cannot support an all-green delivery recommendation.',
     affected_value='contract[kc-dev-flow-2/references/sd/workflow.md#number-guards] requires a passing candidate number check.',
     trigger_evidence='number-guards.log; number-guards-stacked.log; sibling-pr.json; parent task ADR: 0054 read on this date.',
     status='open')
]
(E/'findings.json').write_text(json.dumps(findings,indent=2)+'\n')
criteria=[
dict(name='AC-1: rule and budget',status='passed',note='Both sentences present; 5891/5891 and stacked-parent +55. Removing the step exits 1 and names +55.',evidence='lint.log; mutation-budget.log; word-counts.json'),
dict(name='AC-2: gate output',status='passed',note='Pass/hold/unreadable-input codes 0/1/2 preserved; one reminder before the final ask. Dropping only check emission fails its test while question passes.',evidence='focused-tests.log; mutation-check.log; mutation-question-control.log'),
dict(name='AC-4: observer boundary',status='passed',note='Chat claim listed; committed-summary rule not excluded. Rewording the chat phrase fails lint. This is the static proof the criterion requests, not a native observer-behavior claim.',evidence='lint.log; mutation-chat.log'),
dict(name='AC-5: lifecycle words',status='passed',note='Startup 5836+48 to 5891+48; question 3 to 30; check 57 to 84. Idle/archive/ideation sources unchanged against the stacked parent. Deleting the rule yields +0 instead of +55.',evidence='word-counts.json; count-falsifier.json'),
dict(name='AC-6: callers and ADR',status='untested',note='Full suite still running when this file was initialized; final state is updated from full-suite.log. ADR lint passes; missing required 0055 exits 1.',evidence='full-suite.log; adr-lint.log; adr-missing-falsifier.log'),
dict(name='AC-7: Claude replay',status='blocked',note='Unchanged mechanical grader P 6/6 and K 6/6; independent target-claim read K 3/6, below 5/6. F1 needs disposition. No new model runs.',evidence='replay-audit.json; semantic-read.json; findings.json')
]
(E/'criteria.json').write_text(json.dumps(criteria,indent=2)+'\n')
dispositions=[
('docs/adr/0020-a-rise-in-the-workflow-word-budget-needs-a-captain-ruling-recorded-with-it.md','unaffected: equality arithmetic, quoted authority and loading ledger retained; new +55 step matches task gate.'),
('docs/adr/0037-workers-check-shared-work-and-return-to-fo-early.md','unaffected: Team bullet and protected +144 step unchanged.'),
('docs/adr/0044-delivery-gate-summaries-carry-review-facts-with-legacy-call-compatibility.md','unaffected: optional summary and legacy question behavior retained; added output is advisory.'),
('docs/adr/0049-special-roles-and-stage-defaults-follow-one-model-table.md','unaffected: model table, effort lint and trigger ranking unchanged.'),
('docs/adr/0051-the-merge-ask-check-requires-the-round-count.md','unaffected: round-count refusal still runs before a merge record; reminder adds no acceptance path.'),
('kc-dev-flow-2/README.md','unaffected: entry, adoption and maintenance instructions still describe the candidate.'),
('kc-dev-flow-2/skills/maintain-flow/SKILL.md','unaffected: word ledger, bounded replay and maintenance process still apply.'),
('learning.md','unaffected: local worktree-config prohibition, independent lifecycle recount and caller search followed.')]
(E/'doc-dispositions.json').write_text(json.dumps([dict(file=p,disposition=d,implementation_disposition_checked=True) for p,d in dispositions],indent=2)+'\n')
manifest=dict(checked_at=now,candidate='f79711ca8d6325c1c14781342cf23855dd62b10a',assigned_worktree="/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-claims-name-their-source",detached_worktree=str(C),origin_main='e1bee223c47a1cd534a665a47776b683375b34fc',stacked_parent='128fe3e3fed70fa64ded8657f5a1b36933af3ced',state_at_entry='20027dea82cf251b04668881439dd43d82afcb63',active_package="/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0",dispatch_package='/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0',full_suite_command="PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p 'test_*.py'",acceptance_command='/bin/bash --noprofile --norc acceptance.sh',acceptance_exit=0,new_provider_runs=0)
(E/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Saved criteria, two Needs decision findings, semantic read, and document dispositions.')

