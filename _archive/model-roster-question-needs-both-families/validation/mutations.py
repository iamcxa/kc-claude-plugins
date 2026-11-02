import json, os, shutil, subprocess, sys, tarfile, tempfile
from pathlib import Path
source=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-question-needs-both-families/.context/roster-validation-57321c0b')
base=Path(tempfile.mkdtemp(prefix='roster-validator-falsifiers-', dir='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-question-needs-both-families/.context'))
archive=base/'candidate.tar'
with archive.open('wb') as f: subprocess.run(['git','-C',str(source),'archive','HEAD'],stdout=f,check=True)
repo=base/'repo';repo.mkdir()
with tarfile.open(archive) as tar: tar.extractall(repo,filter='data')
pkg=repo/'kc-dev-flow-2'; script=pkg/'scripts/model_roster.py'; defaults=pkg/'references/model-roster-defaults.json'; text=pkg/'references/model-roster.md'; old_adr=repo/'docs/adr/0047-repository-stage-model-rosters-keep-readme-defaults-when-absent.md'; workflow=pkg/'references/sd/workflow.md'
runner=base/'check.py'
runner.write_text('''import sys\nfrom pathlib import Path\nsys.path.insert(0,sys.argv[1])\nimport test_sd_dispatch as t\nassert all(gap == ([],[]) for gap in t.fix_gaps(t.pinned_texts()).values()), t.fix_gaps(t.pinned_texts())\nif sys.argv[3] == 'behavior': t.exercise_model_roster(Path(sys.argv[2]))\n''')
original={p:p.read_text() for p in (script,defaults,text,old_adr,workflow)}
mutations=[
('missing-claude-condition',script,original[script].replace('for provider in MODELS:', 'for provider in ("codex",):'),'behavior'),
('flat-model-list',script,original[script].replace('if row["model"] not in MODELS[row["provider"]]:','if row["model"] not in tuple(m for models in MODELS.values() for m in models):'),'behavior'),
('xhigh-cap',script,original[script].replace('EFFORTS = ("low", "medium", "high", "xhigh", "max", "ultra")','EFFORTS = ("low", "medium", "high", "xhigh")'),'behavior'),
('unmapped-claude-ultra',script,original[script].replace('("ultracode" if row["provider"]', '("ultra" if row["provider"]'),'behavior'),
('fixed-openai-family',script,original[script].replace('f"same-family: {family}"', '"same-family: openai"'),'behavior'),
('mixed-family-lie',script,original[script].replace('else "different-family")','else f"same-family: {family}")'),'behavior'),
('absent-effort-fabricated',script,original[script].replace('if row else None','if row else "high"'),'behavior'),
('old-recommended-ideation',defaults,original[defaults].replace('"claude-opus-5-5"','"gpt-6-astra"'),'behavior'),
('question-effort-drift',text,original[text].replace('ideation Opus/high','ideation Opus/xhigh'),'behavior'),
('question-condition-removed',text,original[text].replace('Codex and Claude are available','Codex is available'),'text'),
('adoption-follow-removed',text,original[text].replace('retain README behavior; workers follow FO\'s family.','retain README behavior.'),'text'),
('launch-follow-removed',text,original[text].replace('host behavior without a question or fabricated effort; workers follow FO\'s family.','host behavior without a question or fabricated effort.'),'text'),
('provider-host-removed',text,original[text].replace('Build with `--host` set to the row\'s provider.',''),'text'),
('alias-exception-removed',text,original[text].replace('is no conflict.','is a conflict.'),'text'),
('two-accepted-adrs',old_adr,original[old_adr].replace('Superseded by 0050','Accepted'),'behavior'),
('workflow-changed',workflow,original[workflow]+'\nA workflow change.\n','lint'),
]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
results=[]
for name,path,changed,kind in mutations:
    assert changed != original[path],name
    path.write_text(changed)
    try:
        command=([sys.executable,'-B',str(pkg/'scripts/lint-skills.py')] if kind=='lint' else
                 [sys.executable,'-B',str(runner),str(pkg/'scripts'),str(base/name),kind])
        run=subprocess.run(command,cwd=repo,env=env,capture_output=True,text=True,timeout=180)
        (base/(name+'.log')).write_text(run.stdout+run.stderr)
        assert run.returncode != 0, ('mutation survived',name)
        result=dict(name=name,exit=run.returncode,cache='python3 -B; fresh archive without caches')
        results.append(result); print(json.dumps(result),flush=True)
    finally: path.write_text(original[path])
(base/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print('Evidence:',base,flush=True)
