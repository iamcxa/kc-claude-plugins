"""Scan added candidate bytes and named artifacts; print class counts, never matches."""
from collections import Counter
import gzip
import json
import os
from pathlib import Path
import subprocess
import sys

code = Path(sys.argv[1])
sys.path.insert(0, str(code/'kc-dev-flow-2/scripts'))
import state_guard
compiled, present = state_guard.patterns(code)
assert present, 'owner list absent'
def git(*args):
    return subprocess.run(['git','-C',str(code),*args],check=True,capture_output=True).stdout
blobs = []
patch=git('diff','--no-ext-diff','--no-textconv','--no-color','-U0',sys.argv[2])
in_hunk=False
for line in patch.splitlines():
    if line.startswith(b'diff --git '):
        in_hunk=False
    elif line.startswith(b'@@'):
        in_hunk=True
    elif in_hunk and line.startswith(b'+'):
        blobs.append(line[1:])
for name in filter(None,git('ls-files','--others','--exclude-standard','-z').split(b'\0')):
    blobs.append((code/os.fsdecode(name)).read_bytes())
for raw in sys.argv[3:]:
    path=Path(raw)
    for file in sorted(path.rglob('*')) if path.is_dir() else [path]:
        if file.is_file():
            data=file.read_bytes()
            while data.startswith(b'\x1f\x8b'):
                data=gzip.decompress(data)
            blobs.append(data)
counts=Counter(dict.fromkeys(state_guard.CLASSES,0))
for data in blobs:
    for kind,pattern in compiled:
        counts[kind] += bool(pattern.search(data))
print(json.dumps(dict(blobs=len(blobs),hits=dict(counts),
                     list_limit="Owner list covers four adopters' names-only slug lists; the fifth adopter and hostnames outside its pattern are absent."),indent=2))
sys.exit(int(bool(sum(counts.values()))))
