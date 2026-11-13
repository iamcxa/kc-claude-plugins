from pathlib import Path
import contextlib,io,json,os,sys,types,unittest
WT=Path(os.environ['PRODUCT_WORKTREE']);S=Path(__file__).parent
sys.path.insert(0,str(WT/'kc-dev-flow-2/scripts'))
import test_delivery_gate as t
source=(WT/'kc-dev-flow-2/scripts/delivery_gate.py').read_text()
mutations=[
 ('review-judgment','if outcome in {"findings", "answered"}:','if False:', 'test_review_findings_need_the_fo_decision_missing_from_observations'),
 ('quota-disclosure','if reviewer == "copilot" and outcome == "not-run":','if False:', 'test_known_quota_refusal_needs_unread_and_retry_in_question'),
 ('quoted-profile','prod = bool(front and (m := FM_PROFILE.search(front[1])) and m[1] == "prod")','prod = False','test_configured_trigger_guard_includes_quoted_prod_profiles'),
 ('head-token','return bool(grants) and all(head.startswith(sha) for sha in grants)','return all(head.startswith(sha) for sha in grants)','test_merge_head_token_must_be_nonempty_and_bounded'),
 ('config-reread','workflow_dir, scalars, lists = find_readme(task, args.workflow_dir)','workflow_dir, scalars, lists = task.parent, {"second-reviewer": "copilot"}, {"extensions": ["codex", "copilot"]}','test_question_reloads_current_reviewer_configuration'),
 ('computed-disclosures','**disclosure_facts(task_folder(task), gate_text, (facts or {}).get("body") or ""),','**{},','test_computed_disclosures_are_record_fields_without_question_mutation')]
rows=[]
for name,old,new,test in mutations:
 if name=='config-reread':
  offset=source.index('def facts_question(');mutated=source[:offset]+source[offset:].replace(old,new,1)
 else:
  assert source.count(old)==1,(name,source.count(old));mutated=source.replace(old,new)
 module=types.ModuleType('delivery_mutant');module.__file__=str(WT/'kc-dev-flow-2/scripts/delivery_gate.py')
 exec(compile(mutated,module.__file__,'exec'),module.__dict__);t.gate=module
 out=io.StringIO();result=unittest.TextTestRunner(stream=out,verbosity=2).run(t.RecordRouteParityTests(test))
 (S/('mutation-'+name+'.log')).write_text(out.getvalue())
 rows.append(dict(name=name,test=test,status='passed' if not result.wasSuccessful() and not result.errors else 'failed',observed_test_failures=len(result.failures),observed_test_errors=len(result.errors),output='mutation-'+name+'.log',mutation_scope='isolated in-memory module; no product bytes changed'))
 (S/'mutations.json').write_text(json.dumps(rows,indent=2)+'\n')
 assert rows[-1]['status']=='passed',rows[-1]
 print(name,'caught',flush=True)
