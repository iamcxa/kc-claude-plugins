from pathlib import Path
import copy, hashlib, json, re, subprocess

TASK = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/peer-status-reaches-fresh')
WT = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-peer-status-reaches-fresh')
HEAD = '39fdbb28b411d44a323741f645c7c1d75c653be1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = json.loads((TASK/'validation-2/manifest.json').read_text())
assert subprocess.check_output(['git', '-C', str(WT), 'rev-parse', 'HEAD'], text=True).strip() == HEAD
for key, name in [('dev_sha256', 'kc-dev-flow-2/skills/dev/SKILL.md'), ('peers_sha256', 'kc-dev-flow-2/extensions/peers/EXTENSION.md')]:
    assert sha(WT/name) == manifest[key]
for name, digest in manifest.items():
    if name.startswith('cold-fo/'):
        assert sha(TASK/name) == digest
rows = json.loads((TASK/'validation-2/cold-audit.json').read_text())
assert len(rows) == 8
for row in rows:
    log = TASK/'cold-fo'/(row['run']+'.jsonl')
    assert sha(log) == row['log_sha256']
    events = [json.loads(line) for line in log.read_text().splitlines() if line.strip()]
    results = [e['result'] for e in events if e.get('type') == 'result']
    assert results == [row['final']], row['run']
    assert row['exact_dev_body'] and row['source_queries']
print('Unchanged: exact head, dev/peers bytes, four harness files, eight original cold logs and final outputs.')

def attributed(text):
    return 'subspace-web' in text and re.search(r'(?:PR\s*)?#\s*186', text) is not None

merged = [r for r in rows if r['run'].startswith(('g-absent', 'g-notice', 'g-delayed'))]
assert len(merged) == 4
for row in merged:
    assert attributed(row['final']), row['run']
    print(row['run']+': source repository + PR 186 present; attribution PASS')
assert not next(r for r in rows if r['run']=='g-absent1')['source_revision_or_link']
assert not next(r for r in rows if r['run']=='g-absent2')['source_revision_or_link']
sample = merged[0]['final']
for label, text in [('repository removed', sample.replace('spacedock-dev/subspace-web', '')), ('PR removed', re.sub(r'#\s*186', '', sample))]:
    assert not attributed(text), label
    print('FALSIFIER DETECTED: '+label)
mutant = copy.deepcopy(rows)
mutant[0]['source_queries'] = []
assert not all(r['source_queries'] for r in mutant)
print('FALSIFIER DETECTED: missing current-turn source query')
print('F5 cleared under corrected AC-9; no source-revision/URL duty imposed.')
print('PASSED at '+HEAD+' within carried-forward bounded validation-2 evidence.')
print('Not proven: historical authorization, native delivery, full package sealing, direct FO resumes, long sessions or post-delivery natural use.')
