"""Read-only PR evidence collection for the approved integration follow-up."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'evidence'
REPO = 'iamcxa/kc-claude-plugins'
HEAD = '1d5139568122a3af97cbc28333171df3bc2e27be'
MAIN = '1d4e95e0f38e53b525a0c7c272d0d55f0b37ddd2'

def gh(*args):
    return json.loads(subprocess.check_output(['gh', *args], timeout=30))

def save(name, value):
    path = OUT / name
    assert not path.exists(), 'Preserve previous evidence'
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

fields = 'author,headRefOid,isDraft,number,state,url,body,baseRefOid,baseRefName,statusCheckRollup'
before = gh('pr', 'view', '390', '--repo', REPO, '--json', fields)
assert before['headRefOid'] == HEAD and before['state'] == 'OPEN' and before['isDraft']
query = '''query($owner: String!, $name: String!, $number: Int!) {
 repository(owner: $owner, name: $name) { pullRequest(number: $number) {
 number headRefOid author { login }
 reviewThreads(first: 100) { pageInfo { hasNextPage endCursor } nodes {
 id isResolved comments(first: 100) { pageInfo { hasNextPage endCursor } nodes {
 id author { login } body commit { oid }
 } } } }
 } } }'''
threads = gh('api', 'graphql', '-f', 'query=' + query, '-F', 'owner=iamcxa',
             '-F', 'name=kc-claude-plugins', '-F', 'number=390')
pr = threads['data']['repository']['pullRequest']
assert pr['headRefOid'] == HEAD and not pr['reviewThreads']['pageInfo']['hasNextPage']
assert not pr['reviewThreads']['nodes'], 'New feedback requires full disposition before closing'
reviews = gh('api', '--paginate', '--slurp', f'repos/{REPO}/pulls/390/reviews?per_page=100')
assert all(isinstance(page, list) and not page for page in reviews), 'New review needs disposition'
after = gh('pr', 'view', '390', '--repo', REPO, '--json', fields)
assert before == after, 'PR changed during evidence observation'
save('pr-before.json', before)
save('pr-feedback-threads.json', threads)
save('pr-feedback-reviews.json', reviews)
save('pr-after.json', after)
population = {'scheme': 'github-pr-feedback/v1', 'repository': REPO, 'pr_number': 390,
              'stack_layer': 'single', 'head_sha': HEAD, 'items': []}
fingerprint = hashlib.sha256(json.dumps(population, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
save('feedback-observation.json', {**population, 'fingerprint': 'sha256:' + fingerprint,
                                  'dispositions': [], 'complete': True})
for run_id in ('34050891104', '34050891148'):
    run = gh('api', f'repos/{REPO}/actions/runs/{run_id}')
    save('ci-' + run_id + '.json', {k: run[k] for k in
        ('id', 'event', 'head_sha', 'head_branch', 'conclusion', 'run_started_at', 'updated_at', 'html_url', 'path')})
code = ROOT / 'checkout'
overlap = []
for label, left in [('pr390-pr321', HEAD), ('main-pr321', MAIN)]:
    command = ['git', '-C', str(code), 'merge-tree', '--write-tree', left,
               'abbe926929af915c2bbb8bb243eca0f6e3ac11f2']
    result = subprocess.run(command, capture_output=True, text=True, timeout=30)
    assert result.returncode == 1 and 'CONFLICT' in result.stdout
    (OUT / (label + '.log')).write_text(result.stdout + result.stderr)
    overlap.append({'label': label, 'command': command, 'exit': result.returncode,
                    'scope': 'Read-only conflict probe; no merge, retarget or changes to PR 321'})
save('overlap.json', overlap)
print('PR head stable; zero review threads/reviews; both overlap probes preserve the existing PR 321 conflicts')
