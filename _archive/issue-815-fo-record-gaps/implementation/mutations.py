import argparse,json,re,shutil,subprocess,sys,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
scratch=Path(tempfile.mkdtemp(prefix='mutants-',dir=a.out));plugin=scratch/'kc-dev-flow-2';shutil.copytree(a.candidate/'kc-dev-flow-2',plugin,ignore=shutil.ignore_patterns('__pycache__'))
(scratch/'scripts').mkdir();shutil.copy2(a.candidate/'scripts/skill-frontmatter-lint.sh',scratch/'scripts/skill-frontmatter-lint.sh')
scripts=plugin/'scripts';results=[]
cases=[
 ('quote-skipped','decision_ledger.py','if not quotes_bound_question({"question": bound, "reason": reason}):','if False:','test_decision_ledger.OpenAttemptReasonTests.test_only_the_open_attempts_question_passes'),
 ('latest-room-instead-of-open','decision_ledger.py','    fm, _ = split_task(task.read_text(encoding="utf-8"))','    room = re.findall(r"room-ref: (.+)", task.read_text())[-1]\n    return question(task.parent, task, room), task.parent / room / "index.json"\n    fm, _ = split_task(task.read_text(encoding="utf-8"))','test_decision_ledger.OpenAttemptReasonTests.test_newer_resolved_attempt_does_not_replace_the_open_question'),
 ('missing-question-passes','decision_ledger.py','            bound, index = open_question(task)','            bound, index = "Y", task','test_decision_ledger.OpenAttemptReasonTests.test_missing_task_zero_two_open_attempts_and_unreadable_room_are_exit_two'),
 ('only-first-picture','design_surfaces.py','for shot in named or [""]:','for shot in named[:1] or [""]:','test_design_surfaces.BuiltScreenTests.test_every_bad_second_preview_item_is_named'),
 ('picture-bytes-unchecked','design_surfaces.py','if file_digest(picture) in seen:','if False:','test_design_surfaces.BuiltScreenTests.test_preview_sequence_refuses_second_ideation_picture_and_duplicate_keys'),
 ('folder-resolution-removed','dispatch_records.py','        if opts.coverage.is_dir():','        if False:','test_dispatch_records.CoverageTests.test_folder_coverage_matches_file_in_both_layouts'),
 ('literal-record-path','delivery_gate.py','    path = record.resolve()','    path = record','test_delivery_gate.CaptainStepTests.test_steps_holds_misplaced_records_and_accepts_resolved_paths'),
 ('record-path-unchecked','delivery_gate.py','def captain_steps_path_problems(record, folder=None):','def captain_steps_path_problems(record, folder=None):\n    return []','test_delivery_gate.ReviewerDeclarationTests.test_captain_record_path_holds_question_and_check'),
]
# Resolve the existing class rather than guessing its label.
source=(scripts/'test_delivery_gate.py').read_text();cls=re.findall(r'^class (\w+)\(',source[:source.index('    def test_steps_holds_misplaced_records')],re.M)[-1]
cases=[tuple(v.replace('CaptainStepTests.',cls+'.') if isinstance(v,str) else v for v in row) for row in cases]
def run(label,cmd,cwd):
 log=a.out/(label+'.log')
 with log.open('w') as stream:r=subprocess.run(cmd,cwd=cwd,stdout=stream,stderr=subprocess.STDOUT)
 text=log.read_text();assert r.returncode==1 and 'FAIL:' in text,(label,r.returncode,text)
 result={'name':label,'status':'passed','message':'mutated product causes the acceptance test to fail','exit':r.returncode,'log':str(log)};results.append(result);print(json.dumps(result),flush=True)
for label,file,old,new,test in cases:
 path=scripts/file;original=path.read_text();assert old in original,label
 for cache in scratch.rglob('__pycache__'):shutil.rmtree(cache)
 path.write_text(original.replace(old,new,1))
 try:run(label,[sys.executable,'-B','-m','unittest',test],scripts)
 finally:path.write_text(original)
# Drop only the newly approved budget step; retain the candidate README bytes.
path=scripts/'lint-skills.py';original=path.read_text();changed=re.sub(r'    dict\(delta=2, why="the Captain reason check.*?loaded="[^\n]*"\),\n','',original,flags=re.S);assert changed!=original
path.write_text(changed)
r=subprocess.run([sys.executable,'-B',str(path),'--root',str(a.candidate/'kc-dev-flow-2')],capture_output=True,text=True);(a.out/'budget-step-removed.log').write_text(r.stdout+r.stderr);assert r.returncode==1 and 'exceeds the budget' in r.stdout,(r.returncode,r.stdout,r.stderr)
path.write_text(original);results.append({'name':'budget-step-removed','status':'passed','exit':r.returncode,'message':'README above budget without the +2 step'})
# Require the ADR after removing just that record in scratch.
shutil.copytree(a.candidate/'docs/adr',scratch/'docs/adr');(scratch/'docs/adr/0073-a-captain-gate-record-quotes-its-bound-question-before-it-is-written.md').unlink()
r=subprocess.run([sys.executable,'-B',str(scripts/'adr_lint.py'),str(scratch/'docs/adr'),'--require','0073'],capture_output=True,text=True);(a.out/'adr-removed.log').write_text(r.stdout+r.stderr);assert r.returncode==1 and '0073' in r.stdout+r.stderr
results.append({'name':'required-adr-removed','status':'passed','exit':r.returncode,'message':'missing required ADR is refused'})
(a.out/'tests.json').write_text(json.dumps(results,indent=2)+'\n');print('all mutations caught',flush=True)
