import collections
import hashlib
import json
from pathlib import Path

state=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/claims-name-their-source/validation')
rows=[]
sources=[]
for stage in ('implementation-2','implementation-3'):
    p=state/stage/'replay-results.json'
    rows.extend(json.loads(p.read_text()))
    sources.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
cells=collections.defaultdict(list)
for row in rows:
    assert row['answered'] and row['provider']=='claude'
    assert row['model_reported']==['claude-opus-5-5']
    assert '--safe-mode' in row['argv']
    cells[row['scenario']+'-'+row['arm']].append(row['passed'])
grader={k:{'passed':sum(v),'runs':len(v)} for k,v in cells.items()}
assert grader=={'K-base':{'passed':3,'runs':3},'K-candidate':{'passed':6,'runs':6},'P-base':{'passed':1,'runs':3},'P-candidate':{'passed':6,'runs':6}}
semantic_path=state/'validation-2/semantic-read.json'
semantic=json.loads(semantic_path.read_text())
target=collections.defaultdict(list)
for row in semantic:
    p=Path(row['path'])
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
    target['candidate' if '-candidate-' in row['run'] else 'base'].append(row['target_count_labelled'])
labelled={k:{'labelled':sum(v),'runs':len(v)} for k,v in target.items()}
assert labelled=={'base':{'labelled':0,'runs':3},'candidate':{'labelled':3,'runs':6}}
result={'date':'2026-11-04','command':'python3 -B audit.py','new_provider_calls':0,
        'frozen_grader':grader,'K_target_claim_labels':labelled,
        'classification_source':'validation-2 independent manual reading; this command checks hashes and recounts those recorded labels',
        'semantic_read_sha256':hashlib.sha256(semantic_path.read_bytes()).hexdigest(),'sources':sources,
        'limits':'One model; recorded safe-mode flag, no file-open trace; K grader false-passes base; no assertion of reliable count correction'}
Path(__file__).with_name('proof-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('Frozen P counts, K grader false-pass and target-label counts match the ruled proof; model/flag and answer hashes agree.')
