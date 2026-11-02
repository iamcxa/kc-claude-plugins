import copy, json
from datetime import datetime
from pathlib import Path
evidence = Path(__file__).parent
fo = json.loads((evidence / 'fo-primary-extract.json').read_text())
children = json.loads((evidence / 'child-primary-extract.json').read_text())
receipts = json.loads(Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/model-roster-question-needs-both-families/native-runs/final/receipts.json').read_text())
expected = {'8c33c57f': ('claude-opus-5-5','high'), '575a60c6': ('claude-opus-5-5','low'), '84db4474': ('gpt-6.1-sol','xhigh'), '45f8566a': ('gpt-6-astra','xhigh')}
def audit(records, incoming):
    rows=[]
    for child,(model,effort) in expected.items():
        row=records[child]
        assert model in row['models'] and row['efforts']==[effort]
        runtime=children[child]['runtime']
        assert runtime and all(r['model']==model and r.get('perTurnEffort',r.get('effort'))==effort for r in runtime)
        assert row['send_tool_calls']==0
        receipt=next(r for r in incoming if child in r['header'])
        assert row['inbound'][0]['message_id'] in receipt['header']
        assert receipt['timestamp']==row['inbound'][0]['session_time']
        assert 'event="finished"' in receipt['header']
        assert datetime.fromisoformat(receipt['timestamp']) > datetime.fromisoformat(children[child]['last_timestamp'])
        if model.startswith('claude'):
            assert row['process_flags']==[f'--thinking adaptive --effort {effort} --model {model}']
            assert effort in children[child]['safe_flag_values']
        provider=('claude/' if model.startswith('claude') else 'codex/')+model
        spawn=next(r for r in fo['spawn'] if r['input']['provider']==provider and r['input']['settings']['thinkingOptionId']==effort)
        assert spawn['input']['notifyOnFinish'] is True
        if model.startswith('claude'): assert spawn['input']['settings']['modeId']=='auto'
        rows.append(dict(child=child,model=model,effort=effort,received=receipt['timestamp'],last=children[child]['last_timestamp']))
    return rows
rows=audit(receipts,fo['inbound'])
falsifiers=[]
for name in ['low-equals-high','missing-completion']:
    changed=copy.deepcopy(receipts); incoming=copy.deepcopy(fo['inbound'])
    if name=='low-equals-high': changed['575a60c6']['efforts']=['high']
    else: incoming=[r for r in incoming if '84db4474' not in r['header']]
    try: audit(changed,incoming)
    except (AssertionError,StopIteration): falsifiers.append(dict(name=name,rejected=True))
    else: raise AssertionError('falsifier survived')
result=dict(attribution='FO native run; validator independently read linked primary transcripts, no agent started',rows=rows,record_falsifiers=falsifiers)
(evidence/'native-record-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
