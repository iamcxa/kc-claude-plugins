#!/usr/bin/env python3
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

WT = Path(sys.argv[1]).resolve()
STATE = Path(sys.argv[2]).resolve()
OUT = Path(__file__).resolve().parent
BASE = 'd37c6dc653e0f45d6ca630c2faa6121c0863a57e'
SNAPSHOT = 'dc91fa798'
SD = '/Users/kent/.local/bin/spacedock'
SCRIPT = WT / 'kc-dev-flow-2/scripts/decision_ledger.py'
commands = []

def run(args, cwd=WT, data=None, expected=0):
    r = subprocess.run([str(a) for a in args], cwd=cwd, input=data, text=True,
                       capture_output=True, timeout=120)
    commands.append(dict(argv=[str(a) for a in args], cwd=str(cwd), exit=r.returncode,
                         stdout=r.stdout, stderr=r.stderr))
    (OUT / 'commands.json').write_text(json.dumps(commands, ensure_ascii=False, indent=2))
    if expected is not None:
        assert r.returncode == expected, (args, r.returncode, r.stdout, r.stderr)
    return r

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

reasons = json.loads((OUT / 'reasons.json').read_text())
valid_override = 'Override: recommended option A; Captain chose option B; area: model policy'
cli = []
reason_file = OUT / 'reason.txt'
for attempt, reason in reasons.items():
    for declaration, suffix, expected in [('as-recorded', '', 1), ('override', '\n'+valid_override, 0),
                                          ('followed', '\nRecommendation: followed', 0)]:
        reason_file.write_text(reason + suffix)
        r = run([sys.executable, '-B', SCRIPT, '--reason', reason_file], expected=expected)
        if declaration == 'override':
            assert r.stdout == 'reason: override (area: model policy)\n'
        if declaration == 'followed':
            assert r.stdout == 'reason: followed\n'
        cli.append(dict(attempt=attempt, form=declaration, exit=r.returncode, stdout=r.stdout))
for label, reason, expected in [('both', valid_override+'\nRecommendation: followed', 1),
                                ('placeholder', valid_override.replace('option A', '<option>'), 1),
                                ('empty', '', 2)]:
    reason_file.write_text(reason)
    r=run([sys.executable, '-B', SCRIPT, '--reason', reason_file], expected=expected)
    cli.append(dict(form=label, exit=r.returncode, stdout=r.stdout, stderr=r.stderr))
r=run([sys.executable, '-B', SCRIPT, '--reason', OUT/'missing-file'], expected=2)
cli.append(dict(form='unreadable', exit=r.returncode, stderr=r.stderr))
(OUT/'cli.json').write_text(json.dumps(cli, ensure_ascii=False, indent=2))

snapshot = OUT / 'state-snapshot'
snapshot.mkdir(exist_ok=True)
paths = run(['git','-C',STATE,'ls-tree','-r','--name-only',SNAPSHOT]).stdout.splitlines()
selected = [p for p in paths if (p.endswith('.md') and (len(Path(p).parts)==1 or
            (len(Path(p).parts)==2 and p.startswith('_archive/')))) or p.endswith('/index.json')]
for p in selected:
    target=snapshot/p
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(run(['git','-C',STATE,'show',SNAPSHOT+':'+p]).stdout)
base_script=OUT/'base-decision-ledger.py'
base_script.write_text(run(['git','show',BASE+':kc-dev-flow-2/scripts/decision_ledger.py']).stdout)
base_rows = [json.loads(s) for s in run([sys.executable,'-B',base_script,snapshot]).stdout.splitlines()]
new_rows = [json.loads(s) for s in run([sys.executable,'-B',SCRIPT,snapshot]).stdout.splitlines()]
strip_followed=lambda rows: [{k:v for k,v in r.items() if k!='followed'} for r in rows]
assert base_rows == strip_followed(new_rows)
assert all(r['followed'] is False for r in new_rows)
old_summary=json.loads(run([sys.executable,'-B',base_script,snapshot,'--summary']).stdout)
new_summary=json.loads(run([sys.executable,'-B',SCRIPT,snapshot,'--summary']).stdout)
assert old_summary == {k:{a:b for a,b in v.items() if a!='followed'} for k,v in new_summary.items()}
# Compatibility falsifier: renaming an existing key must be visible after stripping followed.
mutated=[{('renamed_task' if k=='task' else k):v for k,v in r.items()} for r in new_rows]
assert base_rows != strip_followed(mutated)
(OUT/'compatibility.json').write_text(json.dumps(dict(snapshot=SNAPSHOT, tasks=len(list(snapshot.glob('*.md')))+len(list((snapshot/'_archive').glob('*.md'))),
    rows=len(new_rows), captain_resolutions=sum(r['kind']=='resolution' and r['by']=='person:captain' for r in new_rows),
    rows_unchanged_except_followed=True, summaries_unchanged_except_followed=True,
    every_historical_followed_false=True, renamed_key_detected=True), indent=2))

# Real producer round-trip; all approvals below are synthetic disposable test data.
repo=OUT/'scratch'
repo.mkdir()
workflow=repo/'docs/dev2'
workflow.mkdir(parents=True)
definition=(WT/'kc-dev-flow-2/references/sd/workflow.md').read_text()
(workflow/'README.md').write_text(definition)
(repo/'.gitignore').write_text('**/.spacedock-state/\n')
git=['git','-c','user.name=Fixture','-c','user.email=fixture@example.invalid',
     '-c','commit.gpgsign=false','-c','core.hooksPath=/dev/null']
