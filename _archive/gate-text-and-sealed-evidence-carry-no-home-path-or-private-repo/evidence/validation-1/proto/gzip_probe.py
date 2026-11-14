"""Exercise real commit and push hooks using invented identifiers and owned remotes."""
import argparse
import gzip
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import zlib

p = argparse.ArgumentParser()
p.add_argument('candidate', type=Path)
p.add_argument('scratch', type=Path)
p.add_argument('output', type=Path)
a = p.parse_args()
code, base, output = (v.resolve() for v in (a.candidate, a.scratch, a.output))
base.mkdir(parents=True, exist_ok=False)
output.mkdir(parents=True, exist_ok=True)
token = b'invented-validation-private-repository-7319'
identifiers = base / 'identifiers.tsv'
identifiers.write_bytes(b'private-repo\t' + token + b'\n')
env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
env.update(KC_DEV2_IDENTIFIERS=str(identifiers), PYTHONDONTWRITEBYTECODE='1',
           GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1',
           GIT_AUTHOR_NAME='Fixture', GIT_COMMITTER_NAME='Fixture',
           GIT_AUTHOR_EMAIL='fixture-identity', GIT_COMMITTER_EMAIL='fixture-identity',
           GIT_CONFIG_COUNT='2', GIT_CONFIG_KEY_0='commit.gpgsign', GIT_CONFIG_VALUE_0='false',
           GIT_CONFIG_KEY_1='user.email', GIT_CONFIG_VALUE_1='fixture-identity')
product, state, remote = [base / n for n in ('product', 'state', 'remote.git')]
guard = code / 'kc-dev-flow-2/scripts/state_guard.py'
commands = []

def safe(value):
    return str(value).replace(str(code), '<candidate>').replace(str(base), '<scratch>')

def run(argv, expected=0, data=None):
    r = subprocess.run(list(map(str, argv)), input=data, env=env, capture_output=True, timeout=60)
    commands.append({'argv': [safe(v) for v in argv], 'exit': r.returncode,
                     'matched_text_printed': token.lower() in (r.stdout+r.stderr).lower()})
    (output / 'gzip-commands.json').write_text(json.dumps(commands, indent=2)+'\n')
    if expected is not None and r.returncode != expected:
        raise RuntimeError('fixture setup failed: ' + json.dumps(commands[-1]))
    return r

def git(*args, expected=0):
    return run(['git', '-C', state, *args], expected)

run(['git', 'init', '-q', '-b', 'main', product])
run(['git', '-C', product, 'commit', '--allow-empty', '-qm', 'test: fixture seed'])
run(['git', 'init', '-q', '--bare', remote])
run(['git', '-C', product, 'remote', 'add', 'origin', remote])
run(['git', '-C', product, 'worktree', 'add', '-b', 'spacedock-state/probe', state])
git('push', '-q', 'origin', 'spacedock-state/probe')
run([sys.executable, '-B', guard, 'install', state, '--shared', '--refuse', 'private-repo,home'])
run([sys.executable, '-B', guard, 'check', state])

def gz(data):
    return gzip.compress(data, mtime=0)

clean = gz(b'public text\n')
def header(flag, field, body=clean):
    return body[:3]+bytes([flag])+body[4:10]+field+body[10:]

name = header(8, token+b'\0')
comment = header(16, token+b'\0')
extra = header(4, struct.pack('<H', len(token))+token)
bad_trailer = name[:-8]+bytes([name[-8]^1])+name[-7:]
bad_deflate = name[:-10]+b'\xff\xff'+name[-8:]
header_all = header(4|8|16, struct.pack('<H', len(token))+token+token+b'\0'+token+b'\0')
fhcrc_head = name[:3]+bytes([10])+name[4:10]+token+b'\0'
fhcrc = fhcrc_head + struct.pack('<H', zlib.crc32(fhcrc_head)&0xffff) + clean[10:]
large_header = header(8, b'a'*(2*1024*1024)+token+b'\0')
deep_second = clean + gz(gz(name))
cases = [
    ('clean_gzip', clean, False, 'accepted'),
    ('ordinary_binary', bytes(range(256))*4, False, 'accepted'),
    ('header_name', name, True, 'refused'),
    ('header_comment', comment, True, 'refused'),
    ('header_extra', extra, True, 'refused'),
    ('combined_header_fields', header_all, True, 'refused'),
    ('header_crc', fhcrc, True, 'refused'),
    ('concatenated_header', clean+name+clean, True, 'refused'),
    ('nested_header', gz(gz(name)), True, 'refused'),
    ('corrupt_trailer', bad_trailer, False, 'refused'),
    ('corrupt_deflate', bad_deflate, False, 'refused'),
    ('large_header', large_header, True, 'refused'),
    ('nested_second_member_header', deep_second, True, 'refused'),
    ('nested_second_member_body', clean+gz(gz(token)), True, 'refused'),
]
results = []
for label, data, hidden, expected in cases:
    target = state / ('evidence.bin' if label=='ordinary_binary' else 'evidence.gz')
    target.write_bytes(data)
    git('add', '--', target.name)
    result = git('commit', '-qm', 'test: '+label, expected=None)
    actual = 'accepted' if result.returncode == 0 else 'refused'
    stderr = result.stderr.decode(errors='replace')
    item = dict(name=label, bytes=len(data), expected=expected, actual=actual,
                commit_exit=result.returncode, passed=actual==expected,
                private_class_reported='private-repo identifier' in stderr,
                matched_text_printed=token.lower() in (result.stdout+result.stderr).lower())
    if hidden:
        item['plain_first_layer_contains_identifier'] = token in gzip.decompress(data)
    if result.returncode == 0:
        pushed = git('push', '-q', 'origin', 'spacedock-state/probe', expected=None)
        item['push_exit'] = pushed.returncode
        item['matched_text_printed'] |= token.lower() in (pushed.stdout+pushed.stderr).lower()
    else:
        git('reset', '--hard', '-q', 'HEAD')
    results.append(item)
    (output / 'gzip-probe.json').write_text(json.dumps(results, indent=2)+'\n')

assert gzip.decompress(gzip.decompress(deep_second)[len(b'public text\n'):]) == name
assert token in name and token not in gzip.decompress(name)
print(json.dumps({'cases':len(results), 'unexpected_acceptances':[x['name'] for x in results if not x['passed']],
                  'matched_text_printed':sum(x['matched_text_printed'] for x in results)}, indent=2))
sys.exit(int(any(not x['passed'] or x['matched_text_printed'] for x in results)))
