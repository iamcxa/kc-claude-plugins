"""Count-only privacy check before retaining validation evidence."""
import gzip
import json
import os
from pathlib import Path
import sys
code,state,folder,identifiers,output=map(lambda s:Path(s).resolve(),sys.argv[1:6])
sys.path.insert(0,str(code/'kc-dev-flow-2/scripts'))
import state_guard as guard
os.environ['KC_DEV2_IDENTIFIERS']=str(identifiers)
patterns,present=guard.patterns(state)
assert present
counts=dict.fromkeys(guard.CLASSES,0)
files=0
for path in folder.rglob('*'):
    if not path.is_file() or path==output:
        continue
    data=path.read_bytes()
    while data.startswith(b'\x1f\x8b'):
        data+=b'\n'+gzip.decompress(data)
        break
    kinds={kind for kind,pattern in patterns if pattern.search(data)}
    for kind in kinds:
        counts[kind]+=1
    files+=1
result=dict(files=files,counts_by_class=counts)
output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
sys.exit(int(any(counts.values())))
