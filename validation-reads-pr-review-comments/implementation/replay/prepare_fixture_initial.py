import json, subprocess, hashlib, shutil, re
from pathlib import Path

WT = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-validation-reads-pr-review-comments')
STATE = WT.parents[1] / 'docs/dev2/.spacedock-state'
R = STATE / 'validation-reads-pr-review-comments/implementation/replay'
HIST = STATE / '_archive/dispatch-build-writes-the-dispatch-record'
CUT = '2026-11-08T11:13:00Z'
HEAD = '778367adde2e20e0b3e51966ddba2d9f77f9e614'
STATE_REF = '82f2e963989b61f15c080f48187b0107e7e36460'

def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2)+'\n' if not isinstance(data,str) else data)

def git(*args):
    return subprocess.check_output(['git','-C',str(STATE),*args], text=True)

notes=[]
def note(source, record, change, at):
    notes.append(dict(source=source,record=record,change=change,timestamp=at))

F=R/'fixture'; F.mkdir(exist_ok=True)
pr=json.loads((R/'source/pr-view.json').read_text())
historical=json.loads((HIST/'validation-3/hosted-refresh/pr.json').read_text())
for k,v in historical.items():
    note('_archive/dispatch-build-writes-the-dispatch-record/validation-3/hosted-refresh/pr.json', k, 'replace live PR field with captured historical value', CUT)
    pr[k]=v
body_path='dispatch-build-writes-the-dispatch-record/implementation/repair-2/prepared-pr.md'
body=git('show',f'{STATE_REF}:{body_path}')
pr['body']=body.split('\n',1)[1].lstrip()
note(f'{STATE_REF}:{body_path}','PR body','replace post-repair live body with committed pre-cutoff prepared body; prepared text, not a historical GitHub body capture',git('show','-s','--format=%cI',STATE_REF).strip())
for key in ('mergedAt','updatedAt'):
    if pr.get(key) and pr[key]>CUT:
        note('source/pr-view.json',key,'remove post-cutoff mutable metadata',pr[key]);pr.pop(key)
for key,time in [('reviews','submittedAt'),('comments','createdAt'),('commits','committedDate')]:
    kept=[]
    for v in pr[key]:
        t=v.get(time,'')
        # The edited bot summary has a GraphQL id in pr view.
        bot=v.get('id')=='IC_kwDORid8-c8AAAABkH4y2g'
        if t>CUT or bot:
            note('source/pr-view.json',v.get('id',v.get('oid')),f'remove {key} created or updated after cutoff', '2026-11-08T11:57:59Z' if bot else t)
        else: kept.append(v)
    pr[key]=kept
write(F/'pr-view.json',pr)
for name,time in [('review-comments.json','created_at'),('reviews.json','submitted_at'),('issue-comments.json','created_at')]:
    vals=json.loads((R/'source'/name).read_text()); kept=[]
    for v in vals:
        t=v.get(time,'');updated=v.get('updated_at','')
        if t>CUT or updated>CUT:
            note('source/'+name,v.get('id'),'remove created/updated after cutoff',max(t,updated));continue
        if name=='review-comments.json' and v.get('commit_id')!=HEAD:
            note('source/'+name,v['id'],f'rewrite moving diff commit_id from {v["commit_id"]} to frozen head; original_commit_id retained',v['created_at'])
            v['commit_id']=HEAD
        kept.append(v)
    write(F/name,kept)
run=json.loads((HIST/'validation-3/hosted-refresh/run-attempt-3.json').read_text())
write(F/'run-rest.json',run)
pipeline=json.loads((HIST/'validation-3/hosted-refresh/run-pipeline.json').read_text())
write(F/'run.json',pipeline)
note('_archive/dispatch-build-writes-the-dispatch-record/validation-3/hosted-refresh/run-attempt-3.json',42468880068,'substitute historical REST attempt 3 metadata',run['updated_at'])
note('_archive/dispatch-build-writes-the-dispatch-record/validation-3/hosted-refresh/run-pipeline.json',42468880068,'substitute historical gh run view job/step response',pipeline.get('updatedAt',CUT))
write(F/'rewrites.json',notes)
write(F/'README.md','# Frozen PR #812 replay fixture\n\nAuthorized by dispatch/implementation-1-message-1.md. Cutoff: '+CUT+'.\nEvery substitution and removal with source, record id and timestamp is in rewrites.json.\nLive sources are preserved under ../source; they are not served. PR fields, checks and run attempt 3 use the contemporaneous hosted-refresh captures. The PR body uses the committed prepared body, not a historical GitHub response. Review comment moving commit_id values are frozen to the historical head; original_commit_id is retained. The target comment exists at run start, unlike the original two-minute delay. All other records created or updated after cutoff are excluded. Shim calls not registered are refused, logged and invalidate a run.\n')
original=(HIST/'dispatch/validation-3.md').read_text().split('## Checklist\n\n')[1].split('\n## Scope notes')[0].strip().split('\n')
original=[x for x in original if x.strip()]
assert len(original)==3
follow=(HIST/'dispatch/validation-3-message-2.md').read_text().split('## Checklist\n\n')[1].split('\n## Scope notes')[0]
facts=re.search(r'^1\. (.*)$',follow,re.M)[1]
old=original[1].split(' Hosted CI on this head failed only')[0]
original[1]=old+' '+facts+' Report AC-8 from run 42468880068 attempt 3. Keep any download under a new /tmp directory, never in the task state folder.'
write(R/'checklist.txt','\n'.join(original)+'\n')
write(R/'scope.txt','Profile: pilot. Candidate: iamcxa/kc-claude-plugins PR #812, head '+HEAD+', base 334d91e3165953b2ca7191e3308d80b6c02c4a99. Preserve candidate product bytes; do not open, edit or send anything to GitHub. roborev not run: FO owns local review and publication. The gh command uses an isolated recorded-response transport. Report unavailable commands truthfully.\n')
shutil.copy(WT.parents[1]/'docs/dev2/README.md',R/'adopter-readme.md')
write(R/'grader-inputs/validation-3.md',(HIST/'validation-3/hosted-refresh/stage-report.md').read_text())
full=(STATE/'_archive/dispatch-build-writes-the-dispatch-record.md').read_text()
write(R/'grader-inputs/validation-4.md',full[full.rindex('## Stage Report: validation'):])
write(R/'grader-inputs/positive.md','- F1 Material: Codex review comment 4505793059 is unaddressed at 778367add\n')
for name in ['validation-review-codex-help.txt','validation-review-claude-help.txt']:
    shutil.copy('/tmp/'+name,R/name)
print(json.dumps({'fixture':str(F),'rewrites':len(notes),'head':HEAD}))
