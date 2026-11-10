"""Replay the extra independent probes after replay.py populated its snapshots."""
import hashlib, json, sys, tempfile, types
from pathlib import Path

out = Path(sys.argv[1])
scripts = out / 'candidate/kc-dev-flow-2/scripts'
sys.path.insert(0, str(scripts))
import decision_ledger as dl
import test_design_surfaces as t

rows = json.loads((out / 'replay/replay.json').read_text())['relay']['rows']
assert len(rows) == 12
assert sum(not dl.quotes_bound_question(row) for row in rows) == 11
assert sum(not True for row in rows) != 11

source = (scripts / 'design_surfaces.py').read_text()
old = ' or not picture.resolve().is_relative_to(folder.resolve())'
assert old in source
mutant = types.ModuleType('symlink_mutant')
mutant.__file__ = str(scripts / 'design_surfaces.py')
exec(compile(source.replace(old, '', 1), mutant.__file__, 'exec'), mutant.__dict__)
with tempfile.TemporaryDirectory(dir=out, prefix='symlink-probe-') as tmp:
    root = Path(tmp)
    folder = root / 'task/design'
    folder.mkdir(parents=True)
    (root / 'preview.html').write_text('<html></html>')
    (root / 'outside.png').write_bytes(b'built screen outside task')
    (folder / 'built-1.png').symlink_to(root / 'outside.png')
    (folder / 'validation-1.yaml').write_text(t.BUILT_REPORT)
    (folder / 'validation-declines-1.yaml').write_text(t.ruled((2, 'upheld', {})))
    task = root / 'task.md'
    task.write_text(t.VALIDATION_TASK.format(
        review='\nDesign review: design/ideation-1.yaml\n', lines=t.BUILT_LINES,
        earlier='', bullet='- F1 Behaviour: the count is said twice in the built header'))
    errors = t.ds.check_task(task, notes=[])
    assert any('built-1.png' in e and 'inside the task folder' in e for e in errors), errors
    assert not mutant.check_task(task, notes=[])
print('PASS: real-string comparator control and symlink containment reverse mutation')
