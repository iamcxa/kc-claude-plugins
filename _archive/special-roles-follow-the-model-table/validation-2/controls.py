from pathlib import Path
import json,subprocess,sys,shutil,importlib.util
WT=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-roles-follow-the-model-table/.validation-8eed70b2')
E=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-roles-follow-the-model-table/.validation-evidence-8eed70b2')
sys.path.insert(0,str(WT/'kc-dev-flow-2/scripts'));import test_sd_dispatch as td
texts=td.pinned_texts();assert td.fix_gaps(texts)['reviewer-record']==([],[])
key='references/sd/workflow.md';changed=texts[key].replace('`kc-dev-flow-2:design-director` and ','',1)
gaps=td.fix_gaps({**texts,key:changed})['reviewer-record'];assert gaps[0]
print('AC7 drop director => reviewer-record missing',len(gaps[0]),'required phrase')
changed=texts[key].replace('from implementation workers','from all workers')
assert changed.count('from implementation workers')==0
print('AC7 restore all workers => implementation-worker phrase count 0')
fixture=E/'missing-adr';shutil.copytree(WT/'docs/adr',fixture,dirs_exist_ok=True)
(fixture/'0049-special-roles-and-stage-defaults-follow-one-model-table.md').unlink()
r=subprocess.run([sys.executable,'-B','/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py',str(fixture),'--require','0049'],capture_output=True,text=True,cwd=WT)
assert r.returncode==1 and '0049' in r.stdout+r.stderr,(r.returncode,r.stdout,r.stderr)
print('AC9 remove ADR 0049 => exit',r.returncode);print(r.stdout+r.stderr)
