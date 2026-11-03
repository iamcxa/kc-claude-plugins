import os, re, subprocess, time
from pathlib import Path
root=Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-second-round-prompts-a-step-back/.context/validation-1-worktree")
evidence=Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-second-round-prompts-a-step-back/.context/validation-1-evidence")
plugin=evidence/'spacedock-ci-pin'
commands=re.findall(r'^        run: (.*python3 .*)$', (root/'.github/workflows/kc-dev-flow-2-tests.yml').read_text(), re.M)
assert len(commands)==26, len(commands)
env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1', 'SPACEDOCK_BIN':'/Users/kent/.local/bin/spacedock'}
rows=[]
for original in commands:
    command=original.replace('"$GITHUB_WORKSPACE/.sd-plugin-root"', str(plugin)).replace('"$HOME/.local/bin/spacedock"', '/Users/kent/.local/bin/spacedock')
    name=re.search(r'([^/ ]+\.py)', command).group(1)
    start=time.monotonic()
    done=subprocess.run(command, shell=True, executable='/bin/bash', cwd=root, env=env, capture_output=True, text=True)
    (evidence/(name+'.log')).write_text('COMMAND: '+command+'\n'+done.stdout+done.stderr)
    row=f'{name} exit={done.returncode} seconds={time.monotonic()-start:.2f}'
    print(row, flush=True)
    rows.append(row)
(evidence/'suite-results.txt').write_text('\n'.join(rows)+'\n')
raise SystemExit(any('exit=0 ' not in row for row in rows))
