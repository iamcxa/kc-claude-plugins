from pathlib import Path
import subprocess,tempfile,json,sys
wt=Path('/tmp/merge-guard-validation-b82f20de/export'); source=wt/'kc-dev-flow-2/scripts/merge_guard.py'; tests=source.with_name('test_merge_guard.py')
text=source.read_text()
cases=[
 ('newest','max(asks)[1].read_text()', 'min(asks)[1].read_text()', 'MergeGuardTests.test_newest_record_supersedes_older'),
 ('codex-ask','"ask" if host == "claude" else "deny"','"ask"','MergeGuardTests.test_host_outputs'),
 ('merges-glob','"_archive/*/merge", "_merges/*/merge"','"_archive/*/merge"','MergeGuardTests.test_merges_folder_newest'),
 ('disk-read','max(asks)[1].read_text()', 'git(root, "show", "HEAD:" + str(max(asks)[1].relative_to(root)))', 'MergeGuardTests.test_linked_worktree_discovery_reads_uncommitted_disk'),
 ('record-head','if args.head[:7].lower() not in question.lower():','if False:', 'RecordTests.test_record_refuses_missing_number_digit_suffix_head_answer_and_invalid_head'),
 ('number-boundary','{match.group(3)}(?!\\d)','{match.group(3)}', 'RecordTests.test_record_refuses_missing_number_digit_suffix_head_answer_and_invalid_head')]
results=[]
for name,old,new,test in cases:
 assert old in text,name
 with tempfile.TemporaryDirectory(prefix='merge-mutant-') as d:
  p=Path(d);(p/'merge_guard.py').write_text(text.replace(old,new));(p/'test_merge_guard.py').write_text(tests.read_text())
  r=subprocess.run([sys.executable,'-B',str(p/'test_merge_guard.py'),test],capture_output=True,text=True)
  Path('/tmp/merge-guard-validation-b82f20de/evidence/merge-guard-mutant-'+name+'.log').write_text(r.stdout+r.stderr)
  results.append({'name':name,'status':'passed' if r.returncode else 'failed','message':'Mutation rejected' if r.returncode else 'Mutation survived'})
Path('/tmp/merge-guard-validation-b82f20de/evidence/merge-guard-mutations.json').write_text(json.dumps(results,indent=2))
assert all(x['status']=='passed' for x in results),results
print('All six mutations rejected')
