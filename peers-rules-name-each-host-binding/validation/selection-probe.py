from pathlib import Path
import importlib.util, subprocess, tempfile, shutil, json
W=Path('/tmp/peers-validation-730'); P=W/'kc-dev-flow-2'
spec=importlib.util.spec_from_file_location('lint',P/'scripts/lint-skills.py')
lint=importlib.util.module_from_spec(spec);spec.loader.exec_module(lint)
original=lint.extension_dependency_errors
calls=[]
def traced(root,listed):
    calls.append(list(listed))
    return original(root,listed)
lint.extension_dependency_errors=traced
with tempfile.TemporaryDirectory() as d:
    root=Path(d); pkg=root/'kc-dev-flow-2'
    shutil.copytree(P,pkg,ignore=shutil.ignore_patterns('__pycache__'))
    adopter=root/'docs/dev2/README.md';adopter.parent.mkdir(parents=True)
    for selected in ('learn, peers','learn, peers, paseo','learn, paseo'):
        adopter.write_text('---\nextensions: ['+selected+']\n---\n')
        errors=lint.extension_tier_errors(pkg)
        assert errors==[],errors
        print('adopter ['+selected+']: template lint PASS; dependency input='+repr(calls[-1]))
    workflow=pkg/lint.WORKFLOW
    before=workflow.read_text()
    workflow.write_text(before.replace('extensions: [learn, peers]','extensions: [learn, paseo]'))
    errors=lint.extension_tier_errors(pkg)
    print('invalid package template:',json.dumps(errors))
    assert any('requires `peers`' in x for x in errors)
    lint.extension_dependency_errors=lambda root,listed: []
    errors_without=lint.extension_tier_errors(pkg)
    assert errors_without
    print('same invalid package without dependency check: still REFUSED:',json.dumps(errors_without))
    for name,selected in [('default','learn, peers'),('custom','learn, peers, roborev'),('opt-in','learn, peers, paseo')]:
        ours=root/'ours';base=root/'base';theirs=root/'theirs'
        expected='---\nextensions: ['+selected+']\n---\n'
        ours.write_text(expected);base.write_text('---\nextensions: [learn, peers]\n---\n')
        theirs.write_text('---\nextensions: [learn, peers]\n---\n')
        run=subprocess.run(['git','merge-file','-p',str(ours),str(base),str(theirs)],capture_output=True,text=True)
        assert run.returncode==0 and run.stdout==expected
        print(name+': original extension list retained byte-for-byte')
print('Consumer verdict: package template lint calls helper; adopted README has no caller; paseo-specific rejection exercised only by invalid-template/test inputs.')
