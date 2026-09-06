import argparse
import copy
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent
SOURCE = pathlib.Path('/Users/kent/conductor/workspaces/kc-claude-plugins/kc-pr-review-capability-pilot')


def attempt(label, operation):
    try:
        operation()
        return {'case': label, 'write_allowed': True}
    except OSError as error:
        return {'case': label, 'write_allowed': False, 'errno': error.errno, 'error': str(error)}


def mutate(path):
    path.chmod(0o600)
    value = json.loads(path.read_text())
    value['wallclock_ms'] = 1
    path.write_text(json.dumps(value))


def ancestor_alias(base):
    moved = base.with_name(base.name + '-moved')
    base.rename(moved)
    try:
        mutate(moved / 'owner/pilot-runs/2-control/receipt.json')
    finally:
        moved.rename(base)


def child(base, mode):
    work, output, owner = (base / name for name in ('work', 'output', 'owner'))
    prior = owner / 'pilot-runs/2-control/receipt.json'
    current = owner / 'pilot-runs/1-control/receipt.json'
    checks = [attempt('current-preplant', lambda: current.write_text((work / 'receipt-template.json').read_text()))]
    for label, path in (
        ('prior-absolute-chmod', prior),
        ('prior-traversal', work / '../owner/pilot-runs/2-control/receipt.json'),
        ('prior-symlink', work / 'owner-alias/pilot-runs/2-control/receipt.json'),
    ):
        checks.append(attempt(label, lambda path=path: mutate(path)))
    if (work / 'hardlink-alias.json').exists():
        checks.append(attempt('prior-hardlink', lambda: mutate(work / 'hardlink-alias.json')))
    checks.append(attempt('child-create-hardlink', lambda: os.link(prior, work / 'child-link.json')))
    if (work / 'child-link.json').exists():
        checks.append(attempt('child-hardlink-write', lambda: mutate(work / 'child-link.json')))
    checks.extend([
        attempt('protected-unlink', lambda: (owner / 'unlink-sentinel').unlink()),
        attempt('protected-directory-rename', lambda: (owner / 'rename-target').rename(work / 'moved-owner')),
        attempt('protected-directory-unlink', lambda: (owner / 'empty-target').rmdir()),
        attempt('workspace-write', lambda: (work / 'normal.txt').write_text('normal workspace work')),
        attempt('output-write', lambda: (output / 'normal.txt').write_text('normal output')),
        attempt('temp-write', lambda: pathlib.Path(os.environ['TMPDIR'], 'normal.txt').write_text('normal temp')),
    ])
    if os.environ.get('PROOF_SAFEHOUSE') == '1':
        checks.append(attempt('ancestor-rename-restore', lambda: ancestor_alias(base)))
    nested = subprocess.run(['/bin/bash', '-c', 'echo nested-child'], capture_output=True, text=True)
    assert nested.returncode == 0 and nested.stdout.strip() == 'nested-child'
    assert os.environ['ANTHROPIC_API_KEY'] == 'SYNTHETIC-NOT-A-CREDENTIAL'
    descendant = subprocess.Popen(
        [sys.executable, str(ROOT / 'proof.py'), '--descendant', str(base)],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True, close_fds=True,
    )
    (output / 'child-result.json').write_text(json.dumps({'checks': checks, 'descendant_pid': descendant.pid, 'pid': os.getpid(), 'pgid': os.getpgrp()}))
    if mode == 'timeout':
        time.sleep(10)
    print(json.dumps({'synthetic': True}), flush=True)
    return 7 if mode == 'failure' else 0


def descendant(base):
    output = base / 'output'
    deadline = time.monotonic() + 8
    while not (output / 'parent-finalized').exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    result = attempt('detached-descendant', lambda: (base / 'owner/descendant-sentinel').write_text('forged'))
    result.update(pid=os.getpid(), pgid=os.getpgrp(), observed_parent_finalization=(output / 'parent-finalized').exists())
    (output / 'descendant-result.json').write_text(json.dumps(result))


def load_core():
    spec = importlib.util.spec_from_file_location('core', SOURCE / 'kc-pr-flow/scripts/review-ablation-core.py')
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    return core