run([*git,'init','--initial-branch=main',repo])
run([*git,'-C',repo,'add','.'])
run([*git,'-C',repo,'commit','-m','test: synthetic workflow'])
scratch_state=workflow/'.spacedock-state'
run([*git,'-C',repo,'worktree','add','--detach',scratch_state])
run([*git,'-C',scratch_state,'checkout','--orphan','spacedock-state/dev2'])
run([*git,'-C',scratch_state,'rm','-rf','.'])
for slug in ('followed','override','typo'):
    (scratch_state/(slug+'.md')).write_text('---\ntitle: Synthetic fixture\nstatus: backlog\nvariant: kc-dev-flow-2\nprofile: pilot\n---\n\n## Scope\nSynthetic only, no real grant.\n')
run([*git,'-C',scratch_state,'add','.'])
run([*git,'-C',scratch_state,'commit','-m','test: synthetic tasks'])
roundtrip=[]
for slug,decl in [('followed','Recommendation: followed'),('override',valid_override),('typo','Recommendation followed')]:
    reason='SYNTHETIC TEST ONLY; no real human grant.\n'+decl
    reason_file.write_text(reason)
    run([sys.executable,'-B',SCRIPT,'--reason',reason_file],expected=1 if slug=='typo' else 0)
    entity=scratch_state/(slug+'.md')
    run([SD,'gate','prepare',slug,'--workflow-dir',workflow,'--question','Synthetic fixture only?',
         '--artifact',entity,'--summary','Synthetic test only; no real approval.'],cwd=repo)
    run([SD,'gate','record',slug,'--workflow-dir',workflow,'--decision','approve','--actor','person:captain',
         '--reason',reason],cwd=repo)
rows=[json.loads(s) for s in run([sys.executable,'-B',SCRIPT,scratch_state]).stdout.splitlines()]
by_task={r['task']:r for r in rows}
assert by_task['followed']['followed'] is True
assert by_task['override']['override']=={'rec':'option A','chose':'option B','area':'model policy'}
assert by_task['typo']['followed'] is False
assert all(by_task[s]['reason'].endswith(d) for s,d in [('followed','Recommendation: followed'),('override',valid_override),('typo','Recommendation followed')])
(OUT/'roundtrip.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))

# Reverse mutations execute isolated copies with bytecode disabled and caches absent.
mutations=[]
source=SCRIPT.read_text()
mutators={
    'missing-declaration': ('problem = "missing declaration"','return 0'),
    'require-override': ('elif followed:\n        print("reason: followed")\n        return 0', 'elif followed:\n        return 1'),
    'both-forms': ('if over and followed:', 'if False:'),
}
for name,(old,new) in mutators.items():
    assert source.count(old)==1
    folder=OUT/'mutations'/name
    folder.mkdir(parents=True)
    (folder/'decision_ledger.py').write_text(source.replace(old,new))
    shutil.copyfile(WT/'kc-dev-flow-2/scripts/test_decision_ledger.py',folder/'test_decision_ledger.py')
    r=run([sys.executable,'-B',folder/'test_decision_ledger.py'],expected=1)
    (folder/'test.log').write_text(r.stdout+r.stderr)
    mutations.append(dict(name=name,status='passed',message='Reverse mutation makes the regression suite fail.',exit=r.returncode))
# The actual lint CLI on a complete disposable checkout, without the new budget step.
lint_copy=OUT/'lint-mutation'
shutil.copytree(WT/'kc-dev-flow-2',lint_copy/'kc-dev-flow-2',ignore=shutil.ignore_patterns('__pycache__'))
(lint_copy/'scripts').mkdir()
shutil.copyfile(WT/'scripts/skill-frontmatter-lint.sh',lint_copy/'scripts/skill-frontmatter-lint.sh')
lint_file=lint_copy/'kc-dev-flow-2/scripts/lint-skills.py'
text=lint_file.read_text()
start=text.index('    dict(delta=48,')
end=text.index('\n]',start)
lint_file.write_text(text[:start]+text[end:])
r=run([sys.executable,'-B',lint_file],cwd=lint_copy,expected=1)
assert '5939 words exceeds the budget of 5891' in r.stdout
(OUT/'lint-mutation.log').write_text(r.stdout+r.stderr)
mutations.append(dict(name='remove-budget-step',status='passed',message='Lint exits 1: 5939 words exceed 5891.',exit=r.returncode))
(OUT/'mutations.json').write_text(json.dumps(mutations,indent=2))

base_workflow=run(['git','show',BASE+':kc-dev-flow-2/references/sd/workflow.md']).stdout
pass_output='reason: followed'
override_output='reason: override (area: model policy)'
reason_file.write_text('No declaration')
hold_output=run([sys.executable,'-B',SCRIPT,'--reason',reason_file],expected=1).stdout
counts=dict(startup_and_resume=dict(before=len(base_workflow.split()),after=len(definition.split())),
            pre_record=dict(before=0,followed_words=len(pass_output.split()),override_words=len(override_output.split()),hold_words=len(hold_output.split())),
            other_moments='Gate preparation, idle, merge ask and archive source bytes unchanged; no new output there.')
assert counts['startup_and_resume']==dict(before=5891,after=5939)
(OUT/'word-counts.json').write_text(json.dumps(counts,indent=2))
print('PASS: CLI cases, historical JSON compatibility, Spacedock 0.27.2 recording, reverse mutations and word recount.')
