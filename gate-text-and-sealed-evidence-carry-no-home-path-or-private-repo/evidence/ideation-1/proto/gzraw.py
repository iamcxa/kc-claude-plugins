"""Every .gz blob at the state tip: does any class match the raw (compressed) bytes, and is that hit absent from the decompressed content? Counts only."""
import gzip, subprocess, sys, collections
from pathlib import Path
sys.path.insert(0, sys.argv[1]); import state_guard as g
root = Path(sys.argv[2]).resolve(); compiled, present = g.patterns(root); assert present
ls = subprocess.run(['git', '-C', str(root), 'ls-tree', '-r', '-z', 'origin/spacedock-state/dev2'], capture_output=True).stdout.split(b'\0')
blobs = [e.split(b'\t')[0].split()[2].decode() for e in ls if e.endswith(b'.gz')]
raw_only, header_named, n = collections.Counter(), 0, 0
for b in blobs:
    raw = g.git(root, 'cat-file', 'blob', b); n += 1
    header_named += bool(raw[3] & 0x18)
    try: plain = gzip.decompress(raw)
    except Exception: continue
    for k, rx in compiled:
        if rx.search(raw) and not rx.search(plain): raw_only[k] += 1
print(f'gz blobs: {n}; with a header name or comment: {header_named}; raw-only class hits: {dict(raw_only) or 0}')
