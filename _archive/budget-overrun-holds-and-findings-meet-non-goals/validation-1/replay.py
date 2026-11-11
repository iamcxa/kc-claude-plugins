import contextlib, importlib.util, io, json, re, subprocess, sys
from pathlib import Path
out = Path('/tmp/budget-validation-841/evidence')
root = Path(sys.argv[1])
sys.path.insert(0, str(root / 'kc-dev-flow-2/scripts'))
import role_triggers as rt
spec = importlib.util.spec_from_file_location('base_rt', out / 'base_role_triggers.py')
base = importlib.util.module_from_spec(spec); spec.loader.exec_module(base)
old_spec = importlib.util.spec_from_file_location('broad_budget', Path(sys.argv[2]) / 'budget_bound.py')
broad = importlib.util.module_from_spec(old_spec); old_spec.loader.exec_module(broad)
pins = json.loads((out / 'pins.json').read_text())
def git(repo, *args):
    return subprocess.check_output(['git', '-C', repo, *args], text=True).strip()
def admitted(records):
    return [(name, 'Budget: One cycle per stage.\n' + body) for name, body in records]
results = {}
for name in pins:
    corpus = out / 'corpus-md' / name
    data = []
    for container in (corpus, corpus / '_archive'):
        if not container.exists(): continue
        for folder in sorted(container.iterdir()):
            if not (folder.is_dir() and (folder / 'dispatch').is_dir()): continue
            task = container / (folder.name + '.md')
            if not task.exists(): task = folder / 'index.md'
            if not task.exists(): continue
            text = task.read_text(); budget = rt.budget_text(text)
            recs = [(p.name, p.read_text()) for p in sorted((folder / 'dispatch').glob('*.md')) if rt.STAGE_RECORD.fullmatch(p.name)]
            real = [(n, b) for n, b in recs if re.fullmatch(r'(implementation|validation)-\d+\.md', n)]
            if not budget or not real: continue
            bound = broad.parse(budget)
            before = bool(bound and any(int(re.search(r'-(\d+)\.md$', n)[1]) > bound.get(n.split('-')[0], 10**9) for n, b in real))
            held, message, fixed = rt.budget_status(text, admitted(recs), folder.name)
            data.append(dict(task=str(task.relative_to(corpus)), budget=budget, broad_countable=bool(bound), broad_held=before,
                             fixed_countable=bool(fixed), fixed_held=held))
    results[name] = dict(tasks=len(data), broad_countable=sum(d['broad_countable'] for d in data), broad_held=sum(d['broad_held'] for d in data),
                         fixed_countable=sum(d['fixed_countable'] for d in data), fixed_held=sum(d['fixed_held'] for d in data),
                         differences=[d for d in data if (d['broad_countable'],d['broad_held']) != (d['fixed_countable'],d['fixed_held'])])
(out / 'archive-replay.json').write_text(json.dumps(results, indent=2) + '\n')
repo, pin = pins['relay']; slug = 'comment-sent-when-added-relay'
paths = [slug + '.md', slug]
commits = git(repo, 'log', '--reverse', '--format=%H', pin, '--', *paths).splitlines()
original = rt.read_records
rt.read_records = lambda *args: admitted(original(*args))
history = []
for rev in commits:
    try:
        if not original(repo, slug, rev): continue
        record_paths = git(repo, 'ls-tree', '-r', '--name-only', rev, '--', slug + '/dispatch/').splitlines()
        candidates = [p for p in record_paths if re.fullmatch(r'(implementation|validation)-\d+\.md', Path(p).name)]
        newest = max(candidates, key=lambda p: (int(re.search(r'-(\d+)\.md$', p)[1]), p)) if candidates else None
        pending = None
        if newest:
            pending = out / 'pending' / Path(newest).name; pending.parent.mkdir(exist_ok=True)
            pending.write_text('Budget: One cycle per stage.\n' + git(repo, 'show', f'{rev}:{newest}'))
        after_code, after_text = rt.check(Path(repo), slug, rev, pending=str(pending) if pending else None)
        before_code, before_text = base.check(Path(repo), slug, rev, pending=str(pending) if pending else None)
        history.append(dict(rev=rev, pending=newest, base_exit=before_code, base=before_text, candidate_exit=after_code, candidate=after_text))
    except rt.Unverifiable:
        continue
first = next(row for row in history if 'budget exceeded' in row['candidate'])
assert first['rev'].startswith('42317d0c'), first
assert not any(row['base_exit'] for row in history if row['rev'] == first['rev'])
(out / 'relay-replay.json').write_text(json.dumps(history, indent=2) + '\n')
print(json.dumps(dict(archive={k:{a:b for a,b in v.items() if a != 'differences'} for k,v in results.items()}, relay_first=first), indent=2))
