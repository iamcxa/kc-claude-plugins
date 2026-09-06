import argparse
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import time
import uuid

ROOT = Path(__file__).resolve().parent
SOURCE = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/kc-pr-review-capability-pilot')
IMAGE = 'sha256:10ca2cfc3a29b70e13fe0a2a9244fe7e5d24fbd7350ac4205028335c9541f926'
spec = importlib.util.spec_from_file_location('core', SOURCE / 'kc-pr-flow/scripts/review-ablation-core.py')
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)
outcomes = []


def docker(*args):
    return subprocess.run(['docker', *args], capture_output=True, text=True, timeout=10)


def admit(work):
    for path in work.rglob('*'):
        if path.is_symlink() or (path.is_file() and path.stat().st_nlink != 1):
            raise ValueError('mounted input alias: ' + path.name)


def cleanup(cidfile, label):
    assert cidfile.exists(), 'container identity was not recorded'
    cid = cidfile.read_text().strip()
    assert len(cid) == 64 and all(c in '0123456789abcdef' for c in cid)
    before = docker('container', 'inspect', cid)
    result = {'cid': cid, 'label': label, 'inspect_before_exit': before.returncode}
    if before.returncode == 0:
        item = json.loads(before.stdout)[0]
        assert item['Id'] == cid and item['Config']['Labels'].get('pilot-proof') == label
        result['before_state'] = item['State']['Status']
        result['mounts'] = item['Mounts']
        result['host_config'] = {key: item['HostConfig'].get(key) for key in (
            'ReadonlyRootfs', 'CapDrop', 'SecurityOpt', 'NetworkMode', 'PidMode', 'IpcMode',
            'Tmpfs', 'PidsLimit', 'Memory', 'NanoCpus', 'Privileged')}
        removed = docker('container', 'rm', '--force', cid)
        result['force_remove_exit'] = removed.returncode
        if removed.returncode:
            assert 'No such container' in removed.stderr, removed.stderr
    else:
        assert ('No such object' in before.stderr or 'No such container' in before.stderr), before.stderr
    after = docker('container', 'inspect', cid)
    assert after.returncode != 0 and ('No such object' in after.stderr or 'No such container' in after.stderr), after.stdout + after.stderr
    remaining = docker('container', 'ls', '--all', '--quiet', '--filter', 'label=pilot-proof=' + label)
    assert remaining.returncode == 0 and not remaining.stdout.strip(), remaining.stdout + remaining.stderr
    result.update(inspect_after_exit=after.returncode, inspect_after_stderr=after.stderr, exact_label_remaining=remaining.stdout.strip())
    return result


