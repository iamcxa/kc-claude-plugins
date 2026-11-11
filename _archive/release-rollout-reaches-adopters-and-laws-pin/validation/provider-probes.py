from pathlib import Path
import json
import subprocess

out = Path('/tmp/rollout-validation-838/evidence')
results = []
for prefix in ['tags/kc-dev-flow-2-v', 'tags/']:
    endpoint = 'repos/iamcxa/kc-claude-plugins/git/matching-refs/' + prefix
    variants = []
    for suffix in ['', '?per_page=1&page=1', '?per_page=1&page=2']:
        p = subprocess.run(['gh', 'api', '--include', endpoint + suffix], capture_output=True, text=True, check=True)
        headers, body = p.stdout.split('\n\n', 1)
        data = json.loads(body)
        variants.append({'suffix': suffix, 'count': len(data), 'link': any(x.lower().startswith('link:') for x in headers.splitlines()), 'refs': sorted(x['ref'] for x in data)})
    assert all(x['refs'] == variants[0]['refs'] for x in variants)
    results.append({'prefix': prefix, 'responses': [{k: v for k, v in x.items() if k != 'refs'} for x in variants], 'sets_equal': True})
    p = subprocess.run(['gh', 'api', '--paginate', endpoint], capture_output=True, text=True, check=True)
    assert sorted(x['ref'] for x in json.loads(p.stdout)) == variants[0]['refs']
    results[-1]['paginate_same'] = True
(out / 'refs-probe.json').write_text(json.dumps(results, indent=2) + '\n')
p = subprocess.run(['gh', 'api', 'repos/github/rest-api-description/contents/descriptions/api.github.com/api.github.com.json?ref=main'], capture_output=True, text=True, check=True)
data = json.loads(p.stdout)
assert data['encoding'] == 'none' and data['content'] == ''
(out / 'integrity/large-content.json').write_text(p.stdout)
print(json.dumps({'matching_refs': results, 'large_file_bytes': data['size'], 'encoding': data['encoding'], 'content_length': len(data['content'])}))
