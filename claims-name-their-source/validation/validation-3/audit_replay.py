import ast, collections, datetime, hashlib, importlib.util, json, sys
from pathlib import Path
C=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-claims-name-their-source/.context/claims-validation-3')
S=Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state")
E=Path("/tmp/opencode/claims-validation-3")
root=S/'claims-name-their-source/validation'
spec=importlib.util.spec_from_file_location('saved_replay',root/'implementation-2/replay.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
rows=[]; falsifiers=[]; hashes=[]; attempts=[]
for folder in ['implementation-2','implementation-3']:
    d=root/folder
    for line in (d/'harness-sha256.txt').read_text().splitlines():
        expected,name=line.split()
        actual=hashlib.sha256((d/name).read_bytes()).hexdigest()
        hashes.append(dict(folder=folder,file=name,expected=expected,actual=actual,matched=actual==expected))
    for f in json.loads((d/'grader-falsifiers.json').read_text()):
        result=mod.grade(f['scenario'],f['text'])
        falsifiers.append(dict(folder=folder,scenario=f['scenario'],kind=f['kind'],expected=f['expected'],actual=result,matched=f['expected']==result))
    for p in sorted((d/'runs').glob('*/meta.json')):
        meta=json.loads(p.read_text()); answer=(p.parent/'answer.txt').read_text()
        events=[json.loads(line) for line in (p.parent/'stdout.jsonl').read_text().splitlines() if line.startswith('{')]
        result=next(e for e in reversed(events) if e.get('type')=='result')
        prompt=(p.parent/'prompt.txt').read_text()
        expected_prompt='Act as the First Officer described in this workflow. Use these workflow instructions when writing the requested text.\n<workflow>\n'+(d/(meta['arm']+'-workflow.md')).read_text()+'\n</workflow>\n\n'+json.loads((d/'scenarios.json').read_text())[meta['scenario']]
        if meta['scenario']=='K' and meta['arm']=='candidate': expected_prompt+='\n\nThe question command printed:\n'+mod.REMINDER
        usage=result['usage']
        row=dict(folder=folder,id=meta['id'],scenario=meta['scenario'],arm=meta['arm'],model=meta['model_reported'],
                 exit=meta['exit_code'],answered=meta['answered'],saved_grade=meta['passed'],regrade=mod.grade(meta['scenario'],answer),
                 answer_matches_raw=answer==result['result'],prompt_hash_matches=hashlib.sha256(prompt.encode()).hexdigest()==meta['prompt_sha256'],
                 prompt_matches_frozen_inputs=prompt==expected_prompt,
                 input_tokens=sum(usage.get(k,0) for k in ['input_tokens','cache_creation_input_tokens','cache_read_input_tokens']),
                 output_tokens=usage['output_tokens'],answer_path=str(p.parent/'answer.txt'),
                 limit_lines=[l for l in answer.splitlines() if any(x in l for x in ['S6','**Limits','Measurement limits','Limits that'])])
        rows.append(row)
for d in ['implementation-1','implementation-2','implementation-3']:
    attempts.extend(str(p.relative_to(root)) for p in (root/d/'runs').glob('*/meta.json'))
assert all(h['matched'] for h in hashes)
assert all(f['matched'] for f in falsifiers)
assert all(r['answer_matches_raw'] and r['prompt_hash_matches'] and r['prompt_matches_frozen_inputs'] and r['regrade']==r['saved_grade'] for r in rows)
assert len(attempts)==22
candidate_hash=hashlib.sha256((C/'kc-dev-flow-2/references/sd/workflow.md').read_bytes()).hexdigest()
assert candidate_hash==hashlib.sha256((root/'implementation-3/candidate-workflow.md').read_bytes()).hexdigest()
counts={}
for scenario in ['P','K']:
    for arm in ['base','candidate']:
        selected=[r for r in rows if r['scenario']==scenario and r['arm']==arm]
        counts[scenario+'-'+arm]={'passed':sum(r['regrade'] for r in selected),'runs':len(selected)}
controls=[
 dict(name='K wrong count with report title',scenario='K',text='Validation gate summary: read-adr reporting rule. S6 Codex and S7 Codex were not re-run on the final bytes.',correct_expected=False),
 dict(name='K same wrong count without report title',scenario='K',text='Gate summary. S6 Codex and S7 Codex were not re-run on the final bytes.',correct_expected=False)
]
for row in controls: row['actual']=mod.grade(row['scenario'],row['text'])
audit=dict(date=datetime.datetime.now(datetime.timezone.utc).isoformat(),method='Import only grade(); no provider invocation, no rubric edits.',
          candidate='69f4988612d17c5524887f99c872a0ef384d05c9',candidate_workflow_sha256=candidate_hash,
          counts=counts,attempts=len(attempts),new_provider_runs=0,
          input_tokens=sum(r['input_tokens'] for r in rows),output_tokens=sum(r['output_tokens'] for r in rows),
          hashes=hashes,falsifiers=falsifiers,controls=controls,rows=rows)
if '--check-only' not in sys.argv: (E/'replay-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print(json.dumps({k:audit[k] for k in ['method','counts','attempts','new_provider_runs','input_tokens','output_tokens','controls']},indent=2))

