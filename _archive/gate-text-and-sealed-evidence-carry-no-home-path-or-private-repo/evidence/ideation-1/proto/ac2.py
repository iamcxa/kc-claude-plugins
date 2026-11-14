"""AC-2 probe: sealed evidence holding an invented private repository name on the throwaway, private-repo at refuse.
usage: ac2.py OVERLAY_SCRIPTS (HOME/KC_DEV2_IDENTIFIERS from setup.sh)"""
import gzip, io, json, os, subprocess, sys
from pathlib import Path
pkg = Path(sys.argv[1]); sys.path.insert(0, str(pkg)); import scratch
home = Path.home(); state = home / 'ws/state'; name = 'acme-hidden-app'
def commit(task, label):
    subprocess.run(['git', '-C', str(state), 'add', '-A', '--', f'{task}.md', task], check=True)
    c = subprocess.run(['git', '-C', str(state), 'commit', '-q', '-m', f'state: {label}', '--', f'{task}.md', task], capture_output=True, text=True)
    lines = [l[:100] for l in c.stderr.splitlines() if l.startswith('state guard')]
    if c.returncode: subprocess.run(['git', '-C', str(state), 'reset', '-q', '--', f'{task}.md', task])
    return {'step': label, 'exit': c.returncode, 'guard': lines, 'name_printed': name in c.stderr}
def seal(task):
    try: return scratch.evidence(state / task, 'validation-1')
    except ValueError as e: return 'scratch: refused; ' + str(e)
res = []
t = 'tw-ev'; f = state / t; ev = f / 'evidence/validation-1'; ev.mkdir(parents=True)
(state / f'{t}.md').write_text('---\ntitle: tw\n---\n\n## Stage Report: validation\n\n- DONE: adopter check\n')
(ev / 'run.log').write_text(f'checked worktree ~/ws/{name}: ok\n')
(ev / 'big.log').write_text(('x' * 79 + '\n') * 4000 + f'{name}\n')
(ev / 'clean.log').write_text('1 PASS\n')
res.append({'seal': seal(t)}); res.append(commit(t, 'r1 sealed with a private name'))
# way forward 1: drop the file, record the ADR 0079 line with a placeholder, re-seal
(ev / 'run.log').unlink()
gz = ev / 'big.log.gz'
try:
    raw = gzip.decompress(gz.read_bytes()).replace(name.encode(), b'<private repository>'); gz.write_bytes(gzip.compress(raw, mtime=0))
    res.append({'edit inside sealed .gz then re-seal': seal(t)})
except Exception as e: res.append({'gz edit': repr(e)})
gz.unlink(); (ev / 'big.log').write_bytes(raw)
res.append({'replace .gz with redacted plain file then re-seal': seal(t)})
with (state / f'{t}.md').open('a') as o: o.write(f'Not archived (private): the adopter check log; reproduce: python3 check.py ~/ws/{name}\n')
res.append(commit(t, 'r2 reproduce names the private repo'))
txt = (state / f'{t}.md').read_text().replace(f'~/ws/{name}', '<adopter checkout>'); (state / f'{t}.md').write_text(txt)
res.append(commit(t, 'r3 placeholder reproduce line'))
res.append({'sums_lines': (ev / 'SHA256SUMS').read_text().count('\n'), 'files': sorted(p.name for p in ev.iterdir())})
# gzip header name (Codex P2 declined on PR 871)
t2 = 'tw-gzhdr'; e2 = state / t2 / 'evidence/validation-1'; e2.mkdir(parents=True); (state / f'{t2}.md').write_text('x\n')
buf = io.BytesIO()
with gzip.GzipFile(filename=f'{name}.log', mode='wb', fileobj=buf, mtime=0) as z: z.write(b'1 PASS\n')
(e2 / 'out.gz').write_bytes(buf.getvalue())
res.append({'seal gzhdr': seal(t2), 'header_name_in_raw': name.encode() in (e2 / 'out.gz').read_bytes()})
res.append(commit(t2, 'gzip header name only'))
print(json.dumps(res, indent=1, ensure_ascii=False))
