"""Bounded count-only scans of real gzip blobs and this task's sealed evidence."""
import gzip
import json
import os
from pathlib import Path
import signal
import sys

code, state, identifiers, output = map(lambda v:Path(v).resolve(),sys.argv[1:5])
tip, slug = sys.argv[5:7]
os.environ['KC_DEV2_IDENTIFIERS']=str(identifiers)
sys.path.insert(0,str(code/'kc-dev-flow-2/scripts'))
import state_guard as guard
compiled,present=guard.patterns(state)
assert present
class SlowPattern(Exception):
    pass
def alarm(*_):
    raise SlowPattern()
signal.signal(signal.SIGALRM,alarm)
counts=lambda:dict.fromkeys(guard.CLASSES,0)
result=dict(tip=tip,gzip_blobs=0,own_evidence_files=0,raw_only=counts(),
            gzip_hits=counts(),own_evidence_hits=counts(),timeouts={k:counts() for k in ('raw','plain','scanned','own')},
            limit='One second per expression search. Timed-out class/phase comparisons remain unverified; no identifier or filename is retained.')
def hits(data,phase):
    found=set()
    incomplete=set()
    for kind,pattern in compiled:
        signal.setitimer(signal.ITIMER_REAL,1)
        try:
            if pattern.search(data):
                found.add(kind)
        except SlowPattern:
            result['timeouts'][phase][kind]+=1
            incomplete.add(kind)
        finally:
            signal.setitimer(signal.ITIMER_REAL,0)
    return found,incomplete
for entry in guard.git(state,'ls-tree','-r','-z',tip).split(b'\0'):
    if not entry:
        continue
    metadata,name=entry.split(b'\t',1)
    own=name.startswith((slug+'/evidence/').encode())
    packed=name.endswith(b'.gz')
    if not own and not packed:
        continue
    blob=metadata.split()[2]
    raw=guard.git(state,'cat-file','blob',blob.decode())
    scanned=guard.added_bytes(state,b'0'*40,blob)
    if packed:
        result['gzip_blobs']+=1
        raw_hits,raw_incomplete=hits(raw,'raw')
        plain_hits,plain_incomplete=hits(gzip.decompress(raw),'plain')
        for kind in raw_hits-plain_hits-raw_incomplete-plain_incomplete:
            result['raw_only'][kind]+=1
        scan_hits,scan_incomplete=hits(scanned+b'\n'+name,'scanned')
        for kind in scan_hits:
            result['gzip_hits'][kind]+=1
    if own:
        result['own_evidence_files']+=1
        own_hits,_=hits(scanned+b'\n'+name,'own')
        for kind in own_hits:
            result['own_evidence_hits'][kind]+=1
    output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
sys.exit(int(any(result['raw_only'].values()) or any(sum(v.values()) for v in result['timeouts'].values())))
