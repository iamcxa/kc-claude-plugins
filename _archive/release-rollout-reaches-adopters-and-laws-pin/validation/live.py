import base64
import datetime
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import quote

root = Path('/tmp/rollout-validation-838')
out = root / 'evidence'
candidate = root / 'candidate'
listing = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/fo-scripts/adopters.md')
state = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
head = '61529999eb4184b44328fe2fbad545b1b0b0ed92'

def api(endpoint):
    p = subprocess.run(['gh', 'api', endpoint], capture_output=True, text=True)
    return p.returncode, json.loads(p.stdout) if p.returncode == 0 else None, p.stderr

def content(repo, path, ref):
    code, data, err = api(f'repos/{repo}/contents/{path}?ref={quote(ref, safe="")}')
    return code, base64.b64decode(data['content']).decode() if code == 0 else '', err

preflight = subprocess.check_output(['git', '-C', str(state), 'grep', '-I', '-h', '-e', '.', 'HEAD', '--', '*.md'])
rows = [r.split('#', 1)[0].strip().split() for r in listing.read_text().splitlines() if r.split('#', 1)[0].strip()]
approved_names = {'kc-claude-plugins', 'qnow', 'me-company', 'subspace-relay', 'subspace-web', 'subspace-v0'}
assert len(rows) == 11
assert all(len(r) == 2 and r[0].split('/')[0] in {'iamcxa', 'spacedock-dev'}
           and r[0].split('/')[1] in approved_names
           and r[0].split('/')[1].encode() in preflight and r[1].encode() in preflight for r in rows)
cmd = ['python3', '-B', str(candidate / 'kc-dev-flow-2/scripts/package_version.py'), 'rollout', str(listing)]
run = subprocess.run(cmd, capture_output=True, text=True)
lines = run.stdout.splitlines()
listed = [x for x in lines if not x.startswith(('unlisted:', 'search:', 'rollout:'))]
summary = {'candidate': head, 'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'listed': len(listed), 'unlisted': sum(x.startswith('unlisted:') for x in lines),
           'unreadable': sum('unreadable:' in x for x in listed),
           'sync_owed': sum(bool(re.search(r' released:\S+ sync owed;', x)) for x in listed),
           'pin_owed': sum(bool(re.search(r'laws: \S+ pin owed', x)) or 'pin unrecognised' in x for x in listed),
           'search_unavailable': sum(x.startswith('search: unavailable') for x in lines),
           'stderr_lines': len(run.stderr.splitlines()), 'exit': run.returncode}
(out / 'live-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
assert len(listed) == len([x for x in listing.read_text().splitlines() if x.split('#', 1)[0].strip()])
assert run.returncode == 0 and summary['unreadable'] == 0, summary

checks = []
for repo in ['iamcxa/kc-claude-plugins', 'iamcxa/qnow']:
    code, readme, _ = content(repo, 'docs/dev2/README.md', 'main')
    assert code == 0
    version = re.search(r'kc-dev-flow-2 (\d+\.\d+\.\d+) x-release-please-version', readme)[1]
    code, laws, err = content(repo, '.github/workflows/dev2-laws.yml', 'spacedock-state/dev2')
    pin = re.search(r'^\s*ref:\s*[\"\']?([0-9a-f]{40})', laws, re.M)[1] if code == 0 else None
    if pin is None:
        assert 'HTTP 404' in err
        assert api(f'repos/{repo}/branches/spacedock-state%2Fdev2')[0] == 0
    line = next(x for x in listed if x.startswith(repo + ' docs/dev2 '))
    def matches(value):
        return f'README:{version} ' in value and (f'laws: {pin} ' in value if pin else 'laws: not installed' in value)
    assert matches(line)
    assert not matches(line.replace(f'README:{version}', 'README:9.9.9'))
    if pin:
        assert not matches(line.replace(pin, 'f' * 40))
    checks.append({'repository': repo, 'workflow': 'docs/dev2', 'readme_release': version,
                   'pin': pin, 'matches': True, 'changed_release_rejected': True,
                   'changed_pin_rejected': True if pin else 'not installed'})
(out / 'live-hand-checks.json').write_text(json.dumps(checks, indent=2) + '\n')

state_sha = subprocess.check_output(['git', '-C', str(state), 'rev-parse', 'HEAD'], text=True).strip()
state_bytes = subprocess.check_output(['git', '-C', str(state), 'grep', '-I', '-h', '-e', '.', state_sha, '--', '*.md'])
discovered = {x.split()[1] for x in lines if x.startswith('unlisted:')}
private = [x.encode() for x in discovered if x.encode() not in state_bytes]
leaks = []
for folder in [candidate, out]:
    for file in folder.rglob('*'):
        if file.is_file() and '__pycache__' not in str(file):
            data = file.read_bytes()
            if any(x in data or x.split(b'/', 1)[1] in data for x in private):
                leaks.append(str(file.relative_to(root)))
assert not leaks, 'privacy leak paths: ' + repr(leaks)
(out / 'privacy.json').write_text(json.dumps({'state_sha': state_sha, 'private_discovered_count': len(private),
    'candidate_and_evidence_matches': len(leaks), 'raw_live_output_saved': False,
    'list_copied': False}, indent=2) + '\n')
print(json.dumps(summary))
print('two independent hand reads match; altered release/pin rejected; privacy scan passed')
