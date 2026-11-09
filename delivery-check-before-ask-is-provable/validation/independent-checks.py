import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import types

root, base, evidence, package = map(Path, sys.argv[1:5])
evidence.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(root / 'kc-dev-flow-2/scripts'))
spec = importlib.util.spec_from_file_location('fixtures', root / 'kc-dev-flow-2/scripts/test_delivery_gate.py')
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)
results = []

def run(name, args, cwd=root, expect=0):
    env = {k: v for k, v in os.environ.items() if k not in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE')}
    p = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True)
    (evidence / (name + '.log')).write_text(p.stdout + p.stderr)
    results.append(dict(name=name, command=list(map(str,args)), exit=p.returncode, expected=expect))
    assert p.returncode == expect, (name, p.stdout, p.stderr)
    return p

def load_module(path):
    m = types.ModuleType('gate_copy')
    m.__file__ = str(path)
    exec(compile(path.read_text(), str(path), 'exec'), m.__dict__)
    return m

counts = []
fixture = t.DeliveryCheckBeforeQuestionTests()
fixture.setUp()
fixture.save()
try:
    for label, directory in [('base', base), ('candidate', root)]:
        workflow = (directory / 'kc-dev-flow-2/references/sd/workflow.md').read_text()
        paragraphs = workflow.split('\n\n')
        selected = [p for p in paragraphs if 'FO runs `python3 <package>/scripts/delivery_gate.py ' in p and (' check <task>' in p or ' question <task>' in p)]
        assert len(selected) == 2
        script = directory / 'kc-dev-flow-2/scripts/delivery_gate.py'
        q = run(label + '-question', ['python3', '-B', str(script), 'question', str(fixture.task), '--text-file', str(fixture.message), '--summary-file', str(fixture.summary)])
        m = load_module(script)
        c = t.run_variant(m)
        assert c.code == 0, c.out
        (evidence / (label + '-check.log')).write_text(c.out)
        counts.append(dict(name=label, readme=len(' '.join(selected).split()), question=len(q.stdout.split()), check=len(c.out.split())))
    assert counts[0] == dict(name='base',readme=80,question=92,check=counts[1]['check']), counts
    assert counts[1]['readme'] == 80 and counts[1]['question'] == 107, counts
    assert (root/'kc-dev-flow-2/scripts/lint-skills.py').read_bytes() == (base/'kc-dev-flow-2/scripts/lint-skills.py').read_bytes()

    mutant = load_module(root / 'kc-dev-flow-2/scripts/delivery_gate.py')
    mutant.ASK_FORM += ' EXTRA'
    capture = io.StringIO()
    with contextlib.redirect_stdout(capture):
        code = mutant.main(['question',str(fixture.task),'--text-file',str(fixture.message),'--summary-file',str(fixture.summary)])
    assert code == 0 and len(capture.getvalue().split()) == 108
    (evidence/'question-word-mutant.log').write_text(capture.getvalue())
    results.append(dict(name='AC-7 extra output word rejected',observed=108,expected=107,mutant_rejected=True))
finally:
    fixture.doCleanups()

workflow_path = root / 'kc-dev-flow-2/references/sd/workflow.md'
original = workflow_path.read_bytes()
try:
    workflow_path.write_bytes(original + b'\nAn extra unbudgeted instruction.\n')
    run('AC-5-unbudgeted-word-mutant', ['python3','-B','kc-dev-flow-2/scripts/lint-skills.py'], expect=1)
finally:
    workflow_path.write_bytes(original)

adr_source = root / 'docs/adr'
adr_copy = evidence / 'adr-copy'
shutil.copytree(adr_source, adr_copy)
adr = next(adr_copy.glob('0071-*.md'))
adr.unlink()
run('AC-8-missing-required-adr-mutant', ['python3', str(package/'scripts/adr_lint.py'), str(adr_copy),'--require','0071'], expect=1)
assert hashlib.sha256(original).digest() == hashlib.sha256(workflow_path.read_bytes()).digest()
(evidence/'independent-words.json').write_text(json.dumps(counts,indent=2))
(evidence/'falsifiers.json').write_text(json.dumps(results,indent=2))
print('PASS: independent recount README 80/80, question 92/107, check unchanged; extra README/output words and missing ADR 0071 rejected.')
