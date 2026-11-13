import json,pathlib,subprocess,sys
root=pathlib.Path(__file__).resolve().parent
blind=json.loads((root/'blind-output/output.json').read_text())
fields=['key','by','waiting_since','waiting_bound','holds','interruptions','state']
snapshots=[];errors=[];rounding=[]
for snap in blind:
    cmd=[sys.executable,'-B',str(root/'candidate/kc-dev-flow-2/scripts/task_timeline.py'),str(root/'blind-input'),'--open','--json','--as-of',snap['clock']]
    run=subprocess.run(cmd,text=True,capture_output=True,check=True)
    rows=json.loads(run.stdout)
    snapshots.append(dict(clock=snap['clock'],open=rows))
    actual={r['key']:r for r in rows};expected={r['key']:r for r in snap['open']}
    if actual.keys()!=expected.keys():errors.append(dict(clock=snap['clock'],reason='key mismatch'))
    for key in actual.keys()&expected.keys():
        for field in fields:
            if actual[key][field]!=expected[key][field]:errors.append(dict(key=key,field=field))
        a,e=actual[key]['waiting_min'],expected[key]['waiting_min']
        if a!=e:rounding.append(dict(clock=snap['clock'],key=key,product=a,blind=e))
        if abs(a-e)>0.051:errors.append(dict(key=key,field='waiting_min',actual=a,expected=e))
(root/'product-replay.json').write_text(json.dumps(snapshots,indent=2,ensure_ascii=False)+'\n')
result=dict(clocks=len(blind),rows=sum(len(s['open']) for s in blind),errors=errors,rounding=rounding,rounding_policy='Product rounds to 0.1 minute; contract does not specify display rounding; tolerance 0.051 min')
(root/'blind-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
assert not errors
