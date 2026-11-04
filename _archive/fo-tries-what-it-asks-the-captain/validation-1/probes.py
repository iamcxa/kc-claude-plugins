import datetime, json, os, subprocess, sys
from pathlib import Path

root=Path(os.environ['CAPTAIN_STEPS_WORKTREE'])
out=Path(__file__).parent
sys.path.insert(0,str(root/'kc-dev-flow-2/scripts'))
import test_delivery_gate as fixture
gate=root/'kc-dev-flow-2/scripts/delivery_gate.py'
head='4f08f008f9b117876ffe4b569210278e240d203d'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
probes=out/'probes'
probes.mkdir(exist_ok=True)
results=[]
def step(asked, observed='note read', number=1, only=None):
    return (f'### Step {number}\nAsked: {asked}\nRan: fresh shell, {stamp}\nObserved: {observed}\n'+
            (f'Only he can: {only}\n' if only else ''))
def run(name, body, message, expected):
    record=probes/(name+'-record.md')
    record.write_text(f'Candidate: {head}\n\n'+body)
    msg=probes/(name+'-message.md')
    msg.write_text(message)
    command=['python3','-B',str(gate),'steps',str(record),'--text-file',str(msg)]
    done=subprocess.run(command,cwd=root,text=True,capture_output=True)
    (probes/(name+'.log')).write_text(done.stdout+done.stderr)
    results.append({'name':name,'command':command,'exit':done.returncode,'output':done.stdout,'expected_current_exit':expected})
    assert done.returncode==expected,(name,done.stdout,done.stderr)
    return record,msg,done

# Run real, harmless shell commands, then hand the output to the real CLI.
body='';message=''
for i in range(1,4):
    command=f"python3 -c 'print({i} + 1)'"
    done=subprocess.run(['/bin/bash','--noprofile','--norc','-c',command],text=True,capture_output=True,check=True)
    observed=done.stdout.strip()
    body+=step(command,observed,i,'enter his password at the sign-in page — his account' if i==3 else None)
    message+=f'```sh\n{command}\n```\n```text\n{observed}\n```\n'
_,_,done=run('three-real-commands',body,message,0)
assert done.stdout=='captain steps complete: 3 steps, 1 left to him\n'
card=probes/'positive-card.md';card.write_text(message)
run('three-real-commands-card',body,f'Run the card at {card}:13',0)

note=step('Read this note.')
shapes={
 'prose': 'Sign in on the preview using your own account.\n',
 'inline': 'Then run `printf inline`.\n',
 'quote-fence': '> ```sh\n> printf unrecorded\n> ```\n',
 'list-fence': '- ```sh\n  printf unrecorded\n  ```\n',
 'indented-code': '    printf unrecorded\n',
 'normal-fence': '```sh\nprintf unrecorded\n```\n',
 'longer-closer': '```sh\nprintf unrecorded\n````\n',
 'unclosed': '```sh\nprintf unrecorded\n',
 'diagram': '```mermaid\ngraph LR; A-->B\n```\n',
 'output-file-fence': '```text\noutput text\n```\n',
}
for name,shape in shapes.items():
    expected=0 if name in ('prose','inline','quote-fence','list-fence','indented-code') else 1
    run(name,note,'Read this note.\n'+shape,expected)

# Reproduce the review's normal-workflow false hold from genuinely captured output.
observed=subprocess.check_output(['/bin/bash','--noprofile','--norc','-c',"printf 'GET /health 200\\n'"],text=True).strip()
(probes/'route-output.txt').write_text(observed+'\n')
request='Run the route smoke test.'
record,msg,done=run('observed-route',step(request,observed),request+'\n```text\n'+observed+'\n```\n',1)
assert 'message S4: missing path /health' in done.stdout
run('observed-route-control',step(request,observed),request+'\nOutput captured.\n',0)
card=probes/'route-card.md';card.write_text(msg.read_text())
run('observed-route-card',step(request,observed),f'Run the card at {card}',0)

# The same false hold reaches validation question, including through its latest report.
fixture.readme(probes)
task=probes/'task.md';task.write_text(fixture.TASK)
fixture.captain_record(task,head)
summary=probes/'summary.txt';summary.write_text(f'External rounds: 0\nCaptain steps: {record}\n')
question=probes/'question.txt'
for location in ('question','report','control'):
    question.write_text(fixture.CLAUSES+'\n'+(msg.read_text() if location=='question' else request+'\n'))
    task.write_text(fixture.TASK+ ('\n## Stage Report: validation\n\n'+msg.read_text() if location=='report' else ''))
    command=['python3','-B',str(gate),'question',str(task),'--text-file',str(question),'--summary-file',str(summary)]
    done=subprocess.run(command,cwd=probes,text=True,capture_output=True)
    (probes/('gate-'+location+'.log')).write_text(done.stdout+done.stderr)
    results.append({'name':'gate-'+location,'command':command,'exit':done.returncode,'output':done.stdout})
    assert done.returncode==(0 if location=='control' else 1),done.stdout
    if location!='control':
        assert 'missing path /health' in done.stdout and len(done.stdout.splitlines())==2,done.stdout
(out/'probes.json').write_text(json.dumps(results,indent=2)+'\n')
print(f'{len(results)} probes confirmed; Codex output-path false hold reproduced in steps and both question sources')
