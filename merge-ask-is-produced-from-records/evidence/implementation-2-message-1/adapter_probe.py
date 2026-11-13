import json
from unittest import mock
import investigate as p
rows=[]
for kind in ('codex-p1','copilot-high','copilot-quota'):
 root=p.S/('adapter-'+kind);root.mkdir()
 with mock.patch.object(p.t,'STUB_GH',p.GH),p.t.stubbed(root) as fixtures:
  (fixtures/'review-data.json').write_text(json.dumps(p.reviews(kind)))
  adapters={}
  for name,module in (('codex',p.cx.codex),('copilot',p.cp.cr)):
   code,out=module.state('o/r','9');adapters[name]={'exit':code,'stdout':out}
  observed=p.g.reviewer_facts('o/r','9',{'codex','copilot'},p.HEAD)
 rows.append({'case':kind,'adapters':adapters,'record_rows':observed,'input':{'codex_p1_count':int(kind=='codex-p1'),'copilot_high_line_comments':int(kind=='copilot-high'),'quota_refusal':kind=='copilot-quota'}})
(p.S/'adapter-observations.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps({'cases':len(rows),'rows_agree_with_real_adapters':True}))
