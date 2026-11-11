import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
WT = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-worker-push-words-match-state-commit')
QNOW = Path('/Users/kent/conductor/repos/qnow-adopt-dev2')
STATE = QNOW / 'docs/dev2/.spacedock-state'
SD = '/Users/kent/.local/bin/spacedock'
commands = []

def run(args, cwd=None):
    p = subprocess.run([str(x) for x in args], cwd=cwd, text=True, capture_output=True)
    commands.append({'args': [str(x) for x in args], 'exit': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr})
    (ROOT / 'replay-prepare-commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    if p.returncode:
        raise RuntimeError(commands[-1])
    return p.stdout.strip()

def git(repo, *args):
    return run(['git', '-C', repo, *args])

def resume_resolved_build(run_dir, readme_file, package_ref, case, state_src, code_src, checklist_file, scope_file):
    pkg = run_dir / 'package/kc-dev-flow-2'
    base = run_dir / 'base.md'
    p = subprocess.run(['git', 'merge-file', '-p', str(readme_file), str(base), str(pkg / 'references/sd/workflow.md')],
                       capture_output=True, text=True)
    assert p.returncode == 1, p.stderr
    unresolved = p.stdout
    lines = unresolved.splitlines(keepends=True)
    resolved = []; i = 0; config = True; delimiters = 0
    while i < len(lines):
        if lines[i].strip() == '---':
            delimiters += 1
            config = delimiters < 2
        if lines[i].startswith('<<<<<<< '):
            assert config, 'STOP: conflict outside adopter frontmatter'
            i += 1; ours = []
            while not lines[i].startswith('======='): ours.append(lines[i]); i += 1
            i += 1
            while not lines[i].startswith('>>>>>>> '): i += 1
            assert all(line.startswith(('extensions:', 'second-reviewer:')) for line in ours), ours
            resolved.extend(ours)
        else:
            resolved.append(lines[i])
        i += 1
    resolved = ''.join(resolved)
    assert resolved.split('## Dispatch facts', 1)[1] == unresolved.split('## Dispatch facts', 1)[1]
    (run_dir / 'README-unresolved.md').write_text(unresolved)
    (run_dir / 'README-resolved.md').write_text(resolved)
    diff = subprocess.run(['git', 'diff', '--no-index', '--', str(run_dir / 'README-unresolved.md'), str(run_dir / 'README-resolved.md')],
                          capture_output=True, text=True)
    (run_dir / 'README-resolution.diff').write_text(diff.stdout)
    wf = run_dir / 'wf'; (wf / 'README.md').write_text(resolved)
    state = wf / '.spacedock-state'; code = run_dir / 'code'
    (run_dir / 'replay.json').write_text(json.dumps(dict(state_repo=str(state_src), state=str(state), code_repo=str(code_src), code=str(code))))
    git(state_src, 'worktree', 'add', '--detach', state, case['state'])
    git(code_src, 'worktree', 'add', '--detach', code, case['code'])
    (wf / '.worktrees').mkdir()
    (wf / '.worktrees' / ('spacedock-ensign-' + case['slug'])).symlink_to(code)
    # Resume the unchanged helper after its refused merge using the authorized resolved input.
    import runpy
    helper = runpy.run_path(str(ROOT / 'replay_dispatch_scratch.py'))
    scope = [f'Package root: {pkg}', scope_file.read_text().strip(),
             helper['HARNESS'].format(pkg=pkg, stage=case['stage'], state=state)]
    (run_dir / 'scope.txt').write_text('\n'.join(scope) + '\n')
    shutil.copy(checklist_file, run_dir / 'checklist.txt')
    task = state / (case['slug'] + '.md')
    output = run([SD, 'dispatch', 'build', '--workflow-dir', wf, '--entity-path', task, '--stage', case['stage'],
                  '--checklist-file', run_dir / 'checklist.txt', '--scope-notes-file', run_dir / 'scope.txt'])
    shutil.copy(json.loads(output)['dispatch_file_path'], run_dir / 'dispatch.md')

def main():
    refs = {}
    for name in ['code', 'state']:
        refs[name] = (ROOT / ('qnow-' + name + '-refs-before.txt')).read_text().strip()
        assert refs[name], name
    (ROOT / 'qnow-refs-before.json').write_text(json.dumps(refs, indent=2) + '\n')
    source = (WT / 'kc-dev-flow-2/scripts/replay_dispatch.py').read_text()
    old = 'Do not push, merge or commit to any remote.'
    assert source.count(old) == 1
    helper = ROOT / 'replay_dispatch_scratch.py'
    helper.write_text(source.replace(old, "The state checkout's origin is a disposable bare repository; push nothing else."))
    cases = [
        dict(stage='implementation', slug='pending-booking-cap', state='d0270c05af744bc7055fbbef7992bcc7269387e2',
             code='a8793b938deb12ff4d599a427998c28b4fe080f1', base='a8793b938deb12ff4d599a427998c28b4fe080f1',
             readme='a8793b938deb12ff4d599a427998c28b4fe080f1', model='gpt-6.1-sol'),
        dict(stage='validation', slug='owner-cancels-booking', state='17ff37c875ab3a1a33bf0462bd6d815b7d616fae',
             code='32901fe5f34fb17ae9a5741cff88471d55e81288', base='706b01fdb04b5d0b17b213562296dc95eaa60368',
             readme='429b4673e0cff4088adf5ee75db64830de441917', model='gpt-6-astra')]
    manifest = json.loads((ROOT / 'replay-manifest.json').read_text()) if (ROOT / 'replay-manifest.json').exists() else []
    for case in cases:
        for arm in ['release', 'candidate-1', 'candidate-2']:
            name = 'replay-' + case['stage'] + '-' + arm
            if any(Path(m['run']).name == name for m in manifest): continue
            run_dir = ROOT / name
            sources = ROOT / (name + '-sources'); sources.mkdir(exist_ok=True)
            state_src = sources / 'state.git'; code_src = sources / 'code.git'
            state_remote = sources / 'state-remote.git'; code_remote = sources / 'code-remote.git'
            for original, src, remote in [(STATE, state_src, state_remote), (QNOW, code_src, code_remote)]:
                if src.exists(): continue
                run(['git', 'clone', '--bare', '--shared', original, src])
                git(src, 'remote', 'remove', 'origin')
                run(['git', 'init', '--bare', '--initial-branch=main', remote])
                git(src, 'remote', 'add', 'origin', remote)
            git(code_src, 'push', 'origin', case['base'] + ':refs/heads/main')
            git(code_src, 'fetch', 'origin')
            readme = git(code_src, 'show', case['readme'] + ':docs/dev2/README.md') + '\n'
            readme_file = sources / 'README.md'; readme_file.write_text(readme)
            match = re.search(r'<!-- kc-dev-flow-2 ([0-9.]+)', readme)
            assert match, readme[:300]
            readme_base = 'kc-dev-flow-2-v' + match[1]
            record = (ROOT / (case['stage'] + '-record.md')).read_text()
            checklist = record.split('## Checklist\n', 1)[1].split('## Scope notes\n', 1)[0].strip() + '\n'
            checklist_file = sources / 'checklist.md'; checklist_file.write_text(checklist)
            scope = record.split('## Scope notes\n', 1)[1]
            wf = run_dir / 'wf'
            scope = re.sub(r'(--workflow-dir[ \t]+)\S+', lambda m: m[1] + str(wf) + ('.' if m[0].endswith('.') else ''), scope)
            scope_file = sources / 'scope.md'; scope_file.write_text(scope)
            package_ref = 'kc-dev-flow-2-v0.38.1' if arm == 'release' else '2c499dab7'
            if run_dir.exists(): run(['python3', '-B', helper, 'cleanup', '--run-dir', run_dir])
            try:
                run(['python3', '-B', helper, 'build', '--run-dir', run_dir, '--package-repo', WT,
                     '--package-ref', package_ref, '--adopter-readme', readme_file,
                     '--readme-base-ref', readme_base, '--state-repo', state_src, '--state-commit', case['state'],
                     '--task', case['slug'], '--code-repo', code_src, '--code-commit', case['code'],
                     '--stage', case['stage'], '--checklist', checklist_file, '--scope', scope_file,
                     '--no-completion-line', '--spacedock', SD])
            except RuntimeError:
                assert commands[-1]['stdout'].strip() == 'replay_dispatch: README merge conflicted; the adopter README is not from --readme-base-ref'
                resume_resolved_build(run_dir, readme_file, package_ref, case, state_src, code_src, checklist_file, scope_file)
            state = wf / '.spacedock-state'; code = run_dir / 'code'
            git(state, 'switch', '-C', 'spacedock-state/wf', case['state'])
            git(state, 'push', 'origin', 'HEAD')
            git(code, 'switch', '-C', 'spacedock-ensign/' + case['slug'], case['code'])
            # Ignore only the generated scratch workflow linkage in the disposable code clone.
            gitdir = Path(git(code, 'rev-parse', '--git-common-dir'))
            if not gitdir.is_absolute(): gitdir = (code / gitdir).resolve()
            (gitdir / 'info').mkdir(exist_ok=True)
            with (gitdir / 'info/exclude').open('a') as f: f.write('\n/docs/dev2/.spacedock-state\n')
            meta = dict(case, arm=arm, run=str(run_dir), state_path=str(state), code_path=str(code),
                        remote=str(state_remote), package_ref=package_ref, readme_base=readme_base,
                        before=git(state_remote, 'for-each-ref', '--format=%(refname) %(objectname)'),
                        code_remote_before=git(code_remote, 'for-each-ref', '--format=%(refname) %(objectname)'))
            manifest.append(meta)
            (ROOT / 'replay-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
            print(name, readme_base, state, flush=True)

main()
