from pathlib import Path
import json
E=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-roles-follow-the-model-table/.validation-evidence')
expected={'chief-engineer':('claude-opus-5-5','xhigh'),'engineering-reviewer':('claude-opus-5-5','xhigh'),'design-director':('claude-sonnet-5-5','high'),'observer':('claude-sonnet-5-5','high')}
evidence={}
for name,marker in [('candidate-native','/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-roles-follow-the-model-table/.validation-562b1a87/kc-dev-flow-2/agents/'),('base-native','/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-roles-follow-the-model-table/.validation-evidence/native-base/kc-dev-flow-2/agents/'),('mutant-native','/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-roles-follow-the-model-table/.validation-evidence/native-mutant/agents/')]:
 data=json.loads((E/f'{name}.json').read_text());assert data['is_error'] is False;sid=data['session_id'];seen={};paths={};calls=[]
 for folder in Path('/Users/kent/.claude/projects').glob(f'*/{sid}/subagents'):
  parent=folder.parent.parent/f'{sid}.jsonl'
  for row in map(json.loads,parent.read_text().splitlines()):
   for content in row.get('message',{}).get('content',[]) if isinstance(row.get('message',{}).get('content'),list) else []:
    if content.get('type')=='tool_use' and content.get('name')=='Agent':
     args=content['input'];assert 'model' not in args;calls.append(args['subagent_type'])
  for meta in folder.glob('*.meta.json'):
   info=json.loads(meta.read_text());assert info['finished'];role=info['agentType'].split(':')[-1]
   log=meta.with_name(meta.name.replace('.meta.json','.jsonl'))
   turns=[r for r in map(json.loads,log.read_text().splitlines()) if r.get('type')=='assistant']
   vals={(r['message']['model'],r.get('perTurnEffort')) for r in turns};assert len(vals)==1;seen[role]=vals.pop();paths[role]=str(log)
 warnings=[l for l in (E/f'{name}.log').read_text().splitlines() if 'does not recognize or apply' in l and marker in l]
 if name=='candidate-native':assert seen==expected and len(calls)==4 and len(warnings)==0,seen
 if name=='base-native':assert len(seen)==4 and all(effort=='medium' for _,effort in seen.values()) and len(warnings)==4
 if name=='mutant-native':assert seen=={'chief-engineer':('claude-opus-5-5','medium')} and len(warnings)==1
 evidence[name]={'session':sid,'turns':seen,'transcripts':paths,'agent_calls_without_model':calls,'warnings':warnings}
 print(name,sid,seen,'warnings',len(warnings))
(E/'native-evidence.json').write_text(json.dumps(evidence,indent=2))
