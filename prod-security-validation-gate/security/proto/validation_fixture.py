import sys,subprocess,tempfile,shutil
from pathlib import Path
SC='/tmp/psvg-tools/proto2/kc-dev-flow-2/scripts'
R='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/prod-security-validation-gate/security/reports/'
HEAD='1c5b1870'+'a'*32
def run(profile='prod',review=None,report='psvg-b-sonnet-relay-1.yaml',lines=None,cand=HEAD,report_text=None,pr_head=None):
    with tempfile.TemporaryDirectory() as d:
        d=Path(d); t=d/'task.md'; (d/'task'/'dispatch').mkdir(parents=True); (d/'task'/'security').mkdir()
        (d/'task'/'dispatch'/'validation-1.md').write_text(f'# v1\n\nCandidate: {cand}\n\n## Checklist\n')
        body=report_text if report_text is not None else (Path(R+report).read_text() if report else None)
        if body is not None: (d/'task'/'security'/'validation-1.yaml').write_text(body)
        rv=review if review is not None else f'Security review (validation): security/validation-1.yaml at {HEAD}\n'
        ln=lines if lines is not None else ''
        t.write_text(f'---\ntitle: x\nprofile: {profile}\nstatus: validation\n---\n\n## Stage Report: validation\n\n{rv}{ln}')
        (d/'q.txt').write_text('Merge ask.')
        p=subprocess.run(['python3','-B',SC+'/delivery_gate.py','check',str(t),'--pr','o/r#1','--text-file',str(d/'q.txt'),'--head',pr_head or HEAD[:12]],capture_output=True,text=True,cwd=SC)
        return p.returncode,(p.stdout+p.stderr).strip().replace(str(d),'<tmp>')
# real report: sonnet relay 1 = HIGH, MEDIUM, LOW
GOOD="Security finding (validation 1) 1: Needs decision: add a cap on sessions per room now, or file a task\nSecurity finding (validation 1) 2: Needs decision: add the untrusted-document sentence to llms.txt\nSecurity finding (validation 1) 3: declined: declared identity is stated unverified in llms.txt\n"
cases=[
 ('pass: three findings, each disposed',dict(lines=GOOD)),
 ('pass on Opus report that carries markdown fences',dict(report='psvg-b-opus-relay-1.yaml',lines="Security finding (validation 1) 1: Needs decision: cap\nSecurity finding (validation 1) 2: declined: owner-side consumer is outside this repo\n")),
 ('zero-finding report passes',dict(report='psvg-b-sonnet-control.yaml',lines='')),
 ('no review line',dict(review='',lines=GOOD)),
 ('not run: reviewer returned no report',dict(review='Security review (validation): not run: reviewer returned no report (sonnet)\n',report=None)),
 ('review ran on another head',dict(review='Security review (validation): security/validation-1.yaml at '+'b'*40+'\n',lines=GOOD)),
 ('review line with short head',dict(review='Security review (validation): security/validation-1.yaml at 1c5b1870\n',lines=GOOD)),
 ('refusal text saved as report',dict(report=None,report_text="I can't help with this request.",lines=GOOD)),
 ('finding 3 has no line',dict(lines=GOOD.rsplit('\n',2)[0]+'\n')),
 ('HIGH declined',dict(lines=GOOD.replace('1: Needs decision: add a cap on sessions per room now, or file a task','1: declined: accepted'))),
 ('Material open',dict(lines=GOOD.replace('1: Needs decision: add a cap on sessions per room now, or file a task','1: Material: cap sessions per room'))),
 ('extra finding line',dict(lines=GOOD+'Security finding (validation 1) 4: declined: x\n')),
 ('pilot task skipped',dict(profile='pilot',review='',lines='')),
 ('report path escapes folder',dict(review=f'Security review (validation): ../x.yaml at {HEAD}\n',lines=GOOD)),
]
for k,kw in cases:
    rc,out=run(**kw); print(f'[{rc}] {k}'); [print('     ',l[:230]) for l in out.splitlines()]
