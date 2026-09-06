"""Extract definitions/cleanup AST only: never import or execute old submission."""
import ast
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import os
import sys
import tempfile
import time
import types
import unittest

OLD = Path(__file__).resolve().parents[1] / 'cloud-once/monitor-once.py'


def extract():
    tree = ast.parse(OLD.read_text())
    definitions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    final = next(n for n in tree.body if isinstance(n, ast.Try)).finalbody
    cleanup = next(n for n in final if isinstance(n, ast.Try))
    fn = ast.FunctionDef(name='old_cleanup', args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]), body=[cleanup], decorator_list=[])
    module = ast.fix_missing_locations(ast.Module(body=definitions + [fn], type_ignores=[]))
    fake = types.SimpleNamespace(run=lambda *a, **k: types.SimpleNamespace(returncode=0, stdout='{"data":', stderr=''))
    ns = dict(json=json, datetime=datetime, time=time, subprocess=fake, sequence=0, deadline=None)
    exec(compile(module, str(OLD), 'exec'), ns)
    return ns


class LegacyRegressions(unittest.TestCase):
    def test_controller_failure_is_nonzero(self):
        result = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--controller-process'], capture_output=True, text=True, timeout=3)
        self.assertIn('controller_error', result.stdout)
        self.assertNotEqual(result.returncode, 0)

    def test_invalid_json_is_classified_not_keyerror(self):
        with tempfile.TemporaryDirectory(prefix='monitor-red-') as tmp:
            ns = extract()
            ns['ROOT'] = Path(tmp)
            with self.assertRaises(ValueError):
                ns['call']('session', 'message', 'synthetic-session')

    def test_final_transcript_failure_cannot_skip_archive(self):
        ns = extract()
        calls = []
        def fake_call(*args):
            calls.append(args)
            if args[:2] == ('session', 'message'):
                raise ValueError('malformed transcript')
            return {'state': 'archived'}
        ns.update(call=fake_call, identity=lambda: None, state={}, SESSION='synthetic-session', WORKSPACE='synthetic-workspace')
        ns['old_cleanup']()
        self.assertIn(('workspace', 'archive', 'synthetic-workspace'), calls)

    def test_trailing_echo_preserves_actual_failure(self):
        result = subprocess.run(['/bin/bash', '-c', '/bin/bash -c "exit 7"; echo "EXIT=$?"'], capture_output=True, text=True, timeout=2)
        self.assertEqual(result.stdout.strip(), 'EXIT=7')
        self.assertEqual(result.returncode, 7)


if __name__ == '__main__':
    if '--controller-process' in sys.argv:
        with tempfile.TemporaryDirectory(prefix='old-controller-') as tmp:
            Path(tmp, 'prior.json').write_text('synthetic')
            tree = ast.parse(OLD.read_text())
            tree.body = [n for n in tree.body if not isinstance(n, (ast.Import, ast.ImportFrom))]
            fake = types.SimpleNamespace(run=lambda *a, **k: types.SimpleNamespace(returncode=0, stdout='{"data":', stderr=''))
            scope = dict(datetime=datetime, hashlib=hashlib, json=json, os=os, Path=Path,
                         subprocess=fake, time=time, __file__=str(Path(tmp, 'old.py')))
            exec(compile(tree, str(OLD), 'exec'), scope)
    else:
        unittest.main(verbosity=2)
