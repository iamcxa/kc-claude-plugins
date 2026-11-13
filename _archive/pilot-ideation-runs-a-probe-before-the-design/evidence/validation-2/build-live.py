from pathlib import Path
import os,subprocess,shutil,re,json
s=Path("/tmp/dev2/kc-claude-plugins-3042bb224e995ded/pilot-ideation-runs-a-probe-before-the-design/validation-2"); task=Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/pilot-ideation-runs-a-probe-before-the-design")
env=dict(os.environ,TMPDIR=str(s/'tmp'),PYTHONDONTWRITEBYTECODE='1',GIT_AUTHOR_NAME='Replay',GIT_AUTHOR_EMAIL='replay@localhost',GIT_COMMITTER_NAME='Replay',GIT_COMMITTER_EMAIL='replay@localhost')
seed=subprocess.check_output(['git','-C',str(s/'state'),'show','08d61c3e48d7365f7e058d16bea85fd61906539a:pr-watch-tasks-foreign-worktree.md'],text=True)
new='\n'.join(line for line in seed.split('\n') if not line.startswith('- Trial (2026-11-13):'))
import difflib
patch=''.join(difflib.unified_diff(seed.splitlines(True),new.splitlines(True),fromfile='a/pr-watch-tasks-foreign-worktree.md',tofile='b/pr-watch-tasks-foreign-worktree.md'))
(s/'seed.patch').write_text(patch);(s/'evidence/live-seed-adjustment.diff').write_text(patch)
cmd=['python3','-B',str(s/'candidate/kc-dev-flow-2/scripts/replay_dispatch.py'),'build','--run-dir',str(s/'live'),'--package-repo',str(s/'code.git'),'--package-ref','45d5ebb9d24665c0904aca5412123a7224d056cc','--adopter-readme',str(s/'adopter-README.md'),'--readme-base-ref','88f86f2749dadb6f4ef0cf9aa089c1827096865b','--state-repo',str(s/'state'),'--state-commit','08d61c3e48d7365f7e058d16bea85fd61906539a','--task','pr-watch-tasks-foreign-worktree','--code-repo',str(s/'code.git'),'--code-commit','88f86f2749dadb6f4ef0cf9aa089c1827096865b','--stage','ideation','--checklist',str(task/'evidence/ideation-1/inputs/pr-watch-tasks-foreign-worktree.checklist.txt'),'--scope',str(task/'evidence/ideation-1/inputs/pr-watch-tasks-foreign-worktree.scope.txt'),'--patch',str(s/'seed.patch'),'--no-completion-line','--spacedock','/Users/kent/.local/bin/spacedock']
with (s/'evidence/live-build.log').open('w') as out:r=subprocess.run(cmd,env=env,cwd=s/'candidate',stdout=out,stderr=subprocess.STDOUT)
(s/'evidence/live-build-command.json').write_text(json.dumps(dict(command=cmd,exit=r.returncode),indent=2)+'\n')
if r.returncode: raise SystemExit(r.returncode)
inputs=s/'evidence/live-inputs';inputs.mkdir(exist_ok=True)
for name in ['dispatch.md','checklist.txt','scope.txt']:
 shutil.copyfile(s/'live'/name,inputs/name)
fetch=re.search(r'### Fetch commands\n\n    (.+)',(s/'live/dispatch.md').read_text()).group(1)
r=subprocess.run(['bash','-c',fetch],env=env,capture_output=True,text=True,check=True)
(inputs/'stage-def.txt').write_text(r.stdout)
(inputs/'task-before.md').write_text((s/'live/wf/.spacedock-state/pr-watch-tasks-foreign-worktree.md').read_text())
shutil.copytree(s/'live/package/kc-dev-flow-2/skills/ideation',inputs/'package/skills/ideation',dirs_exist_ok=True)
for rel in ['README.md','references/sd/workflow.md','references/profiles/pilot.md','skills/implementation/profiles/poc.md','skills/implementation/principles.md']:
 dest=inputs/'package'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(s/'live/package/kc-dev-flow-2'/rel,dest)
print('Native dispatch and exact inputs saved; no subject has run yet.')

