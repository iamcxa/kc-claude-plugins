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
('AC-1 S2', 'if (not fields.get("Observed", "").strip() or unrun) and not (unrun and only):', 'if False:', 'CaptainStepsTests.test_unobserved_steps_hold_even_when_ran_none_has_no_captain_reason'),
('AC-2 S4', 'for path in absolute_paths(fields.get("Asked", "")):', 'for path in []:', 'CaptainStepsTests.test_qnow_card_replay_checks_archived_path_and_unrecorded_fence'),
('AC-2 S5 command', 'for item in required_commands + links(coverage_text):', 'for item in links(message):', 'CaptainStepsTests.test_qnow_card_replay_checks_archived_path_and_unrecorded_fence'),
('AC-3 S5 link', 'for item in required_commands + links(coverage_text):', 'for item in required_commands:', 'CaptainStepsTests.test_message_commands_and_links_each_need_a_step'),
('AC-4 S3', 'if not reason or len(reason[1].split()) < 2:', 'if False:', 'CaptainStepsTests.test_a_captain_only_step_requires_its_reason'),
('AC-5 clause', 'missing = captain_step_problems(task, gate_text, summary if args.summary_file is not None else gate_text)', 'missing = []', 'CaptainGateTests.test_relay_412_holds_without_record_or_at_later_head_and_passes_at_dispatched_head'),
('AC-5 head', 'if candidate not in candidates:', 'if False:', 'CaptainGateTests.test_relay_412_holds_without_record_or_at_later_head_and_passes_at_dispatched_head'),
('AC-6 count', 'captain steps complete: {count} steps, {left} left to him', 'captain steps complete: 0 steps, {left} left to him', 'CaptainStepsTests.test_three_exercised_steps_pass_and_report_the_one_captain_step'),
('S1 text', 'if not request or request not in normalized(expanded):', 'if False:', 'CaptainStepsTests.test_asked_text_is_matched_with_whitespace_normalized'),
('Latest validation report', 'report = (VALIDATION_SECTION.findall(task.read_text()) or [""])[-1]', 'report = ""', 'CaptainGateTests.test_gate_checks_record_against_latest_validation_report_and_returns_input_errors'),
('Ran required', 'if not ran or (not unrun and not execution_recorded(ran)):', 'if False:', 'CaptainStepsTests.test_ran_is_required_even_with_an_observed_output'),
('Ran execution context', 'if not re.search(r"\\b(?:fresh\\s+shell|real\\s+browser)\\b", ran, re.I):', 'if False:', 'CaptainStepsTests.test_ran_records_execution_context_and_a_valid_utc_timestamp'),
('Ran UTC timestamp', 'if not stamp:\n        return False', 'if not stamp:\n        return True', 'CaptainStepsTests.test_ran_records_execution_context_and_a_valid_utc_timestamp'),
('Ran calendar validity', 'return datetime.datetime.fromisoformat(value).utcoffset() == datetime.timedelta(0)', 'return True', 'CaptainStepsTests.test_ran_records_execution_context_and_a_valid_utc_timestamp'),
('Ran gate wiring', 'if not ran or (not unrun and not execution_recorded(ran)):', 'if False:', 'CaptainGateTests.test_gate_holds_a_record_with_observed_output_but_no_ran_field'),
('Observed fence classification', 'required_commands = [body for body in commands if normalized(body) not in observed]', 'required_commands = commands', 'CaptainStepsTests.test_fenced_observed_output_passes_in_message_and_named_card'),
('Observed fence links', 'coverage_text = "\\n".join(FENCE.sub(lambda match: "" if normalized(match[3]) in observed else match[0], text)\n                              for text in texts)', 'coverage_text = expanded', 'CaptainStepsTests.test_links_in_recorded_output_fences_do_not_hide_unrecorded_message_links'),
('Unrecorded commands still held', 'for item in required_commands + links(coverage_text):', 'for item in links(coverage_text):', 'CaptainStepsTests.test_a_fence_that_does_not_match_observed_still_needs_a_recorded_step'),
('Every fence tag', 'return [body.strip() for _, _, body in FENCE.findall(text) if body.strip()]', 'return [body.strip() for _, language, body in FENCE.findall(text) if body.strip() and language.strip().lower() in ("", "sh", "sh run", "bash", "zsh", "shell", "console")]', 'CaptainStepsTests.test_non_shell_fences_need_a_recorded_step_unless_they_match_observed'),
('Longer closing fence', '(?:^[ \\t]*\\1[`~]*[ \\t]*$|\\Z)', '^[ \\t]*\\1[ \\t]*$', 'CaptainStepsTests.test_a_longer_closing_fence_still_requires_a_step'),
('Unclosed fence', '(?:^[ \\t]*\\1[`~]*[ \\t]*$|\\Z)', '^[ \\t]*\\1[ \\t]*$', 'CaptainStepsTests.test_an_unclosed_fence_still_requires_a_step'),
('Named-card Asked text', 'expanded = "\\n".join(texts)', 'expanded = message + "\\n" + "\\n".join(commands)', 'CaptainStepsTests.test_named_card_prose_link_matches_asked_and_holds_when_unrecorded'),
('Named-card unfenced links', 'for text in texts)', 'for text in texts[:1])', 'CaptainStepsTests.test_named_card_prose_link_matches_asked_and_holds_when_unrecorded'),
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
