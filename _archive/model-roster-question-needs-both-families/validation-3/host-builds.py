import json, os, shutil, subprocess, tempfile
from pathlib import Path
root = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-question-needs-both-families/.context/validation-3/candidate')
base = Path(tempfile.mkdtemp(prefix='roster-v3-hosts-', dir='/tmp'))
repo = base / 'repo'
workflow = repo / 'docs/dev2'
workflow.mkdir(parents=True)
template = (root / 'kc-dev-flow-2/references/sd/workflow.md').read_text()
(workflow / 'README.md').write_text(template)
(repo / '.gitignore').write_text('**/.spacedock-state/\n.worktrees/\n')
env = dict(os.environ, CLAUDECODE='1', GIT_AUTHOR_NAME='Fixture', GIT_AUTHOR_EMAIL='fixture@example.invalid', GIT_COMMITTER_NAME='Fixture', GIT_COMMITTER_EMAIL='fixture@example.invalid')
env.pop('CODEX_THREAD_ID', None)
def run(args):
    r = subprocess.run(list(map(str,args)), env=env, cwd=repo, capture_output=True, text=True)
    assert r.returncode == 0, (args, r.stderr, r.stdout)
    return r
run(['git','init','--initial-branch=main',repo])
run(['git','-C',repo,'add','--','.gitignore','docs/dev2/README.md'])
run(['git','-C',repo,'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','-c','commit.gpgsign=false','-c','core.hooksPath=/dev/null','commit','-m','test: fixture'])
state=workflow/'.spacedock-state'
state.mkdir()
run(['git','init','--initial-branch=spacedock-state/dev2',state])
check=base/'checklist.txt'; check.write_text('Synthetic host build; no worker execution.\n')
notes=base/'notes.txt'; notes.write_text(f'Package root: {root}/kc-dev-flow-2\nSend your completion message to `main`.\n')
results=[]; artifacts=set()
try:
    for stage,host,model in [('ideation','claude','opus'),('implementation','codex',None),('validation','codex',None),('implementation',None,'sonnet')]:
        slug='v3-host-'+stage+'-'+(host or 'implicit')
        task=state/(slug+'.md')
        body=template.split('```markdown\n',1)[1].split('```',1)[0]
        task.write_text(body.replace('<task-id>',slug).replace('<selected-profile>','pilot').replace('status: backlog','status: '+stage))
        run(['git','-C',state,'add','--',task])
        run(['git','-C',state,'-c','commit.gpgsign=false','-c','core.hooksPath=/dev/null','commit','-m','test: task fixture'])
        args=['/Users/kent/.local/bin/spacedock','dispatch','build','--workflow-dir',workflow,'--entity-path',task,'--stage',stage,'--checklist-file',check,'--scope-notes-file',notes,'--stamp']
        if host: args += ['--host',host]
        r=run(args); envelope=json.loads(r.stdout)
        artifacts.add(Path(envelope['dispatch_file_path']))
        assert envelope['model']==model,envelope
        assert ('Skill(' if host in ('claude',None) else '$spacedock:ensign') in envelope['prompt']
        results.append(dict(stage=stage,host=host,expected_model=model,command=list(map(str,args)),environment={'CLAUDECODE':'1','CODEX_THREAD_ID':'unset'},exit=r.returncode,envelope=envelope))
        print(stage,host,model)
finally:
    for path in artifacts: path.unlink()
    shutil.rmtree(base)
Path('/tmp/roster-validation-3/provider-host-builds.json').write_text(json.dumps(results,indent=2)+'\n')
