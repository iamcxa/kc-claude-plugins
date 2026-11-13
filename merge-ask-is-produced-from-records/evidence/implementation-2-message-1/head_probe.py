import json
import investigate as p
p.RESULT_NAME='head-results.json'
clean=[{'reviewer':'codex','head':p.HEAD,'exit':0,'outcome':'clean','evidence':'review:5','scope':'pr'},
       {'reviewer':'copilot','head':p.HEAD,'exit':0,'outcome':'answered','evidence':'review:2','scope':'pr'}]
rows=[]
for label,value,want in [('non-hex','not-a-sha',0),('empty','',0),('overlong',p.HEAD+'f',0),('different-valid','f'*40,1),('prefix-control',p.HEAD[:9],0)]:
 def setup(root,task,q,s,c,route):
  q.write_text(q.read_text().replace('--match-head-commit '+p.HEAD,'--match-head-commit '+value));c.write_text(q.read_text()+s.read_text())
 result=p.run('head-'+label,reviewer_rows=clean,setup=setup)
 actual={k:[v['check_exit'],v['question_exit']] for k,v in result.items()}
 expected={'legacy':[0,0 if label=='prefix-control' else 1],'record':[0,want]}
 rows.append({'case':label,'expected':expected,'actual':actual});assert actual==expected,(label,actual)
(p.S/'head-assertions.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps({'cases':len(rows),'expected_route_comparisons_match':True}))
