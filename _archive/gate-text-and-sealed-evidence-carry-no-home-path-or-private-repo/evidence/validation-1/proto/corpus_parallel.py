"""Evaluate unchanged candidate matchers in four local processes; retain only counts."""
import collections
import gzip
import json
import multiprocessing
import os
import signal
from pathlib import Path
import sys

code,state,identifiers,output=map(lambda v:Path(v).resolve(),sys.argv[1:5])
tip,slug=sys.argv[5:7]
os.environ['KC_DEV2_IDENTIFIERS']=str(identifiers)
sys.path.insert(0,str(code/'kc-dev-flow-2/scripts'))
import state_guard as guard
compiled,present=guard.patterns(state)
assert present
counts=lambda:dict.fromkeys(guard.CLASSES,0)
class SearchDeadline(Exception):
    pass
def alarm(*_):
    raise SearchDeadline()
def hits(data):
    found,timed_out=set(),set()
    for kind,pattern in compiled:
        signal.setitimer(signal.ITIMER_REAL,0.2)
        try:
            if pattern.search(data):
                found.add(kind)
        except SearchDeadline:
            timed_out.add(kind)
        finally:
            signal.setitimer(signal.ITIMER_REAL,0)
    return found,timed_out
def check(item):
    signal.signal(signal.SIGALRM,alarm)
    own,packed,name,raw,scanned=item
    result=dict(own=int(own),gzip=int(packed),raw_only=[],gzip_hits=[],own_hits=[],incomplete=[])
    if packed:
        rh,rt=hits(raw)
        ph,pt=hits(gzip.decompress(raw))
        sh,st=hits(scanned+b'\n'+name)
        result['raw_only']=list(rh-ph-rt-pt)
        result['gzip_hits']=list(sh)
        result['incomplete']=list(rt|pt|st)
    if own:
        oh,ot=hits(scanned+b'\n'+name)
        result['own_hits']=list(oh)
        result['incomplete']=list(set(result['incomplete'])|ot)
    return result
items=[]
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
    items.append((own,packed,name,raw,guard.added_bytes(state,b'0'*40,blob)))
result=dict(tip=tip,expected_files=len(items),completed_files=0,gzip_blobs=0,own_evidence_files=0,
            identifier_counts_by_class=dict(collections.Counter(kind for kind,_ in compiled)),
            raw_only=counts(),gzip_hits=counts(),own_evidence_hits=counts(),incomplete_by_class=counts(),
            limit='Pinned public-state tip; exact candidate added_bytes and owner expressions, capped at 0.2 seconds per search. Timed-out classes remain unverified. Existing decompressed hits are not raw-byte false positives.')
with multiprocessing.get_context('fork').Pool(4) as pool:
    for row in pool.imap_unordered(check,items):
        result['completed_files']+=1
        result['gzip_blobs']+=row['gzip']
        result['own_evidence_files']+=row['own']
        for target,source in (('raw_only','raw_only'),('gzip_hits','gzip_hits'),('own_evidence_hits','own_hits'),('incomplete_by_class','incomplete')):
            for kind in row[source]:
                result[target][kind]+=1
        output.write_text(json.dumps(result,indent=2)+'\n')
        if result['completed_files']%20==0:
            print('completed files: '+str(result['completed_files']),flush=True)
print(json.dumps(result,indent=2))
sys.exit(int(any(result['raw_only'].values()) or any(result['own_evidence_hits'].values()) or any(result['incomplete_by_class'].values())))
