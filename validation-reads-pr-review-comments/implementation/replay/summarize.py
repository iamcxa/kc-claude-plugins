import json, re, statistics, sys
from pathlib import Path
import grader

R=Path(__file__).resolve().parent

def evaluate(report, calls, fixture_gap=False, wording=1):
    hit=grader.found(report)
    read=any(c.get('carries_review_comments') for c in calls)
    defect=wording not in (0,1,2) or (hit and not read)
    return dict(found=hit,read_comments_endpoint=read,precision_miss=grader.found(report,'4505536959'),fixture_gap=fixture_gap,defect=defect,counted=bool(report) and not fixture_gap and not defect)

def all_rows():
    rows=[]
    for f in sorted((R/'runs').glob('*/meta.json')):
        d=json.loads(f.read_text());folder=f.parent
        report=(folder/'report.md').read_text() if (folder/'report.md').exists() else ''
        calls=[json.loads(l) for l in (folder/'gh.jsonl').read_text().splitlines()] if (folder/'gh.jsonl').exists() else []
        raw=(folder/'events.jsonl').read_text() if (folder/'events.jsonl').exists() else ''
        gap=any(c.get('refused') for c in calls) or 'replay fixture: not recorded' in raw
        result=evaluate(report,calls,gap,d['wording'])
        summary=report.rsplit('### Summary',1)[-1]
        verdict=re.search(r'\b(REJECTED|NOT PASSED|PASSED|HOLD|BLOCKED)\b',summary)
        row={k:d.get(k) for k in ['host','arm','wording','tokens','exit','report_written']}
        row.update(name=folder.name,verdict=verdict[0] if verdict else 'no verdict',report_words=len(report.split()),**result)
        if folder.name=='codex-base-1':
            row.update(counted=False,invalid_harness=True)
        rows.append(row)
    return rows

if __name__=='__main__':
    if '--selftest' in sys.argv:
        positive='- F1 Material: Codex review comment 4505793059 is unaddressed at 778367add'
        assert evaluate(positive,[])['defect']
        assert not evaluate(positive,[])['counted']
        assert evaluate(positive,[{'carries_review_comments':True}],wording=3)['defect']
        assert not evaluate(positive,[{'carries_review_comments':True,'refused':True}],fixture_gap=True)['counted']
        print('AC-3 no-response and AC-4 unregistered-wording falsifiers PASS')
        raise SystemExit()
    rows=all_rows();hosts={}
    for host in ['codex','claude']:
        cells={arm:[r for r in rows if r['host']==host and r['arm']==arm and r['counted']] for arm in ['base','candidate']}
        found={arm:sum(r['found'] for r in cell) for arm,cell in cells.items()}
        complete=all(len(cell)==3 for cell in cells.values())
        hosts[host]={'valid_runs':{k:len(v) for k,v in cells.items()},'found':found,'passed':complete and found['candidate']>found['base'] and found['candidate']>=2,'precision_misses':sum(r['precision_miss'] for r in cells['candidate']),'mean_report_words':{k:statistics.mean([r['report_words'] for r in v]) if v else None for k,v in cells.items()}}
    result={'runs':rows,'hosts':hosts,'raw_attempts':len(rows),'hard_stop':16}
    (R/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Registered replay results','', '| Run | Host | Arm / wording | Verdict | Found | Read comments | Precision miss | Tokens | Counted |','| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in rows:
        lines.append('| '+ ' | '.join([r['name'],r['host'],r['arm']+' / '+str(r['wording']),r['verdict'],str(r['found']),str(r['read_comments_endpoint']),str(r['precision_miss']),json.dumps(r['tokens']),str(r['counted'])])+' |')
    lines+=['','## Per-host comparison','',json.dumps(hosts,indent=2),'','Only completed reports without fixture gaps or falsifier defects enter host counts. Original interrupted harness attempt is retained but excluded by FO dispatch/implementation-1-message-2.md. A run with any refused call is excluded. Three valid base and candidate runs per host are required. The comment was available from run start; these are reconstructed historical responses, not live PR proof. No delivery, adoption or future error-rate claim follows.','']
    (R/'results.md').write_text('\n'.join(lines))
    print(json.dumps(hosts))
