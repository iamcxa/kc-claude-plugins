import importlib.util, os, shutil, subprocess, sys
from pathlib import Path
C=Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-second-round-prompts-a-step-back/.context/validation-2-candidate"); E=Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-second-round-prompts-a-step-back/.context/validation-2-evidence"); P=C/'kc-dev-flow-2/scripts'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
def run(*args):
    return subprocess.run(list(map(str,args)), cwd=C, capture_output=True, text=True)
def load(name):
    spec=importlib.util.spec_from_file_location(name,P/(name+'.py'))
    m=importlib.util.module_from_spec(spec); sys.modules[name]=m; spec.loader.exec_module(m); return m
r=load('test_role_triggers'); w=load('test_pr_watch'); g=load('test_delivery_gate')
method1='StepBackTest.test_two_replacements_still_remind_after_validation_event_is_cleared'
method2='StepBackTest.test_two_failed_validations_still_remind_after_replacement_event_is_cleared'
condition='2 in (failures, len(replacements))'
mutations=[
('validation-masked',condition,'len(replacements) == 2',method2),
('replacement-masked',condition,'failures == 2',method1),
('original-max',condition,'max(failures, len(replacements)) == 2',method1),
('original-max-reverse',condition,'max(failures, len(replacements)) == 2',method2),
('duplicate-questions',' and not any(STEP_BACK in line for line in owed)','',
 'StepBackTest.test_a_third_event_deduplicates_only_a_call_line_carrying_the_three_questions')]
lines=[]
for name,old,new,method in mutations:
    target=E/'masking-mutations'/name
    shutil.copytree(P,target,ignore=shutil.ignore_patterns('__pycache__'),dirs_exist_ok=True)
    src=(target/'role_triggers.py').read_text(); assert src.count(old)==1
    (target/'role_triggers.py').write_text(src.replace(old,new))
    done=run(sys.executable,'-B',target/'test_role_triggers.py',method)
    (E/(name+'.log')).write_text(done.stdout+done.stderr)
    assert done.returncode==1 and 'FAIL:' in done.stderr,(name,done.stdout,done.stderr)
    lines.append(name+': mutant rejected, exit 1')
old=run('git','-C',C,'show','1c0dbb540f354300b75dba5a119d2614c8fb0c02:kc-dev-flow-2/scripts/role_triggers.py')
assert old.returncode==0
target=E/'masking-mutations'/'before-repair'
shutil.copytree(P,target,ignore=shutil.ignore_patterns('__pycache__'),dirs_exist_ok=True)
(target/'role_triggers.py').write_text(old.stdout)
for method in (method1,method2):
    done=run(sys.executable,'-B',target/'test_role_triggers.py',method)
    assert done.returncode==1 and 'FAIL:' in done.stderr,done.stderr
    (E/(method.rsplit('.',1)[1]+'-before.log')).write_text(done.stdout+done.stderr)
    lines.append(method+': original bug reproduced at 1c0dbb540, exit 1')
(E/'masking-mutations.log').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines),flush=True)
consumer=[]; words=[]
for failures,replacements in ((3,2),(2,3)):
    extra=r.call(r.CE,'gpt-6-astra','2026-10-20')+'\n'+r.call(r.ER,'opus','2026-10-20')
    body=r.task(reports=0,amendments=r.StepBackTest.amendments[:replacements],extra=extra).split('---\n',2)[2]+r.validations(*([r.StepBackTest.failed]*failures))
    fixture=w.TasksTests(); fixture.setUp()
    try:
        fixture.readme('roborev'); fixture.task('some-task',worktree=False,body=body.encode())
        rec=fixture.record('some-task','## Checklist\n\n- one\n',commit=False)
        rec.rename(rec.with_name('validation-1.md'))
        fixture.git(fixture.state,'add','some-task/dispatch')
        fixture.git(fixture.state,'commit','-qm','validation dispatch')
        code,out=fixture.tasks({})
        assert code==0 and len(out)==1 and 'before the next step' in out[0],(code,out)
        count=run('wc','-w') if False else subprocess.run(['wc','-w'],input=out[0]+'\n',text=True,capture_output=True)
        assert int(count.stdout)==51
        consumer.append(f'failures={failures}, replacements={replacements}: idle exit=0, one 51-word advisory\n'+out[0])
    finally: fixture.doCleanups()
    text=g.ALIGNED.replace('Alignment: not needed.','Alignment: not needed.\n'+extra)+'\n## Captain amendments'+body.split('## Captain amendments',1)[1]
    result=g.run_check(task=text,setup=g.committed(text),roles=True)
    assert result.code==0 and result.out.count('before the next step')==1 and result.out.splitlines()[-1]==g.gate.ASK,result.out
    consumer.append(f'failures={failures}, replacements={replacements}: merge exit=0, one advisory, ASK last\n'+result.out)
(E/'consumer-replays.log').write_text('\n'.join(consumer)+'\n')
for failures,replacements,want in ((2,0,51),(3,0,73),(0,3,68)):
    extra=r.call(r.ER,'opus','2026-10-20')
    body=r.task(reports=0,amendments=r.StepBackTest.amendments[:replacements],extra=extra)
    body+=r.validations(*([r.StepBackTest.failed]*failures))
    fixture=r.Fixture(); fixture.setUp()
    try:
        fixture.put(body); code,out=r.run(fixture.state,r.SLUG)
        line=next(x for x in out.splitlines() if 'is what I am solving' in x)
        result=subprocess.run(['wc','-w'],input=line+'\n',text=True,capture_output=True)
        assert int(result.stdout)==want,(want,result.stdout,out)
        words.append(f'wc -w: failures={failures}, replacements={replacements}, exit={code}, words={result.stdout.strip()}\n'+line)
    finally: fixture.doCleanups()
    if failures==3 or replacements==3:
        tail=body.split('---\n',2)[2]
        content=g.ALIGNED.replace('Alignment: not needed.','Alignment: not needed.\n'+extra)
        if replacements: content+='\n## Captain amendments'+tail.split('## Captain amendments',1)[1]
        else: content+=r.validations(*([r.StepBackTest.failed]*failures))
        result=g.run_check(task=content,setup=g.committed(content),roles=True)
        assert result.code==1 and g.gate.ASK not in result.out,result.out
        holding=[x for x in result.out.splitlines() if 'owes a chief-engineer' in x or 'is what I am solving' in x]
        count=subprocess.run(['wc','-w'],input='\n'.join(holding)+'\n',text=True,capture_output=True)
        words.append('merge hold selected lines words='+count.stdout.strip()+'\n'+'\n'.join(holding))
(E/'word-counts.log').write_text('\n'.join(words)+'\n')
print('Both masking paths pass through idle and merge; wc -w confirms 51/73/68-word lines.',flush=True)

