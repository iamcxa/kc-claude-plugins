#!/usr/bin/env python3
"""Check every evidence/*/SHA256SUMS under the given task folders the way scratch.py writes them:
a listed name is hashed as is, or, when only <name>.gz exists, after gunzip. Exit 1 on any mismatch."""
import gzip, hashlib, sys
from pathlib import Path
bad = total = 0
for folder in sys.argv[1:]:
    for manifest in sorted(Path(folder).glob("evidence/*/SHA256SUMS")):
        for line in manifest.read_text().splitlines():
            digest, name = line.split("  ", 1)
            path = manifest.parent / name
            data = path.read_bytes() if path.is_file() else gzip.decompress(path.with_name(path.name + ".gz").read_bytes())
            total += 1
            if hashlib.sha256(data).hexdigest() != digest:
                bad += 1
                print(f"{manifest.parent.name}/{name}: digest differs")
print(f"digests: {total} checked, {bad} differ")
sys.exit(1 if bad else 0)
