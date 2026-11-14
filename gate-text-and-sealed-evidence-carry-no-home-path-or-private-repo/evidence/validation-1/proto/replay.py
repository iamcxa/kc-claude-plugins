"""Replay a pinned public-state interval; output counts and classes, never identifiers."""
import collections
import gzip
import json
import os
import signal
from pathlib import Path
import subprocess
import sys

code, live, base, output, identifiers = map(lambda p:Path(p).resolve(), sys.argv[1:6])
start, end, task_slug = sys.argv[6:9]
mode = sys.argv[9] if len(sys.argv) > 9 else 'all'
base.mkdir(parents=True, exist_ok=False)
os.environ['KC_DEV2_IDENTIFIERS'] = str(identifiers)
sys.path.insert(0, str(code/'kc-dev-flow-2/scripts'))
import state_guard as guard
commands = []
signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('bounded count-only scan timed out')))
signal.alarm(300)
def run(args, data=None, expected=0):
    result = subprocess.run(list(map(str,args)), input=data, capture_output=True)
    def safe(v):
        return str(v).replace(str(Path.home()), '~').replace(str(base), '<scratch>')
    commands.append(dict(command=[safe(v) for v in args], exit=result.returncode))
    if expected is not None:
        assert result.returncode == expected, 'setup or replay command failed'
    print('command completed; exit='+str(result.returncode),flush=True)
    return result

remote, product, state = [base/n for n in ('remote.git','product','state')]
run(['git','clone','--quiet','--bare',live,remote])
run(['git','clone','--quiet','--no-checkout',remote,product])
run(['git','-C',product,'worktree','add','-b','spacedock-state/replay',state,end])
run([sys.executable,'-B',code/'kc-dev-flow-2/scripts/state_guard.py','install',state,
     '--shared','--refuse','home,private-repo'])
run([sys.executable,'-B',code/'kc-dev-flow-2/scripts/state_guard.py','check',state])
compiled, present = guard.patterns(state)
assert present
counts = lambda:dict.fromkeys(guard.CLASSES, 0)
gzip_stats = dict(files=0, task_files=0, raw_only=counts(), scanned_hits=counts(), task_scanned_hits=counts())
for entry in (guard.git(state,'ls-tree','-r','-z',end).split(b'\0') if mode != 'replay-only' else []):
    if not entry.endswith(b'.gz'):
        continue
    meta,name = entry.split(b'\t',1)
    blob = meta.split()[2]
    raw = guard.git(state,'cat-file','blob',blob.decode())
    plain = gzip.decompress(raw)
    scanned = guard.added_bytes(state,b'0'*40,blob)
    owned = name.startswith((task_slug+'/evidence/').encode())
    gzip_stats['files'] += 1
    print('gzip blob completed: '+str(gzip_stats['files']),flush=True)
    gzip_stats['task_files'] += int(owned)
    kinds_raw = {kind for kind,pattern in compiled if pattern.search(raw)}
    kinds_plain = {kind for kind,pattern in compiled if pattern.search(plain)}
    kinds_scan = {kind for kind,pattern in compiled if pattern.search(scanned) or pattern.search(name)}
    for kind in kinds_raw-kinds_plain:
        gzip_stats['raw_only'][kind] += 1
    for kind in kinds_scan:
        gzip_stats['scanned_hits'][kind] += 1
        if owned:
            gzip_stats['task_scanned_hits'][kind] += 1
commits = guard.git(state,'rev-list','--reverse',start+'..'+end).decode().splitlines() if mode != 'gzip-only' else []
results = []
aggregate = counts()
for commit in commits:
    kinds, routes, unresolved = set(), set(), 0
    file_counts = counts()
    for name,before,after in guard.changes(state,commit):
        data = guard.added_bytes(state,before,after)
        found = {kind for kind,pattern in compiled if pattern.search(data) or pattern.search(name)}
        kinds.update(found)
        for kind in found:
            file_counts[kind] += 1
        relevant = found & {'home','private-repo'}
        if not relevant:
            continue
        sealed = b'/evidence/' in name
        if sealed and 'private-repo' in relevant:
            routes.add('drop private evidence; record placeholder reproduction; reseal')
            continue
        try:
            text = data.decode('utf-8')
        except UnicodeError:
            routes.add('drop private binary evidence; record placeholder reproduction; reseal')
            continue
        rewritten = guard.rewrite_home(text).encode()
        new_name = name
        for kind,pattern in compiled:
            if kind=='private-repo':
                rewritten = pattern.sub(b'<private repository>',rewritten)
                new_name = pattern.sub(b'public-placeholder',new_name)
        residue = {kind for kind,pattern in compiled if kind in relevant and
                   (pattern.search(rewritten) or pattern.search(new_name))}
        unresolved += int(bool(residue))
        if 'home' in relevant:
            routes.add('write home as ~; retain existing sealed bytes unchanged when already committed')
        if 'private-repo' in relevant:
            routes.add('replace textual private name with placeholder')
    parent = guard.git(state,'rev-parse',commit+'^').decode().strip()
    payload = ('refs/heads/spacedock-state/replay '+commit+' refs/heads/spacedock-state/replay '+parent+'\n').encode()
    result = run([sys.executable,'-B',code/'kc-dev-flow-2/scripts/state_guard.py','scan',state,
                  '--event','pre-push'], data=payload, expected=None)
    expected = int(bool(kinds & {'home','private-repo'}))
    assert result.returncode == expected, 'scan exit differs from counted classes'
    printed = sorted({kind for kind,pattern in compiled if pattern.search(result.stdout+result.stderr)})
    for kind in kinds:
        aggregate[kind] += 1
    results.append(dict(commit=commit, guard_exit=result.returncode, classes=sorted(kinds),
                        changed_files_by_class=file_counts, way_forward=sorted(routes),
                        unresolved=unresolved, printed_identifier_classes=printed))
    print('replay commit completed: '+commit,flush=True)
summary = dict(mode=mode,start_exclusive=start,end_inclusive=end,commits=len(results),counts_by_class=aggregate,
               no_way_forward=sum(x['unresolved'] for x in results),gzip=gzip_stats,per_commit=results,
               limit='Pinned post-candidate public state interval only; no live flip or future-writer acceptance.')
(output/('replay-'+mode+'.json')).write_text(json.dumps(summary,indent=2)+'\n')
(output/('replay-'+mode+'-commands.json')).write_text(json.dumps(commands,indent=2)+'\n')
print(json.dumps(summary,indent=2))
sys.exit(int(bool(summary['no_way_forward'] or any(gzip_stats['raw_only'].values()) or
                 any(x['printed_identifier_classes'] for x in results))))
