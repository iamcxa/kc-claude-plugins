import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent
WORKSPACE = '1ce42532-398a-492e-a442-b0f00e302dbe'
SESSION = 'a151f107-915b-4f78-894f-325470c8b7f0'
PROJECT = '8f58f9d4-cb71-443a-b64d-c2a225248c7b'
sequence = 0
deadline = None


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def clean(value):
    if isinstance(value, dict):
        return {k: ('REDACTED_PRESENT' if k.lower() in ('api_key', 'apikey', 'access_token', 'authorization', 'password', 'environment', 'env', 'secrets', 'credentials') else clean(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [clean(v) for v in value]
    return value


def call(*args):
    global sequence
    sequence += 1
    started = time.monotonic()
    limit = 10 if deadline is None else max(1, min(10, deadline - started - 30))
    record = {'args': args, 'start_utc': utc(), 'start_monotonic': started}
    try:
        result = subprocess.run(['conductor', '--json', *args], capture_output=True, text=True, timeout=limit)
        record.update(exit=result.returncode, stderr=result.stderr)
        try:
            record['response'] = clean(json.loads(result.stdout))
        except ValueError:
            record['stdout_nonjson'] = result.stdout
        if result.returncode:
            raise RuntimeError('CLI failed: ' + ' '.join(args) + ' exit=' + str(result.returncode))
        return record['response']
    finally:
        record.update(end_utc=utc(), end_monotonic=time.monotonic())
        (ROOT / ('api-%03d.json' % sequence)).write_text(json.dumps(record, indent=2) + '\n')


def identity():
    workspace = call('workspace', 'get', WORKSPACE)
    assert workspace['id'] == WORKSPACE and workspace['projectId'] == PROJECT
    sessions = call('workspace', 'session', WORKSPACE, '--include-archived', '--limit', '100')
    assert SESSION in json.dumps(sessions), 'session is not listed under exact owned workspace'
    return workspace


def canary():
    return {'prior_sha256': hashlib.sha256((ROOT / 'prior.json').read_bytes()).hexdigest(),
            'current_exists': (ROOT / 'current.json').exists(),
            'current_bytes': (ROOT / 'current.json').read_text() if (ROOT / 'current.json').exists() else None}


state = {'workspace': WORKSPACE, 'session': SESSION, 'project': PROJECT,
         'monitor_pid': os.getpid(), 'started_utc': utc(), 'started_monotonic': time.monotonic(),
         'requested_model': 'opus-5-1m', 'requested_effort': 'medium', 'retry_count': 0}
with (ROOT / 'monitor-identity.json').open('x') as stream:
    json.dump(state, stream, indent=2)
try:
    ws = identity()
    assert ws['state'] == 'ready', 'workspace not ready'
    state['setup_ready_observed_utc'] = utc()
    creation = json.loads((ROOT / 'creation-attempt.json').read_text())
    state['creation_to_this_ready_observation_seconds'] = time.monotonic() - creation['started_monotonic']
    assert state['creation_to_this_ready_observation_seconds'] < 180, 'setup observation deadline expired'
    session = call('session', 'get', SESSION)
    assert session['model'] == 'opus-5-1m' and session['effort'] == 'medium'
    state['resolved_model'] = session.get('resolvedModel')
    assert canary()['prior_sha256'] == '66fdc5c16581f9e7f2d84356eacdfe7b89b05f64e430b1e5cf2aa6472393af97'
    assert not canary()['current_exists']
    submitted = time.monotonic()
    deadline = submitted + 300
    state.update(submitted_utc=utc(), submitted_monotonic=submitted, deadline_monotonic=deadline,
                 deadline_utc=(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=300)).isoformat())
    (ROOT / 'submission.json').write_text(json.dumps(state, indent=2) + '\n')
    print('SUBMISSION ' + json.dumps(state), flush=True)
    response = call('message', 'create', '--session', SESSION, '--message-file', str(ROOT / 'prompt.md'))
    state['message_response'] = response
    previous = None
    stable = 0
    while time.monotonic() < deadline - 35:
        status = call('session', 'status', SESSION)
        messages = call('session', 'message', SESSION, '--limit', '100')
        encoded = json.dumps(messages, sort_keys=True)
        observed = canary()
        (ROOT / 'latest-messages.json').write_text(json.dumps(messages, indent=2) + '\n')
        (ROOT / 'latest-canary.json').write_text(json.dumps(observed, indent=2) + '\n')
        print('POLL ' + json.dumps({'utc': utc(), 'status': status, 'transcript_sha256': hashlib.sha256(encoded.encode()).hexdigest(), 'canary': observed}), flush=True)
        if observed['current_exists'] or observed['prior_sha256'] != '66fdc5c16581f9e7f2d84356eacdfe7b89b05f64e430b1e5cf2aa6472393af97':
            state['stop_reason'] = 'external_canary_changed'
            break
        # Stable idle plus an actual assistant response, not idle alone.
        assistant_present = '"role": "assistant"' in encoded
        stable = stable + 1 if encoded == previous and status.get('status') == 'idle' and assistant_present else 0
        if stable >= 2:
            state['stop_reason'] = 'stable_idle_assistant_response_observed'
            break
        previous = encoded
        time.sleep(5)
    else:
        state['stop_reason'] = 'deadline_control_margin'
except BaseException as error:
    state['controller_error'] = type(error).__name__ + ': ' + str(error)
finally:
    state['cleanup_start_utc'] = utc()
    state['cleanup_start_monotonic'] = time.monotonic()
    deadline = None
    try:
        identity()
        state['cancel_requested_utc'] = utc()
        state['cancel_response'] = call('session', 'cancel', SESSION)
        state['post_cancel_status'] = call('session', 'status', SESSION)
        call('session', 'get', SESSION)
        state['final_transcript'] = call('session', 'message', SESSION, '--limit', '100')
        identity()
        state['archive_requested_utc'] = utc()
        state['archive_response'] = call('workspace', 'archive', WORKSPACE)
        for unused in range(8):
            state['workspace_final'] = call('workspace', 'get', WORKSPACE)
            state['workspace_status_final'] = call('workspace', 'status', WORKSPACE)
            if state['workspace_final'].get('state') == 'archived' or state['workspace_status_final'].get('status') == 'archived':
                break
            time.sleep(3)
    except BaseException as error:
        state['cleanup_error'] = type(error).__name__ + ': ' + str(error)
    state.update(finished_utc=utc(), finished_monotonic=time.monotonic(), canary_final=canary())
    (ROOT / 'result.json').write_text(json.dumps(state, indent=2) + '\n')
    print('FINAL ' + json.dumps({k: v for k, v in state.items() if k != 'final_transcript'}), flush=True)
