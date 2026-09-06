"""One approved attempt: pinned monitor plus independent exact-owned cleanup."""
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parent
PROJECT = '8f58f9d4-cb71-443a-b64d-c2a225248c7b'
PRODUCT = '/Users/kent/conductor/workspaces/kc-claude-plugins/kc-pr-review-capability-pilot'
CORE = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/docs/dev/.spacedock-state/profiled-pr-review-capability-protocol/cloud-local-repair/monitor.py')
CORE_HASH = '54d55e640c85b7957173cc3b66a23751fe3be2d515389265669447a82c8f890b'
sequence = 0


def now():
    return {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'monotonic': time.monotonic()}


def save(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2) + '\n')


def invoke(command, *, timeout=10, capture_output=True, text=True):
    global sequence
    sequence += 1
    record = {'command': command, 'start': now(), 'timeout': timeout}
    if command[:2] == ['conductor', '--json'] and tuple(command[2:4]) in (('session', 'cancel'), ('workspace', 'archive')):
        identity = json.loads((ROOT / 'identity.json').read_text())
        expected = identity['sessionId'] if command[2] == 'session' else identity['workspaceId']
        if command[4] != expected:
            raise OSError('refuse foreign cleanup identity')
        with (ROOT / (command[3] + '-attempt.json')).open('x') as stream:
            json.dump(record, stream)
    try:
        result = subprocess.run(['rtk', 'proxy', *command], capture_output=capture_output, text=text, timeout=timeout)
        record.update(exit=result.returncode, stdout=result.stdout, stderr=result.stderr)
        return result
    except subprocess.TimeoutExpired as error:
        record.update(outcome='timeout_unknown', stdout=str(error.stdout), stderr=str(error.stderr))
        raise
    finally:
        record['end'] = now()
        save(f'call-{os.getpid()}-{sequence:03}.json', record)
        if command[:4] == ['conductor', '--json', 'session', 'status'] and 'stdout' in record and record.get('exit') == 0:
            try:
                status = json.loads(record['stdout'])
                print('STATUS ' + json.dumps({'observed': record['end'], 'status': status}), flush=True)
            except ValueError:
                pass


def api(*args, timeout=10):
    response = invoke(['conductor', '--json', *args], timeout=timeout)
    if response.returncode:
        raise RuntimeError('CLI exit ' + str(response.returncode))
    return json.loads(response.stdout)


def owned(identity):
    ws = api('workspace', 'get', identity['workspaceId'])
    sessions = api('workspace', 'session', identity['workspaceId'], '--include-archived', '--limit', '100')
    assert ws['id'] == identity['workspaceId'] and ws['projectId'] == PROJECT
    assert any(row.get('id') == identity['sessionId'] for row in sessions['data'])
    return ws


def failure_cleanup(identity, label):
    evidence = {'start': now(), 'label': label, 'actions': {}}
    for action in ('cancel', 'archive'):
        try:
            ws = owned(identity)
            if ws.get('state') == 'archived' or (ROOT / (action + '-attempt.json')).exists():
                evidence['actions'][action] = 'already_archived_or_attempted_no_retry'
                continue
            args = ('session', 'cancel', identity['sessionId']) if action == 'cancel' else ('workspace', 'archive', identity['workspaceId'])
            evidence['actions'][action] = api(*args)
        except Exception as error:
            evidence['actions'][action] = {'unknown_or_error': type(error).__name__ + ': ' + str(error)}
    for unused in range(4):
        try:
            evidence['workspace'] = api('workspace', 'get', identity['workspaceId'])
            evidence['session'] = api('session', 'status', identity['sessionId'])
            if evidence['workspace'].get('state') == 'archived' and evidence['session'].get('status') == 'idle':
                break
        except Exception as error:
            evidence['readback_error'] = type(error).__name__ + ': ' + str(error)
        time.sleep(3)
    evidence['end'] = now()
    save(label + '.json', evidence)
    return evidence.get('workspace', {}).get('state') == 'archived'


def watchdog():
    save('watchdog-armed.json', {'pid': os.getpid(), **now()})
    owner = json.loads((ROOT / 'owner.json').read_text())
    while time.monotonic() - owner['monotonic'] < 750:
        if (ROOT / 'finished.json').exists():
            result = json.loads((ROOT / 'finished.json').read_text())
            if result.get('archived'):
                save('watchdog-exit.json', {'reason': 'primary_archived', **now()})
                return
        try:
            os.kill(owner['pid'], 0)
            alive = True
        except ProcessLookupError:
            alive = False
        bound = owner['monotonic'] + 180
        if (ROOT / 'submission.json').exists():
            bound = json.loads((ROOT / 'submission.json').read_text())['deadline_monotonic']
        elif (ROOT / 'creation-start.json').exists():
            bound = json.loads((ROOT / 'creation-start.json').read_text())['monotonic'] + 180
        if not alive or time.monotonic() >= bound:
            if (ROOT / 'identity.json').exists():
                failure_cleanup(json.loads((ROOT / 'identity.json').read_text()), 'watchdog-cleanup')
            save('watchdog-exit.json', {'reason': 'owner_dead_or_bound', 'identity_known': (ROOT / 'identity.json').exists(), **now()})
            return
        time.sleep(1)


