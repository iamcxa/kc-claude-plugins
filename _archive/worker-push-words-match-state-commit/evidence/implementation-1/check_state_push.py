import json
from pathlib import Path
import subprocess
import tempfile

OUT = Path(__file__).resolve().parent
SD = '/Users/kent/.local/bin/spacedock'
LOG = []

def run(args, cwd=None):
    p = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    LOG.append({'args': args, 'cwd': str(cwd) if cwd else None, 'exit': p.returncode,
                'stdout': p.stdout, 'stderr': p.stderr})
    if p.returncode:
        raise RuntimeError(LOG[-1])
    return p.stdout

def git(repo, *args):
    return run(['git', '-C', str(repo), *args])

def refs(repo):
    return dict(line.split(' ', 1) for line in git(repo, 'for-each-ref', '--format=%(refname) %(objectname)').splitlines())

def assert_push(before, after, branch, head):
    changed = {ref for ref in before.keys() | after.keys() if before.get(ref) != after.get(ref)}
    assert changed == {branch}, changed
    assert after[branch] == head

def main():
    root = Path(tempfile.mkdtemp(prefix='state-push-proof-', dir=OUT))
    code = root / 'code'; code.mkdir()
    git(code, 'init', '-b', 'main')
    (code / 'tracked').write_text('fixture\n')
    git(code, 'add', 'tracked'); git(code, '-c', 'user.name=replay', '-c', 'user.email=replay@localhost', 'commit', '-m', 'fixture')
    wf = code / 'docs' / 'proof'; wf.mkdir(parents=True)
    (wf / 'README.md').write_text('''---
entity-type: task
id-style: slug
state: .spacedock-state
stages:
  states:
    - name: implementation
      initial: true
    - name: done
      terminal: true
---
\n# Replay\n''')
    state = wf / '.spacedock-state'; state.mkdir()
    git(state, 'init', '-b', 'spacedock-state/proof')
    task = state / 'sample.md'
    task.write_text('---\ntitle: Sample\nstatus: implementation\n---\n\n## Scope\n\nScratch.\n')
    git(state, 'add', 'sample.md'); git(state, '-c', 'user.name=replay', '-c', 'user.email=replay@localhost', 'commit', '-m', 'fixture')
    remote = root / 'remote.git'; run(['git', 'init', '--bare', str(remote)])
    git(state, 'remote', 'add', 'origin', str(remote)); git(state, 'push', 'origin', 'HEAD')
    before = refs(remote)
    task.write_text(task.read_text() + '\n## Stage Report: implementation\n\n- DONE: report\n  scratch\n\n### Summary\n\nScratch.\n')
    pushed = run([SD, 'state', 'commit', 'sample', '--workflow-dir', str(wf), '-m', 'proof: report'])
    assert 'Committed and pushed' in pushed, pushed
    head = git(state, 'rev-parse', 'HEAD').strip(); after = refs(remote)
    assert_push(before, after, 'refs/heads/spacedock-state/proof', head)
    git(remote, 'update-ref', 'refs/heads/unexpected', head)
    try:
        assert_push(before, refs(remote), 'refs/heads/spacedock-state/proof', head)
    except AssertionError:
        extra_ref_caught = True
    else:
        raise AssertionError('extra-ref mutation escaped')
    git(state, 'remote', 'remove', 'origin')
    task.write_text(task.read_text() + '\nLocal-only change.\n')
    local = run([SD, 'state', 'commit', 'sample', '--workflow-dir', str(wf), '-m', 'proof: local'])
    assert 'local-only' in local, local
    local_head = git(state, 'rev-parse', 'HEAD').strip()
    try:
        assert_push(after, after, 'refs/heads/spacedock-state/proof', local_head)
    except AssertionError:
        no_push_caught = True
    else:
        raise AssertionError('no-push mutation escaped')
    result = {'root': str(root), 'before': before, 'after': after, 'pushed_head': head,
              'local_head': local_head, 'published_output': pushed, 'local_only_output': local,
              'extra_ref_mutation_caught': extra_ref_caught, 'no_push_mutation_caught': no_push_caught}
    (OUT / 'state-push.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

try:
    main()
finally:
    (OUT / 'state-push-commands.json').write_text(json.dumps(LOG, indent=2) + '\n')
