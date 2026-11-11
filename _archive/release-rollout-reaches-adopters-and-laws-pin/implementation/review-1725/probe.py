from pathlib import Path
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile

WT=Path(sys.argv[1]).resolve()
OUT=Path(__file__).resolve().parent
SCRIPTS=WT/'kc-dev-flow-2/scripts'
IDENTITY={**os.environ,'GIT_AUTHOR_NAME':'probe','GIT_AUTHOR_EMAIL':'probe@example.invalid','GIT_COMMITTER_NAME':'probe','GIT_COMMITTER_EMAIL':'probe@example.invalid','GIT_CONFIG_GLOBAL':os.devnull,'GIT_CONFIG_SYSTEM':os.devnull}

def run(args,**kw):
    return subprocess.run(args,text=True,capture_output=True,env=IDENTITY,**kw)

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

fixtures=load(SCRIPTS/'test_package_version.py','rollout_tests')
case=fixtures.RolloutTest()
case.setUp()
try:
    case.row('both',pin=case.old)
    case.content(case.repo,case.workflow,case.latest,case.readme('0.38.1')+'Changed rule.\n')
    case.content(case.repo,case.laws[0],case.latest,'changed laws\n')
    before=case.run_rollout()
    (OUT/'both-owed.log').write_text(before.stdout+before.stderr)
    assert before.returncode==1 and 'sync owed; laws:' in before.stdout and ' pin owed' in before.stdout
finally:
    case.doCleanups()

with tempfile.TemporaryDirectory() as d:
    root=Path(d)
    package=root/'kc-dev-flow-2'
    shutil.copytree(WT/'kc-dev-flow-2',package,ignore=shutil.ignore_patterns('__pycache__'))
    code=package/'scripts/package_version.py'
    text=code.read_text()
    old='laws_status(gh, repo, branch, released, set(tags.values()))'
    assert old in text
    code.write_text(text.replace(old,'laws_status(gh, repo, branch, tags[have], set(tags.values()))',1))
    proposed=run([sys.executable,'-B','-m','unittest','test_package_version.RolloutTest.test_each_laws_file_change_owes_pin_and_identical_laws_do_not'],cwd=package/'scripts')
    (OUT/'readme-target-violates-ac4.log').write_text(proposed.stdout+proposed.stderr)
    assert proposed.returncode==1 and 'FAIL' in proposed.stderr

with tempfile.TemporaryDirectory() as d:
    root=Path(d)
    refs={name:subprocess.check_output(['git','-C',str(WT),'rev-parse',tag+'^{commit}'],text=True).strip() for name,tag in [('old','kc-dev-flow-2-v0.26.0'),('new','kc-dev-flow-2-v0.38.1')]}
    for name,ref in refs.items():
        target=root/name
        target.mkdir()
        archive=subprocess.check_output(['git','-C',str(WT),'archive',ref,'kc-dev-flow-2'])
        with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
            stream.extractall(target,filter='data')
    old_readme=root/'old/kc-dev-flow-2/references/sd/workflow.md'
    text=old_readme.read_text()
    assert 'extensions: []' in text
    old_readme.write_text(text.replace('extensions: []','extensions: [roborev]',1))
    state=root/'state'
    state.mkdir()
    assert run(['git','-C',str(state),'init','-b','main']).returncode==0
    (state/'keep.txt').write_text('base\n')
    assert run(['git','-C',str(state),'add','keep.txt']).returncode==0
    assert run(['git','-C',str(state),'commit','-m','base']).returncode==0
    before=run(['git','-C',str(state),'rev-parse','HEAD']).stdout.strip()
    record=state/'t/dispatch/implementation-2.md'
    record.parent.mkdir(parents=True)
    record.write_text('Dispatched: 2026-10-27 '+'a'*40+'\nModel: sonnet\n\n## Checklist\n\nImplement the bounded outcome.\n\n## Scope notes\n\nPackage root: /pkg\nSend the completion message to `main`.\n')
    assert run(['git','-C',str(state),'add','t/dispatch/implementation-2.md']).returncode==0
    assert run(['git','-C',str(state),'commit','-m','old-release second dispatch']).returncode==0
    outputs={}
    for name in ['old','new']:
        runner=root/name/'kc-dev-flow-2/scripts/laws_check.py'
        result=run([sys.executable,'-B',str(runner),str(state),'--before',before,'--readme',str(old_readme)])
        (OUT/f'{name}-checker-old-readme.log').write_text(result.stdout+result.stderr)
        outputs[name]={'ref':refs[name],'exit':result.returncode,'output':result.stdout+result.stderr}
    assert outputs['old']['exit']==0,outputs
    assert outputs['new']['exit']==1 and 'roborev worker instruction is absent' in outputs['new']['output'],outputs
    (OUT/'version-skew.json').write_text(json.dumps(outputs,indent=2))

summary={'candidate':subprocess.check_output(['git','-C',str(WT),'rev-parse','HEAD'],text=True).strip(),'both_owed_exit':1,'both_owed_line':(OUT/'both-owed.log').read_text().strip(),'readme_target_breaks_AC4':True,'old_readme_older_checker_exit':0,'old_readme_newer_checker_exit':1,'exercised_difference':'implementation-2 extension instruction: old release checks implementation-1 only; newer release checks every fresh implementation record','product_changes':False}
(OUT/'probe-summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