def main():
    assert hashlib.sha256(CORE.read_bytes()).hexdigest() == CORE_HASH
    with (ROOT / 'owner.json').open('x') as stream:
        json.dump({'pid': os.getpid(), **now()}, stream)
    identity = None
    watchdog_process = None
    final = {'core_sha256': CORE_HASH, 'retry_count': 0, 'start': now()}
    try:
        status = invoke(['conductor', 'auth', 'status'])
        assert status.returncode == 0
        project = api('project', 'get', PROJECT)
        assert project['id'] == PROJECT and project['gitRemote'] == 'https://github.com/iamcxa/kc-claude-plugins'
        models = api('model')
        claude = next(row for row in models['agents'] if row['agent'] == 'claude')
        assert 'opus-5-1m' in claude['models'] and 'medium' in claude['efforts']
        remote = invoke(['git', '-C', PRODUCT, 'ls-remote', 'origin', 'refs/heads/main'], timeout=20)
        assert remote.returncode == 0
        base = remote.stdout.split()[0]
        tree = invoke(['git', '-C', PRODUCT, 'ls-tree', '--name-only', base, '--', '.conductor', 'conductor.json', '.worktreeinclude'])
        assert tree.returncode == 0 and not tree.stdout.strip(), 'unverified or changed setup/copy prerequisites'
        final['remote_base'] = base
        save('preflight.json', final)
        prior_hash = hashlib.sha256((ROOT / 'prior.json').read_bytes()).hexdigest()
        assert not (ROOT / 'current.json').exists()
        save('frozen-canary.json', {'sha256': prior_hash, **now()})
        watchdog_log = (ROOT / 'watchdog.log').open('x')
        watchdog_process = subprocess.Popen([sys.executable, '-B', str(Path(__file__).resolve()), '--watchdog'], stdout=watchdog_log, stderr=subprocess.STDOUT, start_new_session=True)
        arm_bound = time.monotonic() + 3
        while not (ROOT / 'watchdog-armed.json').exists() and time.monotonic() < arm_bound:
            time.sleep(.05)
        assert (ROOT / 'watchdog-armed.json').exists(), 'watchdog not armed'
        created_at = now()
        with (ROOT / 'creation-start.json').open('x') as stream:
            json.dump(created_at, stream)
        identity = api('workspace', 'create', '--project-id', PROJECT, '--branch', 'main',
                       '--name', 't8cyxd55ve-cloud-followup-cjh5w4', '--session-name', 'Synthetic exit and external stop',
                       '--agent', 'claude', '--model', 'opus-5-1m', '--effort', 'medium', timeout=25)
        save('identity.json', identity)
        print('IDENTITY ' + json.dumps({**identity, 'controller': str(ROOT), 'monitor_pid': os.getpid(), 'watchdog_pid': watchdog_process.pid}), flush=True)
        while time.monotonic() - created_at['monotonic'] < 160:
            ws = owned(identity)
            if ws['state'] == 'ready':
                break
            time.sleep(3)
        assert ws['state'] == 'ready'
        session = api('session', 'get', identity['sessionId'])
        assert session['model'] == 'opus-5-1m' and session['effort'] == 'medium'
        assert time.monotonic() - created_at['monotonic'] < 180
        final['setup_observed'] = {'session': session, 'ready': now(), 'seconds': time.monotonic() - created_at['monotonic']}
        assert hashlib.sha256((ROOT / 'prior.json').read_bytes()).hexdigest() == prior_hash
        assert not (ROOT / 'current.json').exists()
        submitted = now()
        frozen = {**submitted, 'deadline_monotonic': submitted['monotonic'] + 300,
                  'deadline_utc': (datetime.datetime.fromisoformat(submitted['utc']) + datetime.timedelta(seconds=300)).isoformat(),
                  'expected_prior_sha256': prior_hash, 'message_id': str(uuid.uuid4())}
        with (ROOT / 'submission.json').open('x') as stream:
            json.dump(frozen, stream, indent=2)
        spec = importlib.util.spec_from_file_location('pinned_monitor', CORE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        monitor = module.Monitor(module.CommandTransport(runner=invoke, allow_live=True), ROOT, identity['workspaceId'], identity['sessionId'], PROJECT,
                                 submitted_monotonic=frozen['monotonic'], deadline_monotonic=frozen['deadline_monotonic'], expected_prior_sha256=prior_hash)
        print('SUBMISSION ' + json.dumps({**frozen, **identity}), flush=True)
        final['message'] = api('message', 'create', '--session', identity['sessionId'], '--message-id', frozen['message_id'], '--message-file', str(ROOT / 'prompt.md'))
        code, result = monitor.run()
        final.update(monitor_exit=code, monitor_reason=result['reason'])
    except BaseException as error:
        final['error'] = type(error).__name__ + ': ' + str(error)
    finally:
        if identity:
            final['archived'] = failure_cleanup(identity, 'final-cleanup')
        final.update(end=now(), prior_sha256=hashlib.sha256((ROOT / 'prior.json').read_bytes()).hexdigest(), current_exists=(ROOT / 'current.json').exists())
        save('finished.json', final)
        if watchdog_process:
            try:
                watchdog_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                final['watchdog_still_running'] = True
                save('finished.json', final)
        print('FINAL ' + json.dumps(final), flush=True)
    return 0 if final.get('archived') and final.get('monitor_exit') == 0 else 1


if __name__ == '__main__':
    if '--watchdog' in sys.argv:
        watchdog()
    else:
        raise SystemExit(main())
