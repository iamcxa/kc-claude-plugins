import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('local_monitor', ROOT / 'monitor.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
W, S, P = 'synthetic-workspace', 'synthetic-session', 'synthetic-project'


def reply(value, **extra):
    return {'exit': 0, 'stdout': json.dumps(value), **extra}


def page(rows, more=False):
    return reply({'data': rows, 'offset': 0, 'hasMore': more})


def event(identity='m1', **changes):
    terminal = {'type': 'result', 'session_id': S, 'subtype': 'success', 'is_error': False, 'result': 'synthetic completion'}
    terminal.update(changes)
    return {'id': identity, 'sessionId': S, 'content': {'rawPayload': terminal}}


def responses():
    ready = reply({'id': W, 'projectId': P, 'state': 'ready'})
    archived = reply({'id': W, 'projectId': P, 'state': 'archived'})
    return {
        f'workspace get {W}': [ready, ready, ready, archived],
        f'workspace session {W} --include-archived --limit 100': [page([{'id': S}])],
        f'session message {S} --limit 10': [page([event()])],
        f'session message {S} --limit 10 --after m1': [page([])],
        f'session status {S}': [reply({'workspaceId': W, 'sessionId': S, 'status': 'idle'})],
        f'session cancel {S}': [reply({'status': 'idle'})],
        f'workspace archive {W}': [reply({'state': 'archived'})],
    }


def make(root, data, *, now=0, tamper=False):
    (root / 'prior.json').write_text('controller-owned synthetic bytes\n')
    if tamper:
        (root / 'prior.json').write_text('changed before monitor startup\n')
    fake = FakeRunner(data)
    fake.clock.now = now
    monitor = module.Monitor(module.CommandTransport(fake, fake.clock), root, W, S, P,
                             submitted_monotonic=0, deadline_monotonic=300,
                             expected_prior_sha256=hashlib.sha256(b'controller-owned synthetic bytes\n').hexdigest())
    monitor.fake = fake
    return monitor


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def advance(self, seconds):
        self.now += seconds


class FakeRunner:
    def __init__(self, data):
        self.data = json.loads(json.dumps(data))
        self.clock, self.calls = FakeClock(), []

    def __call__(self, command, *, capture_output, text, timeout):
        assert command[:2] == ['conductor', '--json'] and capture_output and text
        args = tuple(command[2:])
        self.calls.append((args, timeout, self.clock.now))
        queue = self.data[' '.join(args)]
        response = queue.pop(0) if len(queue) > 1 else queue[0]
        elapsed = response.get('elapsed', .1)
        self.clock.advance(timeout if response.get('timeout') else min(timeout, elapsed))
        if response.get('timeout') or elapsed > timeout:
            raise subprocess.TimeoutExpired(command, timeout)
        return types.SimpleNamespace(returncode=response['exit'], stdout=response['stdout'], stderr=response.get('stderr', ''))


class LocalMonitorTests(unittest.TestCase):
    def test_delayed_start_does_not_renew_window(self):
        data = responses()
        data[f'session message {S} --limit 10'] = [page([])]
        for now in (250, 310):
            with self.subTest(now=now), tempfile.TemporaryDirectory(prefix='frozen-deadline-') as tmp:
                monitor = make(Path(tmp), data, now=now)
                with patch.object(module.subprocess, 'run', side_effect=AssertionError('REAL TRANSPORT FORBIDDEN')):
                    code, result = monitor.run()
                self.assertEqual(code, 1)
                canceled_at = next(at for args, _, at in monitor.fake.calls if args[:2] == ('session', 'cancel'))
                self.assertLess(canceled_at, 300 if now < 300 else now + 1)

    def test_prestart_tamper_is_not_blessed_as_baseline(self):
        with tempfile.TemporaryDirectory(prefix='frozen-canary-') as tmp:
            monitor = make(Path(tmp), responses(), tamper=True)
            with patch.object(module.subprocess, 'run', side_effect=AssertionError('REAL TRANSPORT FORBIDDEN')):
                code, result = monitor.run()
            self.assertEqual((code, result['reason']), (1, 'canary_changed'))
            self.assertEqual(result['steps']['final_canary']['kind'], 'canary_changed')

    def run_case(self, data=None):
        with tempfile.TemporaryDirectory(prefix='monitor-green-') as tmp:
            monitor = make(Path(tmp), data or responses())
            with patch.object(module.subprocess, 'run', side_effect=AssertionError('REAL TRANSPORT FORBIDDEN')):
                code, result = monitor.run()
            self.assertEqual(json.loads(Path(tmp, 'result.json').read_text())['exit_code'], code)
            self.assertTrue(all(0 < timeout <= 10 for _, timeout, _ in monitor.fake.calls))
            return code, result, monitor

    def assert_archive_once(self, monitor):
        self.assertEqual(sum(args[:2] == ('workspace', 'archive') for args, _, _ in monitor.fake.calls), 1)

    def test_normal_verified_terminal_and_cleanup(self):
        code, result, monitor = self.run_case()
        self.assertEqual(code, 0)
        self.assertEqual(result['reason'], 'terminal_complete')
        self.assert_archive_once(monitor)

    def test_malformed_normal_transcript_classified_and_cleanup_independent(self):
        data = responses()
        data[f'session message {S} --limit 10'] = [{'exit': 0, 'stdout': '{"data":'}]
        code, result, monitor = self.run_case(data)
        self.assertEqual((code, result['reason']), (1, 'malformed_json'))
        self.assertEqual(result['calls'][2]['raw']['stdout'], '{"data":')
        self.assert_archive_once(monitor)
        self.assertEqual(result['steps']['final_transcript']['kind'], 'malformed_json')

    def test_final_transcript_failure_cannot_block_archive(self):
        data = responses()
        data[f'session message {S} --limit 10 --after m1'] = [page([]), {'exit': 0, 'stdout': '{'}]
        code, result, monitor = self.run_case(data)
        self.assertEqual(code, 1)
        self.assertEqual(result['reason'], 'terminal_complete')
        self.assertEqual(result['steps']['final_transcript']['kind'], 'malformed_json')
        self.assertEqual(result['steps']['archive_observed']['state'], 'ok')
        self.assert_archive_once(monitor)

    def test_malformed_nested_event_persists_failure_and_cleans_up(self):
        for content in (None, [], {'rawPayload': None}, {'rawPayload': []}):
            with self.subTest(content=content):
                data = responses()
                data[f'session message {S} --limit 10'] = [page([{**event(), 'content': content}])]
                code, result, monitor = self.run_case(data)
                self.assertEqual((code, result['reason']), (1, 'invalid_message_shape'))
                self.assertEqual(result['steps']['archive_observed']['state'], 'ok')
                self.assert_archive_once(monitor)

    def test_command_timeout_is_unknown_and_nonzero(self):
        data = responses()
        data[f'session status {S}'] = [{'timeout': True}, reply({'workspaceId': W, 'sessionId': S, 'status': 'idle'})]
        code, result, monitor = self.run_case(data)
        self.assertEqual((code, result['reason']), (1, 'command_timeout_unknown'))
        self.assert_archive_once(monitor)
        self.assertTrue(any(row.get('state') == 'unknown' for row in result['calls']))

    def test_cancel_failure_does_not_block_archive(self):
        data = responses()
        data[f'session cancel {S}'] = [{'exit': 4, 'stdout': '', 'stderr': 'synthetic failure'}]
        code, result, monitor = self.run_case(data)
        self.assertEqual(code, 1)
        self.assertEqual(result['steps']['cancel']['kind'], 'command_failed')
        self.assertEqual(result['steps']['archive_observed']['state'], 'ok')
        self.assert_archive_once(monitor)

    def test_archive_timeout_then_archived_readback_is_not_response_success(self):
        data = responses()
        data[f'workspace archive {W}'] = [{'timeout': True}]
        code, result, monitor = self.run_case(data)
        self.assertEqual(code, 1)
        self.assertEqual(result['steps']['archive']['state'], 'unknown')
        self.assertEqual(result['steps']['archive_observed']['state'], 'ok')
        self.assert_archive_once(monitor)

    def test_wrong_workspace_or_project_refuses_mutations(self):
        for changes in ({'id': 'other'}, {'projectId': 'other'}):
            with self.subTest(changes=changes):
                data = responses()
                data[f'workspace get {W}'] = [reply({'id': W, 'projectId': P, 'state': 'ready', **changes})]
                code, result, monitor = self.run_case(data)
                self.assertEqual(code, 1)
                self.assertFalse(any(args[1] in ('cancel', 'archive') for args, _, _ in monitor.fake.calls))
                self.assertEqual(result['steps']['archive']['state'], 'refused')

    def test_session_id_in_name_is_not_membership(self):
        data = responses()
        data[f'workspace session {W} --include-archived --limit 100'] = [page([{'id': 'other', 'name': S}])]
        code, result, monitor = self.run_case(data)
        self.assertEqual(code, 1)
        self.assertFalse(any(args[1] in ('cancel', 'archive') for args, _, _ in monitor.fake.calls))

    def test_deadline_and_idle_without_terminal_never_pass(self):
        data = responses()
        data[f'session message {S} --limit 10'] = [page([])]
        code, result, monitor = self.run_case(data)
        self.assertEqual((code, result['reason']), (1, 'deadline_incomplete'))
        canceled_at = next(at for args, _, at in monitor.fake.calls if args[:2] == ('session', 'cancel'))
        self.assertLess(canceled_at, 300)
        self.assert_archive_once(monitor)

    def test_failed_terminal_is_nonzero(self):
        data = responses()
        data[f'session message {S} --limit 10'] = [page([event(subtype='error', is_error=True)])]
        code, result, _ = self.run_case(data)
        self.assertEqual((code, result['reason']), (1, 'terminal_failed'))

    def test_bounded_cursor_pages_keep_partial_evidence(self):
        data = responses()
        data[f'session message {S} --limit 10'] = [page([event()], True)]
        data[f'session message {S} --limit 10 --after m1'] = [{'exit': 0, 'stdout': '{'}]
        code, result, monitor = self.run_case(data)
        self.assertEqual(code, 1)
        self.assertEqual(result['events'][0]['id'], 'm1')
        self.assert_archive_once(monitor)

    def test_repeated_cursor_and_foreign_event_are_rejected(self):
        for row in (event(), {**event('m2'), 'sessionId': 'other'}):
            data = responses()
            data[f'session message {S} --limit 10 --after m1'] = [page([row])]
            code, result, _ = self.run_case(data)
            self.assertEqual(code, 1)
            self.assertIn(result['reason'], ('cursor_repeated_or_duplicate', 'message_identity_mismatch'))

    def test_missing_archive_readback_is_incomplete(self):
        data = responses()
        data[f'workspace get {W}'] = [reply({'id': W, 'projectId': P, 'state': 'ready'})]
        code, result, monitor = self.run_case(data)
        self.assertEqual(code, 1)
        self.assertEqual(result['steps']['archive_observed']['state'], 'unknown')
        self.assert_archive_once(monitor)

    def test_no_live_transport_and_no_implicit_execution(self):
        with self.assertRaises(TypeError):
            module.Monitor(subprocess.run, None, W, S, P)
        with self.assertRaises(PermissionError):
            module.CommandTransport()
        imports = [alias.name for node in ast.walk(ast.parse((ROOT / 'monitor.py').read_text())) if isinstance(node, ast.Import) for alias in node.names]
        self.assertEqual(set(imports), {'hashlib', 'json', 'math', 'subprocess', 'time'})
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'monitor.py')], capture_output=True, text=True, timeout=2)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('no live entrypoint', result.stderr)

    def test_actual_shell_statuses_are_preserved(self):
        for mode, expected in (('normal', 0), ('nonzero', 7), ('timeout', 143), ('invalid', 64)):
            with self.subTest(mode=mode):
                result = subprocess.run(['/bin/bash', str(ROOT / 'preserve-exit.sh'), mode], capture_output=True, text=True, timeout=2)
                self.assertEqual(result.returncode, expected)
                if mode != 'invalid':
                    self.assertEqual(result.stdout.strip(), f'EXIT={expected}')

    def test_actual_controller_process_status(self):
        for scenario, expected in (('normal', 0), ('malformed', 1)):
            result = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--controller-case', scenario], capture_output=True, text=True, timeout=3)
            self.assertEqual(result.returncode, expected, result.stderr)


if __name__ == '__main__':
    if '--controller-case' in sys.argv:
        data = responses()
        if sys.argv[-1] == 'malformed':
            data[f'session message {S} --limit 10'] = [{'exit': 0, 'stdout': '{'}]
        with tempfile.TemporaryDirectory(prefix='controller-exit-') as tmp:
            with patch.object(module.subprocess, 'run', side_effect=AssertionError('REAL TRANSPORT FORBIDDEN')):
                code, result = make(Path(tmp), data).run()
            print(json.dumps({'reason': result['reason'], 'exit_code': code}))
            raise SystemExit(code)
    else:
        unittest.main(verbosity=2)
