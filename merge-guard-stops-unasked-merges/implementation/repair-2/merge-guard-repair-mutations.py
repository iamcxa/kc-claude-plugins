from pathlib import Path
import subprocess,tempfile,json,sys
wt=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-merge-guard-stops-unasked-merges');source=wt/'kc-dev-flow-2/scripts/merge_guard.py';tests=source.with_name('test_merge_guard.py');text=source.read_text()
old=subprocess.check_output(['git','-C',str(wt),'show','871c6b2f4ebccfc2c67df91d7d39ad038aa0710f:kc-dev-flow-2/scripts/merge_guard.py'],text=True)
forms=['global_short_repo_before_subcommand','global_long_repo_before_subcommand','global_equals_repo_before_subcommand','attached_and_interleaved_repo_flags','env_wrapper','command_wrapper','absolute_gh_with_global_flags','quoted_words','shell_spelling_of_gh','rest_merge_endpoint_stops_even_with_record','graphql_and_opaque_api_stops','ambiguous_wrappers_options_and_shell_text_stop','unknown_gh_alias_or_dynamic_subcommand_stops','implicit_repo_after_shell_context_change_stops','inherited_repo_override_needs_explicit_repo','inherited_host_override_stops']
mutations=[('previous-'+name,old,'MergeGuardTests.test_'+name) for name in forms]
changes=[('rest-endpoint',' or re.search(r"(?:^|/)pulls/[^/]+/merge(?:/|$)", path)','', 'rest_merge_endpoint_stops_even_with_record'),
 ('graphql','path == "graphql" or path.endswith("/graphql")','False', 'graphql_and_opaque_api_stops'),
 ('wrappers','            check_wrapper(words[start:i])','            pass','ambiguous_wrappers_options_and_shell_text_stop'),
 ('endpoint-normalization','path = posixpath.normpath(urlsplit(endpoint).path)','path = urlsplit(endpoint).path','rest_merge_endpoint_stops_even_with_record'),
 ('context','        if context_changed or os.environ.get("GH_REPO"):', '        if False:','implicit_repo_after_shell_context_change_stops'),
 ('nonmerge','        if target is None:\n            return "pass", None','        if target is None:\n            return "stop", "mutated"','readonly_gh_commands_pass')]
for name,a,b,test in changes:
 assert a in text,name
 mutant=text.replace(a,b)
 if name=='graphql':mutant=mutant.replace(r'|\bgraphql\b', '')
 mutations.append((name,mutant,'MergeGuardTests.test_'+test))
results=[];out=Path('/tmp/merge-guard-repair-mutations');out.mkdir(exist_ok=True)
for name,mutant,test in mutations:
 with tempfile.TemporaryDirectory(prefix='merge-repair-mutant-') as d:
  p=Path(d);(p/'merge_guard.py').write_text(mutant);(p/'test_merge_guard.py').write_text(tests.read_text())
  run=subprocess.run([sys.executable,'-B',str(p/'test_merge_guard.py'),test],capture_output=True,text=True)
  (out/(name+'.log')).write_text(run.stdout+run.stderr)
  ok=run.returncode!=0 and 'FAIL:' in run.stderr and 'ERROR:' not in run.stderr
  results.append({'name':name,'status':'passed' if ok else 'failed','message':test+' rejects mutant' if ok else 'Mutation survived or test errored'})
Path('/tmp/merge-guard-repair-mutations.json').write_text(json.dumps(results,indent=2))
print(len(results),'mutation checks; rejected',sum(x['status']=='passed' for x in results))
assert all(x['status']=='passed' for x in results),results
