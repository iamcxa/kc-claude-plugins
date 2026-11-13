from pathlib import Path
import subprocess, shutil, json, os
x=Path(__file__).parent; wt=Path.cwd(); ev=x
m=x/'mutant'; m.mkdir(exist_ok=True)
for folder in ('kc-dev-flow-2','docs/adr'):
    shutil.copytree(wt/folder,m/folder,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
(m/'scripts').mkdir(exist_ok=True)
shutil.copy2(wt/'scripts/skill-frontmatter-lint.sh',m/'scripts/skill-frontmatter-lint.sh')
p=m/'kc-dev-flow-2/scripts'; run=x/'run.py'; results=[]
test=p/'test_dispatch_stage.py'
test.write_text(test.read_text().replace('Package root: {ROOT}', 'Package root: '+'/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-budget-form-counts-ideation-rounds-and-times-each-round/kc-dev-flow-2'))
for record in (m/'docs/adr').glob('*.md'):
    if not record.name.startswith('0085-'): record.unlink()

def mutation(name,file,old,new,cmd,expected=1):
    name='verified-'+name
    path=p/file; original=path.read_text(); assert old in original,(file,old)
    path.write_text(original.replace(old,new,1))
    for cache in m.rglob('__pycache__'): shutil.rmtree(cache)
    try:
        r=subprocess.run(['python3','-B',str(run),name,*map(str,cmd)])
        results.append(dict(name=name,mutation=f'{file}: {old} -> {new}',exit=r.returncode,expected=expected,passed=r.returncode==expected))
        assert r.returncode==expected,(name,r.returncode)
    finally: path.write_text(original)
for name,cmd in [('mutation-dispatch-control',['python3','-B',p/'test_dispatch_stage.py','DispatchStageTests.test_ideation_bound_holds_the_dispatch_past_it','DispatchStageTests.test_pilot_default_holds_the_third_ideation','DispatchStageTests.test_ideation_ignores_owed_special_roles']),('mutation-lint-control',['python3','-B',p/'lint-skills.py']),('mutation-adr-control',['python3','-B','/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts/adr_lint.py',m/'docs/adr','--root',m,'--require','0085'])]:
    r=subprocess.run(['python3','-B',str(run),name,*map(str,cmd)])
    assert r.returncode==0,(name,r.returncode)
mutation('mutation-ac1-no-grammar','role_triggers.py','if rounds:', 'if False:',
         ['python3','-B',p/'test_role_triggers.py','BudgetTest.test_fixed_forms_are_narrow_and_case_insensitive'])
mutation('mutation-ac2-no-ideation-hook','dispatch_stage.py','if args.stage in ("ideation", "implementation", "validation"):', 'if args.stage in ("implementation", "validation"):',
         ['python3','-B',p/'test_dispatch_stage.py','DispatchStageTests.test_ideation_bound_holds_the_dispatch_past_it'])
mutation('mutation-ac3-no-round-print','task_timeline.py','for x in r["rounds"]:', 'for x in []:',
         ['python3','-B',p/'test_task_timeline.py','TimelineTests.test_three_design_dispatches_have_separate_times_and_results'])
mutation('mutation-ac4-no-default','role_triggers.py','if default:', 'if False:',
         ['python3','-B',p/'test_dispatch_stage.py','DispatchStageTests.test_pilot_default_holds_the_third_ideation'])
mutation('mutation-ac5-full-role-check','dispatch_stage.py','role_args.append("--budget-only")', 'pass',
         ['python3','-B',p/'test_dispatch_stage.py','DispatchStageTests.test_ideation_ignores_owed_special_roles'])
mutation('mutation-ac6-hold-admitted','role_triggers.py','return bool(admitted and over), summary, bound', 'return bool(admitted), summary, bound',
         ['python3','-B',ev/'compare_budgets.py',x/'base/kc-dev-flow-2/scripts',p,x/'state'])
mutation('mutation-ac7-no-rounds','task_timeline.py','"rounds": rounds,','"rounds": [],',
         ['python3','-B',ev/'rounds_census.py',p,x/'state'])
mutation('mutation-ac8-prose-hold','../references/sd/workflow.md','ideation dispatch, two by default.', 'ideation dispatch; FO holds a third for the Captain.',
         ['python3','-B',p/'lint-skills.py'])
mutation('mutation-ac9-no-default','role_triggers.py','if default:', 'if False:',
         ['python3','-B',p/'test_dispatch_stage.py','DispatchStageTests.test_pilot_default_holds_the_third_ideation'])
mutation('mutation-ac10-no-pointer','role_triggers.py','    # see docs/adr/0085-a-budget-may-bound-ideation-rounds-and-the-timeline-prints-each-round.md\n','',
         ['python3','-B','/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts/adr_lint.py',m/'docs/adr','--root',m,'--require','0085'])
(ev/'mutations.json').write_text(json.dumps(results,indent=2)+'\n')
print(f'{len(results)} mutations killed')
