from pathlib import Path
import importlib.util, json, subprocess, sys
WT=Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-merge-ask-is-produced-from-records")
SCR=Path(__file__).parent
sys.path.insert(0,str(WT/"kc-dev-flow-2/scripts"))
import test_sd_dispatch as test
texts=test.pinned_texts(); path="references/sd/workflow.md"
assert all(gap==([],[]) for gap in test.fix_gaps(texts).values())
mutated=texts[path].replace("--record-facts", "--record-factz")
assert mutated!=texts[path]
gaps={key:value for key,value in test.fix_gaps({**texts,path:mutated}).items() if any(value)}
spec=importlib.util.spec_from_file_location("flow_lint",WT/"kc-dev-flow-2/scripts/lint-skills.py")
lint=importlib.util.module_from_spec(spec);spec.loader.exec_module(lint)
# The lint's word/budget reader only needs the workflow file at its declared path.
import shutil
copy=SCR/"typo-plugin";shutil.copytree(WT/"kc-dev-flow-2",copy,ignore=shutil.ignore_patterns("__pycache__"),dirs_exist_ok=True)
(copy/path).write_text((WT/"kc-dev-flow-2"/path).read_text().replace("--record-facts", "--record-factz"))
errors=lint.lint_tree(copy)
cmd=[sys.executable,"-B",str(WT/"kc-dev-flow-2/scripts/delivery_gate.py"),"check","/nonexistent/task.md","--pr","o/r#9","--text-file","/nonexistent/question","--record-factz"]
p=subprocess.run(cmd,capture_output=True,text=True)
(SCR/"typo-cli.log").write_text(p.stdout+p.stderr)
assert gaps=={} and errors==[] and p.returncode==2 and "unrecognized arguments" in p.stderr,(gaps,errors,p.returncode,p.stderr)
(SCR/"unguarded.json").write_text(json.dumps(dict(mutation="--record-facts changed to --record-factz in workflow text",word_count_unchanged=True,pin_gaps=gaps,lint_errors=errors,cli_exit=p.returncode,command=cmd,output="typo-cli.log",scope="The retained static pin and lint checks miss this broken workflow command; direct delivery unit tests call the correct flag and do not extract it. This is not a claim that every package test would miss it; the POC recipe suite currently fails for its old consumer."),indent=2)+"\n")
