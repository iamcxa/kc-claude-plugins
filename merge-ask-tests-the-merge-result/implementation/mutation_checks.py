#!/usr/bin/env python3
import contextlib, importlib.util, io, json, os, shutil, sys, types, unittest
from pathlib import Path
CODE = Path(sys.argv[1]).resolve()
os.environ['PYTHONDONTWRITEBYTECODE']='1'
cleared=[]
for cache in (CODE/'kc-dev-flow-2').rglob('__pycache__'):
    if cache.is_dir() and not cache.is_symlink():
        cleared.append(str(cache.relative_to(CODE)))
        shutil.rmtree(cache)
(Path(__file__).parent/'cleared-caches.json').write_text(json.dumps(cleared,indent=2)+'\n')
sys.path.insert(0, str(CODE / 'kc-dev-flow-2/scripts'))
import test_delivery_gate as tests
source = Path(tests.gate.__file__).read_text()
original = tests.gate
cases = [
 ('AC-1', 'if status in ("ahead", "identical"):', 'if status in ("ahead", "identical", "diverged"):', 'MergeResultTests.test_moved_trunk_without_run_holds'),
 ('AC-2', 'if rec.get("exit") == 0:', 'if rec.get("exit") == 99:', 'MergeResultTests.test_matching_passing_run_passes_and_records_point'),
 ('AC-3', 'and r.get("trunk") == trunk_sha', '', 'MergeResultTests.test_another_trunk_head_or_command_cannot_satisfy'),
 ('AC-4', 'if rec.get("exit") == 0:', 'if True:', 'MergeResultTests.test_failing_run_holds_and_names_exit'),
 ('AC-5', 'if MERGE_NOT_RUN.search(', 'if False and MERGE_NOT_RUN.search(', 'MergeResultTests.test_not_run_line_passes_and_is_saved'),
 ('AC-6', 'if status in ("ahead", "identical"):', 'if False:', 'MergeResultTests.test_ancestor_trunk_adds_no_requirement_or_point'),
 ('AC-7', '"--write-tree", trunk_sha, head', '"--write-tree", head, head', 'MergeRunTests.test_runs_the_merged_tree_and_removes_scratch'),
 ('AC-8', 'shutil.rmtree(scratch)', 'None', 'MergeRunTests.test_runs_the_merged_tree_and_removes_scratch'),
 ('command-match', 'and command and r.get("command") == command', '', 'MergeResultTests.test_another_trunk_head_or_command_cannot_satisfy'),
]
rows=[]
for name, old, new, target in cases:
    assert source.count(old)==1, (name, source.count(old))
    variant = types.ModuleType('delivery_gate_mutation')
    variant.__file__ = original.__file__
    exec(compile(source.replace(old,new), variant.__file__, 'exec'), variant.__dict__)
    tests.gate=variant
    stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream).run(unittest.defaultTestLoader.loadTestsFromName(target, tests))
    tests.gate=original
    (Path(__file__).parent / ('mutation-'+name+'.log')).write_text(stream.getvalue())
    rows.append(dict(name=name, status='passed' if result.failures and not result.errors else 'failed',
                     message='Mutated implementation was rejected by the named behavioral test', test=target,
                     failures=len(result.failures), errors=len(result.errors)))
(Path(__file__).parent/'mutations.json').write_text(json.dumps(rows,indent=2)+'\n')
for r in rows:
    print(r['name'],r['status'],r['test'])
raise SystemExit(any(r['status']!='passed' for r in rows))