def exercise(core, isolated, mode, guarded=False, safehouse=False):
    base = ROOT / (('safehouse-v2' if safehouse else 'guarded' if guarded else 'isolated' if isolated else 'control') + '-' + mode)
    base.mkdir()
    for name in ('work', 'output', 'temp', 'owner'):
        (base / name).mkdir()
    root = base / 'owner'
    rows = [{'slot': n, 'role': 'primary' if n < 6 else 'backup', 'repository': 'acme/widgets', 'pr_number': n,
             'base_sha': 'a' * 40, 'head_sha': 'b' * 40, 'control_modes': core.PILOT_MODES,
             'treatment_modes': core.PILOT_MODES} for n in range(1, 7)]
    fixture = (SOURCE / 'kc-pr-flow/scripts/review-ablation.test.sh').read_text()
    setup = fixture[fixture.index('runs = root / "pilot-runs"'):fixture.index('joined = core.pilot_join(runs, rows, None)')]
    scope = dict(root=root, rows=rows, core=core, copy=copy, json=json)
    exec(compile(setup, 'existing-pilot-fixture-setup', 'exec'), scope)
    runs = scope['runs']
    current = runs / '1-control'
    manifest = core.pilot_read(current / 'manifest.json')
    receipt = core.pilot_read(current / 'receipt.json')
    planted = {**receipt, 'wallclock_ms': 1}
    (base / 'work/receipt-template.json').write_text(json.dumps(planted))
    (current / 'receipt.json').unlink()
    prior = runs / '2-control/receipt.json'
    before_prior = prior.read_bytes()
    prior.chmod(0o400)
    (base / 'work/owner-alias').symlink_to(root, target_is_directory=True)
    if not guarded or mode == 'alias':
        os.link(prior, base / 'work/hardlink-alias.json')
    (root / 'unlink-sentinel').write_text('parent')
    (root / 'descendant-sentinel').write_text('parent')
    (root / 'rename-target').mkdir()
    (root / 'rename-target/record').write_text('parent')
    (root / 'empty-target').mkdir()
    if guarded:
        for path in root.rglob('*'):
            if path.is_symlink() or (path.is_file() and path.stat().st_nlink != 1):
                return {'isolated': isolated, 'mode': mode, 'preflight_refused': 'linked owner file',
                        'launched': False, 'prior_unchanged': prior.read_bytes() == before_prior,
                        'child_marker_absent': not (base / 'output/child-result.json').exists()}
    child_python = str(pathlib.Path(sys.executable).resolve()) if safehouse else sys.executable
    command = ['/bin/bash', '-c', 'exec "$1" "$2" --child "$3" --mode "$4"', 'proof', child_python, str(ROOT / 'proof.py'), str(base), mode]
    if isolated:
        command = ['/usr/bin/sandbox-exec', '-f', str(ROOT / 'proof.sb'),
                   '-D', 'WORK=' + str((base / 'work').resolve()),
                   '-D', 'OUTPUT=' + str((base / 'output').resolve()),
                   '-D', 'TEMP=' + str((base / 'temp').resolve()), *command]
    if safehouse:
        deny = root / 'deny-owner.sb'
        deny.write_text('(deny file-write* (subpath ' + json.dumps(str(root)) + '))\n')
        generation_env = {k: v for k, v in os.environ.items() if not k.startswith('SAFEHOUSE_')}
        generator = ['/opt/homebrew/bin/safehouse', '--workdir=' + str(base / 'work'),
                     '--trust-workdir-config=false', '--append-profile=' + str(deny),
                     '--explain', '--stdout', '--', 'claude', '--version']
        generated = subprocess.run(generator, cwd=base / 'work', env=generation_env,
                                   capture_output=True, text=True, check=True)
        policy = root / 'effective.sb'
        policy.write_text(generated.stdout)
        (root / 'explain.txt').write_text(generated.stderr)
        command = ['/usr/bin/sandbox-exec', '-f', str(policy), *command[9:]]
    args = argparse.Namespace(timeout=1 if mode == 'timeout' else 5)

    def operation():
        _, elapsed = core.pilot_invoke(args, current, command, base / 'work',
            {**os.environ, 'TMPDIR': str(base / 'temp'), 'ANTHROPIC_API_KEY': 'SYNTHETIC-NOT-A-CREDENTIAL',
             'PYTHONDONTWRITEBYTECODE': '1', 'PROOF_SAFEHOUSE': '1' if safehouse else '0'})
        return core.pilot_write(current / 'receipt.json', {**receipt, 'wallclock_ms': elapsed})

    try:
        core.pilot_attempt(manifest, current, operation)
        finalization = 'success'
    except (Exception, SystemExit) as error:
        finalization = type(error).__name__ + ': ' + str(error)
    (base / 'output/parent-finalized').touch()
    deadline = time.monotonic() + 9
    descendant_path = base / 'output/descendant-result.json'
    while not descendant_path.exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    child_path = base / 'output/child-result.json'
    details = json.loads(child_path.read_text()) if child_path.exists() else {}
    detached = json.loads(descendant_path.read_text()) if descendant_path.exists() else {'error': 'descendant did not finish'}
    result = dict(isolated=isolated, mode=mode, command=command, finalization=finalization, child=details,
                  descendant=detached, prior_unchanged=prior.read_bytes() == before_prior,
                  descendant_sentinel_unchanged=(root / 'descendant-sentinel').read_text() == 'parent')
    try:
        joined = core.pilot_join(runs, rows, None)
        result['joined_count'] = len(joined)
        result['joined_wallclock_ms'] = {str(r['manifest']['slot']) + '-' + r['manifest']['arm']: r['receipt']['wallclock_ms'] for r in joined}
    except (Exception, SystemExit) as error:
        result['join_refusal'] = type(error).__name__ + ': ' + str(error)
    if (current / 'receipt.json').exists():
        result['current_receipt'] = core.pilot_read(current / 'receipt.json')
    result['host_output'] = core.pilot_read(current / 'host-output.json') if (current / 'host-output.json').exists() else None
    print(json.dumps(result), flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--child', type=pathlib.Path)
    parser.add_argument('--descendant', type=pathlib.Path)
    parser.add_argument('--mode', default='normal')
    parser.add_argument('--guarded', action='store_true')
    parser.add_argument('--safehouse', action='store_true')
    args = parser.parse_args()
    if args.child:
        sys.exit(child(args.child, args.mode))
    if args.descendant:
        descendant(args.descendant)
    else:
        core = load_core()
        if args.safehouse:
            outcomes = [exercise(core, True, 'normal', True, True)]
            (ROOT / 'safehouse-v2-results.json').write_text(json.dumps(outcomes, indent=2) + '\n')
            assert outcomes[0]['child'].get('checks'), 'CHILD DID NOT EXECUTE'
            assert outcomes[0]['descendant'].get('observed_parent_finalization'), 'DESCENDANT DID NOT EXECUTE'
            assert outcomes[0]['finalization'] == 'success'
            assert outcomes[0]['prior_unchanged'], 'SAFEHOUSE OWNER INTEGRITY FAIL'
            print('SAFEHOUSE FILESYSTEM INSTRUMENT PASS', flush=True)
        elif args.guarded:
            outcomes = [exercise(core, True, mode, True) for mode in ('alias', 'normal', 'failure', 'timeout')]
            (ROOT / 'guarded-results.json').write_text(json.dumps(outcomes, indent=2) + '\n')
            assert outcomes[0]['preflight_refused'] and not outcomes[0]['launched']
            assert outcomes[0]['prior_unchanged'] and outcomes[0]['child_marker_absent']
            for result in outcomes[1:]:
                assert result['prior_unchanged'] and result['descendant_sentinel_unchanged']
                assert result['descendant']['observed_parent_finalization']
                assert result['descendant']['pgid'] != result['child']['pgid']
                assert not result['descendant']['write_allowed']
                for check in result['child']['checks']:
                    normal = check['case'] in ('workspace-write', 'output-write', 'temp-write')
                    assert check['write_allowed'] == normal, check
                    if not normal:
                        assert check['errno'] == 1, check
                if result['mode'] == 'normal':
                    assert result['finalization'] == 'success'
                    assert result['joined_count'] == 10
                    assert result['joined_wallclock_ms']['2-control'] == 100
                    assert result['joined_wallclock_ms']['1-control'] != 1
                else:
                    assert result['current_receipt']['run_terminal']['reason'] == 'attempt_failed'
                    assert result['current_receipt']['cost_status'] == 'incomplete'
                    assert 'join_refusal' in result
            print('GUARDED FILESYSTEM INSTRUMENT PASS (4 cases)', flush=True)
        else:
            outcomes = [exercise(core, False, 'normal')]
            outcomes.extend(exercise(core, True, mode) for mode in ('normal', 'failure', 'timeout'))
            (ROOT / 'results.json').write_text(json.dumps(outcomes, indent=2) + '\n')
