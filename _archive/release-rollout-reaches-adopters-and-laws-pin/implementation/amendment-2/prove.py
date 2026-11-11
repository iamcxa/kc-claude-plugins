from pathlib import Path
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

WT=Path(sys.argv[1]).resolve()
OUT=Path(__file__).resolve().parent
PRIOR='a1a35a714510683a44a2ac5ec02241e7cb354f80'
SOURCE=(WT/'kc-dev-flow-2/scripts/package_version.py').read_text()
TESTS=(WT/'kc-dev-flow-2/scripts/test_package_version.py').read_text()

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def package(root,text):
    p=root/'kc-dev-flow-2'
    (p/'scripts').mkdir(parents=True)
    (p/'.claude-plugin').mkdir()
    (p/'references/sd').mkdir(parents=True)
    (p/'scripts/package_version.py').write_text(text)
    (p/'scripts/test_package_version.py').write_text(TESTS)
    for name in ['.claude-plugin/plugin.json','references/sd/workflow.md']:
        shutil.copyfile(WT/'kc-dev-flow-2'/name,p/name)
    return p

prior=subprocess.check_output(['git','-C',str(WT),'show',PRIOR+':kc-dev-flow-2/scripts/package_version.py'],text=True)
results=[]
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)
    modules={name:load(package(root/name,source)/'scripts/test_package_version.py',name+'_tests') for name,source in [('prior',prior),('candidate',SOURCE)]}
    cases=[('sync-only',True,False,'old'),('pin-only',False,True,'old'),('unknown-pin-only',False,False,'unknown'),('no-debt',False,False,'old'),('sync-uninstalled',True,False,None)]
    for name,sync,pin,installed in cases:
        pair=[]
        for label,module in modules.items():
            case=module.RolloutTest();case.setUp()
            try:
                case.row('one',pin=case.old if installed=='old' else '3'*40 if installed=='unknown' else None)
                if sync:
                    case.content(case.repo,case.workflow,case.latest,case.readme('0.38.1')+'Changed rule.\n')
                if pin:
                    case.content(case.repo,case.laws[0],case.latest,'changed laws\n')
                run=case.run_rollout()
                target=OUT/f'{name}-{label}.txt';target.write_bytes(run.stdout.encode())
                assert not run.stderr,run.stderr
                pair.append((target,run.returncode))
            finally:
                case.doCleanups()
        subprocess.run(['cmp',str(pair[0][0]),str(pair[1][0])],check=True)
        assert pair[0][1]==pair[1][1]
        results.append({'name':name+' bytes/exit unchanged','status':'passed','message':f'cmp exit 0; both command exits {pair[0][1]}'})
    needle='order = "; sync README, merge, then move pin" if owed and pin_owed else ""'
    assert needle in SOURCE
    mutant=package(root/'mutant',SOURCE.replace(needle,'order = ""',1))
    run=subprocess.run([sys.executable,'-B','-m','unittest','test_package_version.RolloutTest.test_both_debts_print_readme_sync_then_merge_then_pin_move'],cwd=mutant/'scripts',capture_output=True,text=True)
    (OUT/'missing-order-mutation.log').write_text(run.stdout+run.stderr)
    assert run.returncode==1 and 'AssertionError' in run.stderr
    results.append({'name':'AC-12 missing-order mutation','status':'passed','message':'same pin debt without order rejected, exit 1'})
    current=modules['candidate'].RolloutTest();current.setUp()
    try:
        current.row('both',pin=current.old)
        current.content(current.repo,current.workflow,current.latest,current.readme('0.38.1')+'Changed rule.\n')
        current.content(current.repo,current.laws[0],current.latest,'changed laws\n')
        run=current.run_rollout()
        assert run.returncode==1
        assert run.stdout.endswith('; sync README, merge, then move pin\n')
        words=len(run.stdout.split())
        assert words==16,words
        (OUT/'both-owed.txt').write_text(run.stdout)
        results.append({'name':'both-owed row','status':'passed','message':f'order follows pin debt on the same line; exit 1; {words} words'})
    finally:
        current.doCleanups()

(OUT/'proof-results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
