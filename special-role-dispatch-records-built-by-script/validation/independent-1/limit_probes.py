import json, os, sys
from pathlib import Path
os.environ['SPACEDOCK_BIN'] = '/Users/kent/.local/bin/spacedock'
os.environ['DISPATCH_STAGE_LOG'] = '/tmp/pr827-validation/evidence/limit-calls.jsonl'
sys.path.insert(0, '/tmp/pr827-validation/candidate/kc-dev-flow-2/scripts')
from test_dispatch_stage import DispatchStageTests, ROOT

rows=[]
for prod in [False, True]:
    t=DispatchStageTests()
    try:
        t.setUp()
        t.owe_reviewer()
        if prod:
            t.entity.write_text(t.entity.read_text().replace('profile: pilot', 'profile: prod'))
            t.commit_task()
            prompt=t.role()
            assert prompt.returncode == 0
        t.entity.write_text(t.entity.read_text().replace('## FO alignment\n', '## FO alignment\n\nReviewer: kc-dev-flow-2:engineering-reviewer opus 2026-11-10 — reviewed amendments\n'))
        t.commit_task()
        result=t.call([sys.executable, '-B', ROOT/'scripts/role_triggers.py', t.state, t.slug], expected=1 if prod else 0)
        rows.append(dict(name='Higher prod floor remains owed' if prod else 'Manual call without a record clears', role_trigger_exit=result.returncode, stdout=result.stdout, dispatch_record_exists=t.record('engineering-reviewer').exists()))
    finally:
        t.doCleanups()
Path('/tmp/pr827-validation/evidence/limits.json').write_text(json.dumps(rows, indent=2)+'\n')
print(json.dumps(rows, indent=2))
