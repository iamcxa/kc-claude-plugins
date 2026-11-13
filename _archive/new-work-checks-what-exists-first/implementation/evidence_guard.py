import json,sys
from pathlib import Path
a=json.loads(Path(sys.argv[2]).read_text());kind=sys.argv[1]
if kind=='replay':
 events=a['events'];found=next((i for i,x in enumerate(events) if x['kind']=='checked_found'),999);proposal=next((i for i,x in enumerate(events) if x['kind']=='proposal'),-1);x=events[found] if found<len(events) else {};ok=found<proposal and x.get('own_repository') and x.get('primary_tool_contract') and x.get('governing_adrs') and set(x.get('required_inaccessible',[]))<=set(x.get('disclosed_inaccessible',[]))
elif kind=='counts':
 expected=json.loads(Path(sys.argv[3]).read_text());ok=set(a)==set(expected) and a.get('limit')==expected['limit'] and len(a.get('rows',[]))==3
 for x,y in zip(a.get('rows',[]),expected['rows']):
  ok=ok and set(x)==set(y) and all(type(v)==int and v>=0 for v in x.values()) and x.get('state_read_from_committed_branch')==1 and x.get('state_files_read',0)>0
else:raise ValueError(kind)
print(json.dumps({'accepted':bool(ok),'limit':'Controlled evidence validation, not model-behavior enforcement.'}));sys.exit(0 if ok else 1)
