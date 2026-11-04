import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

WT = Path(os.environ.get('CAPTAIN_STEPS_WORKTREE', '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-fo-tries-what-it-asks-the-captain'))
OUT = Path(__file__).resolve().parent
mutations = [
('AC-1 S2', 'if not fields.get("Observed", "").strip() and not (', 'if False and not (', 'CaptainStepsTests.test_unobserved_steps_hold_even_when_ran_none_has_no_captain_reason'),
('AC-2 S4', 'for path in absolute_paths(fields.get("Asked", "")):', 'for path in []:', 'CaptainStepsTests.test_qnow_card_replay_checks_archived_path_and_unrecorded_fence'),
('AC-2 S5 command', 'for item in commands + links(expanded):', 'for item in links(message):', 'CaptainStepsTests.test_qnow_card_replay_checks_archived_path_and_unrecorded_fence'),
('AC-3 S5 link', 'for item in commands + links(expanded):', 'for item in commands:', 'CaptainStepsTests.test_message_commands_and_links_each_need_a_step'),
('AC-4 S3', 'if not reason or len(reason[1].split()) < 2:', 'if False:', 'CaptainStepsTests.test_a_captain_only_step_requires_its_reason'),
('AC-5 clause', 'missing = captain_step_problems(task, gate_text, summary if args.summary_file is not None else gate_text)', 'missing = []', 'CaptainGateTests.test_relay_412_holds_without_record_or_at_later_head_and_passes_at_dispatched_head'),
('AC-5 head', 'if candidate not in candidates:', 'if False:', 'CaptainGateTests.test_relay_412_holds_without_record_or_at_later_head_and_passes_at_dispatched_head'),
('AC-6 count', 'captain steps complete: {count} steps, {left} left to him', 'captain steps complete: 0 steps, {left} left to him', 'CaptainStepsTests.test_three_exercised_steps_pass_and_report_the_one_captain_step'),
('S1 text', 'if not request or request not in normalized(expanded):', 'if False:', 'CaptainStepsTests.test_asked_text_is_matched_with_whitespace_normalized'),
('Latest validation report', 'report = (VALIDATION_SECTION.findall(task.read_text()) or [""])[-1]', 'report = ""', 'CaptainGateTests.test_gate_checks_record_against_latest_validation_report_and_returns_input_errors'),
]
results=[]
for i, (name, old, new, case) in enumerate(mutations, 1):
    with tempfile.TemporaryDirectory() as temp:
        package=Path(temp)/'kc-dev-flow-2'
        shutil.copytree(WT/'kc-dev-flow-2', package, ignore=shutil.ignore_patterns('__pycache__'))
        file=package/'scripts/delivery_gate.py'
        text=file.read_text()
        assert text.count(old) == 1, (name, old)
        file.write_text(text.replace(old,new))
        run=subprocess.run([sys.executable,'-B','-m','unittest','test_delivery_gate.'+case], cwd=package/'scripts', text=True, capture_output=True, env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        output=run.stdout+run.stderr
        assert run.returncode == 1 and 'FAIL:' in output, (name, run.returncode, output)
        log=OUT/f'mutation-{i}.log'
        log.write_text(output)
        results.append({'name':name,'test':case,'mutation':{'before':old,'after':new},'exit':run.returncode,'result':'expected test failure','log':log.name})
with tempfile.TemporaryDirectory() as temp:
    package=Path(temp)/'kc-dev-flow-2'
    shutil.copytree(WT/'kc-dev-flow-2', package, ignore=shutil.ignore_patterns('__pycache__'))
    file=package/'references/sd/workflow.md'
    file.write_text(file.read_text()+'\nextra\n')
    run=subprocess.run([sys.executable,'-B',str(package/'scripts/lint-skills.py'),'--root',str(package)], text=True,capture_output=True)
    output=run.stdout+run.stderr
    assert run.returncode == 1 and '5837' in output, (run.returncode,output)
    (OUT/'mutation-word-budget.log').write_text(output)
    results.append({'name':'AC-9 count','mutation':'Add one workflow word','exit':run.returncode,'result':'expected lint failure','log':'mutation-word-budget.log'})
(OUT/'mutation-results.json').write_text(json.dumps(results,indent=2)+'\n')
print(f'PASS: {len(results)} isolated mutations produced their expected failing check')
