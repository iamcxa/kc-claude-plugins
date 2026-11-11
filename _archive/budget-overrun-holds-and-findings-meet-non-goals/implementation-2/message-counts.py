import hashlib,json,subprocess,sys
from pathlib import Path
root=Path(sys.argv[1]);state=Path(sys.argv[2]);sys.path.insert(0,str(root/'kc-dev-flow-2/scripts'))
import role_triggers as rt
rev=subprocess.check_output(['git','-C',str(state),'rev-parse',sys.argv[3] if len(sys.argv)>3 else 'HEAD'],text=True).strip();rows=[]
for slug in ('amendment-checked-when-written','release-rollout-reaches-adopters-and-laws-pin'):
    records=rt.read_records(state,slug,rev);counted=rt.budget_dispatches(records);names={name for name,_ in counted}
    paths=subprocess.check_output(['git','-C',str(state),'ls-tree','-r','--name-only',rev],text=True).splitlines()
    specials=[path for path in paths if '/'+slug+'/dispatch/' in '/'+path and Path(path).name.startswith(('chief-engineer-','engineering-reviewer-'))]
    details=[dict(name=name,symptom=rt.symptom_name(text),counted=name in names,sha256=hashlib.sha256(text.encode()).hexdigest()) for name,text in records]
    row=dict(task=slug,state_revision=rev,count=len(counted),stage_records=sum('-message-' not in name for name,_ in records),all_messages=sum('-message-' in name for name,_ in records),counted_messages=sum('-message-' in name for name,_ in counted),records=details,excluded_special_roles=specials)
    rows.append(row);print(slug,'count',row['count'],'stages',row['stage_records'],'messages',row['counted_messages'],'of',row['all_messages'])
Path('/tmp/budget-implementation-2/message-counts-'+rev[:8]+'.json').write_text(json.dumps(rows,indent=2)+'\n')

