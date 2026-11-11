#!/usr/bin/env python3
"""Independent acceptance controls for the two-line Story fixture repair."""
import ast, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path

scratch, evidence = map(Path, sys.argv[1:3])
candidate, base = scratch/'candidate', scratch/'base'
rel = Path('kc-dev-flow-2/scripts/test_design_surfaces.py')
added = ('                    + "\\n## PRFAQ\\n### Worth questions\\n"\n'
         '                    "Asked: check Story agreement; without: mismatches pass; premise: records can disagree, compare the fixture.\\n"\n')
records=[]
def run(name, command, mode='absent', expected=0, native=False, cwd=candidate):
    env=dict(os.environ, PATH=('/usr/bin:/bin' if mode=='absent' else str(scratch/'sd-bin')+':/usr/bin:/bin'), TMPDIR=str(scratch/'temp'), PYTHONDONTWRITEBYTECODE='1')
    env.pop('SPACEDOCK_BIN',None)
    if native: env['SPACEDOCK_BIN']=str(scratch/'sd-bin/spacedock')
    r=subprocess.run(list(map(str,command)),cwd=cwd,env=env,capture_output=True,text=True,timeout=300)
    log=name+'.log'; (evidence/log).write_text(r.stdout+r.stderr)
    records.append(dict(name=name,command=list(map(str,command)),path=env['PATH'],explicit_binary=env.get('SPACEDOCK_BIN'),exit=r.returncode,expected=expected,status='passed' if r.returncode==expected else 'failed',log=log))
    (evidence/'probes.json').write_text(json.dumps(records,indent=2)+'\n')
    assert r.returncode==expected,(name,r.returncode,r.stdout,r.stderr)
    print(name+': expected exit '+str(expected),flush=True)
    return r

original=(base/rel).read_text(); patched=(candidate/rel).read_text()
assert patched.count(added)==1 and patched.replace(added,'')==original
assert ast.dump(ast.parse(patched.replace(added,'')))==ast.dump(ast.parse(original))
changed=[]
for path in sorted(base.rglob('*')):
    if path.is_file() and path.read_bytes()!=(candidate/path.relative_to(base)).read_bytes():changed.append(str(path.relative_to(base)))
assert changed==[str(rel)],changed
def allowed(paths, content):
    return paths==[str(rel)] and content.count(added)==1 and content.replace(added,'')==original
assert allowed(changed,patched)
assert not allowed(changed+['kc-dev-flow-2/scripts/design_surfaces.py'],patched)
assert not allowed(changed,patched.replace('self.assertEqual(self.check(', 'self.assertNotEqual(self.check(',1))
(evidence/'scope.json').write_text(json.dumps({'changed':changed,'exact_added_fixture_only':True,'normalized_ast_equal':True,'second_file_falsifier_rejected':True,'changed_assertion_falsifier_rejected':True,'checker_sha256':hashlib.sha256((candidate/'kc-dev-flow-2/scripts/design_surfaces.py').read_bytes()).hexdigest()},indent=2)+'\n')

mutant=scratch/'mutant';shutil.copytree(candidate/'kc-dev-flow-2',mutant/'kc-dev-flow-2')
(mutant/rel).write_text(original)
for mode in ('absent','present'):
    resolve=run('resolver-'+mode,['/bin/bash','--noprofile','--norc','-c','command -v spacedock'],mode,0 if mode=='present' else 1)
    for label,tree in [('candidate',candidate),('merged',scratch/'merged')]:
        run(label+'-story-'+mode,[sys.executable,'-B',tree/rel,'JourneyStoryTests'],mode)
        if mode=='present':run(label+'-full-'+mode,[sys.executable,'-B',tree/rel],mode)
    run('base-original-'+mode,[sys.executable,'-B',base/rel,'JourneyStoryTests.test_design_compares_story_record_to_counted_field_only_in_map_workflows'],mode,1)
    run('removed-fixture-'+mode,[sys.executable,'-B',mutant/rel,'JourneyStoryTests.test_design_compares_story_record_to_counted_field_only_in_map_workflows'],mode,1)

native_test=candidate/'kc-dev-flow-2/scripts/test_dispatch_stage.py'
names=['DispatchStageTests.test_worth_requirement_uses_native_stage_for_yaml_status_values','DispatchStageTests.test_unreadable_native_stage_does_not_make_design_presentable']
run('native-worth-controls',[sys.executable,'-B',native_test,*names],'present',native=True)

workflow=scratch/'direct';state=workflow/'.spacedock-state';state.mkdir(parents=True)
(workflow/'README.md').write_bytes((candidate/'kc-dev-flow-2/references/sd/workflow.md').read_bytes())
(state/'README.md').write_text('State checkout, not the workflow.\n')
task=state/'task.md'
text='---\ntitle: Task\nstatus: ideation\n---\n## Scope\nShip the bounded checker.\nNon-goals: migrations\nBudget: one cycle per stage\nStop condition: new upstream hook needed\n## FO alignment\nSurfaces: none\nVisible change: none\n## PRFAQ\nA bounded CLI result.\n## Acceptance criteria\n**AC-1**: a bounded result. Evidence: the real check.\n'
checker=candidate/'kc-dev-flow-2/scripts/design_surfaces.py'
word_counts={}
for mode in ('absent','present'):
    for visible in (False,True):
        data=text.replace('## PRFAQ\n','## PRFAQ\n### Worth questions\nAsked, without, premise.\n') if visible else text
        task.write_text(data);before=task.read_bytes()
        name='direct-'+mode+('-visible' if visible else '-missing')
        r=run(name,[sys.executable,'-B',checker,'check',task],mode,0 if visible else 1)
        assert task.read_bytes()==before
        word_counts[name]=len(r.stdout.split())
        if not visible:
            assert 'design surfaces presentable' not in r.stdout
            assert ('cannot read stage for Worth questions' if mode=='absent' else "design needs '### Worth questions'") in r.stdout
task.write_text(text)
bad=mutant/'kc-dev-flow-2/scripts/design_surfaces.py'
source=bad.read_text();needle='                errors.append(f"{path.name}: cannot read stage for Worth questions: {exc}")'
assert source.count(needle)==1;bad.write_text(source.replace(needle,'                pass'))
r=run('swallowed-exception-direct',[sys.executable,'-B',bad,'check',task],expected=0)
assert 'design surfaces presentable' in r.stdout
run('swallowed-exception-existing-test',[sys.executable,'-B',mutant/'kc-dev-flow-2/scripts/test_dispatch_stage.py',names[1]],'present',1,native=True)
(evidence/'direct-counts.json').write_text(json.dumps(word_counts,indent=2)+'\n')
print('PROBES PASS: reverse controls expose the original failure and swallowed-refusal defect',flush=True)
