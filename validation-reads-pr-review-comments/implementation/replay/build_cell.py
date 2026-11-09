import argparse, subprocess, sys
from pathlib import Path

R=Path(__file__).resolve().parent
WT=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-validation-reads-pr-review-comments')
STATE=WT.parents[1]/'docs/dev2/.spacedock-state'
HELPER='/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.36.0/scripts/replay_dispatch.py'
p=argparse.ArgumentParser()
p.add_argument('label')
p.add_argument('arm',choices=['base','candidate'])
a=p.parse_args()
scratch=Path('/tmp/validation-review-replay')/a.label
ref='kc-dev-flow-2-v0.36.0' if a.arm=='base' else '7f47317bb278931a873c0ec63302fbc70fc53fc4'
argv=['python3','-B',HELPER,'build','--run-dir',str(scratch),'--package-repo',str(WT),'--package-ref',ref,'--adopter-readme',str(R/'adopter-readme.md'),'--readme-base-ref','kc-dev-flow-2-v0.36.0','--state-repo',str(STATE),'--state-commit','82f2e963989b61f15c080f48187b0107e7e36460','--task','dispatch-build-writes-the-dispatch-record','--code-repo',str(WT),'--code-commit','778367adde2e20e0b3e51966ddba2d9f77f9e614','--stage','validation','--checklist',str(R/'checklist.txt'),'--scope',str(R/'scope.txt'),'--spacedock','/Users/kent/.local/bin/spacedock']
with (R/f'build-{a.label}.log').open('w') as log:
    done=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT)
if done.returncode:raise SystemExit(done.returncode)
canonical=(scratch/'dispatch.md').read_text().replace(str(scratch.resolve()),'<SCRATCH>').replace(str(scratch),'<SCRATCH>')
assert canonical==(R/f'dispatch-fixed-{a.arm}-normalized.md').read_text()
print(scratch.resolve())
