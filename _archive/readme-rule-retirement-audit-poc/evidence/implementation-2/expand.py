#!/usr/bin/env python3
"""Pinned-source, scratch-only expansion of the README retirement audit."""
import argparse
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tarfile

PIN = 'c2f035b6612f5edb42220576b3414e993531ffd6'
SECTIONS = ['Review-finding disposition', 'FO steps: review findings', 'Decision records',
            'Number guards', 'FO steps: number guards']


def inventory(data):
    text = data.decode()
    rows = []
    for section in SECTIONS:
        start = text.index('## ' + section + '\n') + len('## ' + section + '\n')
        end = text.find('\n## ', start)
        block = text[start:end if end >= 0 else len(text)]
        # Exclude labels/list counters but retain all sentence words and byte spans.
        paragraphs = re.split(r'\n\s*\n|\n(?=- \*\*|\d+\. )', block)
        offset = start
        for p in paragraphs:
            pos = text.index(p, offset) if p else offset
            offset = pos + len(p)
            normalized = ' '.join(p.split())
            normalized = re.sub(r'^(?:- \*\*[^*]+\*\*\s*|\d+\.\s*)', '', normalized)
            if not normalized:
                continue
            # Periods inside code spans and e.g. are not sentence boundaries.
            tokens = {}
            def protect(m):
                key = f'CODETOKEN{len(tokens)}'
                tokens[key] = m[0]
                return key
            masked = re.sub(r'`[^`]*`', protect, normalized).replace('e.g.', 'EGTOKEN')
            parts = re.split(r'(?<=[.!?])\s+(?=[A-Z`<])', masked)
            search_from = pos
            for part in parts:
                sentence = part.replace('EGTOKEN', 'e.g.')
                for key, value in sorted(tokens.items(),key=lambda pair:len(pair[0]),reverse=True):
                    sentence = sentence.replace(key, value)
                # Map the quote back to exact source bytes, preserving source line wraps.
                pattern = r'\s+'.join(re.escape(w) for w in sentence.split())
                match = re.search(pattern, text[search_from:offset])
                assert match, (section, sentence)
                a, b = search_from + match.start(), search_from + match.end()
                search_from = b
                rows.append(dict(number=len(rows)+16, section=section, rule=sentence,
                                 char_start=a, char_end=b,
                                 byte_start=len(text[:a].encode()), byte_end=len(text[:b].encode())))
    return rows


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', type=Path, required=True)
    ap.add_argument('--scratch', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--inventory-only', action='store_true')
    args = ap.parse_args()
    root, out = args.scratch.resolve(), args.out.resolve()
    root.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    def source(*parts):
        return subprocess.run(['git','-C',str(args.repo),*parts], capture_output=True, check=True).stdout
    assert source('rev-parse','HEAD').decode().strip() == PIN
    assert not source('status','--porcelain')
    data = source('show', PIN + ':docs/dev2/README.md')
    rows = inventory(data)
    (out/'inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    if args.inventory_only:
        for row in rows:
            print(f"{row['number']} [{row['section']}] {row['rule']}")
        return
    snapshot = root/'snapshot'
    snapshot.mkdir(exist_ok=True)
    archive = source('archive',PIN,'kc-dev-flow-2','docs/dev2/README.md','docs/adr')
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        bundle.extractall(snapshot,filter='data')
    scripts = snapshot/'kc-dev-flow-2/scripts'
    sys.path.insert(0,str(scripts))
    env = dict(os.environ, GIT_AUTHOR_NAME='Synthetic', GIT_AUTHOR_EMAIL='synthetic',
               GIT_COMMITTER_NAME='Synthetic', GIT_COMMITTER_EMAIL='synthetic',
               GIT_AUTHOR_DATE='2026-11-14T04:00:00Z',GIT_COMMITTER_DATE='2026-11-14T04:00:00Z',
               GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
               PYTHONDONTWRITEBYTECODE='1', TMPDIR=str(root/'tmp'))
    (root/'tmp').mkdir(exist_ok=True)
    runs=[]
    def run(name,script,argv,expected,contains=None,cwd=None):
        command=['python3','-B',str(scripts/script),*map(str,argv)]
        def portable(value):
            return value.replace(str(root)+'/', '').replace(str(root),'.')
        input_files=[]
        for value in argv:
            path=Path(str(value))
            if path.is_absolute() and path.is_relative_to(root) and path.is_file() and path.suffix in ('.md','.txt','.json'):
                content=path.read_text()
                input_files.append(dict(path=portable(str(path)),sha256=hashlib.sha256(content.encode()).hexdigest(),text=content))
        done=subprocess.run(command,capture_output=True,text=True,cwd=cwd or root,env=env)
        rec=dict(id=name,command=portable(shlex.join(command)),cwd=portable(str(cwd or root)),
                 exit_code=done.returncode,stdout=portable(done.stdout),stderr=portable(done.stderr))
        rec['input_files']=input_files
        rec['changed_files']=[]
        for before in input_files:
            path=root/before['path']
            after=path.read_text()
            if after!=before['text']:
                rec['changed_files'].append(dict(path=before['path'],text=after,sha256=hashlib.sha256(after.encode()).hexdigest()))
        runs.append(rec)
        (out/'runs.json').write_text(json.dumps(runs,ensure_ascii=False,indent=2)+'\n')
        assert done.returncode==expected,(name,done.returncode,done.stdout,done.stderr)
        assert not contains or contains in done.stdout+done.stderr,(name,contains,done.stdout,done.stderr)
        return rec
    def put(path,value):
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(value)
        return path
    def git(path,*parts):
        return subprocess.run(['git','-C',str(path),'-c','commit.gpgsign=false',*parts],
                              env=env,capture_output=True,text=True,check=True).stdout.strip()
    def init(name):
        p=root/'fixtures'/name
        p.mkdir(parents=True,exist_ok=True)
        git(p,'init','-q','--initial-branch=main')
        return p
    def commit(p,message):
        git(p,'add','--all')
        git(p,'commit','-qm',message)
        return git(p,'rev-parse','HEAD')

    # Native gate-reason checks: metadata is checked, consent and timing are not.
    d=root/'fixtures/decision'
    task=put(d/'sample.md', '''---
profile: pilot
gates:
    records:
        - stage: validation
          attempts:
            - id: gate-attempt:sample-validation-1
              briefing:
                room-ref: ./sample/review/validation/briefing-1
---
''')
    put(d/'sample/review/validation/briefing-1/index.json',json.dumps({'question':'Approve the synthetic sample?'}))
    for name,value,code,needle in [
        ('decision-good','answering 「Approve the synthetic sample?」; Recommendation: followed',0,'reason: followed'),
        ('decision-missing-declaration','answering 「Approve the synthetic sample?」',1,'missing declaration'),
        ('decision-wrong-question','answering 「A different question?」; Recommendation: followed',1,'does not quote'),
        ('decision-placeholder','answering 「Approve the synthetic sample?」; Override: recommended <option>; Captain chose B; area: scope',1,'placeholder'),
        ('decision-false-followed','Captain chose B against the recommended A, without actual consent. answering 「Approve the synthetic sample?」; Recommendation: followed',0,'reason: followed'),
    ]:
        reason=put(d/(name+'.txt'),value+'\n')
        run(name,'decision_ledger.py',['--reason',reason,'--task',task],code,needle)

    # Gate question checks use only local synthetic files; this command never calls gh.
    d=root/'fixtures/gate'
    workflow=put(d/'README.md','---\ntrunk: main\nextensions: []\n---\n').parent
    head='a'*40
    body='---\nprofile: pilot\n---\n\n## Acceptance criteria\n**AC-1**: synthetic result.\n'
    task=put(d/'sample.md',body)
    put(d/'sample/dispatch/validation-1.md','Candidate: '+head+'\n')
    steptext='Candidate: '+head+'\n\n### Step 1\nAsked: Inspect the synthetic result.\nRan: fresh shell 2026-11-14T04:00:00Z\nObserved: inspected fixture\n'
    step=put(d/'sample/captain-steps/1.md',steptext)
    question='Inspect the synthetic result.\nSufficiency: criteria met\nNecessity: a named consumer uses this result\n'
    summary='External rounds: 0\nCaptain steps: captain-steps/1.md\n'
    def gate_case(name,q=question,s=summary,b=body,expected=0,needle=None):
        put(task,b)
        qf=put(d/(name+'-question.md'),q)
        sf=put(d/(name+'-summary.md'),s)
        return run(name,'delivery_gate.py',['question',task,'--text-file',qf,'--summary-file',sf,'--workflow-dir',workflow],expected,needle)
    gate_case('gate-good')
    gate_case('gate-no-sufficiency',q=question.replace('Sufficiency: criteria met\n',''),expected=1,needle="no 'Sufficiency:'")
    gate_case('gate-no-necessity',q=question.replace('Necessity: a named consumer uses this result\n',''),expected=1,needle="no 'Necessity:'")
    gate_case('gate-no-rounds',s=summary.replace('External rounds: 0\n',''),expected=1,needle='External rounds: N')
    gate_case('gate-false-rounds',s=summary.replace('External rounds: 0','External rounds: 999'))
    gate_case('gate-no-captain-steps',s='External rounds: 0\n',expected=1,needle='Captain steps:')
    gate_case('gate-decline-no-reason',q=question+'Declined: Polish, synthetic formatting.\n',expected=1,needle='no reason')
    gate_case('gate-decline-missing-revision',q=question+'Declined: Polish, synthetic formatting (harmless spacing).\n')
    gate_case('gate-unhandled-polish',b=body+'\n## Stage Report: validation\n- F1 Polish: synthetic formatting.\n',expected=1,needle='declined items')
    gate_case('gate-material-with-no-fields',b=body+'\n## Stage Report: validation\n- F1 Material: no four fields, classified without evidence.\n')
    gate_case('gate-precedent-money',q=question+'Precedent: ADR 0001 — 「spend money without asking」\n')
    # Count disclosure is a record-shape check, not verification that counts were measured.
    gate_case('gate-unverified-count',q=question+'The test suite has 1234 checks.\n')
    put(task,body)
    put(step,steptext.replace('Observed: inspected fixture\n',''))
    sf=put(d/'steps-message.md',question)
    run('steps-no-observation','delivery_gate.py',['steps',step,'--text-file',sf],1,'S2')
    put(step,steptext)
    run('steps-good','delivery_gate.py',['steps',step,'--text-file',sf],0,'captain steps complete')

    # Applied-migration violation is isolated from base immutability (R1).
    p=init('numbers')
    put(p/'migrations/0001_base.sql','SELECT 1;\n')
    base=commit(p,'base')
    git(p,'checkout','-qb','candidate')
    put(p/'migrations/0002_change.sql','SELECT 2;\n')
    applied=commit(p,'applied')
    put(p/'migrations/0002_change.sql','SELECT 3;\n')
    edited=commit(p,'edited applied migration')
    (p/'migrations/0002_change.sql').unlink()
    deleted=commit(p,'deleted applied migration')
    task=put(p/'task.md','---\nprofile: pilot\n---\n## Number guards\nMigration: 0002\nApplied at: synthetic '+applied+'\n')
    common=['check','--repo',p,'--base',base,'--migrations-path','migrations','--task',task]
    run('applied-unchanged','number_guards.py',[*common,'--head',applied],0,'PASS: no findings')
    run('applied-edit','number_guards.py',[*common,'--head',edited],1,'FAIL R2')
    run('applied-delete','number_guards.py',[*common,'--head',deleted],1,'FAIL R2')
    put(task,'---\nprofile: pilot\n---\n## Number guards\nMigration: 0002\nNot applied: synthetic '+applied+' - synthetic rejected push\n')
    run('not-applied-edit','number_guards.py',[*common,'--head',edited],0,'PASS: no findings')
    put(task,'---\nprofile: pilot\n---\n## Number guards\nMigration: 0002\n')
    run('missing-applied-record','number_guards.py',[*common,'--head',edited],0,'PASS: no findings')
    put(task,'---\nprofile: poc\n---\n## Number guards\nMigration: 0002\n')
    for name,sha in [('add',applied),('edit',edited),('delete',deleted)]:
        # For delete, compare with the already-applied branch as the base to exercise D.
        base_args=[x for x in common]
        if name=='delete':
            base_args[base_args.index('--base')+1]=applied
        run('poc-'+name,'number_guards.py',[*base_args,'--head',sha],1,'FAIL R6')
    run('poc-reservation-no-migration-change','number_guards.py',[*common,'--head',base],0,'PASS: no findings')
    put(task,'---\nprofile: pilot\n---\nSurfaces: db\n## Number guards\n')
    run('db-no-migrations-path','number_guards.py',['check','--repo',p,'--base',base,'--head',base,'--task',task],2,'no migrations-path')
    put(task,'---\nprofile: poc\n---\n## Number guards\n')
    run('poc-no-path-unguarded','number_guards.py',['check','--repo',p,'--base',base,'--head',applied,'--task',task],0,'migration guard skipped')
    run('none-rejects-migration','number_guards.py',['check','--repo',p,'--base',base,'--head',applied,'--task',task,'--migrations-path','none'],1,'FAIL R7')
    run('none-clean','number_guards.py',['check','--repo',p,'--base',base,'--head',base,'--task',task,'--migrations-path','none'],0,'PASS: no findings')
    put(task,'---\nprofile: pilot\n---\n## Number guards\nMigration: 0002\nMigration: 0003\n')
    run('multiple-reservations','number_guards.py',['reserve','--repo',p,'--base',base,'--task',task,'--kind','migration','--migrations-path','migrations','--state-dir',p],0,'Migration: 0003')
    # An unreserved candidate must fail R4; base mutation must fail R1.
    put(task,'---\nprofile: pilot\n---\n## Number guards\n')
    run('unreserved-migration','number_guards.py',[*common,'--head',applied],1,'FAIL R4')
    git(p,'checkout','-q','--detach',base)
    put(p/'migrations/0001_base.sql','SELECT 9;\n')
    baseedit=commit(p,'mutate base migration')
    run('base-migration-edit','number_guards.py',[*common,'--head',baseedit],1,'FAIL R1')
    git(p,'checkout','-q','--detach',base)
    put(p/'migrations/0001_collision.sql','SELECT 4;\n')
    collision=commit(p,'colliding number')
    put(task,'---\nprofile: pilot\n---\n## Number guards\nMigration: 0001\n')
    run('migration-collision','number_guards.py',[*common,'--head',collision],1,'FAIL R3')

    # ADR lint: existence/form is checked; decision completeness and routing are not.
    p=init('adrs')
    put(p/'docs/adr/.keep','synthetic\n')
    base=commit(p,'base')
    record='# 1. Synthetic\n\nDate: 2026-11-14\n\n## Status\n\nAccepted\n\n## Context\n\nSynthetic context.\n\n## Decision\n\n**Words:** synthetic words\n\n**Options considered:** A or B\n\n**Recommended:** A\n\n## Consequences\n\nSynthetic consequence.\n'
    path=put(p/'docs/adr/0001-synthetic.md',record)
    commit(p,'record')
    run('adr-good','adr_lint.py',[p/'docs/adr','--since',base,'--require','0001'],0,'1 ADR file(s)')
    run('adr-missing-required','adr_lint.py',[p/'docs/adr','--since',base,'--require','0002'],1,'required ADR 0002 does not exist')
    put(path,record.replace('**Recommended:** A\n',''))
    run('adr-changed-no-recommendation','adr_lint.py',[p/'docs/adr','--since',base],1,"needs a '**Recommended:**'")
    put(path,record)
    run('adr-invalid-base','adr_lint.py',[p/'docs/adr','--since','nonexistent-synthetic-ref'],2,'--since')

    # Form checks listed by the study, exercised on Pilot-shaped synthetic data.
    d=root/'fixtures/design'
    good='---\nprofile: pilot\nstatus: ideation\n---\n\n## Scope\nNon-goals: no unrelated work\nBudget: 1 implementation and 1 validation cycles\nStop condition: covered\n\n## FO alignment\nSurfaces: none\nVisible change: none\n\n## Design\n### Worth questions\nAsked: demonstrate a result\n\n## Acceptance criteria\n**AC-1**: result exists.\nVerified by: inspect a fixture.\n'
    task=put(d/'sample.md',good)
    run('seed-good','design_surfaces.py',['check','--seed',task],0,'seed fields')
    put(task,good.replace('Non-goals: no unrelated work\n',''))
    run('seed-no-non-goals','design_surfaces.py',['check','--seed',task],1,'Non-goals')
    for label,line in [('budget','Budget: 1 implementation and 1 validation cycles\n'),('stop','Stop condition: covered\n'),
                       ('surfaces','Surfaces: none\n'),('visible','Visible change: none\n')]:
        put(task,good.replace(line,''))
        run('seed-no-'+label,'design_surfaces.py',['check','--seed',task],1)
    put(task,good)
    run('design-good','design_surfaces.py',['check',task],0,'presentable')
    put(task,good.replace('### Worth questions','### Different heading'))
    run('design-no-worth','design_surfaces.py',['check',task],1,'Worth questions')
    put(task,good+'\n**AC-1**: duplicate criterion.\n')
    run('design-duplicate-ac','design_surfaces.py',['check',task],0,'presentable')
    amendment='\n## Captain amendments\n### Amendment 1 — 2026-11-14, chat\nCaptain: replace result\nAsked: replace the original criterion\nSupersedes: AC-1\n'
    put(task,good+amendment)
    run('design-unmoved-ac','design_surfaces.py',['check',task],1,'AC-1')
    put(task,good+amendment+'Superseded text:\n**AC-1**: result exists.\n')
    run('design-reused-superseded-id','design_surfaces.py',['check',task],1,'AC-1')
    # A fresh AC is required to name the amendment it implements.
    marked=good.replace('**AC-1**: result exists.','**AC-2**: replacement result exists.')+amendment+'Superseded text:\n**AC-1**: result exists.\n'
    put(task,marked)
    run('design-unmarked-replacement','design_surfaces.py',['check',task],1,'Amended by Captain')

    # Dispatch coverage is existence, not quality or historical sending time.
    d=root/'fixtures/dispatch'
    workflow=put(d/'README.md','---\nentity-type: task\nextensions: []\nstages:\n  - name: implementation\n---\n')
    task=put(d/'sample.md','---\nprofile: pilot\n---\n## Stage Report: implementation\nSynthetic report.\n')
    folder=d/'sample'
    folder.mkdir(exist_ok=True)
    run('dispatch-coverage-missing','dispatch_records.py',['--readme',workflow,'--coverage',task,'--stage','implementation'],1,'no dispatch record')
    record=put(folder/'dispatch/implementation-1.md','empty synthetic record\n')
    run('dispatch-coverage-empty-record','dispatch_records.py',['--readme',workflow,'--coverage',task,'--stage','implementation'],0,'complete')
    complete='Dispatched: 2026-11-14 '+'a'*40+'\nModel: synthetic\n## Checklist\nInspect a fixture.\n## Scope notes\nPackage root: /synthetic-package\nSend completion to main.\n'
    put(record,complete)
    run('dispatch-good','dispatch_records.py',['--readme',workflow,folder],0,'complete')
    put(record,complete.replace('Package root: /synthetic-package\n',''))
    run('dispatch-no-root','dispatch_records.py',['--readme',workflow,folder],1,'Package root:')
    put(record,complete.replace('Send completion to main.','Send completion to team-lead.'))
    run('dispatch-no-main','dispatch_records.py',['--readme',workflow,folder],1,'completion recipient')
    put(record,complete.replace('Inspect a fixture.','Run adr_lint.py.'))
    run('dispatch-bare-name','dispatch_records.py',['--names','--strict',record],1,'bare package')
    put(record,complete.replace('Inspect a fixture.','Same checklist as validation-1.'))
    put(record.with_name('validation-1.md'),complete)
    run('dispatch-pointer-only','dispatch_records.py',['--readme',workflow,folder],1,'checklist of its own')
    put(task,'---\nprofile: pilot\n---\n## Number guards\nADR: 0001\n')
    put(record,complete)
    run('dispatch-reservation-not-copied','dispatch_records.py',['--names','--strict',record],1,'reserved line')
    put(task,'---\nprofile: pilot\n---\n## FO alignment\nAlignment: needed\n')
    ideation=put(record.with_name('ideation-1.md'),complete)
    run('alignment-no-result','dispatch_records.py',['--names','--strict',ideation],1,'Result:')

    # Role call evidence is syntactic; the check does not authenticate that a review happened.
    p=init('roles')
    text='---\nprofile: pilot\n---\n## FO alignment\nSurfaces: none\n\n'+('## Stage Report: implementation\nSynthetic.\n\n'*5)
    task=put(p/'sample.md',text)
    commit(p,'owed role')
    run('role-owed','role_triggers.py',[p,'sample'],1,'chief-engineer')
    put(task,text.replace('Surfaces: none','Surfaces: none\nReviewer: chief-engineer opus 2026-11-14 — synthetic question'))
    commit(p,'synthetic call line only')
    run('role-line-clears','role_triggers.py',[p,'sample'],0)

    # Document impact is a listing helper, and does not lint report dispositions.
    p=init('documents')
    put(p/'src/worker.py','def update_count():\n    return 1\n')
    put(p/'docs/guide.md','Call update_count from src/worker.py.\n')
    base=commit(p,'base')
    put(p/'src/worker.py','def update_count():\n    return 2\n')
    head=commit(p,'change without doc disposition')
    run('doc-impact-missing-disposition','doc_impact.py',[base,head,'--repo',p],0,'review')

    # Exact budget function: run the original function via a small exit-code adapter.
    adapter=put(root/'budget_probe.py',"import importlib.util,sys\ns=importlib.util.spec_from_file_location('lint_tree',sys.argv[1])\nm=importlib.util.module_from_spec(s);s.loader.exec_module(m)\nerrors=m.budget_errors(m.workflow_budget()+int(sys.argv[2]))\nprint('\\n'.join(errors) or 'budget exact')\nsys.exit(bool(errors))\n")
    def adapter_run(name,delta,expected):
        command=['python3','-B',str(adapter),str(scripts/'lint-skills.py'),str(delta)]
        done=subprocess.run(command,capture_output=True,text=True,cwd=root,env=env)
        rec=dict(id=name,command=shlex.join(command).replace(str(root)+'/', ''),cwd='.',exit_code=done.returncode,stdout=done.stdout,stderr=done.stderr)
        runs.append(rec)
        assert done.returncode==expected,(name,done.stdout,done.stderr)
    adapter_run('word-budget-exact',0,0)
    adapter_run('word-budget-over',1,1)
    adapter_run('word-budget-under',-1,1)

    # History shapes: a sentinel with no committed observer must be refused.
    p=init('laws')
    put(p/'keep.txt','synthetic\n')
    before=commit(p,'base')
    task=put(p/'sample.md','---\ntitle: sample\nstatus: implementation\npr:\n---\n')
    commit(p,'task')
    put(task,'---\ntitle: sample\nstatus: implementation\npr: pr-merge:1\n---\n')
    after=commit(p,'sentinel without observer')
    workflow=put(root/'fixtures/laws-readme.md','---\nextensions: [learn]\n---\n')
    run('laws-no-observer','laws_check.py',[p,'--before',before,'--after',after,'--readme',workflow],1,'L1 observer-before-sentinel')
    # A distinct inert witness for every prose sentence, preserving the boundary:
    # these prove parser scope only and never count as an enforcing nonzero exit.
    d=root/'fixtures/rule-witnesses'
    workflow=put(d/'README.md','---\ntrunk: main\nextensions: []\n---\n').parent
    body='---\nprofile: pilot\n---\n\n## Acceptance criteria\n**AC-1**: synthetic result.\n'
    task=put(d/'sample.md',body)
    put(d/'sample/dispatch/validation-1.md','Candidate: '+'a'*40+'\n')
    put(d/'sample/captain-steps/1.md',steptext)
    sf=put(d/'summary.md','External rounds: 0\nCaptain steps: captain-steps/1.md\n')
    for row in rows:
        witness=('\n## Synthetic behavior witness (data only)\n'
                 f"Sentence {row['number']} was not followed in the hypothetical workflow. "
                 'The instruction breached was: '+row['rule']+'\n')
        put(task,body+witness)
        qf=put(d/'question.md',question)
        run(f"rule-{row['number']:02d}-witness",'delivery_gate.py',
            ['question',task,'--text-file',qf,'--summary-file',sf,'--workflow-dir',workflow],0)
    # END PROBES
    assert not source('status','--porcelain')
    (out/'runs.log').write_text('\n\n'.join('$ '+r['command']+'\nexit: '+str(r['exit_code'])+
        '\n'+r['stdout']+r['stderr'] for r in runs)+'\n')
    print(f'{len(rows)} additional sentences inventoried; {len(runs)} probe runs recorded.')


if __name__=='__main__':
    main()
