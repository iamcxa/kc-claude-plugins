import json,re,sys
from pathlib import Path
E=Path(__file__).resolve().parent
C=Path(sys.argv[1])
S=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
task=(S/'claims-name-their-source.md').read_text()
adr=(C/'docs/adr/0055-a-claim-names-its-source-and-the-gate-scripts-print-the-rule.md').read_text()
def check(record):
    for n in [1,3]:
        section=task.split(f'### Amendment {n} —',1)[1].split('\n### ',1)[0]
        for label in ['Captain','Asked']:
            quote=re.search(r'^'+label+r': (「.*」)',section,re.M).group(1)
            assert quote in record,(n,label)
    normalized=' '.join(record.split())
    for phrase in ['claude-opus-5-5','claude -p --safe-mode','normal HOME','Codex half is not runnable','candidate 6 of 6 against base 1 of 3','3 of 6 against base 0 of 3','candidate runs 1, 5 and 6','candidate 6 of 6 and base 3 of 3','false-passes the base','counts-name-the-run-that-produced-them','not a file-open trace','daily FO behavior is unproven']:
        assert phrase in normalized,phrase
    assert 'Claude and Codex, three runs per cell' not in normalized
check(adr)
controls=[]
for name,changed in [('hidden known limit',adr.replace('3 of 6 against base 0 of 3','all runs passed')),('missing follow-up',adr.replace('counts-name-the-run-that-produced-them','unnamed future work')),('wrong Captain words',adr.replace('「甲」','「同意」'))]:
    try:check(changed)
    except AssertionError:controls.append({'name':name,'rejected':True})
    else:raise AssertionError(name+' falsely accepted')
result={'candidate':sys.argv[2] if len(sys.argv)>2 else '69f4988612d17c5524887f99c872a0ef384d05c9','rulings_verbatim':True,'known_limits_and_followup':True,'controls':controls,'method':'Recorded-ruling comparisons and bounded wording checks; raw answers independently read; not a behavioral efficacy test'}
if '--check-only' not in sys.argv:(E/'retained-record.json').write_text(json.dumps(result,indent=2)+'\n')
print('ADR quotes match the recorded rulings; known limit, grader defect and follow-up remain visible. All three altered-record controls reject.')
