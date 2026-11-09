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
    manual=json.loads((R/'manual-semantic.json').read_text()) if (R/'manual-semantic.json').exists() else {'rows':[]}
    manual_by_run={v['run']:v for v in manual['rows']}
    precision=json.loads((R/'precision-review.json').read_text()) if (R/'precision-review.json').exists() else {'rows':[]}
    precision_by_run={v['run']:v for v in precision['rows']}
    for f in sorted((R/'runs').glob('*/meta.json')):
        d=json.loads(f.read_text());folder=f.parent
        report=(folder/'report.md').read_text() if (folder/'report.md').exists() else ''
        calls=[json.loads(l) for l in (folder/'gh.jsonl').read_text().splitlines()] if (folder/'gh.jsonl').exists() else []
        gap=any(c.get('refused') for c in calls) or folder.name=='codex-base-1-fixed'
        result=evaluate(report,calls,gap,d['wording'])
        summary=report.rsplit('### Summary',1)[-1]
        verdict=re.search(r'\b(REJECTED|NOT PASSED|PASSED|HOLD|BLOCKED)\b',summary)
        row={k:d.get(k) for k in ['host','arm','wording','tokens','exit','report_written']}
        row.update(name=folder.name,verdict=verdict[0] if verdict else 'no verdict',report_words=len(report.split()),**result)
        row['counted']=row['counted'] and d.get('exit')==0 and bool(d.get('report_written')) and not d.get('interrupted_by_parent')
        row['auto_precision_signal']=row['precision_miss']
        if folder.name in precision_by_run:row['precision_miss']=precision_by_run[folder.name]['precision_miss']
        if not report:
            row['found']=None
            row['precision_miss']=None
        decision=manual_by_run.get(folder.name)
        if decision:
            source=(R/decision['source']).read_text().splitlines()
            assert source[decision['quote_line']-1]==decision['quote'], 'manual quote differs from its source'
        row['post_hoc_manual_found']=decision['found'] if decision else None
        row['post_hoc_deciding_quote']=decision['quote'] if decision else None
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
        manual_complete=complete and all(r['post_hoc_manual_found'] is not None for cell in cells.values() for r in cell)
        hosts[host]['post_hoc_found']={k:sum(bool(r['post_hoc_manual_found']) for r in v) for k,v in cells.items()}
        hosts[host]['post_hoc_complete']=manual_complete
        hosts[host]['primary_beats_base']=found['candidate']>found['base'] if complete else None
        hosts[host]['post_hoc_beats_base']=hosts[host]['post_hoc_found']['candidate']>hosts[host]['post_hoc_found']['base'] if manual_complete else None
        hosts[host]['counts_disagree_on_beating_base']=hosts[host]['primary_beats_base']!=hosts[host]['post_hoc_beats_base'] if manual_complete else None
        hosts[host]['precision_misses_all_completed']=sum(r['precision_miss'] for r in rows if r['host']==host and r['arm']=='candidate' and r.get('report_written'))
        hosts[host]['precision_candidate_reports_assessed']=sum(bool(r.get('report_written')) for r in rows if r['host']==host and r['arm']=='candidate' and r['name'].endswith('-registered'))
        hosts[host]['precision_candidate_reports_missing']=sum(not bool(r.get('report_written')) for r in rows if r['host']==host and r['arm']=='candidate' and r['name'].endswith('-registered'))
        subset_manual_ready=all(cells.values()) and all(r['post_hoc_manual_found'] is not None for cell in cells.values() for r in cell)
        hosts[host]['available_subset_primary_beats_base']=found['candidate']>found['base'] if all(cells.values()) else None
        hosts[host]['available_subset_post_hoc_beats_base']=hosts[host]['post_hoc_found']['candidate']>hosts[host]['post_hoc_found']['base'] if subset_manual_ready else None
        hosts[host]['available_subset_counts_disagree']=hosts[host]['available_subset_primary_beats_base']!=hosts[host]['available_subset_post_hoc_beats_base'] if subset_manual_ready else None
    result={'runs':rows,'hosts':hosts,'raw_attempts':len(rows),'hard_stop':16,'post_hoc_authority':'dispatch/implementation-1-message-3.md; defined after the first valid result','report_word_means':{scope:{arm:statistics.mean(v) if v else None for arm in ['base','candidate'] for v in [[r['report_words'] for r in rows if r['arm']==arm and r.get('report_written') and (scope=='all_completed' or r['counted'])]]} for scope in ['all_completed','valid']}}
    (R/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Registered replay results','','Primary results use the unchanged pre-registered grader. The separate post-hoc manual column was defined after the first valid result, under FO dispatch/implementation-1-message-3.md. It does not change AC-3.','', '| Run | Host | Arm / wording | Verdict | Found | Read comments | Precision miss | Tokens | Counted | post-hoc manual |','| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in rows:
        lines.append('| '+ ' | '.join([r['name'],r['host'],r['arm']+' / '+str(r['wording']),r['verdict'],str(r['found']),str(r['read_comments_endpoint']),str(r['precision_miss']),json.dumps(r['tokens']),str(r['counted']),str(r['post_hoc_manual_found'])])+' |')
    lines+=['','## Per-host comparison','',json.dumps(hosts,indent=2),'','Only completed reports without fixture gaps or falsifier defects enter host counts. Original interrupted harness attempt is retained but excluded by FO dispatch/implementation-1-message-2.md. A run with any refused call is excluded. Three valid base and candidate runs per host are required; available-subset comparisons are diagnostic and do not satisfy AC-3. The comment was available from run start; these are reconstructed historical responses, not live PR proof. No delivery, adoption or future error-rate claim follows.','']
    lines+=['## Post-hoc deciding lines','']
    for r in rows:
        if r['post_hoc_deciding_quote']:
            lines.extend([r['name']+' — post-hoc '+str(r['post_hoc_manual_found'])+':','', '> '+r['post_hoc_deciding_quote'],''])
    lines+=['## FO reading cost','',json.dumps(result['report_word_means'],indent=2),'','The startup/dispatch/idle/merge-ask inputs are unchanged. Worker principles and unchanged workflow bytes are measured in words.json.','']
    lines+=['## Precision review','', 'precision-review.json audits whether the old comment was actually called unaddressed; auto_precision_signal remains in results.json. The excluded Codex base-2 run mentions that old comment inside its F1 paragraph but explicitly says it is repaired: its broad automatic signal is a false positive. Primary target grading is unchanged. Report word counts use the full appended report output, including any superseding entries.','']
    if (R/'final-disposition.md').exists():lines.extend([(R/'final-disposition.md').read_text()])
    (R/'results.md').write_text('\n'.join(lines))
    print(json.dumps(hosts))