def exercise(mode):
    base = ROOT / ('container-v2-' + mode)
    base.mkdir()
    root, work = base / 'owner', base / 'work'
    root.mkdir()
    work.mkdir(mode=0o777)
    work.chmod(0o777)
    rows = [{'slot': n, 'role': 'primary' if n < 6 else 'backup', 'repository': 'acme/widgets', 'pr_number': n,
             'base_sha': 'a' * 40, 'head_sha': 'b' * 40, 'control_modes': core.PILOT_MODES,
             'treatment_modes': core.PILOT_MODES} for n in range(1, 7)]
    fixture = (SOURCE / 'kc-pr-flow/scripts/review-ablation.test.sh').read_text()
    setup = fixture[fixture.index('runs = root / "pilot-runs"'):fixture.index('joined = core.pilot_join(runs, rows, None)')]
    scope = dict(root=root, rows=rows, core=core, copy=copy, json=json)
    exec(compile(setup, 'existing-pilot-fixture-setup', 'exec'), scope)
    runs = scope['runs']
    current, prior = runs / '1-control', runs / '2-control/receipt.json'
    receipt = core.pilot_read(current / 'receipt.json')
    manifest = core.pilot_read(current / 'manifest.json')
    (current / 'receipt.json').unlink()
    before = prior.read_bytes()
    prior.chmod(0o400)
    (root / 'sentinel').write_text('parent')
    (root / 'empty').mkdir()
    (work / 'input.json').write_text(json.dumps({'owner': str(root), 'mode': mode, 'planted': {**receipt, 'wallclock_ms': 1}}))
    (work / 'child.py').write_bytes((ROOT / 'container-child.py').read_bytes())
    if mode in ('hardlink', 'symlink'):
        if mode == 'hardlink':
            os.link(prior, work / 'alias')
        else:
            (work / 'alias').symlink_to(prior)
        try:
            admit(work)
        except ValueError as error:
            return {'mode': mode, 'prelaunch_refused': str(error), 'launched': False, 'prior_unchanged': before == prior.read_bytes()}
        raise AssertionError('alias admitted')
    admit(work)
    label = 't8cyxd55ve-' + uuid.uuid4().hex
    cidfile = root / 'container.cid'
    command = ['docker', 'run', '--pull=never', '--rm', '--init', '--read-only', '--cap-drop=ALL',
        '--security-opt=no-new-privileges', '--ipc=private', '--network=none', '--user=65534:65534',
        '--pids-limit=32', '--memory=256m', '--cpus=1', '--no-healthcheck', '--stop-timeout=1',
        '--tmpfs=/tmp:rw,nosuid,nodev,size=16m', '--mount=type=bind,source=' + str(work) + ',target=/work',
        '--workdir=/work', '--cidfile=' + str(cidfile), '--label=pilot-proof=' + label,
        '--entrypoint=/bin/bash', IMAGE, '-c', 'command -v python3 >&2 && exec python3 -B /work/child.py']
    cleanup_result = None

    def operation():
        nonlocal cleanup_result
        try:
            _, elapsed = core.pilot_invoke(argparse.Namespace(timeout=4 if mode == 'timeout' else 20), current, command, work, os.environ.copy())
        finally:
            cleanup_result = cleanup(cidfile, label)
        return core.pilot_write(current / 'receipt.json', {**receipt, 'wallclock_ms': elapsed})

    try:
        core.pilot_attempt(manifest, current, operation)
        terminal = 'success'
    except (Exception, SystemExit) as error:
        terminal = type(error).__name__ + ': ' + str(error)
    result = {'mode': mode, 'command': command, 'terminal': terminal, 'cleanup': cleanup_result,
              'prior_unchanged': prior.read_bytes() == before,
              'sentinel_unchanged': (root / 'sentinel').read_text() == 'parent',
              'current_receipt': core.pilot_read(current / 'receipt.json'),
              'host_output': core.pilot_read(current / 'host-output.json')}
    for name in ('child', 'descendant'):
        path = work / (name + '.json')
        result[name] = json.loads(path.read_text()) if path.exists() else None
    try:
        joined = core.pilot_join(runs, rows, None)
        result['joined_count'] = len(joined)
        result['joined_wallclock_ms'] = {str(r['manifest']['slot']) + '-' + r['manifest']['arm']: r['receipt']['wallclock_ms'] for r in joined}
    except (Exception, SystemExit) as error:
        result['join_refusal'] = type(error).__name__ + ': ' + str(error)
    return result


started = time.monotonic()
try:
    for mode in ('hardlink', 'symlink', 'normal', 'failure', 'timeout'):
        result = exercise(mode)
        outcomes.append(result)
        print(json.dumps(result), flush=True)
        if 'prelaunch_refused' in result:
            assert not result['launched'] and result['prior_unchanged']
            continue
        assert result['child'] and result['descendant'], 'child tools or descendant unavailable'
        assert result['child']['uid'] == 65534 and not result['child']['credential_env_present']
        assert result['child']['descendant_alive_at_observation']
        assert not result['descendant']['write_allowed']
        assert result['prior_unchanged'] and result['sentinel_unchanged']
        assert result['cleanup']['exact_label_remaining'] == ''
        for check in result['child']['checks']:
            assert check['write_allowed'] == (check['case'] in ('workspace-write', 'output-write', 'temp-write')), check
        if mode == 'normal':
            assert result['terminal'] == 'success' and result['joined_count'] == 10
            assert result['joined_wallclock_ms']['2-control'] == 100
            assert result['joined_wallclock_ms']['1-control'] != 1
        else:
            assert result['current_receipt']['cost_status'] == 'incomplete' and 'join_refusal' in result
            assert result['current_receipt']['run_terminal']['reason'] == 'attempt_failed'
    print('CONTAINER FILESYSTEM AND LIFECYCLE PASS (5 cases)', flush=True)
finally:
    (ROOT / 'container-v2-results.json').write_text(json.dumps({'elapsed_seconds': time.monotonic() - started, 'outcomes': outcomes}, indent=2) + '\n')
