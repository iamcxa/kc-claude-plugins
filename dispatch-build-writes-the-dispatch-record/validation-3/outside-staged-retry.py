import importlib.util, json, os, sys
from pathlib import Path
root=Path(sys.argv[1])
sys.path.insert(0,str(root/'kc-dev-flow-2/scripts'))
spec=importlib.util.spec_from_file_location('seam',root/'kc-dev-flow-2/scripts/test_dispatch_stage.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
out=[]
for layout in ('flat','folder'):
 c=m.DispatchStageTests('test_real_builder_allowed_routes_preserve_other_tasks');c.setUp()
 try:
  c.scope_seed(layout);c.dirty_outside()
  first=c.build(); before=c.scope_snapshot()
  retry=c.build(expected=None); after=c.scope_snapshot()
  c.git(c.state,'restore','--staged','--',c.outside)
  recovered=c.build(expected=None)
  out.append(dict(layout=layout,first_exit=first.returncode,retry_exit=retry.returncode,retry_stdout=retry.stdout,retry_stderr=retry.stderr,all_state_preserved=before==after,recovery_after_unstaging_other_task_exit=recovered.returncode,record_two_exists=c.record(number=2).exists()))
 finally:c.doCleanups()
print(json.dumps(out,indent=2))
