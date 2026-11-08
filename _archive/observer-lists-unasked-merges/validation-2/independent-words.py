import json,pathlib,re,statistics,sys
root=pathlib.Path(sys.argv[1]);rows=json.loads((root/'windows.json').read_text());seen=set();counts=[];without=[]
rule='"merging the full head `<package>/scripts/delivery_gate.py check` passes, with `--match-head-commit` set to it" (Delivery authority)'
caveat='Coverage: a merge with no ask record may have been approved in chat or recorded in a state checkout this run cannot read; neither shows here.'
for row in rows:
 lines=(root/(row['slug']+'-audit.txt')).read_text().splitlines()
 def render(prior):
  result=[];repeated=[];fresh=[]
  for line in lines:
   if line.startswith('carried:'):result.append(f'ok | rule: {rule} | evidence: "{line} merged PRs" (gh pr list, state refs)')
   elif re.match(r'^(release|sync|learning): #',line):
    kind=line.split(':')[0];result.append(f'observed | {kind} PRs carry no task ask | evidence: "{line}" (gh pr list)')
   elif re.match(r'^(no ask record|head differs):',line):
    token=re.match(r'.*?: #(\d+) head [0-9a-f]{12}',line)
    if token[0] in prior:repeated.append('#'+token[1])
    else:
     fresh.append(token[0]);verdict="can't tell" if line.startswith('no ask record') else 'violation'
     result.append(f'{verdict} | rule: {rule} | evidence: "{line}" (gh pr list, state refs)')
  if repeated:result.append('observed | already in an earlier observer report | evidence: "'+' '.join(repeated)+'"')
  if fresh:result.append(caveat)
  return result,fresh
 rendered,new=render(seen);seen.update(new);uncollapsed,_=render(set())
 assert rendered==row['lines'],row['slug']
 counts.append(sum(len(line.split()) for line in rendered));without.append(sum(len(line.split()) for line in uncollapsed))
assert len(counts)==54 and statistics.median(counts)==60 and max(counts)==320
mutated=[n+1 for n in counts]
assert not(statistics.median(mutated)<=60 and max(mutated)<=320)
summary={'windows':len(counts),'median':statistics.median(counts),'max':max(counts),'uncollapsed_max':max(without),'falsifier':{'change':'append one extra word per rendered report','median':statistics.median(mutated),'max':max(mutated),'budget_accepts':False},'scope':'Independent rendering of candidate audit outputs, pinned chronological verbatim-report simulation; not a promise about arbitrary native model wording.'}
(root.parent/'independent-words.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
